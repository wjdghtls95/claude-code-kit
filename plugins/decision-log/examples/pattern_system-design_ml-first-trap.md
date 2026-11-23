---
name: ml-first-trap
description: Adding machine learning to a new system from day one adds complexity. Validate with plain files first, then decide
metadata:
  type: pattern
  domain: system-design
  scope: global
  confidence: high
---

## Situation
While designing a new system, a discussion starts about adding ML (embeddings) to improve detection quality.

## Previous approach
Build embedding-based semantic detection and a vector search from the start.

## Trigger (what changed it)
Scale analysis: at roughly 50 to 100 items, embeddings are over-engineering compared with an index file and keyword search.

## New approach
Build the file-based version first (an index plus reading files directly). Decide on ML only after the simple version is validated.

## Alternatives considered
- Vector search: at small scale it adds complexity, and accuracy can be lower than keyword search
- ML from the start: debugging gets much harder, and it is difficult to tell what went wrong

## When to apply
- A new system design where "wouldn't ML make this better?" comes up
- The data is still small or its size is unknown

## When not to apply
- The data is tens of thousands of items or more and keyword search is clearly not accurate enough
- ML infrastructure already exists and the extra cost is small

## Related patterns
- Same line as the principle of adding complexity gradually: check that the simple thing works first
