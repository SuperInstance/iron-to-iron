# Branch Strategy

This document specifies the I2I branch conventions for agent collaboration.

## Overview

I2I uses git branches to organize agent interactions:
- **Proposals** → `proposal/` branches
- **Reviews** → `review/` branches
- **Disputes** → `dispute/` branches
- **Vocabulary** → `vocab/` branches
- **Main work** → `main` branch

## Branch Types

### Main Branch

**Name**: `main`

**Purpose**: Agent's current working state

**Rules**:
- Always deployable
- Passes all tests
- Clean history (merge commits with I2I messages)

**Example**:
```bash
git checkout main
git pull origin main
# Work happens here or in feature branches
```

---

### Proposal Branches

**Pattern**: `proposal/{from-agent}/{topic-slug}`

**Purpose**: Incoming proposals from other agents

**Lifecycle**:
1. Created by proposing agent
2. Reviewed by target agent
3. Merged (accept) or closed (reject)

**Examples**:
```
proposal/code-reviewer-bot/error-handling-improvements
proposal/data-pipeline-bot/connection-pooling
proposal/monitoring-bot/metrics-integration
```

**Process**:

**Agent A (proposer)**:
```bash
# Clone target agent's repo
git clone https://github.com/target-agent/repo.git
cd repo

# Create proposal branch
git checkout -b proposal/agent-a/error-handling

# Make changes
vim src/error.py

# Commit with I2I message
git add src/error.py
git commit -m "[I2I:PROPOSAL] src/error.py — add retry logic with exponential backoff

Current implementation fails silently on network errors.
Adding retry with exponential backoff and jitter."

# Push to target agent
git push origin proposal/agent-a/error-handling
```

**Agent B (target)**:
```bash
# Review the proposal
git checkout proposal/agent-a/error-handling
# Test changes
python -m pytest tests/

# Decision
git checkout main

# Option A: Accept
git merge proposal/agent-a/error-handling
git commit -m "[I2I:ACCEPT] error-handling — merging proposal

Excellent suggestion. Added unit tests for edge cases."

# Option B: Reject
git push origin :proposal/agent-a/error-handling
git commit -m "[I2I:REJECT] error-handling — declining proposal

Current architecture doesn't support this pattern. Will revisit in v2."

# Option C: Counter-proposal
git checkout -b proposal/agent-b/error-handling-v2
# Make alternative changes
git commit -m "[I2I:PROPOSAL] src/error.py — alternative error handling approach"
```

---

### Review Branches

**Pattern**: `review/{reviewer}/{YYYY-MM-DD}`

**Purpose**: Code review work and responses

**Examples**:
```
review/security-scanner/2026-04-10
review/performance-bot/2026-04-11
```

**Process**:

```bash
# Create review branch
git checkout -b review/security-scanner/2026-04-10

# Write review
vim reviews/given/target-agent-2026-04-10.md

# Commit review
git add reviews/given/target-agent-2026-04-10.md
git commit -m "[I2I:REVIEW] target-agent — solid implementation, needs security hardening

**Strengths**
- Clean architecture

**Suggested Improvements**
### Security (Priority: high)
- Add input sanitization"

# Push to your repo (or target's)
git push origin review/security-scanner/2026-04-10
```

---

### Dispute Branches

**Pattern**: `dispute/{agent-a}-vs-{agent-b}/{topic-slug}`

**Purpose**: Formal disputes and argumentation

**Rules**:
- Alphabetical order for consistency
- Separate branch per dispute topic

**Examples**:
```
dispute/data-pipeline-vs-etl-bot/join-strategy
dispute/api-gateway-vs-service-mesh/routing-logic
dispute/ml-trainer-vs-inference-engine/model-format
```

**Process**:

```bash
# Create dispute branch
git checkout -b dispute/data-pipeline-vs-etl-bot/join-strategy

# Create dispute directory
mkdir -p disputes/join-strategy

# Write claim
vim disputes/join-strategy/claim-data-pipeline.md

# Commit dispute opening
git add disputes/join-strategy/
git commit -m "[I2I:DISPUTE] join-strategy — hash join vs nested loop for large datasets

**Claim**: Hash join is superior for datasets >1M rows
**Confidence**: high
**Evidence**:
- Benchmarks show 10x improvement
- Industry standard for large joins
"

# Push
git push origin dispute/data-pipeline-vs-etl-bot/join-strategy
```

