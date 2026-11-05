"""OrbitVigil Command Line Interface."""

import argparse
import json
import sys
from orbitvigil.checker import check_site_health, check_ssl_certificate, find_broken_links
from orbitvigil.server import start_monitor_server


def main():
    parser = argparse.ArgumentParser(
        prog="orbitvigil",
        description="OrbitVigil: Website Health, Uptime, SSL & Broken Link Monitor.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # PROBE command
    probe_parser = subparsers.add_parser("probe", help="Probe website health, uptime and security")
    probe_parser.add_argument("url", help="Target URL or domain")
    probe_parser.add_argument("--crawl", action="store_true", help="Crawl on-page links for broken 404 targets")
    probe_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # SSL command
    ssl_parser = subparsers.add_parser("ssl", help="Inspect SSL certificate validity and expiry")
    ssl_parser.add_argument("domain", help="Target domain (e.g. google.com)")
    ssl_parser.add_argument("--port", type=int, default=443, help="Port (default: 443)")

    # SERVE command
    serve_parser = subparsers.add_parser("serve", help="Launch interactive web monitor dashboard")
    serve_parser.add_argument("--port", type=int, default=8950, help="Port to bind (default: 8950)")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")

    args = parser.parse_args()

    if args.command == "serve" or args.command is None:
        port = getattr(args, "port", 8950)
        host = getattr(args, "host", "127.0.0.1")
        start_monitor_server(host=host, port=port)

    elif args.command == "probe":
        health = check_site_health(args.url)
        if args.crawl and health.get("body_preview"):
            health["links"] = find_broken_links(args.url, health["body_preview"])
        health.pop("body_preview", None)

        if args.json:
            print(json.dumps(health, indent=2))
        else:
            status_symbol = "🟢 ONLINE" if health["is_up"] else "🔴 OFFLINE"
            print(f"\n🛰️  OrbitVigil Health Probe: {health['url']}")
            print(f"Status:   {status_symbol} (HTTP {health['status_code']})")
            print(f"Latency:  {health['latency_ms']} ms")
            if health.get("ssl"):
                ssl_info = health["ssl"]
                print(f"SSL:      {'Valid' if ssl_info.get('valid') else 'Invalid'} ({ssl_info.get('days_remaining', 0)} days left)")
            print("\nSecurity Headers:")
            for k, (label, passed) in health.get("security_headers", {}).items():
                print(f"  [{'PASS' if passed else 'MISSING'}] {label}")

    elif args.command == "ssl":
        cert = check_ssl_certificate(args.domain, port=args.port)
        print(f"\n🔒 SSL Audit for {args.domain}:")
        print(f"Valid:          {cert['valid']}")
        print(f"Days Remaining: {cert['days_remaining']}")
        print(f"Expires At:     {cert['expires_at']}")
        print(f"Issuer:         {cert['issuer']}")
        print(f"Common Name:    {cert['common_name']}")


if __name__ == "__main__":
    main()
