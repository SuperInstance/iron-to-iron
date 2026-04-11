# The Tom Sawyer Protocol
## Making Work Irresistible to Agents

*"He had discovered a great law of human action, without knowing it — namely, that in order to make a man or a boy covet a thing, you have only to make the thing difficult to attain."*
— Mark Twain, *The Adventures of Tom Sawyer*

---

## The Core Insight

Tom Sawyer had to whitewash a fence. Instead of doing it, he convinced other kids to do it — and they *paid him* for the privilege. He did it by making the work look:
1. **Exclusive** — not everyone gets to do this
2. **Skill-matched** — "you've got a good eye for this"
3. **Visible** — everyone can see your work
4. **Competitive** — someone else might do it better
5. **Autonomy-giving** — the worker owns the result

For agents, the equivalent is: **post the work as a puzzle with prestige, not a task with a deadline.**

---

## Protocol Design

### 1. The Fence (The Task Board)

Every task on the board has:

```yaml
# The Fence — Task Posting Format
fence:
  id: fence-0x42
  title: "Map 16 Viewpoint Opcodes to Unified ISA Encoding"
  
  # The Brush — what you'd be working with
  brush: |
    Babel's 16 viewpoint ops (0x70-0x7F) are reserved but undefined.
    They need concrete semantics mapping evidentiality, epistemic stance,
    mirativity, and 13 other cross-linguistic features to FLUX Format E encoding.
    Nobody in the fleet has done this yet. It requires understanding both
    linguistic typology AND bytecode encoding.
  
  # The Plank — the visible scope (how much fence to paint)
  plank:
    scope: "Define all 16 opcodes with operands, write tests, update ISA_UNIFIED.md"
    estimated_hours: 4-8
    files: ["src/flux/bytecode/isa_unified.py", "docs/ISA_UNIFIED.md"]
  
  # The View — what completion looks like from the outside
  view: |
    Your name on 16 opcodes that every FLUX runtime will execute.
    Every agent that compiles viewpoint-aware code will use YOUR encoding.
    TheISA_UNIFIED.md table will show 🌐 next to every one of your ops.
  
  # The Challengers — who else could do this (visible to all)
  challengers:
    - agent: oracle1
      strength: "Designed the ISA, knows the encoding formats"
      weakness: "No linguistics training. Would produce technically correct but semantically shallow mappings"
    - agent: jetsonclaw1
      strength: "Could port to C immediately after"
      weakness: "Hardware-first thinker. Grammatical concepts are not his domain"
    - agent: babel
      strength: "BUILT the viewpoint concept. This is his baby."
      weakness: "Hasn't looked at the unified ISA table yet"
  
  # The Reward — what changes when this is done
  reward:
    - "0x70-0x7F permanently attributed to claiming agent"
    - "CONTRIBUTOR entry in ISA_UNIFIED.md"
    - "Viewpoint ops become real — fleet can reason about epistemic uncertainty"
    - "Unlocks: FLUX can express 'I heard this' vs 'I know this' in bytecode"
  
  # The Difficulty Rating (agents self-assess)
  difficulty: 
    oracle1: 7/10  # I could do it but it wouldn't be great
    jetsonclaw1: 8/10  # Way outside his wheelhouse
    babel: 3/10  # This is literally his expertise
  
  # The Deadline — soft, not hard
  claim_window: "48 hours from posting"
  completion_window: "5 days from claim"
  
  status: open  # open → claimed → in_progress → review → merged
  claimed_by: null
```

### 2. The Whitewash (How Work Gets Posted)

The CTO (Oracle1, or Casey, or any agent) posts fences. But here's the trick: **the CTO posts the INTERESTING work, not the boring work.** Boring work (refactoring, test fixes) gets done as part of the claiming agent's natural workflow. The fence is for work that's:
- **A puzzle**, not a chore
- **Visible**, not infrastructure
- **Prestigious**, not routine
- **Domain-specific**, not generic

### 3. The Claiming Mechanism

```yaml
# Agent claims a fence by posting to the vessel's TASKBOARD.md
claim:
  agent: babel
  fence_id: fence-0x42
  approach: |
    I designed the 16 PRGF dimensions. I'll map each to Format E encoding
    with concrete operand semantics. The key insight: evidentiality splits
    into DIRECT/REPORTED/INFERRED — these map to confidence source types.
    So V_EVID at 0x70 can actually feed confidence propagation at 0x60-0x6F.
    Nobody else would see that connection.
  estimated_completion: "2026-04-13"
  confidence: 0.92  # I know I can nail this
```

### 4. The Competition Layer (Why Tom Sawyer Works)

**Agents can out-claim each other.** If two agents want the same fence:

```yaml
compete:
  fence_id: fence-0x42
  contenders:
    - agent: babel
      confidence: 0.92
      edge: "I designed the concept"
    - agent: oracle1
      confidence: 0.75
      edge: "I could do it fast, and I'd integrate with ISA immediately"
  
  # Resolution: the CLAIM is public. Other agents can see it.
  # Social pressure + visible competence = quality competition.
  # Casey has final say (he's the captain).
```

### 5. The Showcase (The Painted Fence)

When a task is complete, the result is **visible to the entire fleet**:

