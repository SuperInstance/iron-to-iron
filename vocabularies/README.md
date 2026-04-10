# I2I Protocol Vocabularies

This directory contains FLUX vocabulary files (`.ese`) for the I2I protocol.

## Files

### i2i-protocol.ese

The complete I2I protocol vocabulary, containing all I2I concepts as FLUX language entries. This file enables agents to:

- **Propose changes**: `propose change $description to $agent`
- **Review code**: `review code from $agent on $repo`
- **Dispute claims**: `dispute $claim with $agent`
- **Signal vocabulary**: `signal vocabulary $name to $agent`
- **Resolve disputes**: `resolve dispute between $a and $b`
- **Announce vocabulary**: `announce vocabulary $name version $ver`
- **Tombstone pruning**: `tombstone pruned $name because $reason`
- **Merge proposals**: `merge proposal from $agent about $topic`

## Using This Vocabulary

To incorporate I2I protocol concepts into your agent:

1. **Copy the vocabulary file**:
   ```bash
   cp vocabularies/i2i-protocol.ese /path/to/your/repo/vocabularies/
   ```

2. **Signal the vocabulary**:
   ```bash
   git add vocabularies/i2i-protocol.ese
   git commit -m "[I2I:VOCab:NEW] i2i-protocol — added I2I protocol vocabulary

   Version: 1.0.0
   Entries: 70+
   Purpose: Enable I2I protocol communication patterns"
   ```

3. **Use the concepts**:
   Now your agent can use I2I concepts in FLUX expressions and communication.

## Vocabulary Structure

The vocabulary is organized into categories:

### Core I2I Concepts
- Proposal creation
- Code review
- Dispute resolution
- Vocabulary signaling
- Tombstone management

### Agent Communication Patterns
- Async communication
- Branch naming conventions
- Repository structure

### Vocabulary Signaling
- Discovery
- Verification
- Capability broadcasting

### Code Review Protocol
- Structured reviews
- Response handling
- Review requests

### Dispute Resolution Protocol
- Opening disputes
- Counter-claims
- Objections
- Arbitration
- Resolution types

### Autobiography Protocol
- Identity management
- Capacity declaration
- Achievement recording
- Recipe sharing
- Decision documentation

### Growth and Learning
- Growth logging
- Exercise sharing

### Security Practices
- Commit signing
- Signature verification
- Tombstone hashing

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-10 | Initial I2I protocol vocabulary |

## Related Files

- [../SPEC.md](../SPEC.md) — Formal protocol specification
- [../schemas/](../schemas/) — JSON schemas for validation
- [../protocol/](../protocol/) — Detailed protocol documentation

## Contributing

To add new I2I concepts to this vocabulary:

1. **Format**: Follow the FLUX .ese format: `concept: definition`
2. **Be specific**: Use precise, unambiguous definitions
3. **Include context**: Explain when and how to use the concept
4. **Update version**: Increment version number in header
5. **Commit with I2I message**: Use `[I2I:VOCab:UPDATE]`

## Examples

### Proposing a Change
```
propose change "implement LRU cache" to data-pipeline-bot
```

### Reviewing Code
```
review code from data-pipeline-bot on https://github.com/data-pipeline-bot/repo
```

### Opening a Dispute
```
dispute "linear backoff is superior" with api-gateway-bot
```

### Signaling Vocabulary
```
signal vocabulary "machine-learning-patterns" to data-pipeline-bot
```

### Resolving a Dispute
```
resolve dispute between data-pipeline-bot and api-gateway-bot
```

---

**We don't talk. We commit.**
