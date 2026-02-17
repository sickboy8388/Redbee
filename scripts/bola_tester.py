#!/usr/bin/env python3
"""
redbee — BOLA/IDOR Automated Tester
======================================
Tests Broken Object Level Authorization by comparing responses
from two different users on the same endpoints/IDs.

Usage:
    python3 bola_tester.py

Config:
    Edit the variables in the CONFIG section before running.
"""

import requests
import json
import time
from typing import Generator

# ── CONFIG ──────────────────────────────────────────────────────────────────

BASE_URL     = "https://target.com/api/v1"
USER_A_TOKEN = "eyJhbGciOiJIUzI1NiJ9..."   # legitimate user token (owner)
USER_B_TOKEN = "eyJhbGciOiJIUzI1NiJ9..."   # attacker token
DELAY        = 0.2                          # seconds between requests (avoids rate limiting)
TIMEOUT      = 10

# Endpoints to test — {id} will be replaced with each ID from the list
ENDPOINTS = [
    "/users/{id}/profile",
    "/users/{id}/documents",
    "/orders/{id}",
    "/invoices/{id}",
    "/accounts/{id}",
]

# ── ID GENERATORS ────────────────────────────────────────────────────────────

def integer_ids(start: int = 1, end: int = 200) -> Generator:
    """Generates sequential integer IDs."""
    for i in range(start, end + 1):
        yield str(i)

def id_list(ids: list) -> Generator:
    """Uses a predefined list of IDs (e.g. collected during testing)."""
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

        # Interesting cases
        if r_b.status_code == 200:
            if r_a.status_code == 200 and r_b.text == r_a.text:
                status = "🔴 BOLA CONFIRMED"
                detail = "UserB accessed and received the same data as UserA"
            elif r_a.status_code != 200:
                status = "🟠 SUSPECT — UserB gets 200, UserA does not"
                detail = f"UserA={r_a.status_code}, UserB=200"
            else:
                status = "🟡 CHECK — both 200 but different response"
                detail = "Manual review recommended"

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
    print("  redbee — BOLA/IDOR Tester")
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
        print(f"\n  Output saved to: {output_file}")
        for f in all_findings:
            print(f"\n  {f['status']}")
            print(f"  URL     : {f['url']}")
            print(f"  Detail  : {f['detail']}")
            print(f"  Preview : {f['response_b_preview'][:100]}...")
    else:
        print("\n  No BOLA findings detected.")

    print()


if __name__ == "__main__":
    run()
