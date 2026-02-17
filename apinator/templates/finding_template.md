# Finding Template

> Copia e compila per ogni vulnerabilità trovata.

---

## [VULN-XXX] Titolo breve e descrittivo

### Metadata

| Campo | Valore |
|-------|--------|
| **Severity** | 🔴 Critical / 🟠 High / 🟡 Medium / 🔵 Low / ℹ️ Informational |
| **CVSS v3.1 Score** | X.X (vettore completo) |
| **CVSS Vector** | `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N` |
| **CWE** | CWE-XXX — Nome |
| **OWASP API Top 10** | API1:2023 — Nome |
| **Endpoint** | `METHOD /api/v1/path` |
| **Data scoperta** | YYYY-MM-DD |

---

### Descrizione

Descrizione tecnica precisa della vulnerabilità. Spiega **cosa** è vulnerabile,
**perché** è vulnerabile e **come** può essere sfruttato.

---

### Impatto Business

Descrizione dell'impatto in linguaggio non tecnico, comprensibile al management.
Includi: dati esposti, utenti coinvolti, implicazioni legali (GDPR, ecc.),
stima del danno economico/reputazionale.

---

### Proof of Concept

Passi riproducibili step-by-step:

**Step 1** — Autentica con utente a basso privilegio:
```bash
curl -X POST https://target.com/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}'
# Salva il token restituito
```

**Step 2** — Sfrutta la vulnerabilità:
```bash
curl -X GET https://target.com/api/v1/resource/VICTIM_ID \
  -H "Authorization: Bearer ATTACKER_TOKEN"
```

**Response attesa:**
```json
{
  "id": "VICTIM_ID",
  "sensitive_data": "...",
  "status": 200
}
```

**Screenshot / Burp request-response** *(allegare)*

---

### Remediation

Indicazioni specifiche per la fix, con esempio di codice se possibile.

```python
# ❌ Vulnerabile
@app.get("/api/v1/users/{user_id}/data")
def get_user_data(user_id: int, token: str):
    return db.query(f"SELECT * FROM users WHERE id={user_id}")

# ✅ Corretto
@app.get("/api/v1/users/{user_id}/data")
def get_user_data(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return db.get_user(user_id)
```

**Riferimenti:**
- [OWASP — Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

---

### Note aggiuntive

Eventuali note: varianti del bug, endpoint correlati, suggerimenti per il remediation test.
