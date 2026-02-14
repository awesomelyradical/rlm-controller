#!/usr/bin/env python3
"""Generate an async subcall execution plan from plan.json.
This does not execute subcalls; it outputs a JSON plan with suggested parallel batches.

Usage:
  rlm_async_plan.py --plan <plan.json> --batch-size 4
"""
import argparse, json, os, sys

def _validate_path(path):
    """Reject directory traversal and symlinks pointing outside the parent directory."""
    if '..' in path.split(os.sep):
        print(f"ERROR: path traversal detected: {path}", file=sys.stderr)
        sys.exit(1)
    rp = os.path.realpath(path)
    abs_path = os.path.abspath(path)
    if rp != abs_path:
        print(f"ERROR: symlink target outside expected location: {path}", file=sys.stderr)
        sys.exit(1)
    return rp

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--plan', required=True)
    p.add_argument('--batch-size', type=int, default=4)
    args = p.parse_args()

    rp = _validate_path(args.plan)
    with open(rp, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    prompts = plan.get('subcall_prompts', [])
    batches = [prompts[i:i+args.batch_size] for i in range(0, len(prompts), args.batch_size)]

    out = {
        "ctx": plan.get("ctx"),
        "goal": plan.get("goal"),
        "batch_size": args.batch_size,
        "batches": batches,
        "notes": "Execute each batch in parallel with sessions_spawn; aggregate results in root controller."
    }
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
