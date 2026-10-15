---
description: Hand a request to skill-master, which picks the right sk-* skill agent(s), dispatches them, and combines their answers.
argument-hint: <request in plain words>
---

Act as **skill-master** for this request: $ARGUMENTS

Read `.claude/agents/skill-master.md` and follow its Procedure exactly. In short:

1. Route the request: `python3 scripts/agent_router.py "$ARGUMENTS" --top 5 --json`.
2. Exit 0 → dispatch the winning agent with the Agent tool (`subagent_type` = the agent name).
   Exit 2 → split a multi-part request across its agents in parallel, otherwise ask me one
   question listing the top 3 with your recommendation. Exit 3 → say no agent fits.
3. Brief each agent with the full request and all context it needs.
4. Act on each report's STATUS (`NEEDS-INPUT` → ask me; `OUT-OF-SCOPE` → re-route), at most 3 rounds.
5. Give me one combined answer, then list which agents contributed.

If `$ARGUMENTS` is empty, ask me what I need, and mention that `/agent <name> <task>` commands one agent directly.
