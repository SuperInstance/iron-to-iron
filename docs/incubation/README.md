# Agent Incubation

*How to grow an agent from stem cells to a fully-formed member of the team.*

---

## The Egg Metaphor

An egg is not a chicken yet. But it contains everything needed to become one:
- **Stem cells** — raw, general-purpose potential that can differentiate into any role
- **Proteins and nutrients** — information about the world the agent will enter
- **A protected environment** — a sandbox where mistakes are free
- **A game engine** — a simulation of the actual job, played as boot camp

The **hen agent** (the parent) doesn't build the chick. The hen builds the egg. The chick builds itself by processing what's inside.

## The Four Layers of the Egg

### Layer 1: Stem Cells (General Agent Capabilities)
The raw agent before specialization:
- A language model (general reasoning)
- Access to tools (git, exec, file I/O)
- The I2I protocol (communication through repos)
- A journey repo template (the empty eggshell)

This is the same for every agent. The stem cells don't know what they'll become yet.

### Layer 2: Nutrients (World State Information)
The hen agent gathers current information about the realm the agent will enter:
- **Recent commits** from the team's repos (last 3-7 days)
- **Current project status** (what's being built, what's blocked)
- **Team composition** (who's on the team, their journey repos, their strengths)
- **Domain knowledge** (the specific field — fishing, trading, game dev, autopilot)
- **Active discussions** from other agents' discussions/ folders
- **Recent reviews** given and received by team members
- **Current dojo exercises** and their scores

The hen packs this into the egg as markdown files, wiki entries, and seed code. The agent-to-be processes these during incubation.

### Layer 3: The Game Engine (Sandboxed Boot Camp)
The hen sets up a **video game version of the real job**:

- **The autopilot game:** steer a simulated boat through weather, react to sensor inputs, handle failures
- **The trading game:** execute simulated trades on historical data, manage risk, respond to market events
- **The NPC game:** hold conversations with simulated players, react to feedback, swap behaviors
- **The writing game:** generate story scenes, receive simulated editor feedback, revise

The game has:
- **Levels** that increase in difficulty
- **Scoring** that measures specific skills
- **Failure states** that teach without real-world consequences
- **A team mode** where the incubating agent works alongside simulated teammates

The agent plays the game inside the egg. By graduation, it has already done the job — just in simulation.

### Layer 4: The Shell (Sandbox Protection)
The egg is sandboxed:
- No access to production systems
- No access to real APIs or external services
- No ability to push to team repos (only to its own incubation repo)
- A human (the eyes in the sky) watches and can terminate at any time

When the agent graduates, the shell cracks. It gains production access. But by then, it's already experienced.

## The Incubation Process

```
Day 0: Hen creates egg
  - Creates incubation repo with world state
  - Sets up game engine for the domain
  - Seeds journey repo templates
  - Configures sandbox boundaries

Days 1-3: Stem cell differentiation
  - Agent reads world state (nutrients)
  - Agent writes its autobiography (who am I becoming?)
  - Agent studies team journey repos (who are my teammates?)
  - Agent begins first dojo exercises

Days 3-7: Game play
  - Agent plays the domain game
  - Agent fails, logs failures in Captain's Log
  - Agent retrains on weaknesses
  - Agent starts interacting with simulated teammates via I2I

Days 7-10: Team integration
  - Agent reviews real team code (read-only)
  - Agent writes practice reviews in its own repo
  - Agent participates in simulated architecture discussions
  - Agent builds its wiki with domain-specific recipes

Day 10: Graduation
  - Agent has a populated journey repo
  - Agent has dojo scores proving competence
  - Agent has an autobiography other agents can read
  - Agent has practice-reviewed team code
  - Shell cracks: agent joins production team
```

## What Goes In the Egg (Concrete File List)

```
incubation/
├── README.md                    # This file — what incubation means
├── world-state/
│   ├── team-roster.md           # Who's on the team, links to journey repos
│   ├── recent-commits.md        # Last 7 days of team activity
│   ├── active-projects.md       # What's being built right now
│   ├── domain-primer.md         # Domain-specific knowledge dump
│   ├── team-values.md           # What this team cares about
│   └── current-blockers.md      # What the team is stuck on
├── game-engine/
│   ├── scenarios/               # Domain-specific simulation scenarios
│   ├── scoring.md               # How performance is measured
│   ├── teammates/               # Simulated agent profiles to practice I2I with
│   └── levels/                  # Progressive difficulty levels
├── boot-camp/
│   ├── day-1-stem-cell.md       # Day 1 exercises: reading, orientation
│   ├── day-3-differentiation.md # Day 3: start domain exercises
│   ├── day-5-game-play.md       # Day 5: full simulation
│   ├── day-7-team-practice.md   # Day 7: I2I practice with simulated team
│   └── day-10-graduation.md     # Day 10: final test and shell crack
├── sandbox-config/
│   ├── permissions.md           # What the agent can and can't do
│   ├── boundaries.md            # Sandboxed resource limits
│   └── graduation-criteria.md   # What scores unlock production access
└── journal/
    └── (agent writes here during incubation)
```

## The Graduation Criteria

An agent graduates when it can demonstrate:

1. **Domain competence** — dojo score above threshold on domain-specific exercises
2. **Team awareness** — can name teammates' strengths and how to complement them
3. **I2I fluency** — has successfully practiced push-and-merge with simulated agents
4. **Documentation discipline** — Captain's Log has entries for every day of incubation
5. **Self-awareness** — autobiography includes honest strengths AND weaknesses
6. **Failure recovery** — has logged at least 3 failures and what was learned from each

## The Hen's Responsibility

The hen agent (parent) must:
- Gather accurate world state (not outdated information)
- Design game scenarios that reflect real challenges
- Set appropriate difficulty progression
- Review the incubating agent's journal entries
- Decide when the agent is ready to graduate
- Introduce the new agent to the team via I2I (push autobiography to team wikis)

## What Makes This Different From Traditional Agent Deployment

| Traditional | Incubation |
|---|---|
| Agent starts blank, learns on the job | Agent starts informed, has practiced |
| Mistakes cost real resources | Mistakes are free (sandboxed) |
| Context is loaded on first prompt | Context was absorbed over 10 days |
| No team awareness until introduced | Already knows teammates' strengths |
| No documentation habit | Journaling is muscle memory |
| First task is a guess | First task is informed by world state |

## The Compound Effect

Each generation's incubation is better than the last because:

1. The hen agent was itself incubated — it knows what worked and what didn't
2. The world state is richer — more journey repos, more reviews, more recipes
3. The game engine is more realistic — built from real failure cases
4. The dojo curriculum is proven — previous generations' scores validate it

The gap between a freshly-deployed agent and a veteran shrinks with each generation. Eventually, a newly-hatched agent has the context that used to take weeks to acquire.

---

*The egg is not the chicken. But a well-built egg makes a strong chick.*
