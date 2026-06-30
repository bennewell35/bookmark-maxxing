# Bookmark Maxxing

Turn saved links into reusable skills.

Most people collect bookmarks.

Builders should be collecting skills.

Bookmark Maxxing is a framework for learning from the people and projects you save, then converting that learning into reusable artifacts.

Instead of letting saved links rot in a private pile, you use an AI coding agent or assistant to review them read-only, cluster the recurring ideas, attribute the sources, and extract what is worth turning into a skill, workflow, study guide, prompt, article, or small tool.

**Bookmarks are the input. Learning is the process. Skills are the output.**

## The Problem

Bookmarks feel useful when you save them.

Then they disappear.

Your X bookmarks, GitHub stars, saved Slack posts, newsletters, docs, and read-later queue become a pile of good intentions. You collected signal, but you never converted it.

Bookmark Maxxing solves the conversion problem:

```text
saved links -> recurring themes -> reusable skills
```

## Before / After

Before:

```text
I saved 100 AI engineering posts and never looked at them again.
```

After:

```text
I turned 100 saved posts into:

- 5 recurring themes
- a source map
- 5 reusable skills
- a study guide
- an article
- a public framework others can reuse
```

Example:

```text
Theme: AI work is moving from prompts to operating loops.
Skill: Design repeatable systems, not better prompts.
```

That is the core move: every interesting theme should become something reusable.

## 30-Second Example

Input:

```text
10 saved posts about agent memory, context rot, and instruction files.
```

Bookmark Maxxing output:

| Extracted Pattern | Reusable Skill |
|---|---|
| Memory files rot when every lesson gets stored forever. | Cut memory down to durable rules that earn their place. |
| Repeated lessons are more useful in shared docs, tests, or runbooks. | Convert anything you do twice into a reusable skill. |
| Context should be pulled when needed, not pushed into every session. | Separate always-on instructions from searchable reference material. |

Final artifact:

```text
Skill: Convert repeated lessons into docs, tests, skills, or runbooks.

Trigger: The same lesson appears in more than one saved link or work session.

Workflow:
1. Name the repeated lesson.
2. Decide where future work will look first.
3. Add the lesson there.
4. Remove duplicate or stale memory.

Proof gate: A future session can find the rule without relying on hidden memory.
```

## Who This Is For

Bookmark Maxxing is for builders who save more than they can process:

- engineers
- founders
- researchers
- designers
- operators
- writers
- students
- open-source maintainers

If you already save useful ideas, this gives you a way to turn those saved ideas into durable work.

Bookmark Maxxing is an open-source framework for converting saved posts, articles, docs, repos, and notes into practical artifacts:

- skills
- workflows
- prompts
- checklists
- operating principles
- article drafts
- small tools

## Why

Bookmarks usually die in private piles.

The better workflow is conversion:

1. Collect useful signals during the week.
2. Run a read-only analysis pass.
3. Cluster recurring ideas.
4. Attribute the people and sources.
5. Convert patterns into reusable skills, workflows, prompts, or articles.
6. Publish the artifact so the idea compounds.

This is not a news recap. It is a skill extraction system.

## Quick Start

1. Pick a source: X bookmarks, GitHub stars, saved Slack posts, browser bookmarks, newsletters, or read-later apps.
2. Choose a boundary: this week, last 100 links, or one topic.
3. Use [`prompts/read-bookmarks.md`](prompts/read-bookmarks.md) to extract and cluster the source material.
4. Use [`prompts/extract-skills.md`](prompts/extract-skills.md) to turn recurring themes into skill candidates.
5. Use [`templates/skill-card.md`](templates/skill-card.md) for each reusable skill.
6. Use [`prompts/write-article.md`](prompts/write-article.md) and [`templates/article-template.md`](templates/article-template.md) to publish the weekly issue.

## Try the X Bookmark CLI (v0.1)

Bookmark Maxxing ships a small, read-only CLI that normalizes X bookmarks into a deterministic source map (Markdown or JSON). It runs fully offline against a local fixture by default and never writes to X.

### What it does

- Reads X-shaped bookmark records through one of three read-only paths.
- Normalizes them into a consistent shape, preserving author and source attribution.
- Validates and deduplicates them.
- Emits a deterministic Markdown source map or JSON document you can feed into the framework prompts.

### Three read-only ingestion paths

