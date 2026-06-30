"""Command-line interface for Bookmark Maxxing."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Sequence, TextIO

from .extract import (
    DEFAULT_EXTRACT_PROMPT,
    EXTRACT_PROMPTS,
    ComposeOnlyPromptRunner,
    ExtractError,
    LLMPromptRunner,
    load_llm_config,
    run_extract,
)
from .x_mcp import (
    InMemoryMCPToolCaller,
    InMemoryXBookmarkClient,
    XAPIReadOnlyBookmarkClient,
    XBookmarkRequest,
    XMCPBookmarkClient,
    XMCPError,
    format_ingestion_result_json,
    format_ingestion_result_markdown,
    ingest_x_bookmarks,
    load_fixture_pages,
    load_mcp_fixture_results,
    load_x_mcp_config,
    validate_x_mcp_config,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO | None = None) -> int:
    output = stdout or sys.stdout
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest-x":
        return _ingest_x(args, output)
    if args.command == "extract":
        return _extract(args, output)

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
        help="Use read-only live X API v2 transport. Requires env auth and never mutates X.",
    )
    ingest_x.add_argument(
        "--mcp",
        action="store_true",
        help=(
            "Use the official X MCP server (read-only) via the xurl mcp bridge. "
            "With --input, replays a recorded MCP fixture offline."
        ),
    )
    ingest_x.add_argument(
        "--input",
        type=Path,
        help="Local JSON fixture containing X bookmark pages, items, or MCP results.",
    )
    ingest_x.add_argument("--format", choices=("markdown", "json"), default="markdown")
    ingest_x.add_argument("--max-pages", type=int, default=10)
    ingest_x.add_argument("--user-id", help="X user ID override for live read-only fetches.")
    ingest_x.set_defaults(handler=_ingest_x)

    extract = subcommands.add_parser(
        "extract",
        help=(
            "Compose a ready-to-run Bookmark Maxxing prompt from ingested bookmarks. "
            "Injects the source map + structured items into a prompt; runs no model by default."
        ),
    )
    extract.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON output of `ingest-x ... --format json` (or a list of normalized bookmarks).",
    )
    extract.add_argument(
        "--prompt",
        choices=EXTRACT_PROMPTS,
        default=DEFAULT_EXTRACT_PROMPT,
        help=f"Which framework prompt to run (default: {DEFAULT_EXTRACT_PROMPT}).",
    )
    extract.add_argument(
        "--prompts-dir",
        type=Path,
        default=Path("prompts"),
        help="Directory containing the prompt files (default: ./prompts).",
    )
    extract.add_argument(
        "--llm",
        action="store_true",
        help=(
            "Run the composed prompt through an OpenAI-compatible LLM server "
            "(default: local Ollama at http://localhost:11434/v1) and emit its output. "
            "Without this flag, the composed prompt is emitted unchanged."
        ),
    )
    extract.add_argument(
        "--llm-model",
        help="Override the LLM model name (default from env or 'llama3.1').",
    )
    extract.add_argument(
        "--output",
        type=Path,
        help="Write the result to this file instead of stdout.",
    )
    extract.set_defaults(handler=_extract)
    return parser


def _ingest_x(args: argparse.Namespace, output: TextIO) -> int:
    if args.live and args.mcp:
        raise SystemExit("Use either --live or --mcp, not both.")

    if args.mcp:
        result = _ingest_via_mcp(args)
    elif args.live:
        result = _ingest_via_live_api(args)
    else:
        result = _ingest_via_fixture(args)

    if args.format == "json":
        output.write(format_ingestion_result_json(result))
    else:
        output.write(format_ingestion_result_markdown(result))
    return 0


def _ingest_via_live_api(args: argparse.Namespace):
    config = load_x_mcp_config()
    try:
        client = XAPIReadOnlyBookmarkClient(config)
        return ingest_x_bookmarks(
            client,
            config,
            max_pages=args.max_pages,
            request=XBookmarkRequest(user_id=args.user_id or config.user_id),
        )
    except XMCPError as error:
        raise SystemExit(str(error)) from error


def _ingest_via_mcp(args: argparse.Namespace):
    if args.input is not None:
        return _ingest_via_mcp_fixture(args)

    config = load_x_mcp_config()
    try:
        validate_x_mcp_config(config)
        client = XMCPBookmarkClient(config)
        return ingest_x_bookmarks(
            client,
            config,
            max_pages=args.max_pages,
            require_auth=False,
            request=XBookmarkRequest(user_id=args.user_id or config.user_id),
        )
    except XMCPError as error:
        raise SystemExit(str(error)) from error


def _ingest_via_mcp_fixture(args: argparse.Namespace):
    with args.input.open("r", encoding="utf-8") as fixture_file:
        payload = json.load(fixture_file)

    config = load_x_mcp_config({})
    try:
        caller = InMemoryMCPToolCaller(load_mcp_fixture_results(payload))
        client = XMCPBookmarkClient(
            config, caller=caller
        )
        return ingest_x_bookmarks(
            client,
            config,
            max_pages=args.max_pages,
            require_auth=False,
            request=XBookmarkRequest(user_id=args.user_id or "fixture-user"),
        )
    except XMCPError as error:
        raise SystemExit(str(error)) from error


def _ingest_via_fixture(args: argparse.Namespace):
    if args.input is None:
        raise SystemExit("--input is required unless --live or --mcp is set.")
    with args.input.open("r", encoding="utf-8") as fixture_file:
        payload = json.load(fixture_file)

    client = InMemoryXBookmarkClient(load_fixture_pages(payload))
    return ingest_x_bookmarks(
        client,
        load_x_mcp_config({}),
        max_pages=args.max_pages,
        require_auth=False,
    )


def _extract(args: argparse.Namespace, output: TextIO) -> int:
    if args.llm:
        config = load_llm_config()
        if args.llm_model:
            config = replace(config, model=args.llm_model)
        runner = LLMPromptRunner(config)
    else:
        runner = ComposeOnlyPromptRunner()

    try:
        result = run_extract(
            input_path=args.input,
            prompts_dir=args.prompts_dir,
            prompt_name=args.prompt,
            runner=runner,
        )
    except ExtractError as error:
        raise SystemExit(str(error)) from error

    if not result.endswith("\n"):
        result += "\n"

    if args.output is not None:
        args.output.write_text(result, encoding="utf-8")
        label = "LLM output for" if args.llm else "composed"
        output.write(f"Wrote {label} '{args.prompt}' prompt to {args.output}\n")
    else:
        output.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
