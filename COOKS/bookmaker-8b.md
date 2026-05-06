# Bookmaker-8B · the substrate winner · COMPLETE

The Granite-4.1-8B cook on Royal Jelly CRE Block-0. Same corpus, same recipe
as Atlas-70B. **Beat the 70B Llama at step 600 · landed 0.467 final eval at
1/9 the parameters and 1/8 the cook time.**

---

## Identity

```
Cook name        Bookmaker-8B (also referenced as atlas-granite-8b-v0-underwriter)
Base model       ibm-granite/granite-4.1-8b
Base license     Apache 2.0
Status           COMPLETE · 2026-05-06 ~21:00 UTC
Rig              smash @ 192.168.0.164 · single RTX 5090 32GB
Adapter path     /home/smash/bookmaker-8b-v0/lora-adapter/
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
  max_seq_len: 4096
  max_steps: 1177
  optim: adamw_torch
  seed: 42

hardware:
  rig: smash · 1× RTX 5090 32GB
  precision_serving: BF16 native
  step_time: ~27 sec/step (measured)
  cook_time_hours: 8.89
```

Recipe YAML at `atlasOS/recipes/bookmaker-8b.yml`.

---

## The trajectory (COMPLETE · 2026-05-06)

```
step      eval_loss   token_acc    notes
─────────────────────────────────────────────────────────────────────────
   200    0.9421      77.65%       early absorption · faster than 70B at same step
   400    0.5615      85.79%       large gain · domain shift completing
   600    0.4983      86.90%       ⚡ ALREADY BEAT 70B's eventual best (0.5018)
   800    0.4756      87.30%       still dropping · cosine kicking in
  1000    0.468       87.45%       sustained
  1177    0.467 ✓     87.46%       FINAL · 8.89 hour cook · landed BETTER than the 70B Llama
─────────────────────────────────────────────────────────────────────────

FINAL eval_loss:    0.467     (whole-sequence methodology · HF Trainer)
FINAL token_acc:    87.46%
FINAL train_loss:   0.7717    (running average across all 1177 steps · NOT comparable to eval)
Tokens evaluated:   76.79 M   (full 996-record holdout)
Cook elapsed:       8.89 hours
Cost:               ~$2 in electrons
```

---

## The strategic finding · LOCKED

**Granite-4.1-8B beats Llama-3.3-70B on the Royal Jelly CRE corpus.**

```
                       final eval_loss   final token_acc   params   cook time   electrons
Atlas-70B (Llama)      0.5018            ?                 70B      73.6h       ~$37
Bookmaker-8B (Granite) 0.467  ⚡         87.46%            8B       8.89h       ~$2
                       ────────────────  ────────────────  ──────   ─────────   ──────────
delta                  −0.035            (8B leads)         1/9      1/8         1/18
```

**Step 600 was the moment.** Granite-8B at 0.4983 eval beat Atlas-70B's
eventual best of 0.5018 — *7 steps before Atlas-70B reached its own peak.*

**Same data. Same recipe. One-ninth the parameters. One-eighth the cook time. One-eighteenth the electrons.**

This is the empirical receipt for the Granite pivot decision made on the same
day the cooks launched. See `granite_pivot_2026_05.md` for the strategic
doctrine that follows from this finding.

---

## What this cook produces

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

## Pending post-cook work

- [ ] Consolidate FSDP-shard adapter to PEFT format (not needed · single-GPU cook
      saves clean PEFT adapter directly · no consolidation step required)
- [ ] Run independent assistant-only eval for apples-to-apples vs Atlas-70B's 1.1739
- [ ] Quantize to Q4_K_M GGUF for HACKER-PRO deployment
- [ ] Anchor Defendable receipt at bookmaker.defendable.eth/\<id\>

---

## See also

- `COOKS/atlas-70b.md` · the Llama comparator this cook beat at step 600
- `COOKS/eval-results.md` · live head-to-head across all four cooks
- `COOKS/atlas-granite-30b.md` · the next-tier Granite cook on the bigger Block-1-v2 corpus
- `MODELS/granite-4.1-8b.md` · the base model architectural detail
- `atlasOS/recipes/bookmaker-8b.yml` · canonical recipe spec
- `atlasOS/PRODUCTS.md` · HACKER-PRO product page
