# Granite-4.1-30B · the next cook · candidate doctrine model

The 30-billion-parameter dense decoder in the Granite 4.1 family. The base for
our queued **Atlas-Granite-30B** cook on Royal Jelly CRE Block-0.

---

## Identity

```
Hugging Face        ibm-granite/granite-4.1-30b
Variant             instruct (RL-aligned post-training)
Base variant        ibm-granite/granite-4.1-30b-base (pre-train only)
License             Apache 2.0
Released            April 29, 2026
Disclosure          github.com/ibm-granite/granite-4.1-language-models/disclosures/granite_4.1_30b_disclosure.json
                    (~175KB JSON · full data + governance + risk)
```

---

## Architecture

```
Type                Decoder-only dense transformer
Parameters          30B
Layers              64
Hidden size         4096
Attention heads     32 (GQA · grouped query)
KV heads            8 (GQA 4:1)
Head dim            128
MLP intermediate    32,768
Vocab size          100,352
Activation          SwiGLU
Normalization       RMSNorm (eps 1e-5)
Position encoding   RoPE (theta varies · long-context extension applies)
Context window      131,072 (128K) · extendable to 512K with long-context phase
Embedding tying     yes (tied input/output)
Precision           BF16 native
Granite-specific    attention_multiplier · embedding_multiplier · residual_multiplier · logits_scaling
                    (small scalar architecture tweaks · IBM's "secret sauce" multipliers)
```

---

## VRAM math (for our cook)

```
BF16 (training, full precision)
  Weights              ~60 GB
  KV cache (4K seq)    ~3-5 GB
  Activations + grads  ~10-15 GB
  Total per cook       ~75-80 GB across 2 GPUs (sharded ~38-40 GB per card)
  Hardware fit         2× RTX PRO 6000 96GB FSDP_FULL_SHARD · comfortable
  No QLoRA needed at this scale on this hardware

INT8 (inference)
  Weights              ~30 GB
  Hardware fit         1× RTX PRO 6000 96GB · or 2× RTX 4500 32GB pair (sharded)

INT4 AWQ / Q4_K_M (deployment)
  Weights              ~15-17 GB
  Hardware fit         AGX Orin 64GB (HACKER-AGX $2K box) · comfortable
                      RTX 4500 32GB single GPU · also fits
                      Anywhere with 24+ GB of VRAM at INT4
```

---

## Capabilities (per IBM benchmarks)

```
General Tasks
  MMLU 5-shot                       80.16
  MMLU-Pro 5-shot, CoT              64.09
  BBH 3-shot, CoT                   83.74
  AGI EVAL 0-shot, CoT              77.80
  GPQA 0-shot, CoT                  45.76

Alignment Tasks
  AlpacaEval 2.0                    56.16
  IFEval Avg                        89.65   ← top-tier instruction following
  ArenaHard                         71.02
  MTBench Avg                       8.61

Math Tasks
  GSM8K 8-shot                      94.16
  Minerva Math 0-shot, CoT          81.32
  DeepMind Math 0-shot, CoT         81.93

Code Tasks
  HumanEval pass@1                  88.41
  HumanEval+ pass@1                 85.37
  MBPP pass@1                       85.45

Tool Calling
  BFCL v3                           73.68   ← strong tool calling

Multilingual
  MMMLU 5-shot                      73.71
  INCLUDE 5-shot                    67.26

Safety
  SALAD-Bench                       96.41
  AttaQ                             85.76
  Tulu3 Safety Eval Avg             78.19
```

For broker-grade work the load-bearing scores are **IFEval (89.65) ·
BFCL (73.68) · GSM8K (94.16) · HumanEval (88.41)**. These predict that 30B
holds the broker-vocab discipline + tool-calling reliability + numerical
accuracy our Royal Jelly cook needs.

---

## Why we cook this

**Three reasons the 30B is the next cook:**

### 1. Substrate scaling validation
Our Bookmaker-8B (Granite 4.1) already beat Atlas-70B (Llama 3.3) at step 600
on our corpus. The 30B fills the missing data point in the Granite family
scaling curve · `(3B · 8B · 30B · vs Llama-70B comparator)`. If the 30B
extends the Granite-beats-Llama trajectory (which the 8B's lead at 1/9 the
params strongly suggests it will), **we have a 4-point measured frontier**
covering every HACKER tier from $250 to $2K plus the doctrine-model decision.

### 2. Candidate doctrine model
If 30B beats Atlas-70B's 0.5018 eval — likely given the 8B already did — we
have a candidate doctrine model that's:
  - 1/2 the parameters of Atlas-70B (faster inference · more concurrent sessions)
  - Apache 2.0 (no Meta CLA friction)
  - Same architectural family as the 3B and 8B (uniform tokenizer · uniform
    tool-call format · simpler operational stack)
  - Same disclosure transparency standard as the smaller Granites

### 3. HACKER-AGX brain
Regardless of doctrine-model decision, the 30B is the production brain for
the **HACKER-AGX ($2K branch box)**. The AGX Orin 64GB has the headroom to run
the 30B at INT4 for branch-tier multi-deal concurrent inference.

---

## Cook plan

See `COOKS/atlas-granite-30b.md` for the full pre-cook checklist and recipe.
Summary:

```
Hardware              swarmrails 2× RTX PRO 6000 Blackwell · FSDP_FULL_SHARD
Recipe                bf16 LoRA r=64 α=32 · LR 1e-5 cosine · eff batch 32 · max_steps 1177
                      Same as Atlas-70B and Bookmaker-8B · apples-to-apples
Corpus                Royal Jelly CRE Block-0 · 125,651 train · 996 eval
                      train.jsonl sha256 d63b05d9e36b... (same)
                      eval.jsonl sha256  7f025a264210... (same)
Estimated time        30-50 hours wall-clock
Launch trigger        swarmrails GPUs free (Atlas-70B finished 17:42 UTC 2026-05-06)
                      pre-cook checklist · download base · adapt training script ·
                      smoke test · launch
```

---

## Tool calling (matters for HACKER-AGX as branch agent runtime)

Native Granite tool calling uses OpenAI function-schema format with `<tool_call>`
XML tags. Compatible with:

- BeeAI Framework (the agent runtime we plan to integrate)
- Our 60-skill catalog (`atlasOS/deed_hack_skill_catalog.md` — 60 tools across 7 categories)
- vLLM OpenAI-compatible endpoints (the harness contract we're standardizing on)
- Any standard agentic runtime that speaks OpenAI tool format

Per IBM's BFCL v3 benchmark, the 30B scores **73.68** — best-in-class for the
size, real not theatre. For our use case (8 CRE tools at minimum: dgwiki_query,
underwrite_tool, comp_lookup, loi_gen, blast_tool, hedera_anchor, honey_inspect,
atlas_jobs), this score predicts reliable tool dispatch with multi-turn
recovery.

---

## See also

- `COOKS/atlas-granite-30b.md` · the queued cook · pre-cook checklist + recipe
- `MODELS/granite-4.1-8b.md` · the same family at smaller scale · already won
- `atlasOS/PRODUCTS.md` · HACKER-AGX product positioning
- `atlasOS/AGENT-ECONOMY.md` · agent runtime requirements (BeeAI · x402 · MCP)
- `BEEAI/README.md` · agent framework integration plan
