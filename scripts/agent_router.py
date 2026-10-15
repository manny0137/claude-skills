#!/usr/bin/env python3
"""agent_router.py — pick the sk-* skill agent(s) for a request.

Used by the skill-master agent (and by any sk-* agent that gets an
out-of-scope request). Reads .claude/agent-roster/registry.json, written by
scripts/build_skill_agents.py, and scores each agent against the request
with deterministic IDF-weighted keyword matching:
name tokens weigh 3x, domain tokens 1.5x, description tokens 1x.

Usage:
  agent_router.py "price our new enterprise tier"        # top candidates
  agent_router.py "..." --top 5 --json                   # machine-readable
  agent_router.py --resolve "slo architect"              # name -> agent
  agent_router.py --list [--domain finance]              # roster

Exit codes:
  0  route     one clear winner (score >= 4 and >= 1.5x the runner-up)
  2  ask       several close candidates — ask the user, or split the request
  3  no-match  nothing scored; no agent fits
  1  error     registry missing or bad arguments

Stdlib only. No writes.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

REGISTRY = Path(__file__).resolve().parent.parent / ".claude" / "agent-roster" / "registry.json"

STOP = set("""a an and are as at be but by can do does for from get give have help how i if in into is it
its me my need of on or our please should so that the their them this to us use using want we what when
which who will with you your skill skills agent agents tool tools run make build create""".split())

SYNONYMS = {
    "k8s": "kubernetes", "pr": "review", "prd": "product", "seo": "seo", "aeo": "aeo",
    "okr": "okrs", "gdpr": "gdpr", "hipaa": "hipaa", "slo": "slo", "sli": "slo",
    "ux": "ux", "ui": "frontend", "db": "database", "sql": "database", "llm": "ai",
    "ml": "ml", "cfo": "cfo", "cto": "cto", "ceo": "ceo", "ads": "ad", "emails": "email",
}


def tokens(text: str) -> list:
    out = []
    raw = []
    for t in re.findall(r"[a-z0-9]+", text.lower()):
        raw.append(t)
        parts = re.findall(r"[a-z]+|[0-9]+", t)
        if len(parts) > 1 and t not in SYNONYMS:  # iso13485 -> iso, 13485 (but keep k8s whole)
            raw.extend(parts)
    for t in raw:
        t = SYNONYMS.get(t, t)
        if t in STOP or len(t) < 2:
            continue
        if len(t) > 4 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        out.append(t)
    return out


def load():
    if not REGISTRY.exists():
        sys.exit(f"registry not found: {REGISTRY}\nrun: python3 scripts/build_skill_agents.py")
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def score_all(agents: list, request: str) -> list:
    fields = []
    for a in agents:
        fields.append({
            "name": set(tokens(a["skill"])),
            "domain": set(tokens(a["domain_label"] + " " + a["domain"])),
            "desc": set(tokens(a.get("description") or a["summary"])),
        })
    n = len(agents)
    df = {}
    for f in fields:
        for t in f["name"] | f["domain"] | f["desc"]:
            df[t] = df.get(t, 0) + 1
    q = set(tokens(request))
    results = []
    for a, f in zip(agents, fields):
        s, hits = 0.0, []
        for t in q:
            if t not in df:
                continue
            idf = math.log(1 + n / df[t])
            w = 3 * (t in f["name"]) + 1.5 * (t in f["domain"]) + 1 * (t in f["desc"])
            if w:
                s += w * idf
                hits.append(t)
        if s > 0:
            results.append({"agent": a["agent"], "score": round(s, 2), "domain": a["domain_label"],
                            "summary": a["summary"], "matched": sorted(hits)})
    results.sort(key=lambda r: (-r["score"], r["agent"]))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("request", nargs="?", help="the user's request, in plain words")
    ap.add_argument("--top", type=int, default=3, help="how many candidates to show (default 3)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--resolve", metavar="NAME", help="resolve an agent or skill name to its agent")
    ap.add_argument("--list", action="store_true", help="list the roster")
    ap.add_argument("--domain", help="with --list: only this domain (folder name or label)")
    args = ap.parse_args()
    reg = load()
    agents = reg["agents"]

    if args.list:
        rows = [a for a in agents if not args.domain
                or args.domain.lower() in (a["domain"].lower(), a["domain_label"].lower())]
        if args.json:
            print(json.dumps(rows, indent=1, ensure_ascii=False))
        else:
            for a in rows:
                print(f"{a['agent']:<46} {a['domain_label']:<24} {a['summary'][:90]}")
            print(f"\n{len(rows)} agents (master: {reg['master']})")
        return 0

    if args.resolve:
        key = re.sub(r"[^a-z0-9]+", "-", args.resolve.lower()).strip("-")
        key = key[3:] if key.startswith("sk-") else key
        exact = [a for a in agents if a["agent"] == f"sk-{key}" or a["skill"] == key]
        partial = exact or [a for a in agents if key in a["agent"]]
        out = [a["agent"] for a in partial]
        if args.json:
            print(json.dumps({"query": args.resolve, "matches": out}))
        else:
            print("\n".join(out) if out else f"no agent named like '{args.resolve}'")
        return 0 if len(out) == 1 else (2 if out else 3)

    if not args.request:
        ap.error("give a request, or use --resolve / --list")

    ranked = score_all(agents, args.request)
    top = ranked[: max(1, args.top)]
    if not ranked:
        verdict, code = "no-match", 3
    elif ranked[0]["score"] >= 4 and (len(ranked) == 1 or ranked[0]["score"] >= 1.5 * ranked[1]["score"]):
        verdict, code = "route", 0
    else:
        verdict, code = "ask", 2

    if args.json:
        print(json.dumps({"request": args.request, "verdict": verdict, "candidates": top}, indent=1))
    else:
        print(f"verdict: {verdict}")
        for r in top:
            print(f"  {r['agent']:<44} {r['score']:>6}  [{r['domain']}]  matched: {', '.join(r['matched'])}")
        if verdict == "no-match":
            print("  no agent fits — answer directly or ask which domain this belongs to")
    return code


if __name__ == "__main__":
    sys.exit(main())
