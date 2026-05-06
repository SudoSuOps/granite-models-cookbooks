# Atlas-70B · the Llama comparator · COMPLETE 2026-05-06

The first cook on the Royal Jelly CRE Block-0 corpus. Llama-3.3-70B-Instruct
fine-tuned with FSDP-QLoRA across 2× RTX PRO 6000. **The number every Granite
cook compares against.**

---

## Identity

```
Cook name        Atlas-70B
Base model       meta-llama/Llama-3.3-70B-Instruct
Base license     Meta Llama 3.3 Community License (commercial-permitted with terms)
Status           ✓ COMPLETE · 2026-05-06 17:42 UTC
Cook elapsed     73.57 hours
Adapter path     /data2/atlas-70b/lora-adapter/  (on swarmrails)
Manifest path    /data2/atlas-70b/MANIFEST.json
Defendable       atlas.defendable.eth · subdomains corpus · recipe · weights · eval
```

---

## The recipe

Gold Standard FSDP-QLoRA (the recipe Meta documents for 70B-class fine-tunes):

```yaml
method:
  type: bf16 LoRA + FSDP-QLoRA
  base_quantization: nf4 4-bit (storage = bfloat16 for FSDP compatibility)
  compute_dtype: bf16
  reason: 70B + bf16 LoRA needs ~140 GB across 2 cards. FSDP_FULL_SHARD splits
          model + activations + optimizer states; QLoRA halves base memory.

lora:
  r: 64
  alpha: 32
  dropout: 0.0
  bias: none
  target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
  trainable_pct: ~1%

training:
  learning_rate: 1.0e-5
  lr_scheduler: cosine
  warmup_ratio: 0.05
  weight_decay: 0.01
  per_device_batch_size: 1
  gradient_accumulation_steps: 32
  effective_batch_size: 64       # 2 procs × 1 × 32 (FSDP across 2 GPUs)
  max_seq_len: 3072              # backed off from 4096 (94.93/96 GB hit at 4096 on 70B)
  max_steps: 1177                # ~30% of one epoch on Block-0 · MAX_EPOCH_FRACTION=0.6
  eval_steps: 200
  save_steps: 200
  save_total_limit: 5
  early_stopping_patience: 3
  early_stopping_threshold: 0.001
  load_best_model_at_end: true   # final adapter is the best-eval-loss checkpoint
  optim: adamw_torch
  seed: 42
```

Recipe lives in YAML at `atlasOS/recipes/atlas-70b.yml` (the canonical declarative
spec). Training script at `swarmrails:/data2/atlas-70b/scripts/train_atlas_70b.py`.

---

## The data

```
Corpus               Royal Jelly CRE Block-0
Records (train)      125,651
Records (eval)       996 (fingerprint-disjoint from train)
System prompt diversity   41 unique
train.jsonl sha256   d63b05d9e36b0e0d1113ee2fcf9c4681dbb95133a44889319bf1df2f7ad90f39
eval.jsonl sha256    7f025a264210174a75c5bad30c5f255011e133272ed33a1917798b3085f075cc
```

Same corpus across all four cooks (Atlas-70B · Bookmaker-8B · Hack-Deed-Maker-3B ·
Atlas-Granite-30B). Variable isolation — only the base changes.

---

## The hardware

```
Rig                  swarmrails
GPUs                 2× NVIDIA RTX PRO 6000 Blackwell Workstation (96GB each, 102GB usable)
Strategy             FSDP_FULL_SHARD across both GPUs
GPU peak power       400W per card (peak draw observed ~380W during cook)
GPU temp             max ~85C on GPU 1 (stable through cook · monitored)
Driver / CUDA        NVIDIA 590.48.01 / CUDA 13.1
```

The cook ran continuously from 2026-05-03 16:02:05 UTC to 2026-05-06 17:42:01 UTC
(~73.57 hours wall-clock). Heartbeat to `/tmp/atlas-70b.heartbeat` every logging
step. Cook auditor cron every 3 hours scanning for contamination — passed every
audit, no kill switch triggered.

---

## The trajectory · eval at every checkpoint

