# Skill Agent Roster

Every skill in this repository is also a Claude Code agent, and all of them report to one
master agent.

| What | Where |
|------|-------|
| One agent per skill (`sk-<skill>`), colored by team | `.claude/agents/sk-*.md` |
| Master agent | `.claude/agents/skill-master.md` |
| Visual roster (open in a browser) | `.claude/agent-roster/roster.html` |
| Machine-readable roster | `.claude/agent-roster/registry.json` |
| Router used by the master | `scripts/agent_router.py` |
| Generator for all of the above | `scripts/build_skill_agents.py` |

## Commanding agents

- **One agent, by name:** `@sk-slo-architect define SLOs for checkout`, or
  `/agent slo-architect define SLOs for checkout`.
- **Not sure which one:** `/master <request>`. The master routes the request, runs one or
  several agents (in parallel when the request has several parts), and combines their
  reports. To make the master your whole session: `claude --agent skill-master`.
- **Find an agent:** `python3 scripts/agent_router.py "<request>"`, or
  `python3 scripts/agent_router.py --list --domain finance`.

The master has to run as the main conversation (through `/master` or `--agent`), because
only the main conversation can start other agents.

Every agent ends its answer with the same report block
(`AGENT / STATUS / RESULT / EVIDENCE / HANDOFFS`), which is how the master combines answers
and spots `NEEDS-INPUT` and `OUT-OF-SCOPE` replies.

## Keeping it in sync

These files are generated. After adding, renaming, or removing a skill, run:

```bash
python3 scripts/build_skill_agents.py          # regenerate
python3 scripts/build_skill_agents.py --check  # verify (also runs in CI, advisory)
```

Claude Code loads every agent's description into each session opened in this repo
(about 17k tokens for all 376). To load fewer, generate only the teams you use:

```bash
python3 scripts/build_skill_agents.py --domains engineering,product-team,finance
```
