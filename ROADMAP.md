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