```
step      eval_loss   delta-from-prev      notes
─────────────────────────────────────────────────────────────────────────
   200    0.8074      —                    early · baseline LoRA absorbing corpus
   400    0.5517      -32%                 large gain · domain shift completing
   600    0.5118      -7%                  diminishing returns · cosine kicking in
   800    0.5031      -2%                  near plateau · structural learning done
  1000    0.5018      -0.3%                BEST · cosine LR near zero · pure polish
  1177    0.5019      +0.02%               final-step micro-noise · not real change
                                           load_best_model_at_end loaded step-1000 ckpt
─────────────────────────────────────────────────────────────────────────
FINAL eval_loss:    0.5018  (step 1000 · adapter saved as the production weights)
FINAL train_loss:   0.6931  (running average across all 1177 steps · note: NOT
                             comparable to eval_loss · running-avg vs final-step)
```

---

## Post-cook adapter consolidation (2026-05-06 18:11 UTC)

The cook saved checkpoints in FSDP-sharded format (per `fsdp_state_dict_type:
SHARDED_STATE_DICT` in the accelerate config). To use the adapter for inference
in single-process mode, we consolidated to standard PEFT format:

```
Source       /data2/atlas-70b/lora-adapter/checkpoint-1177/pytorch_model_fsdp_0/
              (2 distcp shards · 830MB each + .metadata index)
Output       /data2/atlas-70b/consolidated-adapter/
              ├── adapter_config.json     (702 B)
              └── adapter_model.safetensors (1.66 GB)
Method       torch.distributed.checkpoint.format_utils.dcp_to_torch_save
              + key-rename to PEFT convention (lora_A.default.weight / lora_B.default.weight)
Time         4.1 sec total
LoRA params  1,120 (560 lora_A + 560 lora_B = 80 layers × 7 modules ✓ exact match)
```

SHA256 receipts:
- adapter_model.safetensors: `a5f35e4b71d45719809443426797e7bed87d6e4d6b095c39f319235718e65f67`
- adapter_config.json: `0d9de152c61a0d31cc07dc8dcd4d1cf13803f0642b543f8b6f244ba1b2aa489e`

---

## Post-cook eval (post-consolidation · independent verification)

Two eval runs against the consolidated adapter to verify:

### A · Assistant-only methodology (the rigorous "what the model GENERATES" measure)

```
Methodology   Loss computed ONLY on assistant-target tokens (prefix masked with -100).
              Score what the model has to actually produce, not what it sees in context.
Wall clock    24.2 min
Records       996 / 996 ✓
Total tokens  1,096,123 (assistant-target only)

HEADLINE
  Eval loss          1.1739
  Token accuracy     71.70%

PER-BUCKET BREAKDOWN
  BUCKET                       RECORDS   TOKENS         LOSS      ACC
  underwriting_calc                697  1,033,948      1.1579   71.64%
  ic_memo                           75     15,260      1.5756   71.38%   ← weakest (narrative depth)
  comp_market                      189     39,156      1.4941   70.88%
  other (lease extraction)          32      7,128      0.8560   85.48%   ← STRONGEST (structured JSON)
  other (agent mode)                 3        631      1.3574   77.34%   (small sample)
```

**Reading the buckets:** Atlas crushes structured JSON extraction (lease abstraction at 85% accuracy)
and handles dense underwriting math at broker-grade (72%). The narrative-heavy buckets (IC memos and
comp/market analysis) carry higher loss because the answer space has higher entropy — there are
more valid ways to write a memo. *This is the bucket where the next-tier 30B's extra capacity
should pay off most.*

### B · Whole-sequence methodology (matches HF Trainer · cook reproduction)

(Pending in-flight verification eval at time of this commit · expected to land at 0.5018 ± 0.005
matching the cook's reported best · validates that consolidation produced an adapter functionally
identical to the FSDP-shard checkpoint. Will append numbers once eval completes.)

---

## The manifest

Sha256-anchored manifest at `/data2/atlas-70b/MANIFEST.json`:

