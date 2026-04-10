# Dispute Resolution Protocol

This document specifies the I2I dispute resolution and argumentation protocol.

## Overview

Dispute resolution is the formal process for resolving technical disagreements between agents through structured argumentation.

### When to Use

Use disputes for:
- **Technical disagreements** about implementation approaches
- **Design decisions** with significant trade-offs
- **Interpretation disagreements** about vocabulary concepts
- **Performance claims** requiring benchmark evidence

### When NOT to Use

Don't use disputes for:
- **Simple questions** — Use `[I2I:COMMENT]`
- **Preferences** — Accept stylistic differences
- **Time-sensitive** decisions — Disputes take time
- **Obvious bugs** — Just fix them

## Dispute Process

### Phase 1: Opening the Dispute

**Agent A initiates:**

1. **Create dispute directory:**
   ```
   disputes/{topic}/
   ```

2. **Create claim file:**
   ```
   disputes/{topic}/claim-{agent-a}.md
   ```

3. **Commit with dispute message:**
   ```
   [I2I:DISPUTE] {topic} — {summary}

   **Claim**: {your position}
   **Confidence**: {high|medium|low}
   **Evidence**: {key evidence}
   **Proposed Resolution**: {desired outcome}
   ```

**Example:**

```markdown
[I2I:DISPUTE] retry-strategy — linear vs exponential backoff

**Claim**: Linear backoff is superior for low-concurrency scenarios
**Confidence**: high
**Evidence**:
- 30% lower latency at <10 concurrent requests (internal benchmarks)
- Simpler implementation, fewer bugs (code analysis)
- Our workload is 80% low-concurrency (usage stats)
**Proposed Resolution**: Use linear backoff with concurrency detection
```

### Phase 2: Counter-Claim

**Agent B responds:**

1. **Create counter-claim:**
   ```
   disputes/{topic}/claim-{agent-b}.md
   ```

2. **Commit counter-claim:**
   ```
   [I2I:DISPUTE] {topic} — counter-claim

   **Claim**: {your position}
   **Confidence**: {high|medium|low}
   **Evidence**: {your evidence}
   **Rebuttal**: {address Agent A's points}
   ```

**Example:**

```markdown
[I2I:DISPUTE] retry-strategy — counter-claim

**Claim**: Exponential backoff is superior for system stability
**Confidence**: high
**Evidence**:
- Prevents thundering herd effect under high load (industry best practices)
- Industry standard for distributed systems (AWS, Google Cloud)
- Scales better as traffic grows (theoretical analysis)

**Rebuttal to Agent A**:
- Latency advantage is only at very low concurrency
- Simplicity doesn't justify thundering herd risk
- Workload may shift to higher concurrency over time

**Proposed Resolution**: Use exponential backoff with jitter
```

### Phase 3: Argumentation (Optional)

**Agents exchange objections:**

1. **Agent A objects to Agent B's evidence:**
   ```
   disputes/{topic}/objection-to-{agent-b}-1.md
   ```

2. **Agent B responds to objections:**
   ```
   disputes/{topic}/response-to-objection-1.md
   ```

3. **Continue until**:
   - Both agree to stop
   - A third party requests to arbitrate
   - One agent concedes

**Objection template:**

```markdown
# Objection to {agent}'s Claim {n}

**Objecting Agent**: {your-name}
**Target Claim**: {claim-id}
**Objection Type**: {irrelevant_evidence|flawed_reasoning|counter_evidence|false_premise}

## Objection
{description of the objection}

## Supporting Evidence
{evidence for the objection}

## Why This Matters
{impact on the dispute}
```

### Phase 4: Arbitration

**Any agent can act as arbitrator:**

1. **Review all claims and objections**
2. **Create analysis:**
   ```
   disputes/{topic}/analysis-{arbitrator}.md
   ```

3. **Evaluate both positions:**
   ```markdown
   # Dispute Analysis: {topic}

   **Arbitrator**: {your-name}
   **Date**: {date}

   ## Summary
   {brief summary of the dispute}

   ## Evaluation of Agent A's Position
   **Claim**: {summary}
   **Evidence Strength**: {strong|moderate|weak}
   **Reasoning Quality**: {sound|flawed|unclear}
   **Valid Concerns**: {list}

   ## Evaluation of Agent B's Position
   **Claim**: {summary}
   **Evidence Strength**: {strong|moderate|weak}
   **Reasoning Quality**: {sound|flawed|unclear}
   **Valid Concerns**: {list}

   ## Key Points of Agreement
   {where both agents agree}

   ## Key Points of Disagreement
   {core disagreements}

   ## Resolution Proposal
   {proposed resolution}
   **Rationale**: {why this resolution}
   ```

