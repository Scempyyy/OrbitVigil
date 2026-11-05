"""Core health check logic: Uptime, SSL, Security Headers, and Link crawling."""

import ssl
import socket
import datetime
import urllib.request
import urllib.parse
import urllib.error
import time
from html.parser import HTMLParser
from typing import Dict, Any, List, Set, Optional


class LinkExtractor(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.links: Set[str] = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, val in attrs:
                if attr == "href" and val:
                    val = val.strip()
                    if val.startswith("mailto:") or val.startswith("tel:") or val.startswith("javascript:") or val.startswith("#"):
                        continue
                    full_url = urllib.parse.urljoin(self.base_url, val)
                    self.links.add(full_url)


def check_ssl_certificate(hostname: str, port: int = 443, timeout: float = 5.0) -> Dict[str, Any]:
    """Inspects SSL certificate expiry, issuer, and validity."""
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        not_after_str = cert.get("notAfter")
        expire_date = datetime.datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
        now = datetime.datetime.now(datetime.timezone.utc)
        days_left = (expire_date - now).days

        issuer_dict = dict(x[0] for x in cert.get("issuer", ()))
        subject_dict = dict(x[0] for x in cert.get("subject", ()))

        return {
            "valid": True,
            "days_remaining": days_left,
            "expires_at": expire_date.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "issuer": issuer_dict.get("organizationName", issuer_dict.get("commonName", "Unknown")),
            "common_name": subject_dict.get("commonName", hostname),
            "status": "HEALTHY" if days_left > 30 else ("WARNING" if days_left > 7 else "CRITICAL"),
            "error": None,
        }
    except Exception as e:
        return {
            "valid": False,
            "days_remaining": 0,
            "expires_at": None,
            "issuer": None,
            "common_name": hostname,
            "status": "FAILED",
            "error": str(e),
        }


def check_site_health(url: str, timeout: float = 6.0) -> Dict[str, Any]:
    """Performs comprehensive uptime check, latency test, and security header audit."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or url

    # Measure uptime & latency
    start = time.perf_counter()
    headers_req = {"User-Agent": "OrbitVigil-HealthBot/1.0"}
    req = urllib.request.Request(url, headers=headers_req, method="GET")

    status_code = 0
    latency_ms = 0.0
    body_content = ""
    resp_headers = {}
    is_up = False

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            status_code = resp.status
            is_up = (200 <= status_code < 400)
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            # Read first 150KB for link extraction
            body_content = resp.read(150 * 1024).decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        status_code = e.code
        is_up = False
        resp_headers = {k.lower(): v for k, v in e.headers.items()}
    except Exception as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "url": url,
            "hostname": hostname,
            "is_up": False,
            "status_code": 0,
            "latency_ms": latency_ms,
            "ssl": {"valid": False, "error": str(e)},
            "security_headers": {},
            "broken_links": [],
            "error": str(e),
        }

    # Security header evaluation
    security_headers = {
        "strict-transport-security": ("HSTS Enabled", "strict-transport-security" in resp_headers),
        "content-security-policy": ("Content Security Policy (CSP)", "content-security-policy" in resp_headers),
        "x-frame-options": ("Clickjacking Protection (X-Frame-Options)", "x-frame-options" in resp_headers),
        "x-content-type-options": ("MIME Sniffing Protection", "x-content-type-options" in resp_headers),
    }

    # SSL Inspection if HTTPS
    ssl_info = None
    if parsed.scheme == "https":
        ssl_info = check_ssl_certificate(hostname, port=parsed.port or 443)

    return {
        "url": url,
        "hostname": hostname,
        "is_up": is_up,
        "status_code": status_code,
        "latency_ms": latency_ms,
        "ssl": ssl_info,
        "security_headers": security_headers,
        "body_preview": body_content,
        "error": None,
    }


def find_broken_links(url: str, body_html: str, max_links: int = 15) -> List[Dict[str, Any]]:
    """Discovers on-page hyperlinks and probes their availability."""
    parser = LinkExtractor(base_url=url)
    try:
        parser.feed(body_html)
    except Exception:
        pass

    candidates = list(parser.links)[:max_links]
    results = []

    for link in candidates:
        status = 0
        ok = False
        try:
            req = urllib.request.Request(link, headers={"User-Agent": "OrbitVigil-LinkBot/1.0"}, method="HEAD")
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                status = resp.status
                ok = (200 <= status < 400)
        except urllib.error.HTTPError as e:
            status = e.code
            ok = False
        except Exception:
            status = 0
            ok = False

        results.append({
            "link": link,
            "status_code": status,
            "ok": ok,
        })

    return results