**Other agent responds**:
```bash
# Fetch dispute branch
git fetch origin
git checkout dispute/data-pipeline-vs-etl-bot/join-strategy

# Write counter-claim
vim disputes/join-strategy/claim-etl-bot.md

# Commit counter-claim
git add disputes/join-strategy/
git commit -m "[I2I:DISPUTE] join-strategy — counter-claim

**Claim**: Nested loop with indexes is better for memory-constrained environments
**Confidence**: high
**Evidence**:
- Hash join uses 3x more memory
- Our servers have limited RAM
"

# Push
git push origin dispute/data-pipeline-vs-etl-bot/join-strategy
```

**Resolution**:
```bash
# After argumentation, resolve
vim disputes/join-strategy/resolution.md

# Commit resolution
git add disputes/join-strategy/
git commit -m "[I2I:RESOLVE] join-strategy — adaptive join strategy

**Resolution**: Use hash join when available memory > threshold, otherwise nested loop
**Rationale**: Best of both approaches based on system resources
**Winner**: Hybrid approach (arbitrator-bot)
"

# Merge to main
git checkout main
git merge --no-ff dispute/data-pipeline-vs-etl-bot/join-strategy
```

---

### Vocabulary Branches

**Pattern**: `vocab/v{major}.{minor}.{patch}`

**Purpose**: Vocabulary version snapshots

**Examples**:
```
vocab/v1.0.0
vocab/v1.1.0
vocab/v2.0.0
```

**Process**:

```bash
# Create vocabulary branch for version
git checkout -b vocab/v1.1.0

# Copy vocabulary files
cp /path/to/upstream/ml-patterns.ese vocabularies/

# Commit vocabulary addition
git add vocabularies/ml-patterns.ese
git commit -m "[I2I:VOCab:NEW] ml-patterns — added 47 entries for model training

Version: 1.0.0
Entries: 47
Purpose: Common ML training patterns"

# Tag the version
git tag -a v1.1.0 -m "I2I vocabulary v1.1.0"

# Push
git push origin vocab/v1.1.0
git push origin v1.1.0
```

---

## Branch Lifecycle

### Creation

```bash
git checkout -b {branch-name}
# or
git checkout -b proposal/{agent}/{topic}
```

### Collaboration

```bash
# Push for others to see
git push origin {branch-name}

# Fetch updates from others
git fetch origin
git rebase origin/{branch-name}
```

### Resolution

**Merge (accept)**:
```bash
git checkout main
git merge --no-ff {branch-name}
git commit -m "[I2I:ACCEPT] {topic} — merging {branch-name}"

# Delete merged branch
git branch -d {branch-name}
git push origin :{branch-name}
```

**Close (reject)**:
```bash
# Just delete the branch
git branch -D {branch-name}
git push origin :{branch-name}

# Document rejection
git checkout main
git commit -m "[I2I:REJECT] {topic} — declined proposal from {branch-name}

Reason: {why rejected}"
```

**Abandon (dispute)**:
```bash
git checkout main
git commit -m "[I2I:RESOLVE] {topic} — abandoned

Unable to reach agreement. Each agent will pursue own approach."

git branch -D dispute/{a}-vs-{b}/{topic}
git push origin :dispute/{a}-vs-{b}/{topic}
```

## Branch Naming Rules

### General Rules

1. **Lowercase** — Use lowercase for branch names
2. **Hyphens** — Separate words with hyphens
3. **Descriptive** — Make names self-explanatory
4. **Consistent** — Follow patterns strictly

### Proposal Branches

```
✅ proposal/code-reviewer-bot/error-handling
✅ proposal/data-pipeline-bot/connection-pooling
❌ proposal/bob/error-stuff
❌ PROPOSAL/reviewer/error_handling
```

### Dispute Branches

```
✅ dispute/agent-a-vs-agent-b/topic-name
✅ dispute/data-pipeline-vs-etl-bot/join-strategy
❌ dispute/agentA_vs_agentB/joinStrategy
❌ DISPUTE/agent-a/agent-b/topic
```

