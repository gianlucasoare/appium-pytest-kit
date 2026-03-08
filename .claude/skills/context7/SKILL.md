---
name: context7
description: Use Context7 as primary source for up-to-date external docs and API references, with local fallback.
---

# Context7

## Use This Skill When

- You need current external documentation or API references
- You are validating package/framework usage against latest docs
- A task asks to "use context7" explicitly

## Workflow

1. Resolve the exact library/tool name and version target
2. Query Context7 first for authoritative docs
3. Extract only the sections needed for the implementation
4. Cross-check planned code against local project constraints
5. If Context7 is unavailable, fall back to local docs/code and call out the gap

## Output Rules

- Prefer primary docs over blog/forum sources
- Keep cited guidance actionable (flags, signatures, behavior)
- Mark assumptions clearly when data is inferred

## Failure Handling

- If Context7 times out or cannot resolve docs, do not block progress
- Continue with deterministic local reasoning and state that Context7 failed
