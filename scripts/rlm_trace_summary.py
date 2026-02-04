#!/usr/bin/env python3
"""Summarize an RLM JSONL log into markdown for quick inspection.
Usage: rlm_trace_summary.py --log <path>
"""
import argparse, json

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--log', required=True)
    args = p.parse_args()

    actions = []
    final = None
    with open(args.log, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get('type') == 'action':
                actions.append(obj)
            if obj.get('type') == 'final':
                final = obj.get('final')

    print("# RLM Trace Summary\n")
    print(f"Total actions: {len(actions)}")
    print("\n## Actions")
    for a in actions:
        print(f"- {a.get('action')} { {k:v for k,v in a.items() if k not in ['type','ts']} }")

    if final:
        print("\n## Final")
        print(final)

if __name__ == '__main__':
    main()
