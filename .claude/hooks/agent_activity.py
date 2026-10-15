#!/usr/bin/env python3
"""agent_activity.py — Claude Code hook that records what the skill agents are doing.

Wired in .claude/settings.json for UserPromptSubmit, PreToolUse, PostToolUse,
SubagentStart and SubagentStop. Each event becomes one compact line in
.claude/agent-roster/activity.jsonl (gitignored), which the Agent Office
(`python3 scripts/agent_office.py`) streams to the browser.

What is recorded:
  prompt    the user's request (first 240 chars)
  route     the master running scripts/agent_router.py
  dispatch  an Agent/Task tool call: which agent, by whom, the brief's title
  start     a subagent started (SubagentStart)
  tool      a tool call made inside a subagent: tool name + a short label
  stop      a subagent finished (SubagentStop), with STATUS/RESULT parsed
            from the sk-* report block when present
  returned  the Agent/Task tool call came back to its caller

Tool calls in the main conversation are not recorded (only its dispatches
and router runs),
which keeps the log small. Text previews are truncated and passed through a
small secret redactor before they touch disk.

Fail-open: any error exits 0 silently, so the hook can never block work.
Set AGENT_OFFICE=0 to turn recording off.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

MAX_LOG_BYTES = 5 * 1024 * 1024
AGENT_TOOLS = {"Agent", "Task"}

SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"),
    re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def clip(text, n=200) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    for pat in SECRET_PATTERNS:
        text = pat.sub("[redacted]", text)
    return text if len(text) <= n else text[: n - 1] + "…"


def tool_label(name: str, inp: dict) -> str:
    inp = inp or {}
    if name == "Bash":
        return clip(inp.get("description") or inp.get("command"), 90)
    for key in ("file_path", "path", "notebook_path"):
        if inp.get(key):
            return Path(str(inp[key])).name
    if inp.get("pattern"):
        return clip(inp["pattern"], 60)
    if inp.get("url"):
        return clip(inp["url"], 80)
    if inp.get("query"):
        return clip(inp["query"], 80)
    return ""


def parse_report(text: str) -> dict:
    out = {}
    for key in ("STATUS", "RESULT", "HANDOFFS"):
        m = re.search(rf"^\s*{key}:\s*(.+)$", text or "", re.M)
        if m:
            out[key.lower()] = clip(m.group(1), 240)
    status = out.get("status", "")
    for s in ("NEEDS-INPUT", "OUT-OF-SCOPE", "DONE"):
        if s in status.upper():
            out["status"] = s
            break
    else:
        out.pop("status", None)
    return out


def build_event(data: dict):
    ev = data.get("hook_event_name", "")
    who = data.get("agent_type") or ""
    base = {"ts": round(time.time(), 3), "session": (data.get("session_id") or "")[:8]}
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}

    if ev == "UserPromptSubmit":
        return {**base, "kind": "prompt", "text": clip(data.get("prompt"), 240)}
    if ev == "PreToolUse" and tool in AGENT_TOOLS:
        return {**base, "kind": "dispatch", "agent": inp.get("subagent_type") or "general-purpose",
                "from": who or "main", "text": clip(inp.get("description") or inp.get("prompt"), 120),
                "brief": clip(inp.get("prompt"), 240), "id": data.get("tool_use_id", "")}
    if ev == "PostToolUse" and tool in AGENT_TOOLS:
        resp = data.get("tool_response")
        text = resp if isinstance(resp, str) else json.dumps(resp, ensure_ascii=False) if resp else ""
        return {**base, "kind": "returned", "agent": inp.get("subagent_type") or "general-purpose",
                "from": who or "main", "id": data.get("tool_use_id", ""), **parse_report(text)}
    if ev == "PreToolUse" and not who and tool == "Bash" and "agent_router.py" in str(inp.get("command", "")):
        return {**base, "kind": "route", "text": clip(inp.get("command"), 160)}
    if ev == "PreToolUse" and who:
        return {**base, "kind": "tool", "agent": who, "agent_id": data.get("agent_id", ""),
                "tool": tool, "text": tool_label(tool, inp)}
    if ev == "SubagentStart":
        return {**base, "kind": "start", "agent": who or "unknown", "agent_id": data.get("agent_id", "")}
    if ev == "SubagentStop":
        return {**base, "kind": "stop", "agent": who or "unknown", "agent_id": data.get("agent_id", ""),
                **parse_report(data.get("last_assistant_message", ""))}
    return None


def log_path() -> Path:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(root) / ".claude" / "agent-roster" / "activity.jsonl"


def append(event: dict) -> None:
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if path.stat().st_size > MAX_LOG_BYTES:  # keep the newest half
            lines = path.read_text(encoding="utf-8").splitlines(True)
            path.write_text("".join(lines[len(lines) // 2:]), encoding="utf-8")
    except FileNotFoundError:
        pass
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> int:
    if os.environ.get("AGENT_OFFICE", "1") == "0":
        return 0
    try:
        event = build_event(json.load(sys.stdin))
        if event:
            append(event)
    except Exception:  # never block the session
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
