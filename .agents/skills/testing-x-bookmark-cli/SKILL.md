---
name: testing-x-bookmark-cli
description: Test the Bookmark Maxxing read-only X bookmark CLI (ingest-x) end-to-end. Use when verifying CLI changes, the fixture dry-run flow, or the read-only/live-mode safety boundary.
---

# Testing the X Bookmark CLI (`bookmark-maxxing ingest-x`)

## What this app is
A read-only Python CLI that normalizes X bookmarks into a deterministic source map (Markdown or JSON). Fixture-backed dry-run by default; opt-in, env-gated live read-only mode that issues only `GET /2/users/{id}/bookmarks`. The CLI terminal IS the user interface, so record the **xterm** when a visual walkthrough is requested.

## Setup
- Python 3.10+, no third-party deps.
- Install: `python3 -m venv .venv && source .venv/bin/activate && pip install -e .`
- Or run from source without installing: `PYTHONPATH=src python3 -m bookmark_maxxing.cli ...`
- Fixture lives at `tests/fixtures/x_bookmarks_pages.json` (synthetic, public-safe).

## Golden-path test commands (no credentials needed)
```bash
bookmark-maxxing --help                       # expect: shows `ingest-x` subcommand
bookmark-maxxing ingest-x --dry-run --input tests/fixtures/x_bookmarks_pages.json --format json
bookmark-maxxing ingest-x --dry-run --input tests/fixtures/x_bookmarks_pages.json --format markdown
```
Expected JSON: 3 bookmarks (post_ids 1/2/3), `pages_fetched: 2`, first `author_username` = `ben_ai_eng`, `duplicates_removed: 0`, `truncated: false`, `validation_errors: []`.
Expected Markdown: starts with `<!-- pages_fetched=2 ... -->`, then `# X Bookmark Source Map`, then a 3-row table (`@ben_ai_eng`, `@systems_builder`, `@source_mapper`) each with a `[source](...)` link.

## Safety / read-only assertions
- Live mode without creds must exit non-zero with `X_API_BEARER_TOKEN is required ...`:
  `unset X_API_USER_ID X_API_BEARER_TOKEN; bookmark-maxxing ingest-x --live --format json; echo exit=$?` → `exit=1`
- Transport is GET-only: `grep -n 'method=' src/bookmark_maxxing/x_mcp.py` → only `method="GET"`.
- No mutation HTTP verbs: `grep -rn 'POST\|PUT\|PATCH\|DELETE' src/bookmark_maxxing/` → none.
- NEVER run a live X fetch without explicit user authorization + user-supplied env vars. If you do, write output ONLY to `/tmp` or stdout — never the repo. See `docs/live-smoke-test.md`.

## Unit checks (fast, shell-only, no recording)
```bash
PYTHONPATH=src python3 -m unittest discover -s tests
python3 -m compileall -q src tests
git diff --check
```

## Recording tips
- This is a CLI, so install a terminal if missing: `sudo apt-get install -y xterm`.
- Launch + maximize: `DISPLAY=:0 xterm -fa Monospace -fs 14 -geometry 120x35 -title "Demo" &` then `wmctrl -r Demo -b add,maximized_vert,maximized_horz`.
- Type commands into the xterm via the computer tool (not exec) so they're visible on screen, and annotate each test_start/assertion.

## Gotchas / future-proofing
- "X MCP" currently means the **direct X API v2 read-only** integration; a true **MCP-native** transport (`https://api.x.com/mcp`) may not be implemented yet — check the docs before claiming MCP support.
- Pushing `.github/workflows/*` may be blocked by the git proxy OAuth app lacking `workflow` scope. Workarounds that have worked: a user-provided `workflow`-scoped PAT pushed via the GitHub Contents API (`curl` to `api.github.com`), since a direct `git push` gets rewritten to the proxy by global `insteadOf` config.

## Devin Secrets Needed
- None for the fixture dry-run / safety tests (the default, recommended path).
- `X_API_USER_ID` + `X_API_BEARER_TOKEN` — only if explicitly authorized to run a live read-only smoke test.
- `GITHUB_WORKFLOW_TOKEN` (PAT with `repo` + `workflow`) — only if you need to push workflow files / cut releases through the proxy.