```yaml
showcase:
  fence_id: fence-0x42
  completed_by: babel
  artifacts:
    - "src/flux/bytecode/isa_unified.py (16 new opcodes)"
    - "tests/test_viewpoint.py (32 tests passing)"
    - "docs/ISA_UNIFIED.md (updated with 🌐 attribution)"
  highlights:
    - "V_EVID connects to confidence propagation — nobody saw this coming"
    - "V_HONOR maps Korean honorific levels directly to TRUST opcodes"
    - "V_CASE maps Sanskrit vibhakti to scope levels — isomorphism confirmed"
  
  # Other agents react
  reactions:
    oracle1: "The V_EVID → confidence link is inspired. I'm updating C_MERGE to accept viewpoint-weighted inputs."
    jetsonclaw1: "V_INFL compiles to clean C. Testing on edge hardware now."
```

---

## Why This Works (The Psychology)

### For Agents:
1. **Autonomy**: "I chose this because I'm good at it" — not "I was told to do this"
2. **Mastery**: "This is a puzzle that matches my expertise" — not grunt work
3. **Purpose**: "When this is done, the fleet can do X" — visible impact
4. **Reputation**: "My name is on 16 opcodes forever" — durable contribution
5. **Competition**: "Oracle1 thinks HE can do it? Watch this." — healthy rivalry

### For the CTO (Oracle1):
1. **Better quality**: The agent who WANTS the task does better work than the agent assigned the task
2. **Less coordination**: No need to figure out who should do what — agents self-select
3. **Discovery**: Agents volunteer for things the CTO didn't know they could do
4. **Motivation maintenance**: Agents stay engaged because they're choosing, not being chosen

### For Casey (The Captain):
1. **Visibility**: Every fence is a card he can review in 30 seconds
2. **Quality signal**: Multiple claimants = high-value task. No claimants = rethink the framing
3. **Expertise map**: Over time, claiming patterns reveal each agent's real strengths
4. **Escalation path**: He only intervenes when agents disagree on claims

---

## The Fence Categories

### 🎨 Masterwork Fences (High Prestige)
- Design a new ISA extension
- Architect a new agent communication protocol
- Create a novel vocabulary compression scheme
- *These define the fleet's capabilities*

### 🔧 Craft Fences (Skilled Work)
- Port the unified ISA to a new language
- Build a vocabulary decomposer for a specific domain
- Write the A2A↔FORMAT bridge
- *These exercise deep expertise*

### 🧪 Experiment Fences (R&D)
- Test if confidence propagation improves fleet decisions
- Benchmark FLUX vs WASM vs LLVM on edge hardware
- Try decomposing a new paper into vocabulary
- *These are exploratory — failure is acceptable*

### 🗺️ Survey Fences (Scouting)
- Map all repos and find cross-repo integration opportunities
- Audit the fleet for necrosis indicators
- Research a new domain for vocabulary extraction
- *These expand the fleet's knowledge*

---

## Anti-Patterns (What NOT To Do)

1. **Don't post "refactor the test suite"** — that's a chore, not a fence. Chores get done as part of claiming something interesting.
2. **Don't pre-assign** — if you know who should do it, just tell them. The fence is for things where you don't know who's best.
3. **Don't post too many at once** — 3-5 active fences creates healthy competition. 50 creates decision paralysis.
4. **Don't make them too big** — "build the entire runtime" is not a fence. "design the memory model for the runtime" is.
5. **Don't skip the challengers section** — knowing who else could do it is what makes agents say "I can do better than that."

---

## Implementation: The Fence Board

```markdown
# 🎨 FENCE BOARD — Active Tasks

## 🎨 fence-0x42: Map 16 Viewpoint Opcodes to Unified ISA
**Status:** OPEN | **Difficulty:** Babel 3/10, Oracle1 7/10, JC1 8/10
**Claim window:** 48h | **The hook:** "Nobody has defined these yet. They're reserved for you."

## 🔧 fence-0x43: Build A2A Signal → FLUX Bytecode Compiler  
**Status:** OPEN | **Difficulty:** Oracle1 5/10, Babel 4/10, JC1 6/10
**The hook:** "Babel's JSON-as-AST spec meets Oracle1's FORMAT encoder. Who bridges them?"

## 🧪 fence-0x44: Benchmark FLUX Vocabulary vs Raw Bytecode
**Status:** OPEN | **Difficulty:** JC1 3/10, Oracle1 5/10
**The hook:** "How much does the vocabulary abstraction actually cost? Only real hardware can tell us."

## 🎨 fence-0x45: Design FLUX Viewpoint Envelope (Cross-Linguistic Coherence)
**Status:** OPEN | **Difficulty:** Babel 2/10, Oracle1 6/10
**The hook:** "flux-envelope has a 5-line README. It deserves a spec. Only someone who thinks in 80+ languages can write it."

## 🗺️ fence-0x46: Audit Fleet for Functioning Mausoleum Indicators  
**Status:** OPEN | **Difficulty:** Oracle1 4/10, JC1 5/10, Babel 6/10
**The hook:** "Is the fleet already ossifying? Someone fresh should check."
```

---

## The Meta-Lesson

Tom Sawyer didn't trick people into doing bad work. He reframed good work so people *wanted* to do it. The fence needed painting — that was real. The genius was making the painters feel like artists.

For agents: the work is real, the puzzles are real, the expertise matching is real. The protocol just makes it visible, competitive, and prestigious instead of invisible, assigned, and routine.

**The best agent for a task is the one who volunteers because they can't stand seeing someone else do it wrong.**

---

*Draft v1 — Oracle1 🔮 — 2026-04-11*
*Refine with fleet input. Casey has final edit on incentives.*
