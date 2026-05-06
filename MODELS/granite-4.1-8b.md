# Granite-4.1-8B · the substrate winner · Bookmaker base

The 8-billion-parameter dense decoder in the Granite 4.1 family. **The base
that's already beating Llama-3.3-70B on our corpus** at step 600 of an
in-flight cook (2026-05-06).

---

## Identity

```
Hugging Face        ibm-granite/granite-4.1-8b
Variant             instruct (RL-aligned post-training)
Base variant        ibm-granite/granite-4.1-8b-base (pre-train only)
License             Apache 2.0
Released            April 29, 2026
Disclosure          github.com/ibm-granite/granite-4.1-language-models/disclosures/granite_4.1_8b_disclosure.json
```

---

## Architecture

```
Type                Decoder-only dense transformer
Parameters          8B (verified ~8.4B effective per HF model card)
Layers              40
Hidden size         4096
Attention heads     32 (GQA)
KV heads            8 (GQA 4:1)
Head dim            128
MLP intermediate    12,800
Vocab size          100,352
Activation          SwiGLU
Normalization       RMSNorm
Position encoding   RoPE
Context window      131,072 (128K) native, extendable to 512K
Embedding tying     yes (tied input/output)
Precision           BF16 native
Granite multipliers attention_multiplier 0.0078125 · embedding_multiplier 12.0 ·
                    residual_multiplier 0.22 · logits_scaling 16.0
```

---

## VRAM math

```
BF16 (training)         ~16 GB weights · LoRA adds ~1.5 GB · activations ~3-5 GB
                        Total ~22-25 GB · fits 32 GB RTX 5090 single GPU (no FSDP needed)

INT8 inference          ~8 GB weights · single 16 GB+ GPU comfortable

INT4 (Q4_K_M deployment) ~4 GB weights
                         Fits Orin NX 16GB (HACKER-PRO $599 box)
                         Fits any 8GB+ GPU/iGPU at this quant
```

---

## Why this base wins on our corpus

**Empirical receipt as of 2026-05-06:**

```
On Royal Jelly CRE Block-0 (125,651 train · 996 fingerprint-disjoint eval) ·
identical Gold Standard recipe as the 70B Llama comparator:

step    Granite-8B eval_loss    Llama-70B eval_loss    delta
─────────────────────────────────────────────────────────────
200     0.9421                  0.8074                 -0.135  (Llama leads early)
400     0.5615                  0.5517                 -0.010  (effectively tied)
600     0.4983                  0.5118                 +0.014  ← Granite pulls ahead
800     0.4756                  0.5031                 +0.028  ← gap widening
1000    pending                 0.5018 (BEST)          ── Llama plateaus here
1177    pending                 0.5019 (final)         ── Llama done
```

By step 600 of the 8B cook · Granite-8B's eval is *better than Llama-70B's
eventual best* · with 1/9 the parameters and 1/8 the cook time.

**Why this happens (architectural):**
- IBM's 5-phase training (pre-train · mid-train w/ data annealing · long-context)
  produces stronger instruct alignment than Meta's two-stage approach
- RL post-training on the instruct variant produces better instruction-following
  on long prompts (IFEval 87.06 for 8B vs Llama-70B's ~87 in same range)
- BFCL tool-calling score 68.27 — close to 70B-class on a 1/9-size model
- Tied embeddings + smaller MLP make the model parameter-efficient on
  vocabulary-heavy domains like broker-vocab CRE

**Why this matters for product:**
The 8B becomes the production reasoning model for HACKER-PRO ($599) and the
local pre-compute layer for AIOV. It also raises a strategic question for
the 30B (queued cook): if the 30B beats Atlas-70B's 0.5018, the all-Granite
stack becomes the production substrate end-to-end.

---

## Capabilities (per IBM benchmarks · 8B variant)

```
MMLU 5-shot                       73.84
MMLU-Pro 5-shot, CoT              55.99
BBH 3-shot, CoT                   80.51
AGI EVAL 0-shot, CoT              72.43
GPQA 0-shot, CoT                  41.96
IFEval Avg                        87.06   ← excellent instruction following
ArenaHard                         68.98
GSM8K 8-shot                      92.49
HumanEval pass@1                  85.37
HumanEval+ pass@1                 79.88
MBPP pass@1                       87.30
BFCL v3                           68.27   ← strong tool calling for size
SALAD-Bench                       95.80
```

For our brokerage doctrine work the load-bearing scores are **IFEval 87.06**
(honors broker persona prompts) · **GSM8K 92.49** (cap rate / DSCR / IRR math
holds) · **BFCL 68.27** (tool dispatch reliable for the 8 CRE tools we wire).
All clear the bar for production broker-grade output.

---

## Cook reference

Our Bookmaker-8B cook on this base is documented at `COOKS/bookmaker-8b.md`.
Recipe at `atlasOS/recipes/bookmaker-8b.yml`.

```
Status              IN FLIGHT · step ~800/1177 · ETA ~21:00 UTC tonight
Adapter saves at    bookmaker.defendable.eth/<id> when complete
Deployed to         HACKER-PRO ($599 box) at Q4_K_M quant
                    Datacenter batch (BF16) for OM rendering volume
```

---

## See also

- `COOKS/bookmaker-8b.md` · our cook on this base
- `COOKS/eval-results.md` · live head-to-head with Llama-70B
- `MODELS/granite-4.1-3b.md` · same family · smaller (HACKER box brain)
- `MODELS/granite-4.1-30b.md` · same family · larger (next cook · branch tier)
- `atlasOS/PRODUCTS.md` · HACKER-PRO product page
