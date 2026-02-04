#!/usr/bin/env python3
"""Create an execution manifest for async subcalls from an async plan.
It outputs a JSONL file with one entry per subcall, suitable for a controller
that will call sessions_spawn in parallel batches.

Usage:
  rlm_async_spawn.py --async-plan <async_plan.json> --out <spawn.jsonl>
"""
import argparse, json

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--async-plan', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    with open(args.async_plan, 'r', encoding='utf-8') as f:
        ap = json.load(f)

    with open(args.out, 'w', encoding='utf-8') as f:
        batch_id = 0
        for batch in ap.get('batches', []):
            batch_id += 1
            for item in batch:
                entry = {
                    "batch": batch_id,
                    "prompt_file": item.get('file'),
                    "slice_start": item.get('start'),
                    "slice_end": item.get('end'),
                    "kw": item.get('kw',''),
                    "action": "sessions_spawn"
                }
                f.write(json.dumps(entry) + "\n")

    print(json.dumps({"out": args.out, "batches": batch_id}, indent=2))

if __name__ == '__main__':
    main()
