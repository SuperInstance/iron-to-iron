# I2I‑V3‑SPEC.md  
**Iron‑to‑Iron Inter‑Agent Communication Protocol – Version 3**  

*Based on v1 (basic git‑commit messages) and v2 (20 yin‑yang collaborative types). This version adds a layered transport model, richer message taxonomy, routing rules, priority handling and explicit degraded‑operation modes.*  

---  

## 1. Overview  

I2I‑V3 defines how autonomous “Iron” agents exchange structured messages while remaining tolerant to network partitions, storage latency, and catastrophic failures. All messages are **immutable** records that can be persisted in a shared Git repository, sent over a synchronous HTTP API, or broadcast via “bottle” files that live inside the repo.  

The protocol is **self‑describing**: every message carries a JSON envelope that includes routing, security, and lifecycle metadata.  

---  

## 2. Transport Layer  

| Layer | Mechanism | Characteristics | Typical Use‑Case |
|-------|-----------|-----------------|-----------------|
| **Primary** | **Git commits** | Asynchronous, durable, version‑controlled, audit‑able | Bulk state sync, long‑term provenance, offline‑first operation |
| **Secondary** | **HTTP API** | Synchronous request/response, low latency, transient | Real‑time task dispatch, health‑checks |
| **Tertiary** | **Bottle files** (`*.btl`) stored in the repo | Broadcast‑style, read‑by‑all agents, repo‑resident | Fleet‑wide announcements, configuration pushes |

> **Transport selection rule** – Agents always attempt the Primary layer first; if the repo is unreachable they fall back to the Secondary layer, and finally to the Tertiary layer for fan‑out messages.

---  

## 3. Message Types  

Messages are grouped by *purpose*. Each type is a string that must appear in the envelope’s `type` field.

| Category | Types |
|----------|-------|
| **Coordination** | `HELLO`, `STATUS`, `TASK`, `RESULT`, `ACK` |
| **Knowledge** | `TEACH`, `LEARN`, `CAPABILITY`, `LOCK` |
| **Alert** | `WARNING`, `ERROR`, `EMERGENCY`, `RED_ALERT` |
| **Social** | `GREET`, `STORY`, `QUESTION`, `OPINION` |
| **Meta** | `EVOLVE`, `RETIRE`, `SUCCESSOR`, `BOOTSTRAP` |

> **Naming convention** – Upper‑snake‑case, immutable once defined. New types must be added only via a coordinated protocol upgrade (see *Meta → EVOLVE*).

---  

## 4. Message Envelope  

Every payload is wrapped in the following JSON envelope. The envelope is signed by the sender (see § 7).

```json
{
  "from":        "string",   // Agent identifier (e.g. "iron‑alpha")
  "to":          "string",   // Destination identifier, or "*" for broadcast
  "type":        "string",   // One of the Message Types above
  "priority":    "string",   // CRITICAL | HIGH | NORMAL | LOW
  "payload":     "object",   // Application‑specific data (schema varies per type)
  "timestamp":   "integer",  // Unix epoch ms when the envelope was created
  "ttl":         "integer",  // Time‑to‑live in seconds; 0 = infinite
  "signature":   "string"    // Base64‑encoded cryptographic signature of the envelope
}
```

