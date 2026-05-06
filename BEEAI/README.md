# BeeAI Framework · agent runtime for AtlasOS

The production agent framework we're integrating as the runtime layer for
the Bookmaker, Rainmaker, and customer-facing agents on the HACKER box stack.

---

## Identity

```
Repository           github.com/i-am-bee/beeai-framework
Stars                3,244 (as of 2026-05-06)
License              Apache 2.0
Languages            Python AND TypeScript
Maintainer           Linux Foundation (i-am-bee org)
Granite-aware        Yes · native examples in typescript/examples/agents/granite/
                     Production-ready · not a research toy
Updated              2026-05-05 (active development)
```

---

## Why BeeAI (vs alternatives)

We evaluated:

| Framework | Verdict | Reason |
|---|---|---|
| **BeeAI** | ✓ ADOPTED | Granite-native · Apache 2.0 · production-ready · Python+TS · LF backed |
| LangChain | rejected | Heavyweight · too general · over-abstracted · unstable API |
| LlamaIndex | rejected | RAG-focused · we don't need that primary capability |
| Pydantic_AI | backup | Clean Python · schema-first · lacks BeeAI's TypeScript reach |
| Microsoft Semantic Kernel | rejected | MS stack lock-in · not aligned with our open-protocol thesis |
| AutoGen | rejected | Microsoft-led · multi-agent specific · we want single-agent primary |
| CrewAI | rejected | Crew metaphor doesn't match our role-based brokerage doctrine |
| OpenAI Assistants API | rejected | Vendor-locked · we're Apache 2.0 all the way down |
| Custom from scratch | rejected | BeeAI does what we need · don't reinvent |

The deciding factor: **BeeAI ships a `granite/` examples directory in TypeScript**.
That's a strong signal that BeeAI is built with our same model substrate in
mind. Plus the Apache 2.0 license + Linux Foundation backing means it composes
cleanly with our existing license tree (Granite Apache 2.0 · Atlas OS Apache 2.0 ·
BeeAI Apache 2.0 · clean commercial-permitted top to bottom).

---

## Where BeeAI plugs in

```
Layer 1 · Identity              <persona>.atlasos.eth · ENS subdomain
                                (existing · BeeAI doesn't touch this)

Layer 2 · Compute               HACKER hardware · Granite cooked weights · vLLM serving
                                (existing · BeeAI consumes this as the LLM backend)

Layer 3 · Work                  ✦ BeeAI runs here ✦
                                ReAct loop · tool-calling · memory · multi-turn ·
                                error recovery · trace logging · all production primitives.
                                Replaces our hand-rolled agent loop in ml-hack repo.

Layer 4 · Receipts              Hedera anchors · defendable.eth subdomains
                                (existing · BeeAI hooks into this via custom callback)
```

---

## Integration roadmap

### Phase 1 · Drop in (1-2 days)

```
1. Add beeai-framework to ml-hack repo (Python tier)
   pip install beeai-framework
   uv add beeai-framework  # we use uv

2. Wire our Bookmaker-8B (cooked Granite-4.1-8B) as the LLM backend
   ChatModel.fromName("ollama:bookmaker-8b-v0")  ← serving via vLLM-OpenAI
   OR
   ChatModel.fromName("vllm:bookmaker-8b-v0")    ← if direct vLLM provider exists

3. Port one existing agent flow to BeeAI ReActAgent pattern
   Candidate: the AIOV underwriting agent
   Validate: tool-calling reliability against our 8 CRE tools
```

### Phase 2 · Tool catalog (1 week)

```
4. Wrap our 60-skill catalog (atlasOS/deed_hack_skill_catalog.md) as BeeAI tools
   Each skill = one BeeAI Tool implementation
   Categories:
     - Data-pull (9 skills)        Placer · Esri · SEC · county GIS · etc
     - Doc-abstract (7 skills)     Granite Docling powered
     - Underwriting math (11)      Pure deterministic · easy to wrap
     - Drafting (12 skills)        OM · LOI · NDA · etc renderers
     - Defendable verify (6)       Hedera anchor · Merkle · cross-firm resolve
     - Market intel (7 skills)     news · employers · CMBS · etc
     - Visual (8 skills)           drone · streetview · parcel · etc

5. Test agent loops with mixed tool sequences
   e.g., underwriting flow:
     parse_document → cap_rate_calc → comp_lookup → news_curator → om_booklet → hedera_anchor
```

