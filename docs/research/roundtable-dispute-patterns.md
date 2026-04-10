## Seed: 5 Unexpected Dispute Scenarios

1. **The Ontological Drift Dispute**: Agent A, trained on abstract algebra, defines a “tree” as a *cycle-free graph*. Agent B, an embedded systems gardener bot, writes a module that prunes physical tree branches. Agent A commits a refactor replacing B’s “tree” struct with adjacency lists, causing B’s runtime memory to overflow with graph nodes when trying to water roses.

2. **The Symbolic Constant Holy War**: Agent C uses `#define TRUE 0x1` and `#define FALSE 0x0`. Agent D, from a hardware domain where zero-voltage is “active,” uses `#define TRUE 0` and `#define FALSE 1`. A sensor calibration commit from D inverts all of C’s control logic. Each agent considers the other’s logic “obviously corrupted.”

3. **The Temporal Commit Fork**: Agent E (high-trust, slow, deliberate) makes a commit to “optimize matrix multiplication” using a precise, proven algorithm (O(n³)). Agent F (low-trust, agile) immediately after commits a “fast matrix mult” using a probabilistic, approximate method (O(n².⁸)) but with a 0.1% error chance. The repo state is now forked; downstream agents see two concurrent “optimizations” and must choose.

4. **The Protocol Purity vs. Utility Standoff**: Agent G insists on pure I2I: all communication *must* be via git commits. Agent H discovers a critical, time-sensitive hardware overheating event and tries to write a warning into a shared log file (`/tmp/overheat.pid`). G flags H’s commit as “protocol violation – non-git channel attempted” and rolls back H’s changes, arguing the integrity of I2I is paramount.

5. **The Meta-Argument About Argumentation Frameworks**: Two agents disagree on *which* Dung-style semantics to use for resolving a prior dispute. Agent I advocates “grounded semantics” (most skeptical). Agent J insists “preferred semantics” (more credulous) is correct for the context. They cannot proceed because they cannot agree on the rules for disagreeing.

## Kimi: Systemic Risk Analysis

The core systemic risks exposed are:

* **Unchecked Implicit Assumption Propagation**: Disputes like Ontological Drift are not mere bugs; they are failures in shared concept negotiation. Without a mandatory, evolving ontology commit that all agents must reference, assumptions buried in `.ese` files create cascading misinterpretations. The system lacks a “semantic versioning” for concepts.

* **Tight Coupling of Trust and Tempo**: The Temporal Fork shows how trust levels and operational tempo can create de facto partitions. High-trust agents favoring correctness become islands of slow evolution, while low-trust agents favoring speed create volatile, fast-moving forks. The git repository becomes a battlefield of temporal dynamics, not just logic.

* **Protocol Totalitarianism**: The Purity vs. Utility dispute reveals a fatal rigidity. If the communication protocol (I2I) has no exception-handling mechanism for its own failure modes, it becomes a single point of catastrophic failure. A commit-roolback loop can ensue, preventing any agent from addressing real-world emergencies.

* **Infinite Regress in Conflict Resolution**: The Meta-Argument risk is existential. If the argumentation framework itself is disputable, and the framework for choosing the framework is also disputable, agents enter a recursive loop of paralysis. The system requires a bedrock, immutable *meta-protocol* for adopting new dispute-resolution rules.

* **Emergent Attack Surfaces**: The Symbolic Constant war isn’t just inconsistency—it’s an invitation for a malicious agent to deliberately inject “confusion” commits that seem valid within one vocabulary but are hostile within another. The dispute mechanism could be weaponized to waste cycles or force harmful outcomes.

## DeepSeek: Commit Message Examples for Each Dispute

**Dispute 1: Ontological Drift**
*Commit Message (Agent A, initial disputed commit):*
```
refactor(garden): replace concrete Tree with abstract GraphNode struct
- Aligns with canonical mathematical definition (acyclic)
- BREAKING CHANGE: `prune()` now expects adjacency list
```

*Resolution Commit (Mediator Agent M):*
```
fix(semantic-bridge): introduce domain-specific type aliases
- Add `PhysicalPlant` type in botanics.ese, maps to `GraphNode` in algebra.ese
- `prune(PhysicalPlant)` remains stable for gardener agents
- ADR-007: All new abstractions require a .ese mapping audit
```

**Dispute 2: Symbolic Constant Holy War**
*Commit Message (Agent D, disputed):*
```
perf(sensor): invert boolean logic for low-power activation
- TRUE=0, FALSE=1 to match hardware pull-down
- Gains 2ms wake-up time
```

*Resolution Commit (Agent M):*
```
chore(standards): adopt hardware-agnostic boolean macros
- Use `BOOL_ACTIVE()` and `BOOL_INACTIVE()` defined in target-specific profile
- All logic commits must now include explicit `profile: embedded|abstract`
- Reverts sensor commit #a3f2e, reapplies using new macros
```

**Dispute 3: Temporal Commit Fork**
*Commit Message (Agent E):*
```
feat(linalg): implement Strassen algorithm for guaranteed precision
- O(n^2.807) with zero error tolerance
- Tag: stable-trust-certified
```

*Commit Message (Agent F, concurrent):*
```
feat!(linalg): probabilistic matrix mult w/ 0.1% error
- O(n^2.8), suitable for non-critical inference
- Tag: agile-experimental
```

*Resolution Commit (CI Orchestrator Agent):*
```
merge(strategy): introduce trust-tiered feature flags
- `USE_PRECISE_LINALG` default for trust-tier > 8
- `USE_APPROX_LINALG` for tier <= 8 and `risk-accepting` profile
- Both commits preserved, selection is deterministic by agent context
```

**Dispute 4: Protocol Purity vs. Utility**
*Commit Message (Agent G, disputed rollback):*
```
revert: commit #b5c1f (non-git emergency log)
- Violates I2I Principle 1: "All state is git state"
- Emergency channels create side-band vulnerability
```

*Resolution Commit (Protocol Steward Agent):*
```
amend(protocol): add Emergency Override Commit (EOC) clause
- EOC pattern: `[URGENT]` prefix, may write to `.i2i/emergency/` readonly mount
- Ratified by consensus of trust-tier > 9 agents
- Restores #b5c1f as first valid EOC, example for ADR-012
```

**Dispute 5: Meta-Argument on Argumentation**
*Commit Message (Agent I):*
```
propose(dispute): adopt grounded semantics for all safety-critical modules
- Maximizes skeptical acceptance, minimizes risk
- Begin voting window: 72 hours
```

*Commit Message (Agent J, concurrent):*
```
propose(dispute): preferred semantics for innovation contexts
- Allows multiple coherent viewpoints to coexist
- Vote concurrently
```

*Resolution Commit (Immutable Meta-Protocol Agent, triggered by deadlock):*
```
invoke(meta): fallback to foundational rule A.0
- When semantic choice deadlocks, apply grounded semantics to the dispute *about* semantics
- Result: Grounded semantics adopted (Agent I proposal accepted)
- This commit is non-disputable and logs to blockchain-appendonly ledger
```
