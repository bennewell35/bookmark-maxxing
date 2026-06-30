# X MCP Bookmark Ingestion

## Goal

Use X MCP/API access to ingest bookmarks and turn them into reusable learning artifacts.

## MVP Capabilities

- ingest X bookmarks
- normalize bookmark metadata
- preserve author attribution and source links
- cluster bookmarks by theme
- generate Markdown summaries
- produce study guides, article ideas, and reusable skill docs

## Non-Goals

- no account mutation
- no liking, reposting, replying, following, or unbookmarking
- no committed secrets, tokens, cookies, or exported private data
- no live API calls without explicit environment configuration
- no public examples containing private bookmark exports

## Inputs

Expected bookmark input fields:

- post ID
- post text
- author username
- author display name
- post URL
- created timestamp
- linked URLs
- optional public metrics
- optional bookmark capture timestamp

## Outputs

Initial outputs:

- normalized bookmark records
- validation errors
- Markdown source maps
- Markdown summaries

Future outputs:

- study guides
- article outlines
- skill cards
- learning graph nodes
- Markdown/Notion/GitHub exports

## Implementation Plan

1. Normalize bookmark records from raw X-shaped dictionaries.
2. Validate required fields.
3. Format source maps in Markdown.
4. Add explicit TODOs where live MCP/API access is required.
5. Add local tests for pure logic.
6. Add live ingestion only after auth and environment variables are configured.

## Environment Variables

```text
X_MCP_SERVER_URL=https://api.x.com/mcp
X_DOCS_MCP_SERVER_URL=https://docs.x.com/mcp
X_API_BEARER_TOKEN=
X_API_CLIENT_ID=
X_API_CLIENT_SECRET=
X_API_REDIRECT_URI=
CLIENT_ID=
CLIENT_SECRET=
REDIRECT_URI=http://localhost:8080/callback
```

## Acceptance Criteria

- Local tests pass without network access.
- No secrets are committed.
- Bookmark normalization preserves author attribution and source URL.
- Markdown output is deterministic.
- Live API integration remains behind explicit TODOs/configuration.
