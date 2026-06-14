#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

: "${CFST_BIN:=./cfst}"
: "${CFST_THREADS:=200}"
: "${CFST_PING_TIMES:=4}"
: "${CFST_DOWNLOAD_COUNT:=20}"
: "${CFST_DOWNLOAD_TIME:=5}"
: "${CFST_PORT:=443}"
: "${CFST_MAX_DELAY:=300}"
: "${CFST_MAX_LOSS_RATE:=0}"
: "${CFST_MIN_SPEED:=0}"
: "${CFST_IP_FILE:=ip.txt}"
: "${CFST_IP:=}"
: "${CFST_URL:=}"
: "${CFST_COLO:=}"
: "${CFST_RESULT_CSV:=result.csv}"
: "${BESTIP_OUTPUT:=bestip.txt}"
: "${BESTIP_LIMIT:=$CFST_DOWNLOAD_COUNT}"
: "${BESTIP_FALLBACK_COLO:=CF}"

if [[ ! -x "$CFST_BIN" ]]; then
  go build -o cfst .
  CFST_BIN="./cfst"
fi

args=(
  -n "$CFST_THREADS"
  -t "$CFST_PING_TIMES"
  -dn "$CFST_DOWNLOAD_COUNT"
  -dt "$CFST_DOWNLOAD_TIME"
  -tp "$CFST_PORT"
  -tl "$CFST_MAX_DELAY"
  -tlr "$CFST_MAX_LOSS_RATE"
  -sl 0
  -p 0
  -o "$CFST_RESULT_CSV"
)

if [[ -n "$CFST_URL" ]]; then
  args+=(-url "$CFST_URL")
fi

if [[ -n "$CFST_IP" ]]; then
  args+=(-ip "$CFST_IP")
else
  args+=(-f "$CFST_IP_FILE")
fi

if [[ -n "$CFST_COLO" ]]; then
  args+=(-httping -cfcolo "$CFST_COLO")
fi

"$CFST_BIN" "${args[@]}"

python3 script/edgetunnel_bestip.py \
  --csv "$CFST_RESULT_CSV" \
  --output "$BESTIP_OUTPUT" \
  --port "$CFST_PORT" \
  --limit "$BESTIP_LIMIT" \
  --fallback-colo "$BESTIP_FALLBACK_COLO" \
  --min-speed "$CFST_MIN_SPEED"
