# Bookmaker-8B · the substrate winner · IN FLIGHT

The Granite-4.1-8B cook on Royal Jelly CRE Block-0. Same corpus, same recipe
as Atlas-70B. **Already beat the 70B Llama at step 600.**

---

## Identity

```
Cook name        Bookmaker-8B (also referenced as atlas-granite-8b-v0-underwriter)
Base model       ibm-granite/granite-4.1-8b
Base license     Apache 2.0
Status           IN FLIGHT · step ~800/1177 · ETA ~21:00 UTC tonight
Rig              smash @ 192.168.0.164 · single RTX 5090 32GB
Adapter path     /home/smash/bookmaker-8b-v0/lora-adapter/  (legacy dir name; will rename post-cook)
Heartbeat        /tmp/bookmaker-8b-v0.heartbeat
Defendable       bookmaker.defendable.eth · subdomains corpus · recipe · weights · eval
```

---

## The recipe (single-GPU bf16 LoRA · no FSDP, no QLoRA)

```yaml
method:
  type: bf16 LoRA · single-GPU
  reason: Granite-8B BF16 weights ~16GB on 32GB 5090 · LoRA opt + grads ~1.5GB ·
          activations ~3-5GB at seq 4096 · comfortable. FSDP and QLoRA add
          complexity for zero gain at this scale.

lora:
  r: 64
  alpha: 32
  dropout: 0.0
  bias: none
  target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
  notes: Granite has tie_word_embeddings=true · 7-module list excludes embed/lm_head

training:
  learning_rate: 1.0e-5
  lr_scheduler: cosine
  warmup_ratio: 0.05
  weight_decay: 0.01
  per_device_batch_size: 1
  gradient_accumulation_steps: 32
  effective_batch_size: 32
  max_seq_len: 4096          # more headroom than 70B Llama (which had to back off to 3072)
  max_steps: 1177            # apples-to-apples with Atlas-70B
  optim: adamw_torch
  seed: 42

hardware:
  rig: smash · 1× RTX 5090 32GB
  precision_serving: BF16 native
  step_time: ~28-29 sec/step (measured)
  estimated_cook_time_hours: 9-10
```

Recipe YAML at `atlasOS/recipes/bookmaker-8b.yml`.

---

## The trajectory (live · still cooking)

```
step      eval_loss   token_acc    notes
─────────────────────────────────────────────────────────────────────────
   200    0.9421      77.65%       early absorption · faster than 70B at same step
   400    0.5615      85.79%       large gain · domain shift completing
   600    0.4983      86.90%       ⚡ ALREADY BEAT 70B's eventual best (0.5018)
   800    0.4756      87.30%       still dropping · cosine kicking in
  1000    pending     pending      next eval · ETA ~19:00 UTC
  1177    pending     pending      final
─────────────────────────────────────────────────────────────────────────
```

---

## The strategic finding

**Step 600 was the moment.** Granite-8B at 0.4983 eval beat Atlas-70B's
eventual best of 0.5018 — *7 steps before Atlas-70B reached its own peak.*

By step 800, the 8B was 0.026 below Atlas-70B's best · projected step-1177 finish ~0.42-0.45 ·
projected token accuracy ~88%.

**The substrate question is answered:** Granite 4.1 outperforms Llama 3.3 on
this corpus at 1/9th the parameters and 1/8th the cook time.

---

## What this cook produces

When complete (~21:00 UTC):

- **Production weights for HACKER-PRO ($599 box).** The Bookmaker-class brain
  that handles compositional narrative work — full OM rendering, IC memos,
  multi-tenant office underwrites.
- **Production weights for AIOV (the family-office product).** This 8B becomes
  the on-box brain that does the local pre-compute before the encrypted brief
  travels to the doctrine model in the datacenter.
- **Quantized GGUF deliverable.** Q4_K_M GGUF at ~4GB on disk · runs at ~10
  tok/s on Orin NX 16GB inside the HACKER-PRO box.
- **A Defendable receipt anchored at `bookmaker.defendable.eth/<id>`** with
  parent_anchors pointing to the Royal Jelly Block-0 corpus manifest.

---

## See also

- `COOKS/atlas-70b.md` · the Llama comparator this cook beat at step 600
- `COOKS/eval-results.md` · live head-to-head across all four cooks
- `MODELS/granite-4.1-8b.md` · the base model architectural detail
- `atlasOS/recipes/bookmaker-8b.yml` · canonical recipe spec
- `atlasOS/PRODUCTS.md` · HACKER-PRO product page