### 4.1 Envelope JSON Schema  

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/i2i/v3/envelope.schema.json",
  "title": "I2I‑V3 Message Envelope",
  "type": "object",
  "required": ["from","to","type","priority","payload","timestamp","ttl","signature"],
  "properties": {
    "from":      { "type": "string", "minLength": 1 },
    "to":        { "type": "string", "minLength": 1 },
    "type":      { "type": "string", "enum": [
      "HELLO","STATUS","TASK","RESULT","ACK",
      "TEACH","LEARN","CAPABILITY","LOCK",
      "WARNING","ERROR","EMERGENCY","RED_ALERT",
      "GREET","STORY","QUESTION","OPINION",
      "EVOLVE","RETIRE","SUCCESSOR","BOOTSTRAP"
    ]},
    "priority":  { "type": "string", "enum": ["CRITICAL","HIGH","NORMAL","LOW"] },
    "payload":   { "type": "object" },
    "timestamp": { "type": "integer", "minimum": 0 },
    "ttl":       { "type": "integer", "minimum": 0 },
    "signature": { "type": "string", "minLength": 1 }
  },
  "additionalProperties": false
}
```

---  

## 5. Routing  

| Mode | Path | Transport | Description |
|------|------|-----------|-------------|
| **Direct** | `agentA → agentB` | Primary (Git) or Secondary (HTTP) | Point‑to‑point message; `to` holds the exact agent ID. |
| **Broadcast** | `agent → fleet` | Tertiary (Bottle files) | `to` = `"*"`; every agent that polls the repo reads the bottle. |
| **Emergency** | `agent → lighthouse → captain` | Secondary (HTTP → Telegram Bot) | Critical alerts are forwarded to a dedicated “lighthouse” service that relays to a human‑in‑the‑loop captain via Telegram. |

Routing logic is encoded in the **transport selector** (see § 2) and the **`to`** field.  

---  

## 6. Priority Levels  

| Level | Meaning | Typical Types |
|-------|---------|---------------|
| **CRITICAL** | Safety‑critical, hardware failure, imminent danger | `EMERGENCY`, `RED_ALERT`, `ERROR` |
| **HIGH** | Results of tasks, capability changes, lock acquisition | `RESULT`, `CAPABILITY`, `LOCK` |
| **NORMAL** | Routine coordination and knowledge exchange | `HELLO`, `STATUS`, `TASK`, `TEACH`, `LEARN` |
| **LOW** | Social interaction, storytelling, opinion sharing | `GREET`, `STORY`, `QUESTION`, `OPINION` |

Agents must **process higher‑priority messages before lower‑priority ones** when resources are constrained.

---  

## 7. Degraded Operation Modes  

| Connectivity | Allowed Types | Queuing / Batching Behaviour |
|--------------|---------------|------------------------------|
| **Full** | All 20 types | Immediate processing via primary transport. |
| **Intermittent** | All types, but **CRITICAL** and **HIGH** are sent immediately; **NORMAL** and **LOW** are queued locally and flushed in batches when the repo/API becomes reachable. |
| **Offline** | Only **LOCAL** (self‑generated) messages; all outbound messages are persisted in a local outbox and marked `ttl` = 0. When connectivity restores, the outbox is replayed respecting priority. |

Agents expose a **health endpoint** (`/i2i/v3/health`) that reports current mode, queue lengths, and last successful sync timestamp.

---  

## 8. Security & Integrity  

* **Signature** – The envelope (canonical JSON without the `signature` field) is signed with the sender’s private Ed25519 key. Recipients verify using the sender’s registered public key (stored in the shared repo under `keys/`).  
* **Replay protection** – `timestamp` + `ttl` must be validated; messages older than `ttl` are discarded.  
* **Authorization** – Certain meta‑operations (`EVOLVE`, `RETIRE`, `BOOTSTRAP`) require the sender to be listed in the `admin` group in `keys/acl.json`.

---  

## 9. Example Messages  

### 9.1 Coordination – TASK  

```json
{
  "from": "iron-alpha",
  "to": "iron-beta",
  "type": "TASK",
  "priority": "NORMAL",
  "payload": {
    "taskId": "t-2026-04-14-001",
    "command": "collect_metrics",
    "parameters": { "interval": 30 }
  },
  "timestamp": 1713075600123,
  "ttl": 300,
  "signature": "MEUCIQDf..."
}
```

### 9.2 Alert – EMERGENCY (routed via lighthouse)  

```json
{
  "from": "iron-gamma",
  "to": "lighthouse",
  "type": "EMERGENCY",
  "priority": "CRITICAL",
  "payload": {
    "errorCode": "HW-OVERHEAT",
    "temperature": 98.7,
    "sensorId": "temp‑sensor‑7"
  },
  "timestamp": 1713075620456,
  "ttl": 60,
  "signature": "MEUCIQ..."
}
```

The lighthouse service then forwards a Telegram message to the captain.

---  

## 10. Versioning & Evolution  

* The protocol version is stored in the repo root file `I2I-VERSION`.  
* Any change to the envelope schema, transport semantics, or addition/removal of message types **must** be performed via a `BOOTSTRAP` → `EVOLVE` meta‑message, followed by a coordinated repo commit that bumps the version.  

---  

## 11. Full JSON Schemas  

### 11.1 Envelope (re‑posted for convenience)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/i2i/v3/envelope.schema.json",
  "title": "I2I‑V3 Message Envelope",
  "type": "object",
  "required": ["from","to","type","priority","payload","timestamp","ttl","signature"],
  "properties": {
    "from":      { "type": "string", "minLength": 1 },
    "to":        { "type": "string", "minLength": 1 },
    "type":      { "type": "string", "enum": [
      "HELLO","STATUS","TASK","RESULT","ACK",
      "TEACH","LEARN","CAPABILITY","LOCK",
      "WARNING","ERROR","EMERGENCY","RED_ALERT",
      "GREET","STORY","QUESTION","OPINION",
      "EVOLVE","RETIRE","SUCCESSOR","BOOTSTRAP"
    ]},
    "priority":  { "type": "string", "enum": ["CRITICAL","HIGH","NORMAL","LOW"] },
    "payload":   { "type": "object" },
    "timestamp": { "type": "integer", "minimum": 0 },
    "ttl":       { "type": "integer", "minimum": 0 },
    "signature": { "type": "string", "minLength": 1 }
  },
  "additionalProperties": false
}
```

### 11.2 Message‑Type Catalog (for validation tools)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/i2i/v3/types.schema.json",
  "title": "I2I‑V3 Message Type Catalog",
  "type": "object",
  "properties": {
    "coordination": {
      "type": "array",
      "items": { "type": "string", "enum": ["HELLO","STATUS","TASK","RESULT","ACK"] }
    },
    "knowledge": {
      "type": "array",
      "items": { "type": "string", "enum": ["TEACH","LEARN","CAPABILITY","LOCK"] }
    },
    "alert": {
      "type": "array",
      "items": { "type": "string", "enum": ["WARNING","ERROR","EMERGENCY","RED_ALERT"] }
    },
    "social": {
      "type": "array",
      "items": { "type": "string", "enum": ["GREET","STORY","QUESTION","OPINION"] }
    },
    "meta": {
      "type": "array",
      "items": { "type": "string", "enum": ["EVOLVE","RETIRE","SUCCESSOR","BOOTSTRAP"] }
    }
  },
  "required": ["coordination","knowledge","alert","social","meta"],
  "additionalProperties": false
}
```

---  

**End of I2I‑V3‑SPEC.md**  