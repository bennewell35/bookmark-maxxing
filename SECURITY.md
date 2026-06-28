# Security Policy

Bookmark Maxxing is a framework repo, not a hosted service.

The main security concern is protecting private saved content, account access, and credentials while analyzing bookmarks or other saved links.

## Supported Scope

Security reports are in scope when they involve:

- prompts or examples that encourage credential extraction
- scripts that expose private bookmark data
- source-handling workflows that mutate accounts unexpectedly
- unsafe guidance around cookies, tokens, passwords, or private exports
- accidental inclusion of sensitive data in examples

Out of scope:

- general disagreements about article framing
- source links that are already public
- issues in third-party platforms such as X, GitHub, Slack, or browser vendors

## Reporting a Vulnerability

Do not open a public issue for a private security report.

Use GitHub's private vulnerability reporting if it is enabled for this repository. If it is not enabled, contact the maintainer privately through GitHub.

Please include:

- affected file or workflow
- what private data or account action is at risk
- steps to reproduce
- suggested fix, if known

## Handling Expectations

The maintainer will review security reports as maintainer capacity allows.

Accepted fixes should keep the framework read-only by default and should not require users to expose credentials, cookies, tokens, or private exports.