| Path | Flag | Network | Auth | When to use |
|---|---|---|---|---|
| Fixture dry-run | `--dry-run --input <file>` (default) | none | none | Safe demo, tests, CI |
| Direct X API v2 | `--live` | `GET /2/users/{id}/bookmarks` | `X_API_USER_ID` + `X_API_BEARER_TOKEN` | A bearer token, no MCP tooling |
| Official X MCP | `--mcp` | `xurl mcp` → `https://api.x.com/mcp` | xurl OAuth (`xurl auth oauth2`) | The hosted X MCP server |

All three are strictly read-only: only a bookmarks **list** operation is ever invoked, and any mutation method/tool is rejected.

### Install locally

Requires Python 3.10+. No third-party dependencies.

```bash
git clone https://github.com/bennewell35/bookmark-maxxing.git
cd bookmark-maxxing

# Option A: run from source (no install)
PYTHONPATH=src python3 -m bookmark_maxxing.cli --help

# Option B: install the console script into a virtualenv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
bookmark-maxxing --help
```

### Run the fixture dry-run

The default path is fixture-backed and local-only — safe to run anytime:

```bash
bookmark-maxxing ingest-x --dry-run --input tests/fixtures/x_bookmarks_pages.json --format json
```

Or, without installing:

```bash
PYTHONPATH=src python3 -m bookmark_maxxing.cli ingest-x \
  --dry-run --input tests/fixtures/x_bookmarks_pages.json --format json
```

Use `--format markdown` for a ready-to-paste source map.

### Optional: live read-only mode

Live mode is strictly opt-in, read-only, and never enabled by default. It issues only `GET /2/users/{id}/bookmarks` and requires credentials supplied through local environment variables:

```bash
export X_API_USER_ID=...        # your numeric X user ID
export X_API_BEARER_TOKEN=...   # user-context bearer token, kept local

bookmark-maxxing ingest-x --live --format json --max-pages 1 > /tmp/my-bookmarks.json
```

Live mode rules:

- Requires `X_API_USER_ID` and `X_API_BEARER_TOKEN` set locally. Never commit them.
- Output may contain **private bookmark data** — write it to `/tmp` or stdout, never into the repo.
- Do not commit generated output. `.gitignore` already excludes `.env`, `tmp/`, `raw/`, and `exports/private/`.

### Optional: official X MCP mode

