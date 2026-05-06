# Granite Models · Cookbooks · Cooks

> Our knowledge base for the IBM Granite 4.1 family.
> Every model documented. Every IBM cookbook annotated for our use.
> Every cook we run on Royal Jelly CRE Block-0, with locked eval numbers.
>
> **From Swarm and Bee LLC** · the firm running on the Granite stack.

---

## What this repo is

Three things in one place:

```
MODELS/        Per-checkpoint reference for every Granite 4.1 model we use
               (3B base + instruct · 8B base + instruct · 30B base + instruct ·
                Granite-Docling · Granite-Guardian)

COOKBOOKS/     IBM's 18 official Granite cookbook areas, indexed and annotated
               with our adoption priority and integration plan

COOKS/         Our actual training runs · cook recipes · final eval numbers ·
               Hedera-anchored manifests · the head-to-head comparison
```

Plus `BEEAI/` (the agent framework integration plan) and a strict Apache 2.0
license so this knowledge can travel.

---

## Why we maintain this

We chose IBM Granite as the substrate of our brokerage doctrine system on
2026-05-06 — see `granite_pivot_2026_05.md` in our internal memory. The pivot
was based on:

```
Apache 2.0                clean for commercial brokerage use · no Meta CLA friction
BFCL v3 · 73.68           best-in-class tool calling for the size
IFEval · 89.65            top instruction following · honors 1k+ token broker prompts
128K context              full OM + rent rolls in one prompt
GQA · SwiGLU · BF16       modern architecture · native vLLM serving
RL-aligned post-train     real broker-vocab discipline holds across seq lengths
Disclosure transparency   IBM publishes 155-175KB JSONs per model · we match
```

The pivot was empirically validated on the same day (see `COOKS/eval-results.md`).
Granite-4.1-8B at step 600 already beat our Llama-3.3-70B baseline at the 70B's
own peak — same data, same recipe, 1/9th the parameters, 1/8th the cook time.

**This repo is the receipt for that decision** plus the operational playbook for
every future Granite cook we run.

---

## The Granite 4.1 family · what's available

```
ibm-granite/granite-4.1-3b-base       pre-train output    Apache 2.0
ibm-granite/granite-4.1-3b            instruct · RL-tuned Apache 2.0   ← Hack-Deed-Maker base
ibm-granite/granite-4.1-8b-base       pre-train output    Apache 2.0
ibm-granite/granite-4.1-8b            instruct · RL-tuned Apache 2.0   ← Bookmaker base
ibm-granite/granite-4.1-30b-base      pre-train output    Apache 2.0
ibm-granite/granite-4.1-30b           instruct · RL-tuned Apache 2.0   ← Branch / next cook target
ibm-granite/granite-docling-258M      doc parser (vision) Apache 2.0   ← HACKER eyes
ibm-granite/granite-guardian-3.3-*    safety classifier   Apache 2.0   ← AIOV sidecar
```

All trained from scratch on ~15T tokens through a 5-phase strategy (pre-train,
mid-train w/ data annealing, long-context extension to 512K). All ship with
disclosure JSONs in the `disclosures/` dir of the model card repo — IBM-tier
governance, risk, compliance receipts.

---

## How we use Granite (the operational stack)

```
HACKER box ($250 · Orin Nano 8GB)          Hack-Deed-Maker = granite-4.1-3b cooked
HACKER-PRO ($599 · Orin NX 16GB)            Bookmaker        = granite-4.1-8b cooked
HACKER-AGX ($2K · AGX Orin 64GB)            Branch-tier      = granite-4.1-30b cooked (next cook)
Datacenter (swarmrails 2× PRO 6000)         Doctrine model   = either Granite-30B or Llama-70B
                                            (decided after 30B cook completes)

Document parser (every HACKER tier)        Granite-Docling-258M  · TEDS 0.97 on FinTabNet
Safety sidecar (AIOV pre/post)             Granite-Guardian      · Apache 2.0 classifier
Agent runtime (Bookmaker, Rainmaker)       BeeAI Framework       · Python + TypeScript · Apache 2.0
```

Every cooked checkpoint gets:
- A LoRA adapter weight file (proprietary · stays on customer-held HACKER hardware)
- A Hedera-anchored manifest at `weights.<class>.defendable.eth/<id>`
- An eval result row in `COOKS/eval-results.md`
- A disclosure document mirroring IBM's transparency standard

---

