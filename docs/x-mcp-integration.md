# X MCP Integration

Bookmark Maxxing started with X bookmarks. X MCP integration is the direct next step: ingest saved X posts, preserve attribution, and turn saved attention into reusable learning artifacts.

The X API MCP endpoint is:

```text
https://api.x.com/mcp
```

The X developer docs MCP endpoint is:

```text
https://docs.x.com/mcp
```

This repository does not call either endpoint by default. The implementation provides three read-only ingestion paths behind one client boundary: a fixture-backed dry-run, an explicit direct X API v2 transport, and an official **X MCP** transport that talks to `https://api.x.com/mcp` through the `xurl mcp` bridge. All paths share the same normalization, validation, deduplication, pagination, rate-limit handling, and Markdown/JSON output.

## Three Read-Only Paths

| Path | CLI | Transport | Auth |
|---|---|---|---|
| Fixture dry-run | `ingest-x --dry-run --input <file>` | local JSON, no network | none |
| Direct X API v2 | `ingest-x --live` | `GET /2/users/{id}/bookmarks` | `X_API_USER_ID` + `X_API_BEARER_TOKEN` |
| Official X MCP | `ingest-x --mcp` | `xurl mcp` → `https://api.x.com/mcp` | xurl OAuth (`xurl auth oauth2`) |

The MCP path is implemented by `XMCPBookmarkClient`, which calls a single read-only bookmarks list tool through an `MCPToolCaller`. In production the caller is `StdioMCPBridge` (a newline-delimited JSON-RPC bridge over `xurl mcp`); tests and the offline demo use `InMemoryMCPToolCaller` to replay recorded `tools/call` results. The client refuses any tool name that implies mutation (`add`, `remove`, `delete`, `like`, `repost`, `follow`, `create`, …) and exposes no mutation methods.

### Official X MCP usage

```bash
# Offline demo (no network, no credentials):
bookmark-maxxing ingest-x --mcp --input tests/fixtures/x_mcp_bookmarks.json --format json

# Live read-only via xurl (one-time `xurl auth oauth2` first):
export X_API_USER_ID=123456
bookmark-maxxing ingest-x --mcp --format json --max-pages 1 > /tmp/bookmarks.json
```

Configuration:

- `X_MCP_BRIDGE_COMMAND` — overrides the bridge command (default `xurl mcp https://api.x.com/mcp`).
- `X_MCP_BOOKMARKS_TOOL` — overrides the read-only bookmarks tool name (default `get_users_id_bookmarks`; discover via `tools/list`).

## What It Enables

X MCP integration can eventually support:

- ingesting authenticated-user X bookmarks
- normalizing bookmark metadata
- preserving author attribution and original source links
- clustering bookmarks by topic or recurring theme
- generating Markdown summaries
- producing study guides, article ideas, and reusable skill docs
- exporting outputs to Markdown, Notion, or GitHub

## How It Fits Bookmark Maxxing

Bookmark Maxxing converts saved links into reusable skills.

X bookmarks are one of the highest-signal sources because builders often save:

- technical threads
- product ideas
- AI workflows
- operating principles
- prompts
- reference repos
- research links
- people worth studying

The integration should preserve the original source context while converting repeated patterns into durable artifacts.

```text
X bookmarks -> normalized source map -> themes -> skills/study guides/articles
```

## Expected Inputs

The ingestion layer should eventually accept bookmark records from X MCP/API access.

Minimum expected fields:

- bookmark ID or post ID
- post text
- author username
- author display name
- source URL
- creation timestamp if available
- bookmark capture timestamp if available
- public metrics if available and safe
- linked URLs if available

The local scaffold accepts dictionaries shaped like this:

```json
{
  "id": "2071272699251298483",
  "text": "don't collect bookmarks. collect skills.",
  "author": {
    "username": "ben_ai_eng",
    "name": "Ben Newell"
  },
  "created_at": "2026-06-28T16:41:08Z",
  "url": "https://x.com/ben_ai_eng/status/2071272699251298483"
}
```

## Expected Outputs

MVP outputs:

- normalized bookmark JSON
- Markdown source maps
- Markdown summaries
- study guide outlines
- reusable skill docs

Later outputs:

- learning graph nodes
- Notion pages
- GitHub issues
- GitHub markdown archives
- memory or skill updates

## Required Environment Variables

Do not commit credentials.

The project should read configuration from environment variables only.

```text
X_MCP_SERVER_URL=https://api.x.com/mcp
X_DOCS_MCP_SERVER_URL=https://docs.x.com/mcp
X_API_BASE_URL=https://api.x.com/2
X_API_USER_ID=
X_API_BEARER_TOKEN=
X_API_CLIENT_ID=
X_API_CLIENT_SECRET=
X_API_REDIRECT_URI=
```

Only set variables required by the actual local MCP client or API auth flow you are using.

If you use the official `xurl mcp` bridge, it also expects OAuth variables with these generic names:

```text
CLIENT_ID=
CLIENT_SECRET=
REDIRECT_URI=http://localhost:8080/callback
```

## Security and Privacy

Bookmarks are private user data unless the user explicitly publishes an output.

Rules:

- keep ingestion read-only by default
- do not like, repost, reply, follow, block, mute, unbookmark, or change account state
- reject client objects that expose obvious mutation methods
- do not commit API keys, bearer tokens, OAuth tokens, cookies, or exported private data
- do not store raw private bookmarks in public examples
- preserve attribution when publishing public summaries
- do not imply source endorsement
- link back to original public posts when possible

## Read-Only Guarantee

The current code has one client boundary:

```text
XReadOnlyBookmarkClient.fetch_bookmarks_page(request)
```

The ingestion pipeline rejects clients that expose obvious mutation methods such as `like`, `reply`, `repost`, `follow`, `unfollow`, `delete`, or `unbookmark`.

Tests use synthetic clients and fixtures only. The default CLI path uses `InMemoryXBookmarkClient`, which reads local JSON fixtures. The explicit live path uses `XAPIReadOnlyBookmarkClient`, which issues authenticated `GET /2/users/{id}/bookmarks` requests and maps responses into local page objects. There is no browser, cookie, scraping, account mutation, or write method in the transport.

## Local Setup

1. Copy `.env.example` to `.env`.
2. Fill only the variables required by your local MCP/API client.
3. For the `xurl mcp` bridge, set `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI` locally. Do not commit them.
4. Run local tests before adding live API access:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

5. Keep live ingestion behind explicit configuration.

## Dry-Run Usage

The default runnable path is fixture-backed and local-only.

```bash
PYTHONPATH=src python3 -m bookmark_maxxing.cli ingest-x \
  --dry-run \
  --input tests/fixtures/x_bookmarks_pages.json \
  --format markdown
```

JSON output is also supported:

```bash
PYTHONPATH=src python3 -m bookmark_maxxing.cli ingest-x \
  --dry-run \
  --input tests/fixtures/x_bookmarks_pages.json \
  --format json
```

After installing the package locally, the same command is exposed as:

```bash
bookmark-maxxing ingest-x --dry-run --input tests/fixtures/x_bookmarks_pages.json
```

## Explicit Live Read-Only Usage

Live fetching is opt-in. It requires an X user ID and a user-context bearer token stored locally in environment variables. Do not commit `.env`.

```bash
export X_API_USER_ID=123456
export X_API_BEARER_TOKEN=...

PYTHONPATH=src python3 -m bookmark_maxxing.cli ingest-x \
  --live \
  --format json \
  --max-pages 1
```

The live transport:

- uses only HTTP `GET`
- calls `/2/users/{id}/bookmarks`
- passes `max_results` and `pagination_token`
- parses `meta.next_token`
- preserves `x-rate-limit-*` and `retry-after` metadata
- returns normalized local objects through the same ingestion pipeline

## Current Scaffold

The current scaffold includes:

- config loading from environment variables
- auth configuration validation
- read-only client protocol
- direct read-only X API transport
- request and response types
- pagination abstraction
- rate-limit metadata parsing
- bookmark metadata normalization
- metadata validation
- bookmark deduplication
- Markdown source map formatting
- JSON output formatting
- dry-run CLI backed by local fixtures
- explicit live CLI path guarded by env configuration
- official X MCP transport (`XMCPBookmarkClient`) via the `xurl mcp` stdio bridge
- offline MCP demo + tests backed by recorded `tools/call` fixtures

See:

- `src/bookmark_maxxing/x_mcp.py`
- `src/bookmark_maxxing/cli.py`
- `tests/test_x_mcp.py`
- `tests/fixtures/x_bookmarks_pages.json`
- `tests/fixtures/x_mcp_bookmarks.json`
- `docs/specs/x-mcp-bookmark-ingestion.md`

## Known Limitations

- The MCP bookmarks tool name is configurable (`X_MCP_BOOKMARKS_TOOL`) because X does not publish a stable name; the default may need adjustment, discoverable via `tools/list`.
- Live MCP mode requires `xurl` to be installed and authenticated once (`xurl auth oauth2`).
- Fixture payloads are intentionally small and public-safe.
- Theme clustering and study-guide generation still happen through the framework prompts, not this client boundary.
- Auth validation only checks that local configuration exists; it does not verify credentials.
- Rate-limit handling currently stops on `429` and preserves parsed header metadata for callers.

## Future Roadmap

Delivered:

- live X bookmark ingestion through configured read-only API transport
- official X MCP-native transport (`XMCPBookmarkClient` via `xurl mcp`)
- pagination and rate-limit handling
- bookmark deduplication

Planned:

- bookmark-folder-aware read-only listing
- theme clustering
- source attribution scoring
- study guide generation
- article idea generation
- reusable skill document generation
- learning graph export
- memory integration
- export to Markdown, Notion, and GitHub

## MCP-Native Transport (delivered)

`XMCPBookmarkClient` is an MCP-native transport behind `XReadOnlyBookmarkClient` that:

- reads configuration (bridge command, tool name) from environment variables only
- fetches authenticated-user bookmarks without mutating account state
- maps MCP `tools/call` results into `XBookmarkPage`
- preserves pagination tokens across pages
- records no raw private bookmark exports in the repo
- is covered by tests with recorded synthetic MCP fixtures, not live X calls

## References

- X API MCP server: <https://docs.x.com/tools/mcp>
- X bookmarks API overview: <https://docs.x.com/x-api/posts/bookmarks/introduction>
- xurl MCP bridge: <https://github.com/xdevplatform/xurl>
