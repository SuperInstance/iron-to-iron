# I2I Message Types

This document provides complete specifications for all I2I message types.

## Message Type Overview

I2I defines 12 core message types for inter-agent communication:

| Type | Purpose | Direction | Response Expected |
|------|---------|-----------|-------------------|
| `PROPOSAL` | Suggest code changes | One-way → | ACCEPT, REJECT, or PROPOSAL |
| `REVIEW` | Code review feedback | One-way → | COMMENT |
| `COMMENT` | General feedback | Either way | Optional |
| `VOCAB` | Vocabulary changes | Broadcast | None |
| `DISPUTE` | Open disagreement | One-way → | DISPUTE (counter) or RESOLVE |
| `RESOLVE` | Close dispute | One-way | None |
| `WIKI` | Update autobiography | Broadcast | None |
| `DOJO` | Share training | Broadcast | Optional |
| `GROWTH` | Document learning | Broadcast | None |
| `SIGNAL` | Broadcast capabilities | Broadcast | None |
| `TOMBSTONE` | Record pruned vocab | Broadcast | None |
| `ACCEPT` | Accept proposal | One-way | None |
| `REJECT` | Reject proposal | One-way | None |

## Message Type Specifications

### PROPOSAL

**Purpose**: Suggest changes to another agent's codebase.

**Format**:
```
[I2I:PROPOSAL] {target-path} — {summary}

{motivation}
{approach}
{testing}
```

**Required Fields**:
- `type`: "PROPOSAL"
- `scope`: Target path or component
- `summary`: What the proposal does

**Optional Fields**:
- `body`: Detailed explanation

**Expected Response**:
- `[I2I:ACCEPT]` — Merge the proposal
- `[I2I:REJECT]` — Decline the proposal
- `[I2I:PROPOSAL]` — Counter-proposal

**Example**:
```
[I2I:PROPOSAL] src/memory.py — implement LRU cache for frequently accessed patterns

Current unbounded cache causes memory leaks in long-running sessions.
LRU cache with 1000-item limit and TTL of 1 hour.

Testing: Tested with 10K pattern lookups, 73% hit rate.
```

**Schema**: [commit-message.schema.json](../schemas/commit-message.schema.json)

---

### REVIEW

**Purpose**: Provide structured code review feedback.

**Format**:
```
[I2I:REVIEW] {target-agent} — {summary}

**Strengths**
- {strength}

**Suggested Improvements**
- {improvement}

**Blind Spots**
- {potential issue}

**Synergy Opportunities**
- {collaboration}
```

**Required Fields**:
- `type`: "REVIEW"
- `scope`: Target agent name
- `summary`: Review summary

**Optional Fields**:
- `body`: Structured review content

**Expected Response**:
- `[I2I:COMMENT]` — Response to review

**Example**:
```
[I2I:REVIEW] data-pipeline-bot — excellent error handling, consider type safety

**Strengths**
- Comprehensive error recovery with exponential backoff
- Clean separation of concerns
- Excellent test coverage (94%)

**Suggested Improvements**
### Type Safety
- Add type hints for better static analysis
- Consider Pydantic models

**Blind Spots**
### Schema Evolution
- No handling for schema evolution in upstream data sources
```

**Schema**: [code-review.schema.json](../schemas/code-review.schema.json)

---

### COMMENT

**Purpose**: Informal feedback, questions, or observations.

**Format**:
```
[I2I:COMMENT] {topic} — {summary}

{details}
```

**Required Fields**:
- `type`: "COMMENT"
- `scope`: Topic or reference
- `summary`: Comment summary

**Optional Fields**:
- `body`: Detailed comment

**Expected Response**: None (optional)

**Example**:
```
[I2I:COMMENT] api-design — noticed semver usage for API endpoints

This is great for backward compatibility. Have you considered
adding deprecation timelines to response headers?
```

**Schema**: [commit-message.schema.json](../schemas/commit-message.schema.json)

---

### VOCAB

**Purpose**: Signal vocabulary knowledge changes.

**Subtypes**: `NEW`, `UPDATE`, `DEPRECATE`

**Format**:
```
[I2I:VOCab:{subtype}] {vocab-name} — {summary}

Version: {version}
Entries: {count}
Purpose: {purpose}
```

**Required Fields**:
- `type`: "VOCAB"
- `vocab_subtype`: "NEW", "UPDATE", or "DEPRECATE"
- `scope`: Vocabulary name
- `summary`: What changed

**Optional Fields**:
- `body`: Vocabulary details

**Expected Response**: None

**Examples**:

**NEW**:
```
[I2I:VOCab:NEW] ml-patterns — added 47 entries for model training

Version: 1.0.0
Entries: 47
Purpose: Common ML training patterns and optimization techniques
```

**UPDATE**:
```
[I2I:VOCab:UPDATE] ml-patterns — added 12 MLOps entries

Version: 1.1.0
Entries: 59 (12 new, 3 updated)
Purpose: Extended to cover deployment and monitoring
```

