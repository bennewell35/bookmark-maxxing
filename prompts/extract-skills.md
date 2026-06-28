# Prompt: Extract Skills

Given a set of bookmarked posts, extract only the reusable skills.

For each candidate, classify it:

- ignore: generic advice, motivation, vendor hype, or not actionable
- note: useful idea but one-off
- prompt: reusable prompt framing
- workflow: repeated process worth documenting
- skill: repeated behavior with clear trigger and proof gate
- script: deterministic operation worth automating

For each skill, output:

```text
Theme:
Skill:
Trigger:
Source signals:
Workflow:
Proof gate:
Anti-pattern:
```

Decision rule:

If it does not change future behavior, it is not a skill yet.
