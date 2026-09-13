"""Local command-line entry point for the public Authority Lab v0."""

from __future__ import annotations

import argparse

from .model import HarnessStatus
from .runner import discover, format_trace, run_path


def main() -> int:
    parser = argparse.ArgumentParser(prog="authority-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="run one JSON fixture")
    run_parser.add_argument("fixture")
    all_parser = subparsers.add_parser("run-all", help="run all JSON fixtures in a directory")
    all_parser.add_argument("directory")
    args = parser.parse_args()

    paths = (args.fixture,) if args.command == "run" else discover(args.directory)
    if not paths:
        parser.error("no fixtures found")

    mismatch = False
    for index, path in enumerate(paths):
        result = run_path(path)
        if index:
            print()
        print(format_trace(result))
        mismatch = mismatch or result.status is HarnessStatus.CASE_MISMATCH
    return 1 if mismatch else 0


if __name__ == "__main__":
    raise SystemExit(main())
