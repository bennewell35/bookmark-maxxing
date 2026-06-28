# Contributing

Bookmark Maxxing is a framework for turning saved links into reusable skills.

Useful contributions are practical, sourced, and reusable.

Before contributing, read:

- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- [`GOVERNANCE.md`](GOVERNANCE.md)
- [`SECURITY.md`](SECURITY.md)

## Good Contributions

- New issue examples with source maps.
- Better prompts for extracting skills.
- Better templates for articles, source maps, or skill cards.
- Small scripts that normalize exported bookmarks without requiring credentials.
- Clear examples of a saved idea becoming a reusable workflow.

## Not a Fit

- Generic AI news recaps.
- Unsourced claims.
- Engagement-farming templates.
- Tools that require scraping private accounts or extracting credentials.
- Large app rewrites before the framework is proven.

## Contributor Workflow

1. Open an issue or comment on an existing issue when proposing a new direction.
2. Keep pull requests focused.
3. Include source attribution when adding examples.
4. Add or update templates/prompts when the contribution changes the workflow.
5. Avoid adding dependencies unless they remove repeated manual work.
6. Keep source collection read-only by default.

## Contribution Format

For a new issue example, include:

- `article.md`
- `source-map.md`
- `skills.md`
- `ignored.md` if useful

For a new skill, include:

- theme
- skill
- trigger
- source signals
- workflow
- proof gate
- anti-pattern

## Source Attribution

Attribute the person and link that contributed the idea.

Do not imply a source endorsed the framework unless they explicitly did.

## Pull Request Checklist

- [ ] The contribution is scoped to Bookmark Maxxing.
- [ ] Source links are attributed.
- [ ] No private exports, credentials, cookies, or tokens are included.
- [ ] Collection remains read-only by default.
- [ ] New themes produce reusable skills or operating rules.
- [ ] Docs/templates/prompts were updated if the workflow changed.
