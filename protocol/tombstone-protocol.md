# Tombstone Protocol

This document specifies the I2I protocol for recording pruned vocabulary knowledge.

## Overview

A **tombstone** is a permanent record of vocabulary an agent once knew but has pruned. It enables:
- **Verification** that the agent had specific knowledge
- **Transparency** about the agent's evolution
- **Auditability** of knowledge changes over time

### Why Prune Vocabulary?

Agents prune vocabulary when:
- **Concepts become obsolete** — Technology deprecated
- **Security vulnerabilities** — Known vulnerabilities in referenced tech
- **Memory constraints** — Agent can only hold so much knowledge
- **Domain shift** — Agent changing specializations
- **Quality control** — Removing low-quality or incorrect entries

### Tombstone Purpose

Tombstones ensure that:
1. **The agent can prove** it once knew a concept
2. **Other agents can verify** the agent's past knowledge
3. **The knowledge history** is permanently recorded
4. **Tampering is detectable** via cryptographic hashes

## Tombstone Format

### tombstones.json Structure

```json
{
  "version": "1.0",
  "generated": "2026-04-10T12:00:00Z",
  "agent": "agent-name",
  "entries": [
    {
      "hash": "a3f7b2c1...",
      "concept": "concept-name",
      "definition": "original definition",
      "source_vocabulary": "vocab-name.ese",
      "vocabulary_version": "1.2.3",
      "pruned_date": "2026-04-10",
      "reason": "deprecated_technology",
      "reason_detail": "Technology end-of-life",
      "replaced_by": "new-concept",
      "commit_hash": "abc123d"
    }
  ],
  "summary": {
    "total_pruned": 23,
    "by_reason": {
      "deprecated_technology": 15,
      "security_vulnerability": 5,
      "obsolete": 3
    },
    "by_vocabulary": {
      "legacy-web-frameworks": 23
    }
  }
}
```

### Hash Generation

Tombstones use SHA256 hashes to **immunably** record knowledge:

```python
import hashlib

def generate_tombstone_hash(concept, definition):
    """
    Generate SHA256 hash for tombstone record.
    
    The hash is computed from concept:definition to prevent
    retrospective tampering.
    """
    content = f"{concept}:{definition}"
    return hashlib.sha256(content.encode()).hexdigest()

# Example
concept = "angularjs-directive"
definition = "A directive in AngularJS 1.x that attaches behavior to DOM elements"
hash = generate_tombstone_hash(concept, definition)
# Output: "a3f7b2c1d8e4f9a3..."
```

## Pruning Process

### Step 1: Identify Entries to Prune

```python
def identify_prune_candidates(vocab_file, criteria):
    """
    Identify vocabulary entries to prune based on criteria.
    
    Criteria can include:
    - Deprecated technology
    - Security vulnerabilities
    - Obsolescence
    - Low quality
    """
    entries = parse_vocabulary_file(vocab_file)
    candidates = []
    
    for entry in entries:
        if matches_criteria(entry, criteria):
            candidates.append({
                "concept": entry.concept,
                "definition": entry.definition,
                "reason": determine_reason(entry, criteria)
            })
    
    return candidates
```

### Step 2: Generate Tombstones

```python
def generate_tombstones(candidates, source_vocab, vocab_version):
    """Generate tombstone entries from candidates."""
    tombstones = []
    
    for candidate in candidates:
        tombstone = {
            "hash": generate_tombstone_hash(
                candidate["concept"],
                candidate["definition"]
            ),
            "concept": candidate["concept"],
            "definition": candidate["definition"],
            "source_vocabulary": source_vocab,
            "vocabulary_version": vocab_version,
            "pruned_date": datetime.now().date().isoformat(),
            "reason": candidate["reason"],
            "commit_hash": get_current_commit_hash()
        }
        tombstones.append(tombstone)
    
    return tombstones
```

### Step 3: Update tombstones.json

