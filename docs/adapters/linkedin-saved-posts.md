# LinkedIn Saved Posts Adapter

Use this adapter to turn saved LinkedIn posts into skills, study guides, article ideas, or operating principles.

LinkedIn is useful for Bookmark Maxxing because people often save:

- career advice
- founder lessons
- product strategy
- sales and GTM posts
- hiring/leadership posts
- AI and engineering workflows
- industry analysis

Those saves usually become a private pile. This adapter converts them into reusable work.

## Source Options

Use one of these paths.

### Option A: Saved Items Page

Open LinkedIn's saved items page in a browser and review it read-only.

Typical path:

```text
LinkedIn -> My Items -> Saved Posts / Saved Items
```

Use this when you want a fast weekly review.

### Option B: LinkedIn Data Export

LinkedIn also provides account data export controls through account settings.

Use this when you want a larger archive or want to work from downloaded files instead of a live browser session.

Do not paste private exports into public issues.

## Read-Only Rules

During collection, do not:

- like
- comment
- repost
- connect
- follow
- message people
- unsave items
- change profile/account settings

Bookmark Maxxing should inspect saved content, not mutate LinkedIn.

## Capture Fields

For each saved item, capture:

- author
- author role/company if visible
- URL
- date if visible
- post text or title
- linked article/video/document if visible
- why it looked useful
- possible theme

Example:

```json
{
  "source": "linkedin",
  "author": "Example Builder",
  "url": "https://www.linkedin.com/posts/example",
  "title_or_text": "Post about turning customer calls into product requirements...",
  "why_it_matters": "Shows a repeatable customer-research workflow.",
  "theme": "customer discovery",
  "classification": "workflow"
}
```

## Classification

Classify each saved post:

- `ignore`: generic motivation or personal update
- `note`: interesting but one-off
- `prompt`: useful prompt framing
- `workflow`: repeatable process
- `skill`: reusable behavior with a trigger and proof gate
- `script`: deterministic task worth automating

## Conversion Examples

```text
Saved post: A founder explains how they review ten customer calls each Friday.
Theme: customer feedback loops
Skill: Turn raw customer conversations into weekly product decisions.
```

```text
Saved post: An engineering leader explains how they write incident reviews.
Theme: operational learning
Skill: Convert incidents into reusable runbook improvements.
```

```text
Saved post: A recruiter explains what strong portfolios show.
Theme: career proof
Skill: Turn project work into evidence-backed portfolio artifacts.
```

## Output Options

LinkedIn saves can become:

- study guides
- career operating principles
- sales/GTM playbooks
- product discovery workflows
- leadership checklists
- article drafts
- skill cards

## Safety Notes

LinkedIn posts may include personal stories, employment details, screenshots, or private context.

Before publishing:

- attribute public posts accurately
- do not expose private messages or non-public exports
- do not imply endorsement
- do not summarize sensitive personal details unless they are essential and public
- prefer linking to the original source

## Prompt

```text
Review my LinkedIn saved posts read-only.

Do not like, comment, repost, connect, follow, message, unsave, or change anything.

Capture author, URL, visible date, post text/title, linked artifact, and why it matters.

Filter out generic motivation and personal updates unless they contain a reusable workflow.

Cluster the recurring themes.

For each strong theme, create:
- Theme
- Skill
- Trigger
- Source signals
- Workflow
- Proof gate
- Anti-pattern

Then produce a study guide or article outline from the strongest skills.
```
