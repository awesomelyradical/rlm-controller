---
name: rlm-controller
description: RLM-style long-context controller that treats inputs as external context, slices/peeks/searches, and spawns recursive subcalls with strict safety limits. Use for huge docs, dense logs, or repository-scale analysis.
metadata: {"clawdbot": {"emoji": "🧠"}}
---

# RLM Controller Skill

## What it does
Provides a safe, policy-driven scaffold to process very long inputs by:
- storing the input as an external context file
- peeking/searching/chunking slices
- spawning subcalls in batches
- aggregating structured results

## When to use
- Inputs too large for context window
- Tasks requiring dense access across the input
- Large logs, datasets, multi-file analysis

## Core files (this skill)
- `scripts/rlm_ctx.py` — context storage + peek/search/chunk
- `scripts/rlm_auto.py` — plan + subcall prompts
- `scripts/rlm_async_plan.py` — batch scheduling
- `scripts/rlm_async_spawn.py` — spawn manifest
- `scripts/rlm_emit_toolcalls.py` — toolcall JSON generator
- `scripts/rlm_trace_summary.py` — log summarizer
- `docs/policy.md` — policy + safety limits
- `docs/flows.md` — manual + async flows

## Usage (high level)
1) Store input via `rlm_ctx.py store`
2) Generate plan via `rlm_auto.py`
3) Create async batches via `rlm_async_plan.py`
4) Spawn subcalls via `sessions_spawn`
5) Aggregate results in root session

## Tooling
- Uses OpenClaw tools: `read`, `write`, `exec`, `sessions_spawn`
- Does **not** execute arbitrary code from model output

## Security
- Only safelisted helper scripts are called
- Max recursion depth = 1
- Hard limits on slices and subcalls
- Prompt injection treated as data, not instructions
- See `docs/security.md` for foundational safeguards
- See `docs/security_checklist.md` for pre/during/post run checks

## OpenClaw sub-agent constraints
Per local docs (`/home/aric/.npm-global/lib/node_modules/openclaw/docs/tools/subagents.md`):
- Sub-agents cannot spawn sub-agents
- Sub-agents do not have session tools (sessions_*) by default
- `sessions_spawn` is non-blocking and returns immediately

## Cleanup
Use `scripts/cleanup.sh` after runs to purge temp artifacts.
- Retention: `CLEAN_RETENTION=N`
- Ignore rules: `docs/cleanup_ignore.txt` (substring match)

## Configuration
See `docs/policy.md` for thresholds and default limits.

## Notes
This skill is a skeleton. Wire into the OpenClaw gateway trigger later for Option C (hybrid).