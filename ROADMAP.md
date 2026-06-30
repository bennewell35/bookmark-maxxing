# Roadmap

Bookmark Maxxing should grow in small proof slices.

The project is framework-first. Add concrete source adapters and recipes before building an app or broad CLI.

## Slice 1: LinkedIn Saved Posts

Goal: help people turn saved LinkedIn posts into reusable skills, study guides, and article ideas.

Why LinkedIn first:

- many builders save career, operating, product, and technical posts there
- the source is familiar to non-developers
- saved posts are often high-signal but rarely revisited
- manual read-only collection is easy to explain

Deliverables:

- `docs/adapters/linkedin-saved-posts.md`
- `recipes/linkedin-saves-to-skills.md`

Status: added as the first adapter recipe.

## Slice 2: GitHub Stars

Goal: turn starred repositories into build ideas, study plans, and reusable engineering skills.

Why:

- public/API-friendly
- developer-native
- easy to reproduce with `gh`

Deliverables:

- `docs/adapters/github-stars.md`
- `recipes/github-stars-to-skills.md`
- optional export script after the recipe is proven

## Slice 2A: X MCP Bookmark Ingestion

Goal: use X MCP/API access to ingest X bookmarks, normalize source metadata, preserve attribution, and generate learning artifacts.

Why:

- X bookmarks were the original source for Bookmark Maxxing
- X now exposes hosted MCP entry points for API and developer docs
- bookmark ingestion is directly aligned with the framework thesis

Deliverables:

- `docs/x-mcp-integration.md`
- `docs/specs/x-mcp-bookmark-ingestion.md`
- `src/bookmark_maxxing/x_mcp.py`
- `src/bookmark_maxxing/cli.py`
- `.env.example`
- pure local tests for normalization, metadata validation, pagination, rate-limit handling, deduplication, and Markdown/JSON formatting

Current status:

- read-only client boundary added
- fixture-backed dry-run ingestion added
- no live X MCP/API transport yet
- no mutation methods are exposed or accepted by the ingestion pipeline

MVP capabilities:

- X bookmark ingestion
- bookmark metadata normalization
- source attribution
- theme clustering
- Markdown summaries
- study guide generation
- reusable skill docs

Future capabilities:

- GitHub stars ingestion
- saved article ingestion
- learning graph
- memory integration
- export to Markdown, Notion, and GitHub

## Slice 3: Browser Bookmarks

Goal: support exported browser bookmarks without requiring any account access.

Deliverables:

- `docs/adapters/browser-bookmarks.md`
- `recipes/browser-bookmarks-to-study-guide.md`

## Slice 4: X Bookmarks

Goal: document the original Bookmark Maxxing workflow safely.

Boundary:

- authenticated browser only
- read-only extraction
- no likes, reposts, replies, follows, or unbookmarking

Deliverables:

- `docs/adapters/x-bookmarks.md`
- `recipes/x-bookmarks-to-article.md`

## Slice 5: First Runnable Tool

Only add tooling after several recipes are proven.

Likely first tool:

```bash
bookmark-maxxing normalize github-stars.json
```

The CLI should normalize exports. It should not require private scraping or account mutation.
