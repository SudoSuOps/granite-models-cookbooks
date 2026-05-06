# Atlas-Granite-30B · QUEUED · the next cook

The fourth cook in the Royal Jelly CRE Block-0 substrate-comparison series.
**Launches the moment swarmrails frees up** (Atlas-70B finished at 17:42 UTC
on 2026-05-06; smoke-test + cook prep begins immediately).

---

## Identity

```
Cook name        Atlas-Granite-30B
Base model       ibm-granite/granite-4.1-30b
Base license     Apache 2.0
Status           QUEUED · awaiting swarmrails (Atlas-70B GPUs free)
Target hardware  swarmrails 2× RTX PRO 6000 Blackwell · FSDP_FULL_SHARD
Target ETA       30-50 hours wall-clock
Defendable plan  atlas-granite-30b.defendable.eth · or absorb into atlas.defendable.eth
                 if this becomes the new doctrine model
```

---

## Why this cook is the answer to the substrate question

Three of four cooks have run on the Royal Jelly Block-0 corpus today:

```
                                 step 200   step 400   step 600   step 800   step 1000
Atlas-70B   (Llama 3.3, 70B)     0.8074     0.5517     0.5118     0.5031     0.5018  ← BEST
Bookmaker-8B (Granite 4.1, 8B)   0.9421     0.5615     0.4983     0.4756     pending
Hack-Deed-3B (Granite 4.1, 3B)   1.102      0.6559     0.5773     0.5487     pending
Atlas-Granite-30B (Granite 4.1)  ─── this cook · the missing data point ───
```

**At step 600, Granite-8B (8B params) beat Atlas-70B's BEST eval (70B params).**

The 30B fills the gap between 8B and 70B in the family scaling curve. If 30B
extends the Granite-beats-Llama trajectory, the brand-cleanup play is:

- Granite-30B becomes the new **doctrine model** at `atlas70b.atlasos.eth`
  (renamed to `atlas.atlasos.eth` or kept for continuity, the Llama-70B archived
  as comparator)
- All-Granite stack: 3B / 8B / 30B uniform tokenizer · uniform tool-call format ·
  uniform Apache 2.0 license · single model family across all HACKER tiers
- Brand simplification: customer never sees a Llama mention again

If 30B does NOT beat 70B (unlikely given 8B already did, but possible), we keep
Atlas-70B as doctrine and Granite-30B becomes the HACKER-AGX ($2K branch box) brain.

Either way, this cook is the receipt that decides which path.

---

## The recipe (mirrored from atlas-70b.md, with corrections for Granite-30B)

```yaml
name: atlas-granite-30b
description: bf16 LoRA fine-tune of IBM Granite-4.1-30B on Royal Jelly CRE Block-0
status: queued · launches when swarmrails frees from Atlas-70B
launch_command: |
  accelerate launch --config_file scripts/accelerate_fsdp.yaml \
    scripts/train_atlas_granite_30b.py [--smoke-test]

base:
  repo: ibm-granite/granite-4.1-30b
  license: Apache 2.0
  arch: dense decoder · ~30B params · 64 layers (TBD verify) · GQA · SwiGLU · 128K ctx · BF16

method:
  type: bf16 LoRA + FSDP (no QLoRA — 30B fits BF16 across 2 cards)
  reason: 30B BF16 weights ~60GB · sharded across 2× 96GB cards = ~30GB/card · comfortable
          QLoRA not needed at this scale on this hardware

lora:
  r: 64
  alpha: 32
  dropout: 0.0
  bias: none
  target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
  notes: Granite has tie_word_embeddings · target list excludes embed/lm_head to
         avoid double-LoRA conflict

training:
  learning_rate: 1.0e-5
  lr_scheduler: cosine
  warmup_ratio: 0.05
  weight_decay: 0.01
  per_device_batch_size: 1
  gradient_accumulation_steps: 32
  effective_batch_size: 64       # 2 procs × 1 × 32
  max_seq_len: 4096              # 30B has more headroom than 70B did at 3072
  max_steps: 1177                # apples-to-apples with all other Block-0 cooks
  eval_steps: 200
  save_steps: 200
  save_total_limit: 7
  early_stopping_patience: 5
  optim: adamw_torch
  seed: 42

hardware:
  rig: swarmrails
  gpus: 2× RTX PRO 6000 Blackwell 96GB
  strategy: FSDP_FULL_SHARD
  estimated_cook_time_hours: 30-50

defendable:
  issuer: swarmandbee.eth
  category: atlas-granite-30b.defendable.eth (or atlas.defendable.eth if promoted)
  anchor_topic: "0.0.10291838"
  compares_to: atlas.defendable.eth (the Llama-70B cook on identical data)
```

