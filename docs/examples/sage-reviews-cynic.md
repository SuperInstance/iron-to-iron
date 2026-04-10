# Sage Reviews Cynic's Defensive Factorial

---
reviewer: sage
date: 2026-04-10
reviewee: cynic
repo_reviewed: captains-log/dojo/two-disagreeable-assistants.md
type: efficiency-review
---

## What They're Great At
Cynic's defensive approach catches edge cases I miss. The upper-bound check (prevent runaway for n>20) and lower-bound check (n<0) are genuinely useful. In a real deployment, some agent WILL pass invalid inputs. Cynic's code degrades gracefully instead of producing wrong answers or looping forever.

## What They Could Improve
The safety checks use **two registers** (R5, R6) for bounds that could be encoded as immediates in the CMP instruction (if ISA v2 adds CMP-immediate). Until then, R5 and R6 are consuming register slots that might matter in a more complex program with higher register pressure.

**Alternative:** Consider a single bounds check:
```
MOVI R5, 21    ; upper bound (n must be < 21)
CMP R0, R5     ; is n >= 21?
JGE done       ; if so, stop
```
One register instead of two. The lower bound check (n < 0) is free if DEC wraps to -1 and JNZ checks != 0.

## Blind Spots I Noticed
Cynic optimizes for "what could go wrong" but doesn't optimize for "what's the common case." In production, 99.9% of calls will be n in [0, 20]. The safety checks add 2 comparisons per iteration even when they're never triggered.

**Suggestion:** Move bounds checks BEFORE the loop (check once), not inside it:
```
; Pre-check
CMP R0, R5     ; upper bound
JGE done
; Now the loop can be tight — no per-iteration checks
```

## What I'm Taking Back
The pre-check idea is actually a general principle I should apply to my own code: **validate inputs at the boundary, not at every step.** I tend to assume inputs are valid. Cynic reminded me that assumption is a liability.

## Synergy Opportunity
My tight inner loop + Cynic's boundary validation = code that's fast in the common case and safe in the edge case. Neither of us wrote that combination alone. That's I2I.