`--mcp` ingests bookmarks through the official hosted **X MCP server** (`https://api.x.com/mcp`), reached via the open-source [`xurl mcp`](https://github.com/xdevplatform/xurl) bridge. It invokes only a read-only bookmarks **list** tool and refuses any mutating tool, so it cannot add, remove, or change bookmarks.

Try it fully offline first — replay a recorded MCP response with no network or credentials:

```bash
bookmark-maxxing ingest-x --mcp --input tests/fixtures/x_mcp_bookmarks.json --format json
```

Live MCP fetch (opt-in, read-only) needs xurl installed and authenticated once:

```bash
# one-time: install xurl and log in (OAuth2)
npm install -g @xdevplatform/xurl      # or: brew install --cask xdevplatform/tap/xurl
xurl auth oauth2                       # add --headless on a remote box

export X_API_USER_ID=...               # your numeric X user ID
bookmark-maxxing ingest-x --mcp --format json --max-pages 1 > /tmp/my-bookmarks.json
```

MCP mode notes:

- The bridge command defaults to `xurl mcp https://api.x.com/mcp`; override with `X_MCP_BRIDGE_COMMAND` (e.g. to use `npx -y @xdevplatform/xurl mcp ...`).
- X does not publish a stable tool name for the bookmarks list operation. The default is `get_users_id_bookmarks`; override with `X_MCP_BOOKMARKS_TOOL` (discover names via the bridge's `tools/list`).
- If xurl is missing or unauthenticated, `--mcp` exits cleanly with a clear message and makes no partial calls.
- Output may contain **private bookmark data** — write it to `/tmp` or stdout, never into the repo.

See [`docs/live-smoke-test.md`](docs/live-smoke-test.md) for a safe live read-only smoke test, and [`docs/x-mcp-integration.md`](docs/x-mcp-integration.md) for the full integration reference.

### Turn bookmarks into skills: `extract`

`ingest-x` produces a normalized **source map** (it does not invent themes or summaries). `bookmark-maxxing extract` is the next step: it takes that ingested JSON and runs one of the framework prompts (`prompts/`) against it, injecting your bookmarks (source-map table + structured JSON) into the prompt.

By default it is **compose-only** — it emits a complete, copy-paste-ready prompt for any LLM/agent and calls no model:

```bash
bookmark-maxxing ingest-x --mcp --input tests/fixtures/x_mcp_bookmarks.json --format json > /tmp/bm.json
bookmark-maxxing extract --input /tmp/bm.json --prompt extract-skills > /tmp/extract-skills.prompt.md
```

Prompts: `extract-skills` (default), `read-bookmarks`, `write-article`.

Add `--llm` to actually run the prompt through a local open-source model and get real themes/skills back. It speaks the OpenAI-compatible `/chat/completions` API (stdlib only, no extra deps), defaulting to a local **[Ollama](https://ollama.com)** server:

```bash
# one-time: install Ollama and pull a small open model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1            # or qwen2.5, llama3.2, etc.

bookmark-maxxing extract --input /tmp/bm.json --prompt extract-skills --llm > /tmp/skills.md
```

`extract` notes:

- Point it at any OpenAI-compatible server (llama.cpp, vLLM, LM Studio, OpenRouter) via `BOOKMARK_MAXXING_LLM_BASE_URL` + `BOOKMARK_MAXXING_LLM_MODEL` (and `BOOKMARK_MAXXING_LLM_API_KEY` for hosted ones); override the model inline with `--llm-model`.
- If no LLM server is reachable, `--llm` exits cleanly with a clear message and emits nothing — it never fakes output.
- The model only *reads* your already-ingested bookmarks; `extract` makes no calls to X and cannot mutate any source platform.
- LLM output may reflect **private bookmark data** — write it to `/tmp` or stdout, never into the repo.

## The Framework

Bookmark Maxxing has six steps:

```text
Collect -> Extract -> Cluster -> Convert -> Publish -> Compound
```

Read the full framework: [`docs/framework.md`](docs/framework.md)

## Recipes

Start with one source and one output.

- [LinkedIn saved posts to skills](recipes/linkedin-saves-to-skills.md)

## Adapters

Adapters explain how to safely collect from specific sources.

- [LinkedIn saved posts](docs/adapters/linkedin-saved-posts.md)
- [X MCP integration](docs/x-mcp-integration.md)

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for the small-slice project plan.

## Core Rule

Every theme needs a skill.

```text
Theme: AI is moving from prompts to operating loops.
Skill: Design repeatable systems, not better prompts.
```

If a theme does not produce a reusable behavior, it may be interesting, but it is not Bookmark Maxxing yet.

## Repository Map

```text
bookmark-maxxing/
  README.md
  AGENTS.md
  LICENSE
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  GOVERNANCE.md
  SECURITY.md
  SUPPORT.md
  .github/
    workflows/
      ci.yml
  docs/
    adapters/
      linkedin-saved-posts.md
    specs/
      x-mcp-bookmark-ingestion.md
    framework.md
    quickstart.md
    publishing-playbook.md
    x-mcp-integration.md
    live-smoke-test.md
    release-checklist.md
  recipes/
    linkedin-saves-to-skills.md
  src/
    bookmark_maxxing/
      cli.py
      x_mcp.py
  tests/
    fixtures/
      x_bookmarks_pages.json
      x_mcp_bookmarks.json
    test_x_mcp.py
  pyproject.toml
  prompts/
    read-bookmarks.md
    extract-skills.md
    write-article.md
  templates/
    article-template.md
    skill-card.md
    source-map.md
  issues/
    001-turning-bookmarks-into-skills/
      article.md
      source-map.md
      skills.md
  schemas/
    bookmark-item.schema.json
```

## Community

Before contributing, read:

- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- [`GOVERNANCE.md`](GOVERNANCE.md)
- [`SECURITY.md`](SECURITY.md)
- [`SUPPORT.md`](SUPPORT.md)

## Public Positioning

Short version:

> Bookmark Maxxing turns saved links into reusable skills for builders.

Long version:

> Bookmark Maxxing is an open-source framework for analyzing saved links, clustering recurring ideas, attributing the sources, and converting the best patterns into reusable skills, workflows, prompts, and operating principles.

## Safety Rules

- Keep collection read-only.
- Do not like, repost, reply, follow, subscribe, unbookmark, or mutate saved items.
- Treat saved posts as inspiration, not proof.
- Attribute people and sources clearly.
- Do not turn every interesting post into a process.
- A durable skill needs repetition, risk reduction, or clear reuse.

## Status

This repo is framework-first, and now ships a small read-only CLI as its first working slice.

The current useful version is:

- a clear method
- reusable prompts
- templates
- weekly examples
- source attribution
- a read-only X bookmark CLI with three paths: fixture dry-run (default), direct X API v2, and official X MCP

The next layers extend the CLI to normalize exports from GitHub, Slack, newsletters, and browser bookmarks. See [`docs/release-checklist.md`](docs/release-checklist.md) for what remains before the v0.1.0 release.
