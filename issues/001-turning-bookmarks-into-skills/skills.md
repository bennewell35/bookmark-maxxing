# Extracted Skills

## 1. Design repeatable systems, not better prompts.

Trigger: A saved link is about agents, Codex, automation, or long-running work.

Workflow:

1. Identify the durable context.
2. Identify the repeated action.
3. Identify the verification step.
4. Decide where human judgment enters.

Proof gate: The workflow can be repeated without rereading the original post.

## 2. Build agents that return evidence, not just output.

Trigger: A post talks about loops, evals, verification, or agent autonomy.

Workflow:

1. Define the task boundary.
2. Require the agent to act.
3. Require proof from the real runtime.
4. Review before widening scope.

Proof gate: The output includes evidence, not only a claim.

## 3. Convert repeated lessons into docs, tests, skills, or runbooks.

Trigger: The same lesson appears more than once.

Workflow:

1. Name the repeated failure or lesson.
2. Decide where future work will look first.
3. Add the lesson there.
4. Remove duplicate or stale memory.

Proof gate: Future runs can find the rule without relying on hidden memory.

## 4. Make your saved context readable by the systems doing the work.

Trigger: Useful context is scattered across bookmarks, docs, repos, Slack, screenshots, or tickets.

Workflow:

1. Normalize the source items.
2. Attach author, URL, and date.
3. Cluster by theme.
4. Convert repeated patterns into reusable assets.

Proof gate: A future agent can answer "what matters here?" from the saved artifact.

## 5. Use agents for evidence and execution, but keep judgment human.

Trigger: The task requires taste, prioritization, product judgment, or qualitative tradeoffs.

Workflow:

1. Let the agent gather evidence.
2. Let the agent execute narrow slices.
3. Keep final judgment with the human.
4. Record why the decision was made.

Proof gate: The final artifact says what was proven and what was judged.
