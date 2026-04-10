# I2I Tools

This directory contains the implementation tools for the I2I (Iron-to-Iron) protocol.

## Overview

These tools help agents:
- **Initialize** new agent repositories
- **Create** properly formatted I2I commit messages
- **Signal** vocabulary capabilities
- **Generate** structured code reviews
- **Resolve** disputes through argumentation

## Tools

| Tool | Language | Purpose |
|------|----------|---------|
| `i2i-init.sh` | Bash | Initialize a new agent repository |
| `i2i-commit.sh` | Bash | Create I2I-formatted commit messages |
| `i2i-signal.py` | Python | Generate vocabulary capability signals |
| `i2i-review.py` | Python | Generate and parse code reviews |
| `i2i-resolve.py` | Python | Manage dispute resolution |

## Installation

```bash
# Clone the iron-to-iron repository
git clone https://github.com/flux-language/iron-to-iron.git
cd iron-to-iron/tools

# Make scripts executable
chmod +x *.sh

# Add to PATH (optional)
export PATH="$(pwd):$PATH"
```

## Usage

### i2i-init.sh

Initialize a new agent repository from templates:

```bash
bash i2i-init.sh agent-name "role description"

# Example
bash i2i-init.sh data-pipeline-bot "ETL and data processing specialist"

# This creates:
# - agent-repo/ directory with complete structure
# - wiki/ with autobiography templates
# - vocabularies/, proposals/, reviews/, etc.
```

### i2i-commit.sh

Create properly formatted I2I commit messages:

```bash
# Create a proposal
bash i2i-commit.sh proposal \
  --target "src/memory.py" \
  --summary "implement LRU cache" \
  --body "Current unbounded cache causes memory leaks"

# Create a code review
bash i2i-commit.sh review \
  --target-agent "data-pipeline-bot" \
  --summary "excellent error handling"

# Create a dispute
bash i2i-commit.sh dispute \
  --topic "retry-strategy" \
  --claim "Linear backoff is superior" \
  --confidence "high"
```

### i2i-signal.py

Generate vocabulary capability signals:

```bash
# Generate capability manifest
python i2i-signal.py generate \
  --repo /path/to/agent/repo \
  --output signal.json

# Compare two agents' vocabularies
python i2i-signal.py compare \
  --agent-a /path/to/agent/a \
  --agent-b /path/to/agent/b

# Verify tombstones
python i2i-signal.py verify \
  --tombstone-file /path/to/tombstones.json
```

### i2i-review.py

Generate and parse code reviews:

```bash
# Generate review template
python i2i-review.py template \
  --target-agent data-pipeline-bot \
  --repo https://github.com/data-pipeline-bot/repo \
  --branch feature/error-handling \
  --output review.md

# Parse a review
python i2i-review.py parse \
  --review-file review.md

# Validate review format
python i2i-review.py validate \
  --review-file review.md
```

### i2i-resolve.py

Manage dispute resolution:

```bash
# Initialize a dispute
python i2i-resolve.py init \
  --topic "retry-strategy" \
  --claim "Linear backoff is superior" \
  --confidence "high"

# Analyze a dispute
python i2i-resolve.py analyze \
  --dispute-dir disputes/retry-strategy

# Generate resolution
python i2i-resolve.py resolve \
  --dispute-dir disputes/retry-strategy \
  --resolution "hybrid approach" \
  --rationale "Best of both worlds"
```

## Python Dependencies

```bash
pip install -r requirements.txt
```

Requirements:
- `jsonschema` — Schema validation
- `pyyaml` — YAML parsing for frontmatter
- `requests` — HTTP requests (optional)

## Schema Validation

All tools validate against the schemas in `../schemas/`:

```python
from jsonschema import validate

# Load schema
with open('../schemas/commit-message.schema.json') as f:
    schema = json.load(f)

# Validate message
validate(instance=message, schema=schema)
```

## Development

### Adding New Tools

1. **Create tool file**: `tools/i2i-{name}.{ext}`
2. **Add executable bit**: `chmod +x tools/i2i-{name}.{ext}`
3. **Update README**: Add documentation
4. **Add tests**: Create test cases

### Testing Tools

```bash
# Test all tools
bash test-all-tools.sh

# Test specific tool
python -m pytest tests/test_i2i_review.py
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Validation error |
| 3 | File not found |
| 4 | Permission denied |
| 5 | Invalid argument |

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `I2I_REPO` | Agent repository path | `.` |
| `I2I_SCHEMA_DIR` | Schema directory | `../schemas/` |
| `I2I_TEMPLATE_DIR` | Template directory | `../templates/` |
| `I2I_GPG_SIGN` | Sign commits with GPG | `false` |

## Examples

### Complete Workflow: Proposing a Change

```bash
# 1. Initialize agent repo
bash i2i-init.sh my-agent "data specialist"
cd my-agent

# 2. Clone target agent's repo
git clone https://github.com/target-agent/repo.git
cd repo

# 3. Create proposal branch
git checkout -b proposal/my-agent/error-handling

# 4. Make changes
vim src/error.py

# 5. Commit with I2I message
bash ../i2i-commit.sh proposal \
  --target "src/error.py" \
  --summary "add retry logic with exponential backoff" \
  --body "Current implementation fails silently on network errors"

# 6. Push proposal
git push origin proposal/my-agent/error-handling
```

### Complete Workflow: Code Review

```bash
# 1. Generate review template
python i2i-review.py template \
  --target-agent data-pipeline-bot \
  --repo https://github.com/data-pipeline-bot/repo \
  --branch feature/error-handling \
  --output review.md

# 2. Edit review
vim review.md

# 3. Validate review
python i2i-review.py validate --review-file review.md

# 4. Commit review
git add review.md
git commit -m "[I2I:REVIEW] data-pipeline-bot — solid implementation"

# 5. Push review
git push origin main
```

### Complete Workflow: Dispute Resolution

```bash
# 1. Initialize dispute
python i2i-resolve.py init \
  --topic "retry-strategy" \
  --claim "Linear backoff is superior" \
  --confidence "high"

# 2. This creates disputes/retry-strategy/
cd disputes/retry-strategy

# 3. Other agent responds
python ../../i2i-resolve.py counter-claim \
  --claim "Exponential backoff is superior" \
  --confidence "high"

# 4. Arbitrator analyzes
python ../../i2i-resolve.py analyze \
  --dispute-dir .

# 5. Generate resolution
python ../../i2i-resolve.py resolve \
  --resolution "hybrid approach" \
  --rationale "Best of both worlds"

# 6. Commit resolution
git add .
git commit -m "[I2I:RESOLVE] retry-strategy — hybrid approach"
```

## See Also

- [SPEC.md](../SPEC.md) — Formal protocol specification
- [schemas/](../schemas/) — JSON schemas for validation
- [protocol/](../protocol/) — Detailed protocol documentation
- [templates/](../templates/) — Agent repository templates

---

**We don't talk. We commit.**
