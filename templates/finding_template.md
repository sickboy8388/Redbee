# Finding Template

> Copy and fill in for every vulnerability discovered.

---

## [VULN-XXX] Short and descriptive title

### Metadata

| Field | Value |
|-------|-------|
| **Severity** | 🔴 Critical / 🟠 High / 🟡 Medium / 🔵 Low / ℹ️ Informational |
| **CVSS v3.1 Score** | X.X (full vector) |
| **CVSS Vector** | `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N` |
| **CWE** | CWE-XXX — Name |
| **OWASP API Top 10** | API1:2023 — Name |
| **Endpoint** | `METHOD /api/v1/path` |
| **Date found** | YYYY-MM-DD |

---

### Description

Precise technical description of the vulnerability. Explain **what** is vulnerable,
**why** it is vulnerable, and **how** it can be exploited.

---

### Business Impact

Description of the impact in plain language, understandable to management.
Include: exposed data, affected users, legal implications (GDPR, HIPAA, etc.),
estimated financial/reputational damage.

---

### Proof of Concept

Step-by-step reproducible walkthrough:

**Step 1** — Authenticate as a low-privilege user:
```bash
curl -X POST https://target.com/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}'
# Save the returned token
```

**Step 2** — Exploit the vulnerability:
```bash
curl -X GET https://target.com/api/v1/resource/VICTIM_ID \
  -H "Authorization: Bearer ATTACKER_TOKEN"
```

**Expected response:**
```json
{
  "id": "VICTIM_ID",
  "sensitive_data": "...",
  "status": 200
}
```

**Screenshot / Burp request-response** *(attach)*

---

### Remediation

Specific fix guidance with code example where possible.

```python
# ❌ Vulnerable
@app.get("/api/v1/users/{user_id}/data")
def get_user_data(user_id: int, token: str):
    return db.query(f"SELECT * FROM users WHERE id={user_id}")

# ✅ Fixed
@app.get("/api/v1/users/{user_id}/data")
def get_user_data(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return db.get_user(user_id)
```

**References:**
- [OWASP — Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

---

### Additional Notes

Any extra notes: bug variants, related endpoints, suggestions for remediation testing.