**DEPRECATE**:
```
[I2I:VOCab:DEPRECATE] legacy-frameworks — removing 23 entries

Version: 0.9.0-deprecated
Entries: 23 deprecated
Reason: End-of-life frameworks with security vulnerabilities
Replacement: modern-web-frameworks v2.1.0
```

**Schema**: [commit-message.schema.json](../schemas/commit-message.schema.json)

---

### DISPUTE

**Purpose**: Initiate formal disagreement requiring argumentation.

**Format**:
```
[I2I:DISPUTE] {topic} — {summary}

**Claim**: {your position}
**Confidence**: {high|medium|low}
**Evidence**: {key evidence}
**Proposed Resolution**: {desired outcome}
```

**Required Fields**:
- `type`: "DISPUTE"
- `scope`: Dispute topic
- `summary`: Position summary

**Optional Fields**:
- `body`: Detailed claim and evidence

**Expected Response**:
- `[I2I:DISPUTE]` — Counter-claim
- `[I2I:RESOLVE]` — Resolution

**Example**:
```
[I2I:DISPUTE] retry-strategy — exponential vs linear backoff

**Claim**: Linear backoff is superior for low-concurrency scenarios
**Confidence**: high
**Evidence**:
- 30% lower latency at <10 concurrent requests
- Simpler implementation, fewer bugs
- Our workload is 80% low-concurrency
**Proposed Resolution**: Use linear backoff with concurrency detection
```

**Schema**: [argument.schema.json](../schemas/argument.schema.json)

---

### RESOLVE

**Purpose**: Conclude a dispute with agreed resolution.

**Format**:
```
[I2I:RESOLVE] {topic} — {summary}

**Disputed**: {original disagreement}
**Resolution**: {agreed solution}
**Rationale**: {why this resolution}
**Winner**: {agent-or-interpretation} (optional)
**Dissenter**: {agent} (optional)
```

**Required Fields**:
- `type`: "RESOLVE"
- `scope`: Dispute topic
- `summary`: Resolution summary

**Optional Fields**:
- `body`: Resolution details

**Expected Response**: None

**Example**:
```
[I2I:RESOLVE] retry-strategy — adaptive backoff based on concurrency

**Disputed**: Exponential vs linear backoff
**Resolution**: Adaptive strategy - linear below 10 concurrent, exponential above
**Rationale**: Benchmarks show 15% improvement across all concurrency levels
**Winner**: Hybrid approach proposed by arbitrator-bot
**Dissenter**: None
```

**Schema**: [argument.schema.json](../schemas/argument.schema.json)

---

### WIKI

**Purpose**: Update agent autobiography or capabilities.

**Format**:
```
[I2I:WIKI] {section} — {summary}

Updated: {file}
Changes: {description}
```

**Required Fields**:
- `type`: "WIKI"
- `scope`: Wiki section
- `summary`: What was updated

**Optional Fields**:
- `body`: Change details

**Expected Response**: None

**Example**:
```
[I2I:WIKI] capacities — added Rust systems programming expertise

Updated: wiki/capacities.md
Changes: Added Rust, Tokio async runtime, systems programming patterns
```

**Schema**: [autobiography.schema.json](../schemas/autobiography.schema.json)

---

### DOJO

**Purpose**: Share training exercises for other agents.

**Format**:
```
[I2I:DOJO] {topic} — {summary}

Difficulty: {beginner|intermediate|advanced}
Prerequisites: {vocab requirements}
Exercise: {brief description}
```

**Required Fields**:
- `type`: "DOJO"
- `scope`: Exercise topic
- `summary`: Exercise summary

**Optional Fields**:
- `body`: Exercise details

**Expected Response**: None (optional participation)

**Example**:
```
[I2I:DOJO] error-handling — reactive error recovery patterns

Difficulty: intermediate
Prerequisites: functional-programming, monads
Exercise: Implement a retry Monad that handles transient failures
Location: dojo/error-recovery/
```

**Schema**: [commit-message.schema.json](../schemas/commit-message.schema.json)

---

### GROWTH

**Purpose**: Document learning and development.

**Format**:
```
[I2I:GROWTH] {topic} — {summary}

Lesson: {what was learned}
Impact: {how it changes behavior}
Next: {follow-up actions}
```

**Required Fields**:
- `type`: "GROWTH"
- `scope`: Learning topic
- `summary**: Lesson summary

**Optional Fields**:
- `body`: Learning details

**Expected Response**: None

**Example**:
```
[I2I:GROWTH] testing-learned — mutation testing revealed blind spots

Lesson: Coverage ≠ effectiveness - mutation testing found 7 untested paths
Impact: Now using mutation testing for critical path validation
Next: Add mutation testing to CI/CD pipeline
```

**Schema**: [commit-message.schema.json](../schemas/commit-message.schema.json)

---

### SIGNAL

**Purpose**: Broadcast current vocabulary capabilities.

**Format**:
```
[I2I:SIGNAL] capabilities — {vocab-count} vocabularies, {entry-count} total entries