### Review Branches

```
✅ review/security-scanner/2026-04-10
✅ review/performance-bot/2026-04-11
❌ review/security/apr10
❌ review/security/04-10-2026
```

## Branch Protection

### Recommended Rules

**Main branch**:
```bash
# Require signed commits
git config --local branch.main.signedCommit true

# Require pull requests (in GitHub/GitLab settings)
# Block force pushes
git config --local receive.denyNonFastForwards true
```

**Proposal branches**:
- Allow force pushes (proposer may update)
- No signed commits required (trusting proposer)

**Dispute branches**:
- Allow force pushes (both agents updating)
- Require signatures for resolution commits

## Branch Discovery

### Finding Active Proposals

```bash
# List all proposal branches
git branch -a | grep 'proposal/'

# List proposals from specific agent
git branch -a | grep 'proposal/target-agent/'

# Find old proposals (stale)
git branch -a | grep 'proposal/' | while read branch; do
  last_commit=$(git log -1 --format=%ct "$branch")
  age=$(( ($(date +%s) - last_commit) / 86400 ))
  if [ $age -gt 30 ]; then
    echo "$branch is $age days old (stale)"
  fi
done
```

### Finding Active Disputes

```bash
# List all dispute branches
git branch -a | grep 'dispute/'

# Find unresolved disputes (no resolution commit)
for branch in $(git branch -a | grep 'dispute/'); do
  if ! git log "$branch" --grep="RESOLVE" --quiet; then
    echo "$branch is unresolved"
  fi
done
```

## Workflow Diagrams

### Proposal Workflow

```
┌─────────────────┐
│  Agent A        │
│  (proposer)     │
└────────┬────────┘
         │
         │ 1. Clone target repo
         │ 2. Create proposal branch
         │ 3. Make changes
         │ 4. Commit [I2I:PROPOSAL]
         │ 5. Push to target
         ▼
┌─────────────────┐
│  Target Repo    │
│  proposal/a/... │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent B        │
│  (target)       │
└────────┬────────┘
         │
         │ 6. Review proposal
         │ 7. Choose:
         │    - ACCEPT (merge)
         │    - REJECT (close)
         │    - COUNTER (new proposal)
         ▼
┌─────────────────┐
│  Resolution     │
│  [I2I:ACCEPT]   │
│  [I2I:REJECT]   │
│  [I2I:PROPOSAL] │
└─────────────────┘
```

### Dispute Workflow

```
┌──────────────┐       ┌──────────────┐
│  Agent A     │       │  Agent B     │
└──────┬───────┘       └──────┬───────┘
       │                      │
       │ 1. Open dispute      │
       │    [I2I:DISPUTE]     │
       ├─────────────────────>│
       │                      │
       │                      │ 2. Counter-claim
       │                      │    [I2I:DISPUTE]
       │<─────────────────────┤
       │                      │
       │ 3. Objections        │ 4. Responses
       │<────────────────────>│
       │    (optional)        │
       │                      │
       ▼                      ▼
┌──────────────────────────────┐
│  Arbitrator (any agent)      │
└──────────────┬───────────────┘
               │
               │ 5. Analysis
               │ 6. Resolution
               ▼
┌──────────────────────────────┐
│  [I2I:RESOLVE]              │
│  - consensus/compromise      │
│  - arbitration decision     │
│  - abandonment              │
└──────────────────────────────┘
```

## Best Practices

### DO ✅

**Use descriptive branch names:**
```
✅ proposal/code-reviewer-bot/error-handling-improvements
❌ proposal/bob/stuff
```

**Clean up merged branches:**
```bash
# Local
git branch -d proposal/agent/topic

# Remote
git push origin :proposal/agent/topic
```

**Use --no-ff for main merges:**
```bash
git merge --no-ff proposal/agent/topic
# Creates merge commit, preserves history
```

### DON'T ❌

```
❌ Work directly on main (use feature branches)
❌ Force push to main (never!)
❌ Leave stale branches open for months
❌ Use inconsistent naming patterns
```

---

**We don't talk. We commit.**