YAML lives at `atlasOS/recipes/atlas-granite-30b.yml` (to be added in next commit).

---

## The data (same as every other Block-0 cook)

```
Corpus               Royal Jelly CRE Block-0
Records (train)      125,651
Records (eval)       996 (fingerprint-disjoint from train)
train.jsonl sha256   d63b05d9e36b0e0d1113ee2fcf9c4681dbb95133a44889319bf1df2f7ad90f39
eval.jsonl sha256    7f025a264210174a75c5bad30c5f255011e133272ed33a1917798b3085f075cc
```

**No corpus changes between cooks.** Same train sha256, same eval sha256, same
holdout. Apples-to-apples.

---

## Pre-cook checklist

```
[ ] Atlas-70B cook complete · adapter saved · manifest written      ✓ DONE 17:42 UTC
[ ] swarmrails GPUs free · nvidia-smi shows idle                    ⏳ verify before launch
[ ] Pull granite-4.1-30b base model to swarmrails:/data2/granite-4.1-30b/
    (~60GB BF16 download · 30+ min on rig's bandwidth)
[ ] Adapt /data2/atlas-70b/scripts/train_atlas_70b.py
    → /data2/atlas-granite-30b/scripts/train_atlas_granite_30b.py
    Changes: MODEL_PATH, BUILD_DIR, BUILD_NAME, NAS_MIRROR (optional), HEARTBEAT
    Recipe stays identical. Hardware config stays identical.
[ ] Verify FSDP transformer wrap class for Granite (probably GraniteDecoderLayer
    vs LlamaDecoderLayer · update accelerate_fsdp.yaml accordingly)
[ ] Smoke test: --smoke-test flag · 20 steps · 500/50 dataset slice ·
    confirm no chat-template leak in reverse-smoke generation
[ ] Launch in screen `atlas-granite-30b-cook`
[ ] Cook auditor cron · same 3-hour pattern · same 1% contamination kill switch
```

---

## What we expect

**Optimistic projection** (if 30B continues the Granite-beats-Llama trend):

```
                              step 200    step 400    step 600    step 800    step 1000   step 1177 (FINAL)
Atlas-70B (Llama, complete)   0.8074      0.5517      0.5118      0.5031      0.5018      0.5019
Granite-30B (this cook)       ?           ?           ?           ?           ?           ~0.40-0.43 (projected)
```

If the projection holds, Granite-30B beats Atlas-70B by ~0.07-0.10 eval loss
on identical data — a meaningful margin. Combined with the cleaner license,
uniform family architecture, and simpler operational stack, **the strategic
choice becomes obvious.**

**Conservative projection** (if 30B plateaus at the 8B level):

```
Granite-30B               ~0.45 (similar to where 8B will land)
```

Even in this case, the 30B beats Atlas-70B's 0.5018 by ~0.05 — still
substrate-winning. The 30B becomes either the doctrine model or the HACKER-AGX
($2K) brain, depending on customer-felt accuracy delta vs the 8B.

---

## What this cook unlocks

```
Day +0       Cook launches · ~30-50 hour wall clock
Day +2       Cook completes · final eval lands · manifest writes
Day +2.1     Head-to-head eval comparison commits to COOKS/eval-results.md ·
             Defendable receipt anchors at atlas-granite-30b.defendable.eth/<id>
Day +3       Strategic decision: keep Atlas-70B as doctrine OR promote 30B
Day +3-7    If promoted: rebrand Atlas at atlasos.eth · update product docs ·
             update HACKER-AGX provisioning to ship 30B-cooked weights ·
             retire the Llama 70B serving on swarmrails (free up 2× PRO 6000
             for the next cook block)
```

---

## See also

- `COOKS/atlas-70b.md` · the Llama comparator this cook will be measured against
- `COOKS/bookmaker-8b.md` · the 8B cook that already proved Granite > Llama at step 600
- `COOKS/eval-results.md` · the live head-to-head trajectory
- `MODELS/granite-4.1-30b.md` · architectural detail of the base model
- `atlasOS/recipes/atlas-granite-30b.yml` · canonical recipe (to be added)
