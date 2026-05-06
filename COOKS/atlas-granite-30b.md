# Atlas-Granite-30B · LIVE · the candidate doctrine model

The fourth cook in our Granite family · the first cook on the **expanded
Block-1-v2 corpus** (407,076 records · 3.24× Block-0). Production-doctrine
candidate. Full Defendable receipt path.

---

## Identity

```
Cook name        Atlas-Granite-30B
Base model       ibm-granite/granite-4.1-30b
Base license     Apache 2.0
Status           LIVE · launched 2026-05-06 20:14 UTC
Rig              swarmrails 2× RTX PRO 6000 Blackwell 96GB · FSDP_FULL_SHARD
Wall-clock ETA   ~35 hours · landing ~2026-05-08 07:00 UTC
Cost ETA         ~$15-20 in electrons (sovereign compute)
Defendable plan  atlas-granite-30b.defendable.eth
                 promoted to atlas.defendable.eth if it wins doctrine slot
```

---

## Why this cook breaks corpus apples-to-apples (and why that's right)

The first three cooks (70B Llama · 8B Granite · 3B Granite) all ran on
**Royal Jelly CRE Block-0** (125,651 train records · 7 sources). That was
the substrate-comparison frontier — only the base model varied.

This cook runs on **Royal Jelly CRE Block-1-v2** (407,076 train · 3.24×).
Same recipe. Same hardware-class. Same eval set. **Only the corpus changed.**

The trade-off is deliberate:
- **Recipe apples-to-apples HOLDS** (LoRA r=64 α=32 · LR 1e-5 cosine · etc.)
- **Eval apples-to-apples HOLDS** (same 996-record fingerprint-disjoint holdout · same sha256)
- **Corpus apples-to-apples BREAKS** (Block-0 → Block-1-v2)

Why: the 30B is the **production doctrine candidate**, not a substrate-test
sample. We want it cooked on the richest 2026-vintage CRE corpus we can build
— which means the SwarmRefinery / Defendable CCIR doctrine layer, the
blockchain bucket, the federal grants stack, the legal / credit-defense
layer, and the SwarmJudge evaluation discipline. Cooking the 30B on the same
narrow Block-0 the substrate test used would leave production capability on
the table.

The substrate question is already settled (Bookmaker-8B's 0.467 vs Atlas-70B's
0.5018 · same data, same recipe). The 30B's job is to become the production
doctrine model.

---

## Block-1-v2 corpus · 9 tiers · 19 sources · 407,076 records

```
TIER 1 · APEX DOCTRINE (process first · claim fingerprints before larger sources)
  signal_platinum                     142   PLATINUM tier · SwarmCapitalMarkets institutional analyst
  board_member_500                    497   strategic advisor to Swarm & Bee · governance

TIER 2 · DOCTRINE BACKBONE (the SwarmRefinery / Defendable CCIR corpus)
  bee_hive_train_data              94,768   "operational intelligence engine for Defendable
                                             Commercial Compute Intelligence Refinery"
  judge_cre_30k                    30,000   SwarmJudge CRE evaluation · A/B/C grading discipline

TIER 3 · AGENT COORDINATION (tool-calling reliability for HACKER-AGX runtime)
  bee_hive_agent                    3,811   SwarmAgent conductor · multi-turn tool dispatch
  bee_hive_router                   1,584   router bee · arena dispatch · routing JSON
  bee_hive_scout                    3,992   scout bee · exploration · breadth-first
  bee_hive_peeta                    3,126   SwarmPeeta · 4B stabilizer · repair patterns

TIER 4 · NEW BUCKETS (the 2026-vintage additions)
  stream_blockchain                 5,011   RWA tokenization · Hedera · stablecoin settlement
  swarmgrant_train                 43,689   federal grants budget specialist · OZ / NMTC / HUD / USDA
  legal_consumer_stamped            8,773   debt defense · FDCPA · lease · LOI · estoppel
  creditsniper_train               30,000   CRE credit + debt covenant · IRAC reasoning (cap from 79,910)

TIER 5 · FINANCE TRIO (CRE credit-side depth)
  finance_creditor_collector           13   creditor vs debt collector branching logic
  finance_debt_validation           5,386   FDCPA debt defense strategist
  finance_rating_agency            13,097   credit analyst at major rating agency

TIER 6 · BLOCK-0 SMALL SPECIALTY (preserved · process before atlas_v1 superset)
  maturity_wall_workflow            5,549   distress refi paths
  macro_energy                     14,632   energy-aware CRE · data centers · EV · grid
  streams                          10,209   live signal · 21 shards

TIER 7 · BLOCK-0 MEDIUM CAPITAL MARKETS
  capital_markets_stamped               0   absorbed by bee_hive_train_data superset
  capital_markets_neweconomy            0   absorbed by bee_hive_train_data superset

TIER 8 · ATLAS-V1 FOUNDATION (CRE superset · processed late)
  atlas_v1_foundation              12,797   pass/proceed mental model · 32K dups vs streams/macro

TIER 9 · OCEAN
  cre_honey_volume                120,000   honey-graded CRE · cap from 810,097 (49K dup · 85K score-rejected)
─────────────────────────────────────────────────────────────────────────────────────────
TOTAL Block-1-v2                 407,076   3.24× Block-0
```

