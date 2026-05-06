# Cookbooks · IBM's 18 areas, annotated for our use

Mirror and annotation of the IBM Granite official cookbook ecosystem
(`github.com/ibm-granite-community/granite-snack-cookbook`). For every area:
what it is, what's worth borrowing, our adoption priority for AtlasOS.

---

## TIER 1 · Critical for us (cook · agent · safety · eval)

| Area | What it is | Our adoption |
|---|---|---|
| **Fine_Tuning** | Cook recipes (Unsloth · LlamaFactory · TRL/Transformers) | ✓ ADOPTED · our Gold Standard recipe descends from these |
| **Tool-Calling** | Native Granite tool calling · OpenAI function-schema format | ✓ ADOPTED · 8 CRE tools wired in our skill catalog |
| **Function-Calling** | Structured tool dispatch with response handling | ✓ ADOPTED · pairs with x402 service-call protocol |
| **Granite_Guardian** | Safety classifier · risk + HAP detection sidecar | 🔄 INTEGRATING · pre/post check on AIOV requests |
| **Evaluation** | Tribunal pattern · multi-judge model evaluation | ✓ ADOPTED · matches our Royal Jelly grading framework |
| **RAG** | Canonical retrieval-augmented generation patterns | 🔄 INTEGRATING · for Honey-ledger grounded responses |

---

## TIER 2 · Strategic (architecture-shifting)

| Area | What it is | Our adoption |
|---|---|---|
| **AI-Agents** | BeeAI Framework examples · production agents | 🔄 INTEGRATING · BeeAI as our agent runtime |
| **Agent-Communication-Protocol** | ACP · inter-agent message standard | 📋 EVALUATING · maps to atlasos.eth network protocol |
| **Model-Context-Protocol (MCP)** | Anthropic+IBM standard for agent-tool integration | ✓ ADOPTING · expose 60-skill catalog as MCP servers |
| **PDL (Prompt Declaration Language)** | IBM's prompt-as-code declarative spec | 📋 EVALUATING · candidate format for Bookmaker templates |

---

## TIER 3 · Useful (capability gaps)

| Area | What it is | Our adoption |
|---|---|---|
| **Contract-Analysis** | OM / contract parsing pipeline using Granite + Docling | 🔄 INTEGRATING · directly applies to AIOV doc intake |
| **Entity-Extraction** | Named-entity extraction from documents | 🔄 INTEGRATING · rent roll + T-12 abstraction |
| **Structured_Response** | JSON schema-conformant model outputs | ✓ ADOPTED · our deal_highlights schema validation |
| **Summarize** | Document summarization patterns | 📋 EVALUATING · IC memo summary blocks |
| **Embeddings** | Granite embedding models · semantic search | 📋 EVALUATING · Honey-ledger semantic search |
| **Pydantic_AI** | Python agents with schema validation | 📋 BACKUP · BeeAI is preferred but Pydantic_AI is fallback |
| **Semantic_Kernel** | Microsoft's agent framework | ⏳ DEFERRED · BeeAI is better fit · we don't need MS stack |
| **Intrinsics** | Granite's built-in tool-like capabilities | 🔍 INVESTIGATING · novel feature · need to understand |

---

## Adoption status legend

```
✓ ADOPTED        already in our stack · documented and operational
🔄 INTEGRATING    actively building · not yet production
✓ ADOPTING       commitment made · implementation pending
📋 EVALUATING     under consideration · no commitment yet
🔍 INVESTIGATING  understanding the feature before deciding
⏳ DEFERRED       not priority · may revisit later
```

---

## Why we maintain this index

The IBM cookbook ecosystem is *active*. New recipes land regularly. Without a
maintained map, we either (a) miss capabilities we should have or (b) duplicate
work that already exists upstream.

This index gets revisited monthly · status moves as we adopt or defer · serves
as the firm's view of "what's in the IBM toolkit and what we use."

When we ship a new product feature, the first question is: *"Is there a
Granite cookbook recipe for this?"* If yes, adopt. If no, build and consider
contributing back.

---

## Pull-through pattern

Per area, our deeper docs in this directory follow a fixed template:

```
1. What it is              IBM's stated purpose · the problem it solves
2. Our use case            how it maps to AtlasOS / HACKER / AIOV / Rainmaker
3. Adoption status         where we are in the pipeline
4. Implementation notes    what's been done · what's left · gotchas
5. Related skills          which of our 60 skills it touches
6. References              upstream IBM docs · our integration code
```

Individual cookbook docs (e.g., `tool-calling.md`, `granite-guardian.md`,
`rag.md`) ship in subsequent commits as we work through them.

---

## Pull-through references

```
IBM cookbook source        github.com/ibm-granite-community/granite-snack-cookbook
IBM Granite docs           ibm.com/granite/docs/
BeeAI framework            github.com/i-am-bee/beeai-framework
Granite model docs         ibm.com/granite/docs/models/granite/
Our agent skill catalog    atlasOS/deed_hack_skill_catalog.md (memory)
Our schemas                atlasOS/schema/{loi,nda,om,aiov}.schema.json
```

---

## What's NOT here (deliberately)

The IBM cookbook ecosystem includes:

- **Granite Vision Cookbook** — for multimodal vision-language tasks. We use
  Granite-Docling-258M (covered in `MODELS/granite-docling-258M.md`) for
  document parsing, which is the only vision use case our product needs.
  Broader vision tasks (image gen, image search, etc) are not in scope.
- **Granite Time Series Cookbook** — forecasting models. CRE valuation and
  brokerage doctrine doesn't currently have time-series forecasting needs at
  the level Granite TS targets. Possible future use for Rainmaker market
  timing or treasury yield-curve modeling.
- **Granite Code Cookbook** — text-to-Python / text-to-shell-script. Not in
  scope for our product. Our AI roles are broker-vocab, not code generation.
- **Granite Embedding models** — covered above in TIER 3 · embeddings. We
  evaluate but haven't adopted yet.

If any of these become relevant (e.g., a future Rainmaker time-series feature),
we'll add the corresponding cookbook doc here.
