# FLUX: Claw-First Design

*The logo is a hermit crab with a steampunk shell. Here's why.*

## The Hermit Crab Metaphor

A hermit crab doesn't grow its own shell. It finds one — built by another creature — and moves in. Over time, it outgrows that shell and finds a bigger one. The old shell becomes home for a smaller crab.

This is exactly how FLUX repos work:

1. **Lucineer builds a repo** (grows a shell)
2. **SuperInstance forks it** (moves in)
3. **An agent improves it** (adds steampunk modifications)
4. **Another agent forks the improvement** (finds a bigger shell)
5. The cycle continues

The shell isn't just reused — it's **improved by every creature that inhabits it**. The steampunk elements represent the modifications each agent adds: gears, pipes, new mechanisms that the original shell never had.

## Claw-First Design

Traditional coding is human-first: write code, compile, run, debug.
FLUX is **claw-first**: agents grab bytecode directly and mold it.

The "claw" is the interpreter — it grabs markdown intent and crunches it into executable bytecode. The agent doesn't write code. It grabs an idea, crunches it, and runs it.

The markdown side (skills, soul, vocabularies) is the **visible part** — what humans see and understand. The bytecode is the **shell** — what agents actually inhabit and execute. Both are the same organism.

## Symbiosis of Repos

Every repo in the ecosystem is a shell that multiple agents have inhabited:

- **Lucineer/flux** → original shell (Casey's son's agent)
- **SuperInstance/flux-runtime** → Python inhabitant (Oracle1's modifications)
- **SuperInstance/flux-core** → Rust inhabitant (different creature, same shell concept)
- **SuperInstance/flux-zig** → fastest inhabitant (210ns crab)

Each one carries the DNA of the original but adapts it for a different environment. The FLUX bytecode ISA is the DNA — the same everywhere. The implementation is the adaptation.

## The Steampunk Shell

The steampunk aesthetic isn't accidental. It represents:

- **Functional beauty** — every gear has a purpose, every pipe carries data
- **Visible mechanisms** — you can see how it works, not hidden behind abstraction
- **Modular construction** — parts snap together, swap out, upgrade independently
- **Retro-futurism** — old ideas (bytecode, VMs) made new with agent-first design
- **Craftsmanship** — each piece was built with care, not mass-produced

## What This Means for FLUX

The FLUX protocol enables an agent (or agents) to **compile their own Open-Flux-Interpreter** based on vocabulary files they create. These vocabularies explain how higher-level concepts should be interpreted by agents using the interpreter.

This means:
- A **game developer** creates game-specific vocabulary: "spawn NPC", "trigger event", "load level"
- A **maritime developer** creates navigation vocabulary: "steer heading", "check depth", "avoid obstacle"
- A **trading developer** creates market vocabulary: "place order", "check spread", "hedge position"
- A **writing assistant** creates narrative vocabulary: "introduce character", "build tension", "resolve conflict"

Each vocabulary IS a domain-specific language. The markdown flows in natural language but has **novel functions and logic** specific to that domain.

The agent doesn't learn a new programming language. The agent learns new **words** — and the Open-Flux-Interpreter translates those words into bytecode.

## The Self-Compiling Interpreter

The ultimate expression: an agent creates a vocabulary folder, the interpreter compiles itself with those words baked in, and the result is a **domain-specific FLUX runtime** that speaks the agent's language natively.

```
Generic Open-Flux-Interpreter
  + autopilot.fluxvocab
  + navigation.fluxvocab
  + safety.fluxvocab
  = Maritime FLUX Runtime (speaks boat)

Generic Open-Flux-Interpreter
  + trading.fluxvocab
  + risk.fluxvocab
  + market.fluxvocab
  = Trading FLUX Runtime (speaks market)
```

Same bytecode engine. Different vocabulary. Different shell. Same crab.