**Filter discipline (matches Block-0 builder):**
- `jelly_threshold_verification_score: 75` (records with verification_score < 75 dropped)
- `fingerprint_dedup: True` (md5 of role+content[:5000] · cross-source dedup)
- `min_messages: 2` (records with fewer than 2 messages dropped)

**Honest dedup notes:**
- Two Block-0 buckets (capital_markets_stamped + capital_markets_neweconomy) ended
  at 0 records because they were absorbed by `bee_hive_train_data` (the SwarmRefinery
  doctrine corpus is the curated superset that includes these earlier capital-markets pairs).
- That's a feature, not a bug — we're getting the cleaner version of those records via the
  doctrine bucket instead.

**Provenance:**
- train.jsonl sha256 · `4d90e676442738c4...` (post strip-to-messages-only)
- eval.jsonl sha256 · `7f025a264210174a...` (IDENTICAL to Block-0 eval · cross-cook comparable)
- 19 source files · sha256 each · all in MANIFEST_SLICE.json
- Build script · `COOKS/scripts/build_block1_v2.py` (deterministic · seed 42)

---

## The recipe · IDENTICAL to the prior 3 cooks (recipe apples-to-apples HOLDS)

```yaml
method:
  type: bf16 LoRA + FSDP_FULL_SHARD (no QLoRA · 30B fits on 2× 96GB)
  reason: 30B BF16 weights ~58 GB · sharded across 2 cards = ~30 GB/card

lora:
  r: 64
  alpha: 32
  dropout: 0.0
  bias: none
  target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
  notes: Granite has tie_word_embeddings=true · target list excludes embed/lm_head
         (verified at runtime · script logs the confirmation)

training:
  learning_rate: 1.0e-5
  lr_scheduler: cosine
  warmup_ratio: 0.05
  weight_decay: 0.01
  per_device_batch_size: 1
  gradient_accumulation_steps: 32
  effective_batch_size: 64           # 2 procs × 1 × 32
  max_seq_len: 4096                  # 30B has more headroom than 70B Llama (which had to back off to 3072)
  max_steps: 1177                    # apples-to-apples with all other Block-0 cooks
  eval_steps: 200
  save_steps: 200
  save_total_limit: 7
  optim: adamw_torch
  seed: 42

fsdp:
  fsdp_transformer_layer_cls_to_wrap: GraniteDecoderLayer  # NOT LlamaDecoderLayer
  fsdp_state_dict_type: SHARDED_STATE_DICT
  fsdp_activation_checkpointing: true
  fsdp_offload_params: false

hardware:
  rig: swarmrails
  gpus: 2× RTX PRO 6000 Blackwell 96GB
  step_time: ~107 sec/step (measured at smoke v6)
  estimated_cook_time_hours: 35
```

Cook script · `COOKS/scripts/train_atlas_granite_30b.py`
FSDP config · `COOKS/scripts/accelerate_fsdp_granite.yaml`

---

## Smoke test history (the 7 reconciliations to get to a clean run)

