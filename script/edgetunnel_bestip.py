#!/usr/bin/env python3
"""Convert CloudflareSpeedTest result.csv to EdgeTunnel bestip.txt."""

from __future__ import annotations

import argparse
import csv
import ipaddress
import os
import tempfile
from pathlib import Path


IP_COLUMN = "IP 地址"
COLO_COLUMN = "地区码"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate EdgeTunnel plain text API from CloudflareSpeedTest CSV."
    )
    parser.add_argument("--csv", default="result.csv", help="CloudflareSpeedTest CSV path.")
    parser.add_argument("--output", default="bestip.txt", help="Output text API path.")
    parser.add_argument("--port", type=int, default=443, help="EdgeTunnel node port.")
    parser.add_argument("--limit", type=int, default=20, help="Max nodes to write.")
    parser.add_argument(
        "--fallback-colo",
        default="CF",
        help="Label used when CloudflareSpeedTest does not return a colo.",
    )
    return parser.parse_args()


def host_port(ip: str, port: int) -> str:
    parsed = ipaddress.ip_address(ip)
    if parsed.version == 6:
        return f"[{parsed.compressed}]:{port}"
    return f"{parsed.compressed}:{port}"


def normalize_colo(value: str, fallback: str) -> str:
    colo = value.strip().upper()
    if not colo or colo == "N/A":
        return fallback.strip().upper()
    return colo


def read_nodes(csv_path: Path, port: int, limit: int, fallback_colo: str) -> list[str]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    nodes: list[str] = []
    seen: set[str] = set()

    with csv_path.open("r", encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {csv_path}")
        missing = {IP_COLUMN, COLO_COLUMN} - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            ip = (row.get(IP_COLUMN) or "").strip()
            if not ip or ip in seen:
                continue
            label = normalize_colo(row.get(COLO_COLUMN) or "", fallback_colo)
            nodes.append(f"{host_port(ip, port)}#{label}")
            seen.add(ip)
            if len(nodes) >= limit:
                break

    if not nodes:
        raise ValueError(f"No valid nodes found in {csv_path}")
    return nodes


def write_atomic(output_path: Path, lines: list[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(output_path.parent), prefix=f".{output_path.name}.", text=True
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fp:
            fp.write("\n".join(lines))
            fp.write("\n")
        os.replace(tmp_name, output_path)
    except Exception:
        try:
            os.unlink(tmp_name)
        finally:
            raise


def main() -> None:
    args = parse_args()
    if args.port <= 0 or args.port > 65535:
        raise ValueError("--port must be between 1 and 65535")
    if args.limit <= 0:
        raise ValueError("--limit must be greater than 0")

    nodes = read_nodes(
        Path(args.csv),
        port=args.port,
        limit=args.limit,
        fallback_colo=args.fallback_colo,
    )
    write_atomic(Path(args.output), nodes)
    print(f"Wrote {len(nodes)} EdgeTunnel nodes to {args.output}")


if __name__ == "__main__":
    main()
