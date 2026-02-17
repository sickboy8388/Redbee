#!/usr/bin/env bash
# ============================================================
# redbee — Subdomain & API Recon Pipeline
# ============================================================
# Prerequisites: subfinder, amass, dnsx, httpx, katana, gau
#
# Usage:
#   chmod +x subdomain_pipeline.sh
#   ./subdomain_pipeline.sh target.com
# ============================================================

set -euo pipefail

TARGET="${1:-}"
if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 <domain>"
  echo "  Es.: $0 target.com"
  exit 1
fi

OUTDIR="recon_${TARGET}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

echo "============================================================"
echo "  redbee — Recon Pipeline"
echo "  Target : $TARGET"
echo "  Output : $OUTDIR/"
echo "============================================================"
echo

# ── STEP 1: Subdomain Enumeration ──────────────────────────────
echo "[1/6] Subdomain enumeration..."
subfinder -d "$TARGET" -all -silent -o "$OUTDIR/subs_subfinder.txt" 2>/dev/null || true
amass enum -passive -d "$TARGET" -o "$OUTDIR/subs_amass.txt" 2>/dev/null || true
cat "$OUTDIR"/subs_*.txt 2>/dev/null | sort -u > "$OUTDIR/subs_all.txt"
echo "      Found $(wc -l < "$OUTDIR/subs_all.txt") unique subdomains"

# ── STEP 2: DNS Resolution ──────────────────────────────────────
echo "[2/6] Resolving live hosts..."
dnsx -silent -l "$OUTDIR/subs_all.txt" -o "$OUTDIR/subs_live.txt" 2>/dev/null || true
echo "      Live hosts: $(wc -l < "$OUTDIR/subs_live.txt")"

# ── STEP 3: HTTP Probing ────────────────────────────────────────
echo "[3/6] HTTP probing..."
httpx -silent -l "$OUTDIR/subs_live.txt" \
  -title -status-code -tech-detect \
  -o "$OUTDIR/http_hosts.txt" 2>/dev/null || true

# Filter hosts that look like APIs
grep -iE "api|rest|graphql|swagger|v[0-9]" "$OUTDIR/http_hosts.txt" \
  > "$OUTDIR/api_hosts.txt" || true
echo "      HTTP hosts : $(wc -l < "$OUTDIR/http_hosts.txt")"
echo "      API-like   : $(wc -l < "$OUTDIR/api_hosts.txt")"

# ── STEP 4: Historical URLs ─────────────────────────────────────
echo "[4/6] Fetching historical URLs (gau)..."
gau "$TARGET" 2>/dev/null | \
  grep -iE "api|v[0-9]|rest|graphql|endpoint|swagger" | \
  sort -u > "$OUTDIR/historical_urls.txt" || true
echo "      Historical API URLs: $(wc -l < "$OUTDIR/historical_urls.txt")"

# ── STEP 5: Swagger/OpenAPI Discovery ──────────────────────────
echo "[5/6] Spec file discovery..."
SPEC_PATHS=(
  "/swagger.json" "/swagger.yaml" "/openapi.json" "/openapi.yaml"
  "/api-docs" "/api-docs/swagger.json" "/v1/api-docs" "/v2/api-docs"
  "/.well-known/openapi" "/graphql" "/graphiql" "/playground"
)

> "$OUTDIR/spec_found.txt"
while IFS= read -r host; do
  for path in "${SPEC_PATHS[@]}"; do
    url="${host}${path}"
    status=$(curl -s -o /dev/null -w "%{http_code}" \
      --connect-timeout 5 --max-time 8 "$url" 2>/dev/null || echo "000")
    if [[ "$status" =~ ^(200|201)$ ]]; then
      echo "$url [HTTP $status]" | tee -a "$OUTDIR/spec_found.txt"
    fi
  done
done < <(awk '{print $1}' "$OUTDIR/http_hosts.txt" 2>/dev/null | head -50)

echo "      Spec files found: $(wc -l < "$OUTDIR/spec_found.txt")"

# ── STEP 6: Summary ─────────────────────────────────────────────
echo "[6/6] Generating summary..."
cat > "$OUTDIR/SUMMARY.md" << EOF
# Recon Summary — $TARGET
**Date**: $(date)

## Stats
| Metric | Count |
|--------|-------|
| Subdomains found | $(wc -l < "$OUTDIR/subs_all.txt") |
| Live hosts | $(wc -l < "$OUTDIR/subs_live.txt") |
| HTTP hosts | $(wc -l < "$OUTDIR/http_hosts.txt") |
| API-like hosts | $(wc -l < "$OUTDIR/api_hosts.txt") |
| Historical API URLs | $(wc -l < "$OUTDIR/historical_urls.txt") |
| Spec files found | $(wc -l < "$OUTDIR/spec_found.txt") |

## API Hosts
\`\`\`
$(cat "$OUTDIR/api_hosts.txt" 2>/dev/null || echo "none")
\`\`\`

## Spec Files Found
\`\`\`
$(cat "$OUTDIR/spec_found.txt" 2>/dev/null || echo "none")
\`\`\`
EOF

echo
echo "============================================================"
echo "  DONE — Output in $OUTDIR/"
echo "  Next step: kr scan -w routes-large.kite --filename $OUTDIR/api_hosts.txt"
echo "============================================================"