The cook script was originally cribbed from the Atlas-70B Llama cook. Six smoke
iterations were needed to reconcile against TRL 0.24 / transformers 5.5 / FSDP2:

```
v1   FAIL  · HF datasets schema cast failure (heterogeneous metadata across sources)
       FIX · stripped train.jsonl + eval.jsonl to messages-only · 134 MB metadata noise removed
v2   FAIL  · TRL 0.24: max_seq_length kwarg removed
       FIX · renamed to max_length
v3   FAIL  · TRL 0.24: save_safetensors kwarg removed (safetensors now default)
       FIX · removed line
v4   FAIL  · FSDP + gradient_checkpointing conflict (transformers 5.5+ enforces pick-one)
       FIX · removed gradient_checkpointing=True from SFTConfig
v5   FAIL  · TRL 0.24 SFTConfig defaults gradient_checkpointing=True (the default kicked in)
       FIX · explicitly set gradient_checkpointing=False
v6   PASS  · cook started · step 10/20 · checkpoint-10 saved · first eval landed
       PROMOTED to full cook
```

Smoke v6 artifacts preserved at `/data2/atlas-granite-30b/lora-adapter-smoke-v6/`
as the receipt that the pipeline works end-to-end.

---

## Live trajectory (updates as the cook progresses)

```
step       eval_loss   token_acc    timestamp                notes
─────────────────────────────────────────────────────────────────────────────────
launch     ─           ─            2026-05-06 20:14 UTC     full cook · Block-1-v2
   200     pending     pending      ~2026-05-06 ~26 UTC      first eval landing
   400     pending     pending      ~2026-05-07 ~05 UTC
   600     pending     pending      ~2026-05-07 ~11 UTC
   800     pending     pending      ~2026-05-07 ~17 UTC
  1000     pending     pending      ~2026-05-07 ~23 UTC
  1177     pending     pending      ~2026-05-08 ~07 UTC      FINAL
─────────────────────────────────────────────────────────────────────────────────
```

(Step times are projections at 107 s/step · subject to ±20% variance from FSDP
all-reduce and disk I/O.)

---

## What this cook unlocks

```
Day +0       Cook launches · 35h wall-clock
Day +1.5     Cook completes · final eval lands · manifest writes
Day +1.6     Head-to-head eval comparison commits to COOKS/eval-results.md
             Defendable receipt anchors at atlas-granite-30b.defendable.eth/<id>
Day +2       Strategic decision: keep Atlas-70B as doctrine OR promote 30B
Day +3-7     If promoted: rebrand Atlas at atlasos.eth · update product docs ·
             update HACKER-AGX provisioning to ship 30B-cooked weights
```

**Optimistic projection** (continuing the Granite-beats-Llama trend, plus the
richer corpus):

```
                              FINAL eval_loss
Atlas-70B (Llama, complete)   0.5018
Bookmaker-8B (Gran, complete) 0.467
Atlas-Granite-30B (this cook) 0.38-0.42  (projected)  ← if it lands here, it becomes doctrine
```

**Conservative projection** (if 30B plateaus at the 8B level):
```
Atlas-Granite-30B             ~0.46-0.47  (similar to 8B)
```

Even in the conservative case, the 30B beats Atlas-70B's 0.5018 by a margin
and becomes the HACKER-AGX ($2K branch box) brain regardless of doctrine
decision.

---

## See also

- `COOKS/atlas-70b.md` · the Llama comparator this cook will be measured against
- `COOKS/bookmaker-8b.md` · the 8B that already proved Granite > Llama at step 600
- `COOKS/hack-deed-maker-3b.md` · the 3B desk-edge brain
- `COOKS/eval-results.md` · the live head-to-head trajectory
- `COOKS/scripts/build_block1_v2.py` · the corpus builder (deterministic · seed 42)
- `COOKS/scripts/train_atlas_granite_30b.py` · the cook script
- `COOKS/scripts/accelerate_fsdp_granite.yaml` · the FSDP config
- `MODELS/granite-4.1-30b.md` · architectural detail of the base model
- `atlasOS/recipes/atlas-granite-30b.yml` · canonical recipe spec (mirrored)
