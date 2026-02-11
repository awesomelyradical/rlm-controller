#!/usr/bin/env python3
"""Emit OpenClaw sessions_spawn toolcall JSON from spawn.jsonl.
This prints a JSON array of tool calls grouped by batch.

Usage:
  rlm_emit_toolcalls.py --spawn <spawn.jsonl> --subcall-system <path>
"""
import argparse, json, sys

# --- Safelist enforcement ---
# Only these tools may appear in emitted toolcalls.
ALLOWED_TOOLS = frozenset({"sessions_spawn"})
# Only these action types are accepted in spawn manifests.
ALLOWED_ACTIONS = frozenset({"sessions_spawn"})
MAX_SUBCALLS = 32

def read_spawn(path):
    items = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                action = entry.get("action", "")
                if action not in ALLOWED_ACTIONS:
                    print(f"ERROR: disallowed action '{action}' in spawn manifest", file=sys.stderr)
                    sys.exit(1)
                items.append(entry)
    if len(items) > MAX_SUBCALLS:
        print(f"ERROR: spawn manifest contains {len(items)} entries, exceeding limit of {MAX_SUBCALLS}", file=sys.stderr)
        sys.exit(1)
    return items

def read_text(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--spawn', required=True)
    p.add_argument('--subcall-system', required=True)
    args = p.parse_args()

    sys_prompt = read_text(args.subcall_system)
    items = read_spawn(args.spawn)

    batches = {}
    for it in items:
        batches.setdefault(it['batch'], []).append(it)

    out = []
    for batch_id in sorted(batches.keys()):
        batch_calls = []
        for it in batches[batch_id]:
            user_prompt = read_text(it['prompt_file'])
            full_prompt = f"SYSTEM:\n{sys_prompt}\n\nUSER:\n{user_prompt}\n"
            batch_calls.append({
                "tool": "sessions_spawn",
                "params": {
                    "task": full_prompt,
                    "label": f"rlm_subcall_b{batch_id}"
                }
            })
        out.append({"batch": batch_id, "calls": batch_calls})

    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