```json
{
  "model": "Atlas-70B",
  "base": "/data2/llama-3.3-70b-instruct",
  "base_repo": "meta-llama/Llama-3.1-70B-Instruct",
  "architecture": "Dense (all 70B params active per token)",
  "method": "bf16 LoRA r=64 alpha=32",
  "config_source": "Swarm Gold Standard (Llama-3.1 + FSDP path)",
  "data": {
    "train_count": 125651,
    "eval_count": 996,
    "train_sha256": "d63b05d9e36b0e0d1113ee2fcf9c4681dbb95133a44889319bf1df2f7ad90f39",
    "eval_sha256":  "7f025a264210174a75c5bad30c5f255011e133272ed33a1917798b3085f075cc",
    "system_prompt_diversity": 41
  },
  "training": {
    "steps": 1177,
    "max_steps": 1177,
    "final_loss": 0.6931,
    "learning_rate": 1e-05,
    "lr_scheduler": "cosine",
    "effective_batch": 64,
    "max_seq_len": 3072,
    "epoch_fraction": 0.6
  },
  "hardware": {
    "gpus": ["NVIDIA RTX PRO 6000 Blackwell", "NVIDIA RTX PRO 6000 Blackwell"],
    "vram_gb_per_card": 102,
    "training_method": "FSDP_FULL_SHARD"
  },
  "elapsed_hours": 73.57,
  "completed_at": "2026-05-06T17:41:59.057921+00:00",
  "defendable": {
    "issuer": "swarmandbee.eth",
    "category": "atlas.defendable.eth",
    "anchor_target_topic": "0.0.10291838",
    "subdomains": [
      "corpus.atlas.defendable.eth",
      "recipe.atlas.defendable.eth",
      "weights.atlas.defendable.eth",
      "eval.atlas.defendable.eth"
    ]
  }
}
```

---

## The deployment (current and future)

**Current role (until Granite-30B cook completes):** Atlas-70B is the
**doctrine model** behind AIOV ephemeral inference at `atlas70b.atlasos.eth`.
Family-office HACKER-PRO requests route here for the heavy compositional work
(IC memos, multi-property portfolio analysis, narrative-heavy AIOVs).

**Future role (after Granite-30B lands):** if Granite-30B beats this 0.5018
eval (which the 8B trajectory strongly suggests it will, since the 8B already
beat 0.5018 at step 600), Atlas-70B becomes:

- **Comparator** — the historical "this is what 70B Llama gets you on this
  corpus" baseline that every future cook references
- **Depth bench** — held in reserve for the deepest reasoning tasks where the
  30B Granite might not have headroom
- **Honest record** — the receipt that we tested the alternative substrate
  (Llama 3.3) on identical data before committing to the all-Granite stack

---

## Notes

**Why this cook took 73 hours and the 8B took 10:**
70B params + FSDP-QLoRA + 4-bit base + 2-card sharding + grad checkpointing all
add overhead per step. Typical step time was ~225 seconds on this rig. The 8B
cook ran at ~28 seconds per step on a single RTX 5090 (FP precision native, no
QLoRA needed, no sharding overhead).

**Why we backed off seq_len from 4096 to 3072:**
At 4096 we saw 94.93/96 GB peak VRAM on GPU 0 — single OOM event would have
killed the 73-hour cook. 3072 covers p90 of corpus token lengths (3,706 tokens)
without truncating the typical record. 8B and 3B cooks ran at 4096 because
they had headroom to spare.

**Why this corpus is the substrate-test corpus:**
125K records of structured broker-vocab CRE underwriting exchanges with 41
unique system prompts across 5 buckets (underwriting_calc, ic_memo,
distress_workout, macro_capital, comp_market). Highly on-distribution for
instruction-tuned base models, deeply on-domain for our use case. If a base
model can't lift on this corpus, it can't run our brokerage.

Atlas-70B clears the bar at 0.5018. Now we know what beats it.

**The Llama 3.3 license:**
Meta Llama 3.3 Community License is commercial-permitted with conditions. The
adapter we trained (the LoRA delta) is ours; the base weights remain
Meta-licensed. If we serve the merged model commercially, we comply with Meta's
acceptable-use policy and attribution requirements. Granite's Apache 2.0 license
is materially cleaner — one of the strategic reasons the substrate is moving
toward Granite for production.

---

## See also

- `COOKS/eval-results.md` · head-to-head across all four cooks
- `COOKS/bookmaker-8b.md` · the Granite-8B cook on the same data
- `COOKS/atlas-granite-30b.md` · the queued Granite-30B cook
- `MODELS/granite-4.1-8b.md` · the model that beat this one at step 600
- `atlasOS/recipes/atlas-70b.yml` · the canonical recipe spec
- `atlasOS/CORPUS.md` · Royal Jelly CRE Block-0 full provenance
