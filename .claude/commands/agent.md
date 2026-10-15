---
description: Command one skill agent directly by name, e.g. /agent slo-architect define SLOs for checkout.
argument-hint: <agent-or-skill-name> <task>
---

Arguments: $ARGUMENTS

The first word is an agent or skill name; the rest is the task.

1. Resolve the name: `python3 scripts/agent_router.py --resolve "<first word>"`.
   - Exactly one match → dispatch it with the Agent tool (`subagent_type` = that name), passing the
     task and any context from this conversation it needs.
   - Several matches → ask me which one, listing them.
   - No match → run `python3 scripts/agent_router.py "<task>"` and suggest the top candidates, or offer `/master`.
2. Relay the agent's answer and its report block to me unchanged in substance.

With no arguments, print the roster summary: `python3 scripts/agent_router.py --list | tail -n 1`, and
point me to `.claude/agent-roster/roster.html` for the visual roster.
