#!/usr/bin/env python3
"""Minimal RLM runner scaffold for OpenClaw-style workflows.

This runner does NOT call the LLM directly. It prints a step plan and
emits JSONL action templates to log file so an agent/controller can
execute them (e.g., via OpenClaw tools + sessions_spawn).

Usage:
  rlm_runner.py init --ctx <path> --goal <text> --log <path>
  rlm_runner.py add  --log <path> --action <json>
  rlm_runner.py finalize --log <path> --final <text>
"""
import argparse, json, os, sys, time, uuid

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

def log_write(path, obj):
    rp = _validate_path(path)
    obj["ts"] = int(time.time())
    with open(rp, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")


def cmd_init(args):
    run_id = str(uuid.uuid4())[:8]
    header = {
        "type": "init",
        "run_id": run_id,
        "ctx_path": args.ctx,
        "goal": args.goal,
        "policy": {
            "max_depth": 1,
            "max_subcalls": 32,
            "max_slice_chars": 16000
        }
    }
    log_write(args.log, header)
    print(json.dumps(header, indent=2))
    print("\nSuggested next actions:")
    print("- peek/search to find relevant slices")
    print("- spawn subcalls on slices with a precise goal")
    print("- aggregate results and finalize")


def cmd_add(args):
    obj = json.loads(args.action)
    obj["type"] = "action"
    log_write(args.log, obj)


def cmd_finalize(args):
    obj = {"type": "final", "final": args.final}
    log_write(args.log, obj)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)

    i = sub.add_parser('init')
    i.add_argument('--ctx', required=True)
    i.add_argument('--goal', required=True)
    i.add_argument('--log', required=True)

    a = sub.add_parser('add')
    a.add_argument('--log', required=True)
    a.add_argument('--action', required=True, help='JSON action object')

    f = sub.add_parser('finalize')
    f.add_argument('--log', required=True)
    f.add_argument('--final', required=True)

    args = p.parse_args()
    if args.cmd == 'init': cmd_init(args)
    elif args.cmd == 'add': cmd_add(args)
    elif args.cmd == 'finalize': cmd_finalize(args)

if __name__ == '__main__':
    main()
