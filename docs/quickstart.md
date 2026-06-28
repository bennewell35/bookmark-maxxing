# Quickstart

Use this when you want to turn one pile of saved links into a publishable issue.

## Step 1: Pick a Source

Examples:

- X bookmarks
- GitHub stars
- saved Slack posts
- browser bookmarks
- newsletter links
- read-later queue

Pick a boundary:

- this week
- last 100 items
- one topic
- one source

## Step 2: Extract

Use [`../prompts/read-bookmarks.md`](../prompts/read-bookmarks.md).

Capture:

- author
- URL
- date
- title/text
- linked artifact
- why it matters

## Step 3: Cluster

Group the bookmarks by repeated theme.

Use this rule:

```text
If the idea only appears once and does not change future behavior, keep it as a note.
If the idea repeats and changes future behavior, convert it into a skill.
```

## Step 4: Convert

Use [`../prompts/extract-skills.md`](../prompts/extract-skills.md).

For each skill, write:

- theme
- skill
- trigger
- source signals
- workflow
- proof gate
- anti-pattern

## Step 5: Write

Use [`../prompts/write-article.md`](../prompts/write-article.md).

Use the article template:

[`../templates/article-template.md`](../templates/article-template.md)

## Step 6: Publish

Before publishing, check:

- source links work
- people are attributed accurately
- no private/personal content leaked
- read-only boundary is clear
- every theme has a skill
- title leads with a transformation

## Step 7: Save the Issue

Create:

```text
issues/[number]-[slug]/
  article.md
  source-map.md
  skills.md
```