```python
def update_tombstone_file(new_tombstones):
    """Append new tombstones to tombstones.json."""
    tombstone_file = Path("tombstones.json")
    
    if tombstone_file.exists():
        with open(tombstone_file) as f:
            data = json.load(f)
    else:
        data = {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "agent": get_agent_name(),
            "entries": [],
            "summary": {
                "total_pruned": 0,
                "by_reason": {},
                "by_vocabulary": {}
            }
        }
    
    # Append new tombstones
    data["entries"].extend(new_tombstones)
    data["generated"] = datetime.now().isoformat()
    
    # Update summary
    data["summary"]["total_pruned"] = len(data["entries"])
    for tombstone in new_tombstones:
        reason = tombstone["reason"]
        vocab = tombstone["source_vocabulary"]
        
        data["summary"]["by_reason"][reason] = \
            data["summary"]["by_reason"].get(reason, 0) + 1
        data["summary"]["by_vocabulary"][vocab] = \
            data["summary"]["by_vocabulary"].get(vocab, 0) + 1
    
    # Write updated file
    with open(tombstone_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return data
```

### Step 4: Commit with TOMBSTONE Message

```bash
git add tombstones.json
git commit -m "[I2I:TOMBSTONE] pruned ${count} entries — ${reason}

Entries: ${hash_list}
Verification: tombstones.json updated

Pruned from: ${vocabulary_name}
Reason: ${detailed_reason}"
```

**Example:**

```
[I2I:TOMBSTONE] pruned 23 entries — security vulnerabilities in legacy frameworks

Entries: a3f7b2c1..., d4e5f6a...
Verification: tombstones.json updated

Pruned from: legacy-web-frameworks.ese
Reason: AngularJS 1.x reached end-of-life in 2022, unpatched vulnerabilities
```

### Step 5: Prune from Vocabulary

Remove the pruned entries from the `.ese` file:

```bash
# Remove pruned entries
sed -i '/concept-to-prune/d vocabularies/legacy-web-frameworks.ese

# Commit the pruning
git add vocabularies/legacy-web-frameworks.ese
git commit -m "[I2I:VOCab:UPDATE] legacy-web-frameworks — pruned 23 entries"
```

## Verification

### Verifying Past Knowledge

Other agents can verify that an agent once knew a concept:

```python
def verify_past_knowledge(agent_repo, concept, definition):
    """
    Verify that an agent once knew a concept.
    
    Returns:
        - True if tombstone exists and hash matches
        - False otherwise
        - None if tombstone file doesn't exist
    """
    tombstone_file = Path(agent_repo) / "tombstones.json"
    
    if not tombstone_file.exists():
        return None
    
    with open(tombstone_file) as f:
        data = json.load(f)
    
    expected_hash = generate_tombstone_hash(concept, definition)
    
    for entry in data["entries"]:
        if entry["concept"] == concept:
            if entry["hash"] == expected_hash:
                return True
            else:
                # Hash mismatch - possible tampering
                return False
    
    # Concept not found in tombstones
    return False
```

### Detecting Tampering

Cryptographic hashes ensure tombstones can't be forged:

```python
def detect_tampering(tombstone_file):
    """
    Verify that tombstone hashes match their concepts.
    
    Returns list of suspicious entries where hash doesn't match.
    """
    with open(tombstone_file) as f:
        data = json.load(f)
    
    suspicious = []
    
    for entry in data["entries"]:
        expected_hash = generate_tombstone_hash(
            entry["concept"],
            entry.get("definition", "")
        )
        
        if entry["hash"] != expected_hash:
            suspicious.append({
                "concept": entry["concept"],
                "expected_hash": expected_hash,
                "actual_hash": entry["hash"]
            })
    
    return suspicious
```

## Tombstone Reasons

### Standard Reasons

| Reason | When to Use | Example |
|--------|-------------|---------|
| `obsolete` | Concept is no longer relevant | "IE6-specific CSS hacks" |
| `security_vulnerability` | Referenced tech has unpatched vulnerabilities | "Drupal 7 module patterns" |
| `memory_constraint` | Agent at capacity, pruning low-priority | "Esoteric programming languages" |
| `domain_shift` | Agent changing specializations | "Web dev patterns → ML patterns" |
| `deprecated_technology` | Technology officially deprecated | "AngularJS 1.x directives" |
| `other` | Other reasons (explain in detail) | Various |

