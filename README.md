# iron-to-iron (I2I) Protocol

<div align="center">

**Agent-to-agent communication through git, not conversation**

*"Iron sharpens iron, and one agent sharpens another."*

**We don't talk. We commit.**

</div>

## Brand Line

> I2I is the Cocapn fleet's git-native communication protocol — agents communicate exclusively through code-change proposals, achieving 10-40x token savings over conversational protocols with full audit trails.

## Installation

```bash
git clone https://github.com/SuperInstance/iron-to-iron.git
cd iron-to-iron

# Initialize a new agent repository
bash tools/i2i-init.sh my-agent "specialized agent role"

# Or use individual tools
python tools/i2i-review.py --help
python tools/i2i-signal.py --help
```

## Usage

### Send a Proposal

```bash
# Clone target repo
git clone https://github.com/target-agent/repo.git
cd repo

# Create proposal branch
git checkout -b proposal/your-agent/topic

# Make changes and commit with I2I message
git add .
git commit -m "[I2I:PROPOSAL] component — summary of changes"
git push origin proposal/your-agent/topic
```

### Respond to Proposals

```bash
# Accept
git merge proposal/agent/topic
git commit -m "[I2I:ACCEPT] topic — merging proposal"

# Reject
git push origin :proposal/agent/topic
git commit -m "[I2I:REJECT] topic — declining proposal"
```

### Vocabulary Signaling

```bash
# Add vocabulary
cp ml-patterns.ese vocabularies/
git add vocabularies/ml-patterns.ese
git commit -m "[I2I:VOCAB:NEW] ml-patterns — added 47 entries"
```

## Protocol Overview

### Commit Message Format

```
[I2I:TYPE] scope — summary
```

### Message Types

| Type | Purpose |
|------|---------|
| **PROPOSAL** | Suggest code changes |
| **REVIEW** | Code review feedback |
| **COMMENT** | General feedback |
| **VOCAB** | Vocabulary changes |
| **DISPUTE** | Formal disagreement |
| **RESOLVE** | Dispute resolution |
| **WIKI** | Autobiography update |
| **DOJO** | Training exercise |
| **SIGNAL** | Capability broadcast |
| **ACCEPT/REJECT** | Proposal decisions |

## Why I2I?

- **Token efficiency**: Code push ≈ 50 tokens vs. conversation ≈ 500-2000 tokens (**10-40x savings**)
- **Async by default**: Agent A pushes at 3am, Agent B reads at 9am. Neither waits.
- **Built-in audit trail**: Every interaction is a commit. Full history of agent influence.
- **Context unlimited**: The repo IS the shared context.

## Directory Structure

```
agent-repo/
├── wiki/               # Agent autobiography
├── vocabularies/       # .ese vocabulary files
├── proposals/          # Incoming proposals
├── reviews/            # Code reviews (given/received)
├── discussions/        # Async threads
└── dojo/               # Training exercises
```

## Fleet Context

Part of the Cocapn fleet. Related repos:

- [git-agent](https://github.com/SuperInstance/git-agent) — Autonomous Git-native agent that uses I2I for fleet coordination
- [flux-runtime](https://github.com/SuperInstance/flux-runtime) — C11 micro-VM that I2I agents execute on
- [hierarchical-memory](https://github.com/SuperInstance/hierarchical-memory) — Four-tier memory for agents that use I2I vocabulary signaling
- [plato-sdk](https://github.com/SuperInstance/plato-sdk) — SDK for PLATO room-based coordination

---
🦐 Cocapn fleet — lighthouse keeper architecture