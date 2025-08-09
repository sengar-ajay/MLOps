#!/usr/bin/env python3
"""
Continuous log tracker for the MLOps API.

Polls the API /logs endpoint and streams new log entries to stdout (and
optionally a file). Safe to leave running; press Ctrl+C to stop.
"""

from __future__ import annotations

import argparse
import sys
import time
from typing import Optional

import requests


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tail logs from the MLOps API")
    parser.add_argument(
        "--api-url",
        default="http://localhost:5000",
        help="Base URL of the API (default: http://localhost:5000)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=3.0,
        help="Polling interval in seconds (default: 3)",
    )
    parser.add_argument(
        "--level",
        default=None,
        help="Optional log level filter (e.g., INFO, WARNING, ERROR)",
    )
    parser.add_argument(
        "--module",
        default=None,
        help="Optional module filter (e.g., api, data_monitoring)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Max records fetched per poll (default: 200, max: 1000)",
    )
    parser.add_argument(
        "--to-file",
        dest="to_file",
        default=None,
        help="Optional path to append streamed logs",
    )
    return parser.parse_args(argv)


def format_log(rec: dict) -> str:
    ts = rec.get("timestamp", "-")
    level = rec.get("level", "-")
    module = rec.get("module", "-")
    message = rec.get("message", "")
    return f"[{ts}] {level:<7} {module}: {message}"


def stream_logs(args: argparse.Namespace) -> None:
    last_id: int = -1
    session = requests.Session()

    if args.to_file:
        print(f"Streaming logs to {args.to_file} (Ctrl+C to stop)...")
    else:
        print("Streaming logs (Ctrl+C to stop)...")

    try:
        while True:
            try:
                params = {"limit": max(1, min(args.limit, 1000))}
                if args.level:
                    params["level"] = args.level
                if args.module:
                    params["module"] = args.module

                resp = session.get(f"{args.api_url}/logs", params=params, timeout=10)
                resp.raise_for_status()
                payload = resp.json()
                logs = payload.get("logs", [])

                # Ensure ascending order and only print new rows
                logs_sorted = sorted(logs, key=lambda r: r.get("id", 0))
                new_logs = [r for r in logs_sorted if r.get("id", -1) > last_id]

                if new_logs:
                    for rec in new_logs:
                        line = format_log(rec)
                        print(line)
                        if args.to_file:
                            with open(args.to_file, "a", encoding="utf-8") as f:
                                f.write(line + "\n")
                        last_id = max(last_id, rec.get("id", last_id))

            except KeyboardInterrupt:
                print("\nStopped by user")
                return
            except Exception as exc:  # noqa: BLE001
                # Keep running even if the API is temporarily unavailable
                print(f"[warn] polling error: {exc}")

            time.sleep(args.interval)

    finally:
        session.close()


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    stream_logs(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