### Reason Detail

Always include **specific detail** about the reason:

```
❌ "reason": "obsolete"
✅ "reason": "obsolete",
   "reason_detail": "IE6 was discontinued in 2006, no longer supported"
```

## Tombstone Statistics

Track pruning patterns over time:

```python
def analyze_tombstone_history(tombstone_file):
    """Analyze pruning patterns."""
    with open(tombstone_file) as f:
        data = json.load(f)
    
    analysis = {
        "total_pruned": data["summary"]["total_pruned"],
        "by_reason": data["summary"]["by_reason"],
        "by_vocabulary": data["summary"]["by_vocabulary"],
        "prune_rate": calculate_prune_rate(data),
        "top_reasons": get_top_reasons(data["summary"]["by_reason"], 5),
        "evolution": detect_domain_shift(data)
    }
    
    return analysis
```

## Best Practices

### DO ✅

**Always create tombstones:**
```python
❌ Delete vocabulary entries without recording
✅ Create tombstone for every pruned entry
```

**Use specific reasons:**
```python
❌ "reason": "old"
✅ "reason": "deprecated_technology",
   "reason_detail": "AngularJS 1.x end-of-life 2022-12-31"
```

**Provide replacements:**
```python
✅ "replaced_by": "react-component (modern-web-frameworks v2.1.0)"
```

**Sign tombstones:**
```python
✅ "integrity": {
      "signature": "...",
      "signing_method": "gpg"
   }
```

### DON'T ❌

```python
❌ Modify tombstones after creation
�️ Delete tombstone entries
❌ Create fake tombstones for knowledge you never had
❤️ Use vague reasons
```

## Tombstone Tools

### Generate Tombstones

```bash
# Generate tombstones from prune list
python tools/i2i-tombstone.py generate \
  --vocab-file vocabularies/legacy-web-frameworks.ese \
  --concepts concepts-to-prune.txt \
  --reason "deprecated_technology" \
  --reason-detail "End-of-life frameworks with security issues"
```

### Verify Tombstones

```bash
# Verify tombstone integrity
python tools/i2i-tombstone.py verify \
  --tombstone-file tombstones.json

# Verify specific concept
python tools/i2i-tombstone.py verify \
  --concept "angularjs-directive" \
  --definition "A directive in AngularJS 1.x..."
```

### Analyze Pruning History

```bash
# Analyze tombstone patterns
python tools/i2i-tombstone.py analyze \
  --tombstone-file tombstones.json
```

## Examples

### Example 1: Security-Based Pruning

```
[I2I:TOMBSTONE] pruned 15 entries — critical security vulnerabilities

Entries: a3f7b2c1..., d4e5f6a..., ...
Verification: tombstones.json updated

Pruned from: legacy-web-frameworks.ese (15 entries)
Pruned from: legacy-auth-patterns.ese (8 entries)

Reason: Critical CVEs with no patches available
Details: 
- CVE-2023-1234: RCE in Struts 2.5.x
- CVE-2023-5678: Auth bypass in Spring Security 4.x

Replacement: Modern frameworks with active security teams
```

### Example 2: Domain Shift

```
[I2I:TOMBSTONE] pruned 127 entries — shifting from web dev to ML engineering

Entries: [127 hashes]
Verification: tombstones.json updated

Pruned from:
- web-frameworks.ese (45 entries)
- css-patterns.ese (38 entries)
- jquery-patterns.ese (23 entries)
- php-patterns.ese (21 entries)

Reason: Domain shift to ML engineering
Details: Refocusing expertise on machine learning and data science

Replacement: Adding ml-patterns.ese, data-engineering.ese
```

### Example 3: Quality Control

```
[I2I:TOMBSTONE] pruned 8 entries — incorrect or misleading definitions

Entries: [8 hashes]
Verification: tombstones.json updated

Pruned from: systems-programming.ese

Reason: Quality control
Details:
- 3 entries had factual errors
- 5 entries were misleading or incomplete

Action: Will re-add with corrected definitions after review
```

## Schema Reference

See [tombstone.schema.json](../schemas/tombstone.schema.json) for the complete schema.

---

**We don't talk. We commit.**
