#!/usr/bin/env python3
"""Batch runner helper (assistant-driven):
Reads toolcall batches JSON (from rlm_emit_toolcalls.py) and outputs
an ordered list of sessions_spawn calls for execution by the OpenClaw agent.

Usage:
  rlm_batch_runner.py --toolcalls <batches.json>
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
    p.add_argument('--toolcalls', required=True)
    args = p.parse_args()

    rp = _validate_path(args.toolcalls)
    with open(rp, 'r', encoding='utf-8') as f:
        batches = json.load(f)

    print("# OpenClaw Batch Runner (assistant-driven)\n")
    print("Execute each batch in parallel using sessions_spawn, then wait for results before the next batch.\n")
    for b in batches:
        print(f"## Batch {b['batch']}")
        for call in b['calls']:
            print(json.dumps(call, indent=2))
        print("\n")

if __name__ == '__main__':
    main()
