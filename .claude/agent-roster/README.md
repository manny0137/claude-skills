# Skill Agent Roster

Every skill in this repository is also a Claude Code agent, and all of them report to one
master agent.

| What | Where |
|------|-------|
| One agent per skill (`sk-<skill>`), colored by team | `.claude/agents/sk-*.md` |
| Master agent | `.claude/agents/skill-master.md` |
| Visual roster (open in a browser) | `.claude/agent-roster/roster.html` |
| Agent Office — live view of agents at work | `.claude/agent-roster/office.html`, served by `scripts/agent_office.py` |
| Activity hook that feeds the office | `.claude/hooks/agent_activity.py` (wired in `.claude/settings.json`) |
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

## Watching them work: the Agent Office

```bash
python3 scripts/agent_office.py      # opens http://127.0.0.1:8765/
```

or `/office` inside Claude Code. Then use `/master`, `/agent` or `@sk-…` as usual.

The office is a floor plan: the master's desk on top and one room per team, with a desk
(small square) for every agent. When an agent is dispatched it steps out onto its room's
floor as a card, wired back to whoever sent it. The card shows the tool it is using right
now (`Bash · Pick a pricing model`, `Read · SKILL.md`), its elapsed time and tool count,
and when it finishes, its report status (DONE / NEEDS INPUT / OUT OF SCOPE) and result.
The feed on the right lists every step.

How it works: the hook `.claude/hooks/agent_activity.py` runs on each prompt, each agent
dispatch, every tool call made *inside* an agent, and each agent start/stop, and appends
one line to `.claude/agent-roster/activity.jsonl` (gitignored, owner-only permissions,
truncated previews with secrets redacted). The server tails that file and streams it to
the page. Tool calls in the main conversation are not recorded.

- Pause recording: `AGENT_OFFICE=0 claude`
- Replay a past session: open the page and use **Load activity log** with an
  `activity.jsonl` file.
- Opened as a plain file (no server), the page plays a labeled demo run instead.

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
