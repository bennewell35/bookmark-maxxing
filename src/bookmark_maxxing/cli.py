"""Command-line interface for Bookmark Maxxing."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

from .x_mcp import (
    InMemoryXBookmarkClient,
    format_ingestion_result_json,
    format_ingestion_result_markdown,
    ingest_x_bookmarks,
    load_fixture_pages,
    load_x_mcp_config,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO | None = None) -> int:
    output = stdout or sys.stdout
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest-x":
        return _ingest_x(args, output)

    parser.print_help(output)
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bookmark-maxxing")
    subcommands = parser.add_subparsers(dest="command")

    ingest_x = subcommands.add_parser(
        "ingest-x",
        help="Normalize X bookmarks from a local fixture without making live X calls.",
    )
    ingest_x.add_argument("--dry-run", action="store_true", default=True)
    ingest_x.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Local JSON fixture containing X bookmark pages or items.",
    )
    ingest_x.add_argument("--format", choices=("markdown", "json"), default="markdown")
    ingest_x.add_argument("--max-pages", type=int, default=10)
    ingest_x.set_defaults(handler=_ingest_x)
    return parser


def _ingest_x(args: argparse.Namespace, output: TextIO) -> int:
    if not args.dry_run:
        raise SystemExit("Only --dry-run is currently supported for X ingestion.")

    with args.input.open("r", encoding="utf-8") as fixture_file:
        payload = json.load(fixture_file)

    client = InMemoryXBookmarkClient(load_fixture_pages(payload))
    result = ingest_x_bookmarks(
        client,
        load_x_mcp_config({}),
        max_pages=args.max_pages,
        require_auth=False,
    )

    if args.format == "json":
        output.write(format_ingestion_result_json(result))
    else:
        output.write(format_ingestion_result_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