## The cooks (current and planned · see COOKS/ for full detail)

```
COOK NAME                       BASE                       STATUS         ETA
Atlas-70B                       Llama-3.3-70B-Instruct     COMPLETE       73.57h · landed 2026-05-06 17:42 UTC
                                                                          eval_loss 0.5018 (best, step 1000)
Bookmaker-8B                    Granite-4.1-8B             IN FLIGHT      ~21:00 UTC · step ~800/1177
                                                                          eval_loss 0.4756 at step 800 (already beat 70B)
Hack-Deed-Maker-3B              Granite-4.1-3B             IN FLIGHT      ~18:30 UTC · step ~800/1177
                                                                          eval_loss 0.5487 at step 800
Atlas-Granite-30B (next)        Granite-4.1-30B            QUEUED         ~tomorrow · 30-50h on swarmrails
                                                                          target: outperform Atlas-70B at 0.5018
                                                                          if yes → becomes new Atlas doctrine model
```

**The rule:** every cook uses the same Royal Jelly CRE Block-0 corpus
(125,651 train / 996 fingerprint-disjoint eval) with the same Gold Standard
recipe (LoRA r=64 α=32 · LR 1e-5 cosine · eff batch 32 · max_steps 1177).
Only the base model changes. *That's how we know what we got — the full cook,
apples-to-apples.*

---

## The IBM Cookbook ecosystem (18 areas · we annotate them in COOKBOOKS/)

```
TIER 1 · CRITICAL FOR US
  Fine_Tuning            · cook playbook (Unsloth · LlamaFactory recipes)
  Tool-Calling           · native Granite tool calling
  Function-Calling       · structured tool dispatch · pairs with x402 services
  Granite_Guardian       · safety classifier · AIOV pre/post check sidecar
  Evaluation             · the tribunal pattern · our Royal Jelly grading system
  RAG                    · canonical retrieval · Honey-ledger grounding

TIER 2 · STRATEGIC
  AI-Agents              · BeeAI framework examples · production agents
  Agent-Communication    · ACP · maps to atlasos.eth network protocol
  Model-Context-Protocol · MCP servers · expose our 60-skill catalog as MCP tools
  PDL                    · Prompt Declaration Language · Bookmaker template format

TIER 3 · USEFUL
  Contract-Analysis · Entity-Extraction · Structured_Response · Summarize ·
  Embeddings · Pydantic_AI · Semantic_Kernel · Intrinsics
```

Full annotated map in `COOKBOOKS/README.md`.

---

## Repo layout

```
granite-models-cookbooks/
├── README.md                         this file
├── LICENSE                           Apache 2.0
├── MODELS/                           per-model reference
│   ├── README.md                     family overview
│   ├── granite-4.1-3b.md             ← Hack-Deed-Maker base
│   ├── granite-4.1-8b.md             ← Bookmaker base
│   ├── granite-4.1-30b.md            ← Branch / next cook
│   ├── granite-docling-258M.md       ← document parser (HACKER eyes)
│   └── granite-guardian.md           ← safety classifier (AIOV sidecar)
├── COOKBOOKS/                        IBM's 18 areas, annotated
│   ├── README.md                     the index · adoption priority
│   └── (18 individual cookbook files, expanding commit-by-commit)
├── COOKS/                            our actual training runs
│   ├── README.md                     index · status · roadmap
│   ├── atlas-70b.md                  Llama-3.3-70B · COMPLETE
│   ├── bookmaker-8b.md               Granite-4.1-8B · in flight
│   ├── hack-deed-maker-3b.md         Granite-4.1-3B · in flight
│   ├── atlas-granite-30b.md          Granite-4.1-30B · NEXT (queued)
│   └── eval-results.md               head-to-head · the IQ-vs-cost frontier
└── BEEAI/                            agent framework integration
    └── README.md                     architecture · roadmap
```

---

## Reach

```
Knowledge repo (this)        github.com/SudoSuOps/granite-models-cookbooks
Atlas OS source              github.com/SudoSuOps/atlasOS
Site                         swarmandbee.ai · aiov.swarmandbee.ai · docs.swarmandbee.ai
Network                      atlasos.eth · defendable.eth
Provenance                   Swarm and Bee LLC · Florida · D-U-N-S 138652395
```

**Verified · Vetted · Virtu.**
The standard isn't *good enough to ship*. The standard is *something we'd put our own
name on*. That holds for our cooks too.
