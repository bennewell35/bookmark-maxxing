# Bookmark Maxxing

Turn saved links into reusable skills.

Most people collect bookmarks. Builders should be collecting skills.

Bookmark Maxxing is an open-source framework for converting saved posts, articles, docs, repos, and notes into practical artifacts:

- skills
- workflows
- prompts
- checklists
- operating principles
- article drafts
- small tools

**Bookmarks are the input. Skills are the output.**

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

## The Framework

Bookmark Maxxing has six steps:

```text
Collect -> Extract -> Cluster -> Convert -> Publish -> Compound
```

Read the full framework: [`docs/framework.md`](docs/framework.md)

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
  CONTRIBUTING.md
  docs/
    framework.md
    quickstart.md
    publishing-playbook.md
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

This repo is framework-first. It is intentionally not an app yet.

The first useful version is:

- a clear method
- reusable prompts
- templates
- weekly examples
- source attribution

If the workflow keeps proving useful, the next layer can be a CLI for normalizing exports from X, GitHub, Slack, newsletters, and browser bookmarks.
