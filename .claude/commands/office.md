---
description: Open the Agent Office — a live floor plan where you watch the skill agents work.
---

Start the Agent Office server in the background and tell me where to open it:

1. Run `python3 scripts/agent_office.py --no-browser` in the background (Bash `run_in_background`).
2. Tell me to open http://127.0.0.1:8765/ in a browser on this machine.
3. Remind me that agents appear there when I use `/master <request>`, `/agent <name> <task>` or `@sk-…`,
   and that recording can be paused with `AGENT_OFFICE=0`.

If port 8765 is taken, use `--port 8766`.
