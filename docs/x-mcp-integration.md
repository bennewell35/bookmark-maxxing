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

This repository does not call either endpoint by default. The current implementation is a local scaffold for configuration, normalization, validation, and Markdown output.

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
- do not commit API keys, bearer tokens, OAuth tokens, cookies, or exported private data
- do not store raw private bookmarks in public examples
- preserve attribution when publishing public summaries
- do not imply source endorsement
- link back to original public posts when possible

## Local Setup

1. Copy `.env.example` to `.env`.
2. Fill only the variables required by your local MCP/API client.
3. For the `xurl mcp` bridge, set `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI` locally. Do not commit them.
4. Run local tests before adding live API access:

```bash
python3 -m unittest discover -s tests
```

5. Keep live ingestion behind explicit configuration.

## Current Scaffold

The current scaffold includes:

- config loading from environment variables
- bookmark metadata normalization
- metadata validation
- Markdown source map formatting
- TODOs for live X MCP/API fetching

See:

- `src/bookmark_maxxing/x_mcp.py`
- `tests/test_x_mcp.py`
- `docs/specs/x-mcp-bookmark-ingestion.md`

## Future Roadmap

- live X bookmark ingestion through configured MCP/API access
- pagination and rate-limit handling
- bookmark deduplication
- theme clustering
- source attribution scoring
- study guide generation
- article idea generation
- reusable skill document generation
- learning graph export
- memory integration
- export to Markdown, Notion, and GitHub

## References

- X API MCP server: <https://docs.x.com/tools/mcp>
- X bookmarks API overview: <https://docs.x.com/x-api/posts/bookmarks/introduction>
- xurl MCP bridge: <https://github.com/xdevplatform/xurl>
