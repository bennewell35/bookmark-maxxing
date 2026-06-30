<!--
Generated example output. Source: tests/fixtures/x_mcp_bookmarks.json (synthetic, public-safe).
Produced by: bookmark-maxxing extract --prompt extract-skills --llm  (local Ollama, pinned model `bookmark-maxxing` = llama3.2:1b).
LLM output is non-deterministic and the 1B model is small; treat this as an illustrative sample, not a fixed contract.
-->

I'll extract the reusable skills from the bookmarked posts and classify them accordingly.

**Skills:**

| # | Author | Theme | Text | Link |
|---|---|---|---|---|
| 1 | @ben_ai_eng | uncategorized | Bookmarks are the input. Skills are the output. | [source](https://x.com/ben_ai_eng/status/1) |
| 2 | @systems_builder | workflow | Design repeatable systems, not better prompts. | [source](https://x.com/systems_builder/status/2) |
| 3 | @source_mapper | source_map | Source maps make learning artifacts auditable. | [source](https://x.com/source_mapper/status/3) |

**Classification:**

* `ignore`: Bookmarks are the input.
* `note`: Reusable prompt framing (text "Bookmarks are the input.")
* `prompt`: Reusable prompt framing (trigger "Bookmarks are the input.", proof gate "is the output.")
* `skill`: Source maps make learning artifacts auditable (trigger "Source maps make learning artifacts auditable.", proof gate "make learning artifacts auditable.")

**Output:**

```text
Theme:
Skill:
Trigger:
Source signals:
Workflow:
Proof gate:
Anti-pattern:

Theme: workflow
Skill: source_map
Trigger: Source maps make learning artifacts auditable.
Source signals: [https://x.com/source_mapper/status/3]
Workflow: repeated process worth documenting
Proof gate: deterministic operation worth automating
Anti-pattern: not better prompts.

Theme: prompt
Skill: reusable_prompt_framing
Trigger: Bookmarks are the input.
Source signals: [https://x.com/ben_ai_eng/status/1]
Workflow: repeated process worth documenting
Proof gate: deterministic operation worth automating
Anti-pattern: better prompts.
```

Note that I've only extracted skills that have a clear trigger and proof gate, as per the decision rule. The `anti-pattern` column indicates that the skill is not actionable or relevant to the context.
