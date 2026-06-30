# Live Read-Only Smoke Test

This is an **optional, maintainer-only** check that confirms the live X transport can fetch your own bookmarks read-only. Most users never need this — the [fixture dry-run](../README.md#run-the-fixture-dry-run) is the supported path. Do not run this in CI or on shared machines.

## Safety contract

This smoke test is read-only by construction:

- It issues **only** `GET /2/users/{id}/bookmarks`.
- It never likes, reposts, replies, follows, unfollows, deletes, unbookmarks, or otherwise mutates any account state.
- It reads credentials from local environment variables only.
- It writes output **only to `/tmp` or stdout** — never into the repository.
- The output may contain **private bookmark data**. Treat it as sensitive and do not commit, paste, or share it.

> Warning: `/2/users/{id}/bookmarks` returns the authenticated user's private bookmarks. Anything you save here can expose private reading habits and source links. Keep it out of the repo, PRs, and issue comments.

## Prerequisites

- Python 3.10+ and a local clone of this repo.
- An X developer app with bookmark read access and a **user-context** bearer token.
- Your numeric X user ID.

Required environment variables:

| Variable | Purpose |
|---|---|
| `X_API_USER_ID` | Your numeric X user ID (the `{id}` in the bookmarks endpoint). |
| `X_API_BEARER_TOKEN` | User-context bearer token. Kept local; never committed. |

Optional: `X_API_BASE_URL` (defaults to `https://api.x.com/2`).

## Run it

Set credentials in your shell only (do not write them into the repo):

```bash
export X_API_USER_ID=...        # numeric user ID
export X_API_BEARER_TOKEN=...   # user-context bearer token
```

Write the result to `/tmp` (recommended) so nothing lands in the working tree:

```bash
PYTHONPATH=src python3 -m bookmark_maxxing.cli ingest-x \
  --live \
  --format json \
  --max-pages 1 \
  > /tmp/bookmark-maxxing-smoke.json
```

Or inspect a single page directly on stdout:

```bash
PYTHONPATH=src python3 -m bookmark_maxxing.cli ingest-x --live --format markdown --max-pages 1
```

If you installed the console script (`pip install -e .`), replace the
`PYTHONPATH=src python3 -m bookmark_maxxing.cli` prefix with `bookmark-maxxing`.

## What success looks like

- The command exits `0`.
- The JSON output contains a `bookmarks` array and a `pages_fetched` count of `1`.
- Author usernames and `source_url` links are populated for valid items.

If credentials are missing or empty, the CLI exits cleanly **before any network call** with a message such as `X_API_BEARER_TOKEN is required ...`. That is expected and safe.

If you hit a `429`, you have been rate limited; the pipeline stops and surfaces the rate-limit metadata. Wait and retry with `--max-pages 1`.

## Clean up

```bash
rm -f /tmp/bookmark-maxxing-smoke.json
unset X_API_USER_ID X_API_BEARER_TOKEN
```

## Do not

- Do not commit `/tmp` output or any private bookmark export.
- Do not paste live output into PRs, issues, or chat.
- Do not store the bearer token in `.env` that is tracked by git (`.env` is already gitignored; keep it that way).
- Do not run live mode in automated CI.
