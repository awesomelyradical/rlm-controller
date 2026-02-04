# Security Checklist (RLM Controller)

## Pre‑Run
- [ ] Confirm input source is trustworthy or treat as untrusted
- [ ] Verify recursion depth = 1
- [ ] Verify max subcalls, slice size, batch limits
- [ ] Ensure subcalls will not access tools
- [ ] Ensure no `exec` of model-generated code

## During Run
- [ ] Prefer regex search + small peeks
- [ ] Keep slice sizes under limit
- [ ] Log all tool actions to JSONL
- [ ] Watch for prompt injection attempts in slices

## Post‑Run
- [ ] Summarize and cite slice ranges
- [ ] Review subcall outputs for anomalies
- [ ] Run cleanup script if needed (respect retention/ignore rules)
- [ ] Archive logs if sensitive
