# Hack-Deed-Maker-3B · desk-edge underwriter · IN FLIGHT

The Granite-4.1-3B cook on Royal Jelly CRE Block-0. The brain that ships
inside the $250 HACKER box at every brokerage Hack desk.

---

## Identity

```
Cook name        Hack-Deed-Maker-3B (also referenced as atlas-granite-3b-v0-underwriter)
Base model       ibm-granite/granite-4.1-3b
Base license     Apache 2.0
Status           IN FLIGHT · step ~800/1177 · ETA ~18:30 UTC tonight
Rig              192.168.0.99 · single RTX 5090 32GB
Adapter path     /home/swarm/atlas-granite-3b-v0-underwriter/lora-adapter/
Heartbeat        /tmp/atlas-granite-3b-v0-underwriter.heartbeat
Defendable       hack-deed-maker.defendable.eth · subdomains corpus · recipe · weights · eval
```

---

## The recipe

Identical to Bookmaker-8B (single-GPU bf16 LoRA) · only the base changes.

```yaml
method:
  type: bf16 LoRA · single-GPU
  reason: 3B BF16 weights ~6GB · trivially fits on 32GB 5090 · ~2× faster step time
          than 8B (smaller model · less compute per forward pass)

lora:
  r: 64
  alpha: 32
  dropout: 0.0
  bias: none
  target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]

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
  rig: 192.168.0.99 · 1× RTX 5090 32GB
  step_time: ~17 sec/step (measured · ~2× faster than 8B)
  estimated_cook_time_hours: 5-6
```

Recipe YAML at `atlasOS/recipes/hack-deed-maker-3b.yml`.

---

## The trajectory (live · still cooking)

```
step      eval_loss   token_acc    notes
─────────────────────────────────────────────────────────────────────────
   200    1.102       75.17%       early · slower start than 8B (smaller capacity)
   400    0.6559      84.17%       big gain · still tracking proportionally with 8B
   600    0.5773      85.64%       gap with 8B narrowing slightly
   800    0.5487      86.09%       cosine kicking in · plateau pattern
  1000    pending     pending      next eval · ETA ~18:00 UTC
  1177    pending     pending      final
─────────────────────────────────────────────────────────────────────────
```

The gap between the 3B and 8B at step 800: only **~1.21 percentage points**
of token accuracy (86.09% vs 87.30%). That's smaller than the noise floor
on most broker-grade output tasks.

---

## What 86% token accuracy at $250 hardware means

A 996-record fingerprint-disjoint broker holdout · 86% next-token match with
the gold-standard analyst output is **broker-grade output**. This is the
empirical receipt for the HACKER ($250 box) pricing thesis:

- The $250 box delivers 86% token accuracy on routine underwriting
- The $599 box (HACKER-PRO with 8B) delivers 87% — invisible 1pt delta to most
  customers
- The pricing tier exists because of *reasoning depth on harder problems*
  (Bookmaker-class narrative · multi-property · distress workouts), not because
  the small box "doesn't work"

The labor-business model holds: $250 hardware + $108K/yr labor SKU per desk
replaces ~$200K/yr of legacy brokerage cost-to-staff per desk. The 3B's
performance is what makes that math defensible.

---

## What this cook produces

When complete (~18:30 UTC tonight):

- **Production weights for HACKER ($250 box).** Daily underwriting brain at
  every brokerage Hack desk. Q4_K_M GGUF ~2.1GB · runs at 13.5 tok/s sustained
  on Orin Nano 8GB.
- **The desk-edge product is empirically validated.** With the 3B at this
  accuracy, the HACKER box ships as a defensible product, not a marketing
  promise.
- **A Defendable receipt at `hack-deed-maker.defendable.eth/<id>`** parent-anchored
  to the Royal Jelly Block-0 corpus manifest.

---

## See also

- `COOKS/atlas-70b.md` · the Llama comparator
- `COOKS/bookmaker-8b.md` · the 8B cook (HACKER-PRO brain)
- `COOKS/eval-results.md` · live head-to-head across all four cooks
- `MODELS/granite-4.1-3b.md` · base model architectural detail
- `atlasOS/recipes/hack-deed-maker-3b.yml` · canonical recipe spec
- `atlasOS/PRODUCTS.md` · HACKER ($250) product page
