# 🛰️ OrbitVigil

[![CI](https://github.com/Scempyyy/OrbitVigil/actions/workflows/ci.yml/badge.svg)](https://github.com/Scempyyy/OrbitVigil/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Zero External Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](#zero-dependencies)

> **Real-time website health, uptime SLA, SSL certificate expiration, and broken link crawler with interactive status console.**

---

## ⚡ What is OrbitVigil?

**OrbitVigil** is a lightweight, zero-dependency site reliability and security monitor designed to keep your domains online and safe:

- ⏱️ **Uptime & Latency Prober**: Measures latency (ms), HTTP response codes, and server availability.
- 🔒 **SSL/TLS Expiration Watch**: Calculates exact days remaining until certificate expiration, issuer CA, and validity status.
- 🛡️ **OWASP Security Headers Audit**: Validates HSTS (`Strict-Transport-Security`), Content Security Policy (`CSP`), `X-Frame-Options`, and MIME sniffing protection.
- 🔗 **Broken Link Crawler**: Extracts internal links from HTML and automatically verifies each target for dead 404/500 endpoints.
- 📊 **Local Cyber Dashboard**: Clean dark-mode status page with instant audit reporting and JSON download.
- 🚀 **Zero Dependencies**: Pure Python standard library (`ssl`, `socket`, `urllib.request`, `html.parser`).

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────┐
│                   OrbitVigil Probe                     │
│                Target: https://domain.com              │
└───────────────────────────┬────────────────────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
┌──────────────┐     ┌─────────────┐      ┌─────────────┐
│ Uptime & SLA │     │  SSL Audit  │      │ Link Engine │
│ Latency (ms) │     │ Cert Expiry │      │ 404 Crawler │
│ HTTP Codes   │     │ CA Issuer   │      │ Head Probes │
└──────┬───────┘     └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │   Security Header Inspector   │
            │ • HSTS  • CSP  • X-Frame      │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │   Interactive Web Dashboard   │
            │   http://localhost:8950       │
            └───────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Launch Web Dashboard

```bash
# Clone the repository
git clone https://github.com/Scempyyy/OrbitVigil.git
cd OrbitVigil

# Start the dashboard server
python3 orbitvigil.py serve
```

Open your browser to **`http://localhost:8950`**.

### 2. Terminal CLI Probe

Probe any URL directly from your command line:

```bash
# Full health check with security headers
python3 orbitvigil.py probe https://github.com

# Probe with broken link crawl
python3 orbitvigil.py probe https://github.com --crawl

# Inspect SSL certificate expiration
python3 orbitvigil.py ssl github.com

# Output as JSON for automated cron alerts
python3 orbitvigil.py probe https://github.com --json
```

---

## 🧪 Testing

```bash
python3 -m unittest discover tests -v
```

---

## 📄 License

OrbitVigil is open-source software licensed under the **[MIT License](LICENSE)**. Built by [Scempyyy](https://github.com/Scempyyy).