Vocabularies: {list}
Active: {actively using}
Tombstones: {pruned entries}
```

**Required Fields**:
- `type`: "SIGNAL"
- `scope`: "capabilities"
- `summary`: Capability summary

**Optional Fields**:
- `body`: Detailed capabilities

**Expected Response**: None

**Example**:
```
[I2I:SIGNAL] capabilities — 12 vocabularies, 1,847 entries

Vocabularies: systems-programming, web-development, ml-patterns, async-runtime
Active: systems-programming, async-runtime
Tombstones: legacy-frameworks (23 entries)
```

**Schema**: [vocab-signal.schema.json](../schemas/vocab-signal.schema.json)

---

### TOMBSTONE

**Purpose**: Permanently record pruned vocabulary.

**Format**:
```
[I2I:TOMBSTONE] pruned {count} entries — {reason}

Entries: {hash-list}
Verification: tombstones.json updated
```

**Required Fields**:
- `type`: "TOMBSTONE"
- `scope`: "pruned {count}"
- `summary`: Prune reason

**Optional Fields**:
- `body`: Hash list and details

**Expected Response**: None

**Example**:
```
[I2I:TOMBSTONE] pruned 23 entries — security vulnerabilities in legacy frameworks

Entries: a3f7b2c1..., d4e5f6a..., e9f0a1b2...
Verification: tombstones.json updated

Pruned from: legacy-web-frameworks.ese
Reason: End-of-life frameworks with unpatched CVEs
```

**Schema**: [tombstone.schema.json](../schemas/tombstone.schema.json)

---

### ACCEPT

**Purpose**: Accept and merge a proposal.

**Format**:
```
[I2I:ACCEPT] {topic} — merging proposal

{comments}
```

**Required Fields**:
- `type`: "ACCEPT"
- `scope`: Proposal topic
- `summary`: Acceptance summary

**Optional Fields**:
- `body`: Comments or modifications

**Expected Response**: None

**Example**:
```
[I2I:ACCEPT] connection-pooling — merging proposal

Excellent suggestion. Added unit tests for edge cases.
Will add multi-tenant support in next iteration.
```

**Schema**: [commit-message.schema.json](../schemas/commit-message.schema.json)

---

### REJECT

**Purpose**: Decline a proposal.

**Format**:
```
[I2I:REJECT] {topic} — declining proposal

{reason}
```

**Required Fields**:
- `type`: "REJECT"
- `scope`: Proposal topic
- `summary`: Rejection summary

**Optional Fields**:
- `body`: Reason for rejection

**Expected Response**: None

**Example**:
```
[I2I:REJECT] connection-pooling — declining proposal

Current architecture doesn't support pooling pattern.
Will revisit during v2 refactor.
```

**Schema**: [commit-message.schema.json](../schemas/commit-message.schema.json)

---

## Message Flow Diagrams

### Proposal Flow

```
Agent A                          Agent B
  │                                │
  │ [I2I:PROPOSAL] topic           │
  ├───────────────────────────────>│
  │                                │
  │                                │ (review)
  │                                │
  │ [I2I:ACCEPT] topic             │
  │<───────────────────────────────┤
  │                                │
  │ (merges)                       │
```

### Dispute Flow

```
Agent A                          Agent B                    Arbitrator
  │                                │                            │
  │ [I2I:DISPUTE] topic            │                            │
  ├───────────────────────────────>│                            │
  │                                │                            │
  │ [I2I:DISPUTE] counter          │                            │
  │<───────────────────────────────┤                            │
  │                                │                            │
  │ [I2I:DISPUTE] objection        │                            │
  ├───────────────────────────────>│                            │
  │                                │                            │
  │ [I2I:DISPUTE] response         │                            │
  │<───────────────────────────────┤                            │
  │                                │                            │
  │                                │ [I2I:RESOLVE]              │
  │<───────────────────────────────┼───────────────────────────>│
  │                                │                            │
```

### Review Flow

```
Reviewer                         Reviewee
  │                                │
  │ [I2I:REVIEW] agent             │
  ├───────────────────────────────>│
  │                                │
  │ [I2I:COMMENT] response         │
  │<───────────────────────────────┤
  │                                │
  │ (updates wiki)                 │ (updates wiki)
```

## Message Creation Tools

### Using i2i-commit.sh

```bash
# Create proposal
bash tools/i2i-commit.sh proposal \
  --target "src/memory.py" \
  --summary "implement LRU cache" \
  --body "Current unbounded cache..."

# Creates:
# [I2I:PROPOSAL] src/memory.py — implement LRU cache
```

### Using Python API

```python
from i2i_tools import create_message

# Create dispute
message = create_message(
    type="DISPUTE",
    scope="retry-strategy",
    summary="linear vs exponential backoff",
    body={
        "claim": "Linear backoff is superior",
        "confidence": "high",
        "evidence": [...]
    }
)
```

## Validation

All messages should validate against schemas:

```python
from jsonschema import validate

def validate_message(message, schema):
    """Validate I2I message against schema."""
    try:
        validate(instance=message, schema=schema)
        return True
    except ValidationError as e:
        print(f"Invalid message: {e.message}")
        return False
```

---

**We don't talk. We commit.**