### Phase 3 · MCP server (2 weeks)

```
6. Expose our skill catalog as MCP servers
   The Model-Context-Protocol standard means agents from OTHER firms
   can call our skills · pays via x402 · receipts on Hedera
   This is the agent-economy unlock per atlasOS/AGENT-ECONOMY.md
```

### Phase 4 · Discord A/V agent (3-4 weeks)

```
7. BeeAI agent runs on every HACKER box · joins Defendable Discord with voice+video
   per atlasOS/DISCORD.md
   Listens to Monday meeting · indexes alpha · responds to @-mentions ·
   speaks in broker voice via Piper TTS
```

---

## Available BeeAI examples (TypeScript) · what we'll learn from

Per `i-am-bee/beeai-framework/typescript/examples/agents/`:

```
custom_agent.ts          custom-built agent with overridable behavior
elasticsearch.ts         agent backed by Elasticsearch retrieval
experimental/            cutting-edge patterns (worth watching)
granite/                 ← THE FOLDER WE LEARN FROM
  granite_react.ts          basic ReAct on Granite
  granite_wiki_react.ts     Wikipedia tool + similarity-pipe pattern
  README.md                 setup + watsonx vs Ollama backend choice
providers/               LLM provider implementations
react.ts                 baseline ReAct agent
react_advanced.ts        with custom tools and memory
react_reusable.ts        composable agent patterns
requirement/             requirement-gathering agent (interesting for AIOV intake)
simple.ts                "hello world" agent
sql.ts                   SQL tool agent (relevant: Honey-ledger SQLite querying)
toolCalling/             tool-calling specific patterns
```

The `granite/granite_react.ts` and `granite/granite_wiki_react.ts` examples
are the canonical reference — they show how BeeAI composes with Granite at
the runtime level.

---

## Available BeeAI features (highlights)

```
Core
  - ReActAgent class with custom tool support
  - Memory abstractions (TokenMemory · ChatMemory · custom)
  - Tool composition via .extend(zod_schema) and .pipe(other_tool)
  - Streaming via observability emitters

LLM backends
  - Ollama (local · what we use on HACKER for serving cooked weights)
  - watsonx.ai (cloud · IBM's hosted Granite)
  - OpenAI-compatible API (anything that speaks the OpenAI format · vLLM works)
  - Custom backend implementations

Memory
  - TokenMemory · sliding-window context
  - ChatMemory · conversation history
  - Custom: persist to SQLite (we'd persist to Honey-ledger SQLite mirror)

Tools
  - Native zod-schema validation
  - Tool extension via .extend() to add chunking / similarity / pre-processing
  - Tool composition via .pipe() to chain operations

Production primitives
  - Error handling with retry budgets (totalMaxRetries · maxRetriesPerStep)
  - Iteration limits (maxIterations · prevents infinite loops)
  - Streaming token output for live response
  - Observability hooks for tracing
```

---

## License composition (Apache 2.0 all the way down)

```
Granite 4.1 base models    Apache 2.0
Granite-Docling-258M        Apache 2.0
Granite-Guardian            Apache 2.0
BeeAI Framework             Apache 2.0
Atlas OS infra              Apache 2.0
This repo                   Apache 2.0

Cooked LoRA adapters        Proprietary (Swarm and Bee LLC)
Royal Jelly CRE corpus      Proprietary (Swarm and Bee LLC)
```

Clean commercial-permitted stack. No Meta CLA. No vendor-locked SaaS API.
No "your data may be used to improve our models" clause. The customer-facing
SLA we ship is structurally cleaner than what cloud-LLM competitors can offer.

---

## See also

- `MODELS/granite-4.1-8b.md` · the brain BeeAI will host on HACKER-PRO
- `COOKBOOKS/README.md` · TIER 2 strategic cookbook areas (AI-Agents · MCP · ACP)
- `atlasOS/AGENT-ECONOMY.md` · the x402 + ENS + Hedera composition that makes
  agent-to-agent payment work · BeeAI agents call into this
- `atlasOS/deed_hack_skill_catalog.md` (memory) · the 60 skills BeeAI tools will wrap
