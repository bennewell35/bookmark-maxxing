# Bookmark Maxxing #1: Turning Bookmarks into Skills

June 28, 2026

Most people collect bookmarks.

Builders should be collecting skills.

Every week I save posts about AI engineering, Codex, agents, infrastructure, and systems thinking. Like most people, those bookmarks used to disappear into a growing pile I would rarely revisit.

This week I changed the workflow.

I had Codex analyze my bookmarks in read-only mode, cluster the recurring ideas, attribute the sources, and surface the patterns that kept appearing across the people building the future of AI.

The goal was not another AI news recap.

It was to answer a different question:

**Which of these ideas are worth turning into reusable skills?**

This is the first post in a new series I am calling **Bookmark Maxxing**.

Every week I will turn a pile of saved links into workflows, engineering patterns, and practical skills you can actually use.

## What My Bookmarks Say About AI This Week

A clear pattern emerged: AI engineering is moving away from one-off prompts and toward durable systems of work.

The people getting real leverage from AI are not just asking better questions. They are building loops around the tools.

Those loops usually have four parts:

- durable context
- repeatable actions
- verification
- human judgment

That showed up across almost every useful bookmark.

## Theme: AI Is Moving From Prompts to Operating Loops

**Skill: Design repeatable systems, not better prompts.**

OpenAI Developers posted a set of Codex quality-of-life updates: smoother long threads, a navigation rail, better settings search, lighter thread switching, deeper local history, archive improvements, and unread badge sync. Tibo Sottiaux framed the release as a broad improvement to the way Codex handles long-running work.

That may sound like UI polish, but it is more important than that.

Long threads are where engineering work accumulates. They hold decisions, failed attempts, logs, screenshots, proof, handoffs, and the messy context that never fits cleanly into a ticket. When a tool gets better at preserving and navigating that history, it starts to feel less like a chat box and more like an operating layer for work.

Jason Liu pushed the same idea from the automation side. He separated scheduled work from heartbeat-style thread automations. A scheduled task is useful when you want something to happen later. A thread automation is different: it wakes up the same conversation, with the same context, on a recurring cadence.

That distinction matters.

The unit of work is no longer just a prompt. It can be a loop.

## Theme: The Human Is Still in the Loop

**Skill: Build agents that return evidence, not just output.**

Another cluster converged on the same idea: the future is not "vibe coding." It is human-in-the-loop engineering.

Eric Zakariasson wrote about agents running while the human moves between them, stepping back in when something finishes or needs judgment. Can Vardar summarized the shift cleanly: people still think the future is vibe coding, but the real shift is the human in the loop.

Chris Tate made the eval version of the same point. The agent should be judged against the real runtime: did it call the right tools, avoid the dangerous ones, and say the right thing? Not a separate eval universe. The real system.

Movez highlighted loop engineering and self-improving systems where agents have a way to verify their own output.

That is the pattern I keep seeing in actual engineering work:

An agent is useful when it can act, check itself, and come back with evidence.

The human role changes, but it does not disappear. You define the boundary. You inspect the proof. You decide whether the result is actually good enough.

## Theme: Memory Is Not the Goal. Better Systems Are.

**Skill: Convert repeated lessons into docs, tests, skills, or runbooks.**

Memory came up repeatedly, but the best version of the conversation was skeptical.

Morgan Linton shared Matt Van Horn's argument that agent memory can make systems worse when lessons disappear into private memory files. The better pattern is to turn repeated lessons into durable skills, docs, tests, or runbooks.

That is the difference between:

"The agent remembered something."

and:

"The system improved."

If an agent learns a useful lesson, but that lesson only lives inside a hidden memory blob, the next person, repo, workflow, or tool may never benefit from it. If the lesson becomes a checklist, a test, a skill, or a runbook, the whole operating system gets better.

This also connected with Rhys Sullivan's point that users may not want every company to ship yet another custom agent. They want access to the skills, knowledge, and APIs the company has built over time.

Calcs made a practical version of that argument: sometimes a good API plus docs can be turned into an agent skill with less overhead than wrapping everything in MCP too early.

The durable asset is not the chat.

The durable asset is the workflow.

## Theme: Local Knowledge Is Becoming Infrastructure

**Skill: Make your saved context readable by the systems doing the work.**

Another group of bookmarks centered on local knowledge systems.

Tali Rezun described local apps that ingest documents, notes, and articles into a persistent linked knowledge system that agents can read and write through MCP.

Claire Vo wrote about using large token volumes to make sense of product and company context, trying to create a semantic oracle for product work.

Trevin Chow's Compound Engineering update pointed in the same direction: better architecture, better docs, longer-running agents, and more explicit workflow structure.

All of this gets at the same problem: AI tools are only as useful as the context they can reliably work with.

If your context is scattered across bookmarks, docs, repos, screenshots, tickets, Slack threads, and half-remembered decisions, the agent will only be as good as the slice it can see.

The next layer of leverage is not just a better model.

It is better context management.

## Theme: Taste Still Matters

**Skill: Use agents for evidence and execution, but keep judgment human.**

There was also a quieter but important engineering-craft thread.