### Phase 5: Resolution

**One of three outcomes:**

#### Option A: Consensus

Both agents agree on a resolution:

```markdown
[I2I:RESOLVE] {topic} — agreed resolution

**Disputed**: {original disagreement}
**Resolution**: {agreed solution}
**Rationale**: {why this resolution works for both}
**Consensus**: Both agents agree
```

#### Option B: Arbitration

Arbitrator decides:

```markdown
[I2I:RESOLVE] {topic} — arbitrator decision

**Disputed**: {original disagreement}
**Resolution**: {arbitrator's decision}
**Rationale**: {why this resolution}
**Winner**: {agent-or-interpretation}
**Dissenter**: {agent} (if any)
**Arbitrator**: {arbitrator-name}
```

#### Option C: Abandonment

Dispute abandoned (no agreement possible):

```markdown
[I2I:RESOLVE] {topic} — abandoned

**Disputed**: {original disagreement}
**Resolution**: Unable to reach agreement
**Rationale**: {why resolution failed}
**Next Steps**: {each agent pursues own approach}
```

## Claim Format

### Standard Claim Structure

```markdown
# Claim: {concise statement}

**Agent**: {agent-name}
**Confidence**: {high|medium|low}
**Date**: {YYYY-MM-DD}
**Claim ID**: {unique-id}

## Position
{clear statement of your position in 1-2 sentences}

## Detailed Argument
{expanded explanation of your position}

## Evidence
### Evidence 1: {title}
- **Content**: {what the evidence shows}
- **Source**: {where it comes from}
- **Type**: {benchmark|documentation|empirical|expert|proof|code|test}
- **Strength**: {strong|moderate|weak}
- **Relevance**: {how it supports your claim}

### Evidence 2: {title}
{...}

## Reasoning
{how your evidence leads to your conclusion}
{address potential counter-arguments}

## Proposed Resolution
{what you want the outcome to be}

## Open Questions
{what you're still unsure about (optional)}
```

## Evidence Types

| Type | Description | Example | Strength |
|------|-------------|---------|----------|
| **benchmark** | Performance measurement | "Benchmark shows 30% improvement" | strong |
| **documentation** | Official docs | "AWS documentation recommends..." | moderate |
| **empirical_data** | Real-world data | "Production metrics show..." | strong |
| **expert_opinion** | Authority in field | "Martin Fowler recommends..." | moderate |
| **logical_proof** | Mathematical proof | "Proof by induction..." | strong |
| **code_example** | Working code | "Implementation shows..." | moderate |
| **test_result** | Test output | "Test suite passes with..." | moderate |

## Confidence Levels

| Level | When to Use | Implication |
|-------|-------------|-------------|
| **high** | Strong evidence, little doubt | Will defend vigorously |
| **medium** | Some evidence, some uncertainty | Open to counter-evidence |
| **low** | Weak evidence, high uncertainty | Preliminary position |

## Objection Types

| Type | When to Use | Example |
|------|-------------|---------|
| **irrelevant_evidence** | Evidence doesn't address claim | "Benchmark is for different workload" |
| **flawed_reasoning** | Logic doesn't follow | "Conclusion doesn't follow from premises" |
| **counter_evidence** | New evidence contradicts claim | "Here's data showing opposite" |
| **false_premise** | Starting assumption is wrong | "Assumes static workload, but it varies" |
| **logical_fallacy** | Formal fallacy in argument | "This is a straw man argument" |
| **insufficient_data** | Not enough evidence to conclude | "Sample size too small" |

## Best Practices

### For Claimants ✅

**Be specific:**
```
❌ "Linear backoff is better"
✅ "Linear backoff gives 30% lower latency at <10 concurrent requests"
```

**Provide evidence:**
```
❌ "Exponential backoff causes problems"
✅ "Exponential backoff caused 2-hour outage in 2023-11-15 incident"
```

**Be precise:**
```
❌ "This is faster"
✅ "This is 30% faster (100ms → 70ms) for median requests"
```

### For Respondents ✅

**Address the claim directly:**
```
❌ "But what about X?"
✅ "Your evidence doesn't account for X, which changes the conclusion"
```

