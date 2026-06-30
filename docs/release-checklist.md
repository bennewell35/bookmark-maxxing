# Release Checklist — v0.1.0

Work top to bottom. Do not tag or publish until every box above the release steps is checked.

## Code & review

- [ ] PR merged into `main`.
- [ ] CI passing on `main` (GitHub Actions: unit tests, byte-compile, `git diff --check`).
- [ ] GitGuardian / security checks passing on the merge commit.

## Verification

- [ ] Fixture dry-run tested:
      `PYTHONPATH=src python3 -m bookmark_maxxing.cli ingest-x --dry-run --input tests/fixtures/x_bookmarks_pages.json --format json`
- [ ] Live read-only smoke test run by a maintainer only, per [`live-smoke-test.md`](live-smoke-test.md) (optional but recommended; never in CI).
- [ ] README quickstart verified end-to-end on a clean clone (install + dry-run).

## Safety

- [ ] No secrets committed (API keys, OAuth tokens, cookies, bearer tokens).
- [ ] No private bookmark data committed (no live exports in the repo, PRs, or issues).
- [ ] Read-only guarantee intact: no POST/PUT/PATCH/DELETE and no mutation methods exposed.

## Release

- [ ] Version in `pyproject.toml` set to `0.1.0`.
- [ ] `v0.1.0` git tag created (`git tag -a v0.1.0 -m "Bookmark Maxxing v0.1.0" && git push origin v0.1.0`).
- [ ] GitHub Release published from the `v0.1.0` tag with concise notes.

## Post-release

- [ ] Announce the runnable CLI in the README badge / positioning if desired.
- [ ] Open follow-up issues for the next slice (MCP-native transport, more source adapters).