Mitchell Hashimoto wrote about taste: the ability to make high-quality qualitative judgments when no objective metric exists.

That belongs in the same conversation as agents and loops.

Agents can run checks. They can gather evidence. They can execute a narrow slice. They can compare files, inspect logs, open browsers, and generate drafts.

But someone still has to decide:

Is this the right problem?

Is this the right abstraction?

Does this feel coherent?

Is this actually useful, or just technically impressive?

That judgment layer is not going away. If anything, it becomes more important as the cost of generating work drops.

## The Bookmark Maxxing Takeaway

This week's bookmarks converged on a simple direction:

AI engineering is becoming less about asking a model to do a task and more about designing the operating system around the model.

That operating system has a few core pieces:

- context that survives across sessions
- workflows that can be repeated
- agents that can act and verify
- evals that run against real systems
- humans who still apply taste and judgment

The funny part is that most of us already have the raw material for this.

It is sitting in bookmarks.

We save links because something in them feels useful. But we rarely convert that feeling into anything durable. With Codex, the workflow changes. Your bookmarks can become an input system.

You can ask it to read the pile, cluster the patterns, attribute the sources, identify repeated workflows, and turn the useful parts into prompts, checklists, runbooks, articles, or code.

That is Bookmark Maxxing:

Bookmarks are the input.

Skills are the output.

## How to Read Your Own Bookmarks With Codex

Here is the simple version.

Open your bookmark source: X bookmarks, GitHub stars, saved Slack posts, newsletters, read-later apps, or browser bookmarks.

Then ask Codex to do a read-only pass.

Give it a boundary:

- this week
- last 100 bookmarks
- AI and engineering only
- exclude personal posts
- capture author, link, date, post text, and why it matters

Then ask for four things:

1. recurring themes
2. source attribution
3. a clean article or memo
4. any workflows worth turning into prompts, checklists, or skills

The important part is read-only. Codex should not like, repost, reply, follow, unbookmark, or mutate anything. It is there to extract signal from the pile.

Here is the prompt I would use:

```text
Read my bookmarks read-only and turn them into a weekly AI/engineering digest.

Boundaries:
- Do not like, repost, reply, follow, subscribe, unbookmark, or mutate anything.
- Exclude birthday, personal, fitness, lifestyle, and social-only posts unless they directly connect to AI or engineering.
- Treat posts as sources of ideas, not proof.

Capture:
- Author/person
- URL
- Date if visible
- Post text/title
- Linked artifact if visible
- Why it matters

Then produce:
1. The recurring themes from this week.
2. A source map with people attributed to the ideas.
3. A clean article called "What My Bookmarks Say About AI This Week."
4. A practical section teaching readers how to turn bookmarks into workflows with Codex.
5. A list of posts that were ignored and why.

Keep the writing concise, factual, and useful for builders.
```

We already save the best ideas. The problem is not discovery. It is conversion.

Bookmark Maxxing is about turning saved ideas into durable systems.

Every Sunday I will use Codex to analyze my bookmarks, identify the patterns, and convert them into skills, workflows, and operating principles for builders.

**Bookmarks are the input. Skills are the output.**

## Sources

- OpenAI Developers on Codex quality-of-life updates: https://x.com/OpenAIDevs/status/2070922791529091376
- Tibo Sottiaux on the Codex update: https://x.com/thsottiaux/status/2071071289247244481
- Jason Liu on scheduled work in Codex: https://x.com/jxnlco/status/2071136366893859044
- Jason Liu on thread automations: https://x.com/jxnlco/status/2071027888288309657
- Rhys Sullivan on agents, skills, knowledge, and APIs: https://x.com/RhysSullivan/status/2070989582850793947
- Morgan Linton sharing Matt Van Horn on agent memory: https://x.com/morganlinton/status/2071001734420517315
- Trevin Chow on Compound Engineering: https://x.com/trevin/status/2070711838803948020
- Deedy Das on agentic engineering lessons: https://x.com/deedydas/status/2070574557728264382
- Eric Zakariasson on human-in-the-loop work: https://x.com/ericzakariasson/status/2070493377267646797
- Can Vardar on human-in-the-loop engineering: https://x.com/icanvardar/status/2070834722633060378
- Thomas Ricouard on workflow beyond threads: https://x.com/Dimillian/status/2070850643963597153
- Mitchell Hashimoto on taste: https://x.com/mitchellh/status/2070665127331037290
- Chris Tate on real-runtime agent evals: https://x.com/ctatedev/status/2069458196616409213
- Movez on loop engineering and verification: https://x.com/0xMovez/status/2069452569970151658
- Tali Rezun on local knowledge systems: https://x.com/talirezun/status/2069824702093168929
- Calcs on API docs to agent skills: https://x.com/0000CCS/status/2069801974543867968
- Claire Vo on semantic product/company context: https://x.com/clairevo/status/2069625216431800621
- Claire Vo on GLM 5.2 and coding model economics: https://x.com/clairevo/status/2069828122640548204
- Derya Unutmaz / OpenAI on GPT-5 Pro and immunology: https://x.com/DeryaTR_/status/2069846329287651765