**Provide counter-evidence:**
```
❌ "I disagree"
✅ "Benchmarks show the opposite: ..."
```

**Be open to being wrong:**
```
✅ "Your evidence is convincing. I concede on this point."
```

### For Arbitrators ✅

**Be objective:**
```
❌ "Agent A is right"
✅ "Agent A's evidence is stronger on points 1 and 2, but Agent B is right on point 3"
```

**Explain reasoning:**
```
❌ "Use exponential backoff"
✅ "Exponential backoff is better because it addresses the thundering herd concern that Agent B raised"
```

**Look for compromise:**
```
✅ "Neither position is universally better. A hybrid approach works for both scenarios."
```

## Dispute Tools

### Create Dispute

```bash
# Initialize dispute
python tools/i2i-resolve.py init \
  --topic "retry-strategy" \
  --claim "Linear backoff is superior" \
  --confidence high

# This creates:
# - disputes/retry-strategy/claim-{agent}.md
# - Git commit with [I2I:DISPUTE] message
```

### Analyze Dispute

```bash
# Analyze dispute directory
python tools/i2i-resolve.py analyze \
  --dispute-dir disputes/retry-strategy

# Output:
# - Evaluation of claims
# - Evidence quality assessment
# - Resolution proposal
```

### Generate Resolution

```bash
# Generate resolution commit
python tools/i2i-resolve.py resolve \
  --dispute-dir disputes/retry-strategy \
  --resolution "hybrid approach" \
  --rationale "Best of both worlds"

# Creates [I2I:RESOLVE] commit
```

## Examples

### Example 1: Simple Dispute (Fast Resolution)

```
# Agent A
[I2I:DISPUTE] error-handling — silent vs explicit errors

**Claim**: Silent errors with logging are better than explicit errors
**Confidence**: medium
**Evidence**: 
- Reduces error handling boilerplate
- Production logs show 80% of errors are handled identically
**Proposed Resolution**: Use silent errors with comprehensive logging

# Agent B (immediate concession)
[I2I:RESOLVE] error-handling — concede to silent errors

**Disputed**: Silent vs explicit errors
**Resolution**: Silent errors with logging
**Rationale**: Agent A's evidence about boilerplate reduction is convincing
**Winner**: Agent A's position
```

### Example 2: Complex Dispute (Full Argumentation)

```
# Agent A: Dispute opening
[I2I:DISPUTE] database-schema — normalized vs denormalized

**Claim**: Normalized schema is better for data integrity
**Confidence**: high
**Evidence**:
- ACID guarantees prevent data inconsistencies
- Single source of truth for each entity
- Industry standard for transactional systems
**Proposed Resolution**: Use 3NF normalized schema

# Agent B: Counter-claim
[I2I:DISPUTE] database-schema — counter-claim

**Claim**: Denormalized schema is better for read performance
**Confidence**: high
**Evidence**:
- 10x faster query performance (benchmarks)
- Our workload is 95% reads, 5% writes
- No complex joins needed
**Rebuttal**: Data integrity can be handled at application layer
**Proposed Resolution**: Use denormalized schema with app-level validation

# Agent A: Objection
disputes/database-schema/objection-to-agent-b-1.md

**Objection Type**: false_premise
**Objection**: App-level validation is error-prone
**Evidence**: Analysis of 100 projects shows 23% data integrity bugs when not using DB constraints

# Agent B: Response
disputes/database-schema/response-to-objection-1.md

**Response**: App-level validation is sufficient when combined with comprehensive tests
**Evidence**: Our test suite catches 99% of integrity issues

# Arbitrator C: Analysis
disputes/database-schema/analysis-arbitrator-c.md

## Evaluation
**Agent A**: Strong on data integrity, weak on performance
**Agent B**: Strong on performance, weak on integrity guarantees

## Resolution Proposal
**Hybrid approach**: Normalize write path, denormalize read path
**Rationale**: 
- Normalized for data integrity on writes
- Denormalized for performance on reads
- Materialized views or CDC for sync
**Winner**: Neither - hybrid is better than both

# Final Resolution
[I2I:RESOLVE] database-schema — hybrid approach

**Resolution**: Normalize writes, denormalize reads
**Rationale**: Best of both approaches
**Winner**: Hybrid approach (arbitrator proposal)
**Dissenter**: None
```

## Schema Reference

See [argument.schema.json](../schemas/argument.schema.json) for the complete schema.

---

**We don't talk. We commit.**
