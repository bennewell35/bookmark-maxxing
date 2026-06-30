"""Command-line interface for Bookmark Maxxing."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

from .x_mcp import (
    InMemoryXBookmarkClient,
    XAPIReadOnlyBookmarkClient,
    XBookmarkRequest,
    XMCPError,
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
        help="Normalize X bookmarks from a fixture or explicit read-only live fetch.",
    )
    ingest_x.add_argument("--dry-run", action="store_true", default=True)
    ingest_x.add_argument(
        "--live",
        action="store_true",
        help="Use read-only live X API transport. Requires env auth and never mutates X.",
    )
    ingest_x.add_argument(
        "--input",
        type=Path,
        help="Local JSON fixture containing X bookmark pages or items.",
    )
    ingest_x.add_argument("--format", choices=("markdown", "json"), default="markdown")
    ingest_x.add_argument("--max-pages", type=int, default=10)
    ingest_x.add_argument("--user-id", help="X user ID override for live read-only fetches.")
    ingest_x.set_defaults(handler=_ingest_x)
    return parser


def _ingest_x(args: argparse.Namespace, output: TextIO) -> int:
    if args.live:
        config = load_x_mcp_config()
        try:
            client = XAPIReadOnlyBookmarkClient(config)
            result = ingest_x_bookmarks(
                client,
                config,
                max_pages=args.max_pages,
                request=XBookmarkRequest(user_id=args.user_id or config.user_id),
            )
        except XMCPError as error:
            raise SystemExit(str(error)) from error
    else:
        if args.input is None:
            raise SystemExit("--input is required unless --live is set.")
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
