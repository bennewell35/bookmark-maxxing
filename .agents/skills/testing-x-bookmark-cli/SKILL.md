---
name: testing-x-bookmark-cli
description: Test the Bookmark Maxxing read-only X bookmark CLI (ingest-x) end-to-end. Use when verifying CLI changes, the fixture dry-run flow, the official X MCP path, or the read-only/live-mode safety boundary.
---

# Testing the X Bookmark CLI (`bookmark-maxxing ingest-x`)

## What this app is
A read-only Python CLI that normalizes X bookmarks into a deterministic source map (Markdown or JSON). It has three read-only ingestion paths: fixture dry-run (offline, default), direct X API v2 (`--live`, `GET /2/users/{id}/bookmarks`), and official X MCP (`--mcp`, via the `xurl mcp` bridge to `https://api.x.com/mcp`). The CLI terminal IS the user interface, so record the **xterm** when a visual walkthrough is requested.

## Setup
- Python 3.10+, no third-party deps.
- Install: `python3 -m venv .venv && source .venv/bin/activate && pip install -e .`
- Or run from source without installing: `PYTHONPATH=src python3 -m bookmark_maxxing.cli ...`
- Fixtures (synthetic, public-safe): `tests/fixtures/x_bookmarks_pages.json` (simple shape), `tests/fixtures/x_mcp_bookmarks.json` (recorded MCP `tools/call` results, 2 pages, cursor `mcp-page-2`).

## Golden-path test commands (no credentials needed)
```bash
bookmark-maxxing --help                       # expect: shows `ingest-x` subcommand
# Fixture dry-run:
bookmark-maxxing ingest-x --dry-run --input tests/fixtures/x_bookmarks_pages.json --format json
bookmark-maxxing ingest-x --dry-run --input tests/fixtures/x_bookmarks_pages.json --format markdown
# Official X MCP, fully offline (replays recorded MCP results):
bookmark-maxxing ingest-x --mcp --input tests/fixtures/x_mcp_bookmarks.json --format json
bookmark-maxxing ingest-x --mcp --input tests/fixtures/x_mcp_bookmarks.json --format markdown
```
Expected JSON (both dry-run and MCP fixture): 3 bookmarks (post_ids 1/2/3), `pages_fetched: 2` (proves the 2nd page cursor was followed), first `author_username` = `ben_ai_eng`, then `systems_builder`, `source_mapper`, `duplicates_removed: 0`, `truncated: false`, `validation_errors: []`.
Expected Markdown: starts with `<!-- pages_fetched=2 ... -->`, then `# X Bookmark Source Map`, then a 3-row table each with a `[source](...)` link. Note: in the MCP fixture, the `source_mapper` row comes from an MCP `content` text-block (vs `structuredContent` for the others), so a missing 3rd row means the text-block mapping branch is broken.

## Safety / read-only assertions
- Live API mode without creds must exit non-zero: `unset X_API_USER_ID X_API_BEARER_TOKEN; bookmark-maxxing ingest-x --live --format json; echo exit=$?` -> `exit=1` with `X_API_BEARER_TOKEN is required ...`.
- Live MCP mode without xurl must exit cleanly (no faked success): `X_API_USER_ID=42 bookmark-maxxing ingest-x --mcp --format json; echo exit=$?` -> `exit=1` with `MCP bridge command not found: 'xurl'. ... or set X_MCP_BRIDGE_COMMAND.` (xurl is usually NOT installed in the dev env, so this is the expected live-MCP result there).
- `--live` and `--mcp` are mutually exclusive: `bookmark-maxxing ingest-x --live --mcp --format json; echo exit=$?` -> `exit=1`, `Use either --live or --mcp, not both.`.
- Transport is GET-only: `grep -n 'method=' src/bookmark_maxxing/x_mcp.py` -> only `method="GET"`.
- No mutation HTTP verbs: `grep -rn 'POST\|PUT\|PATCH\|DELETE' src/bookmark_maxxing/` -> none.
- MCP read-only: mutating tool names are rejected by `assert_read_only_mcp_tool` (config `X_MCP_BOOKMARKS_TOOL`); the MCP client exposes no mutation methods.
- NEVER run a live X/MCP fetch without explicit user authorization + user-supplied env/xurl auth. If you do, write output ONLY to `/tmp` or stdout, never the repo. See `docs/live-smoke-test.md`.

## Unit checks (fast, shell-only, no recording)
```bash
PYTHONPATH=src python3 -m unittest discover -s tests   # ~51 tests as of PR #5
python3 -m compileall -q src tests
git diff --check
```

## Recording tips
- This is a CLI, so install a terminal if missing: `sudo apt-get install -y xterm wmctrl`.
- Launch a clean shell with an alias so the visible command reads `bookmark-maxxing ...`:
  write an rcfile that sets `PYTHONPATH=src`, a short `PS1`, and `alias bookmark-maxxing='python3 -m bookmark_maxxing.cli'`, then
  `DISPLAY=:0 xterm -fa Monospace -fs 14 -geometry 140x38 -title Demo -e bash --rcfile /tmp/demo_bashrc &` and `wmctrl -r Demo -b add,maximized_vert,maximized_horz`.
- Type commands into the xterm via the computer tool (not exec) so they're visible on screen, and annotate each test_start/assertion.
- Long JSON scrolls off-screen; pipe to `tail -6` or `python3 -c '...'` to surface just the summary fields when you need them legible in-frame.

## Gotchas / future-proofing
- As of PR #5, "X MCP" includes a real MCP-native transport (`XMCPBookmarkClient` -> `StdioMCPBridge` over `xurl mcp https://api.x.com/mcp`) in addition to the direct X API v2 path. The exact MCP bookmarks tool name is not published by X, so it defaults to `get_users_id_bookmarks` and is overridable via `X_MCP_BOOKMARKS_TOOL` (discover via the bridge's `tools/list`); the default may need adjustment for a real live run.
- The live MCP path needs `xurl` installed and authenticated once (`xurl auth oauth2`, add `--headless` on a remote box). If it's missing, expect the clean `exit=1` above rather than a real fetch.
- Pushing `.github/workflows/*` may be blocked by the git proxy OAuth app lacking `workflow` scope. Workaround that has worked: a user-provided `workflow`-scoped PAT pushed via the GitHub Contents API (`curl` to `api.github.com`), since a direct `git push` gets rewritten to the proxy by global `insteadOf` config.

## Devin Secrets Needed
- None for the fixture dry-run / MCP-fixture / safety tests (the default, recommended paths).
- `X_API_USER_ID` + `X_API_BEARER_TOKEN` -- only if explicitly authorized to run a live direct-API read-only smoke test.
- For a live MCP read-only smoke test: xurl installed + authenticated (no Devin secret; user/maintainer machine state), plus `X_API_USER_ID`.
- `GITHUB_WORKFLOW_TOKEN` (PAT with `repo` + `workflow`) -- only if you need to push workflow files / cut releases through the proxy.
