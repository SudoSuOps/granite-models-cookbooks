# Eval Results · the IQ-vs-cost frontier

Head-to-head eval across every cook in the substrate-comparison series.

**Apples-to-apples discipline:** identical recipe (Gold Standard LoRA r=64 α=32 ·
LR 1e-5 cosine · eff batch 32-64 · max_steps 1177). Identical 996-record
fingerprint-disjoint eval (sha256 `7f025a264210174a...`).

The first three cooks (70B Llama · 8B Granite · 3B Granite) used **Royal Jelly
CRE Block-0** (125,651 train records). The fourth cook (30B Granite) uses the
expanded **Royal Jelly CRE Block-1-v2** (407,076 train records · 3.24× Block-0)
since it's the production-doctrine candidate, not a substrate-test sample. See
`atlas-granite-30b.md` for the corpus rationale.

Numbers below are **measured, not extrapolated.** Pending cells fill in as
cooks complete.

---

## Live status (updated 2026-05-06 20:14 UTC)

### Whole-sequence eval (cook methodology · HF Trainer)

```
                              step 200   step 400   step 600   step 800   step 1000   step 1177   final
Atlas-70B (Llama 3.3, 70B)    0.8074     0.5517     0.5118     0.5031     0.5018 ✓    0.5019      0.5018  ✓ DONE
Bookmaker-8B (Granite, 8B)    0.9421     0.5615     0.4983 ⚡  0.4756     0.468       0.467 ✓     0.467   ✓ DONE
Hack-Deed-Maker-3B (Gran, 3B) 1.102      0.6559     0.5773     0.5487     0.5393      0.5383 ✓    0.5383  ✓ DONE
Atlas-Granite-30B (Gran, 30B) ─── LIVE · launched 20:14 UTC · 1st eval ~step 200 ~26h from launch ───
```

⚡ = the moment Granite-8B beat Atlas-70B's eventual best (0.4983 < 0.5018).
This happened at step 600 of the 8B cook · 7 steps before Atlas-70B reached its
own best at step 1000.

### Post-cook independent verification (assistant-target-only methodology)

After consolidating each cooked LoRA adapter to standard PEFT format, we
re-run a stricter eval that masks prefix tokens — scoring only the assistant
target. This measures what the model **actually generates**, not what it
sees in context. Numbers are different (higher) than cook-reported because
prompt tokens (system persona, market env, deal facts) are excluded.

```
                              records   loss       token_acc   per-bucket weakest
Atlas-70B (Llama 3.3, 70B)        996   1.1739     71.70%      ic_memo (1.58 / 71.4%)
Bookmaker-8B (Granite, 8B)        ─── pending consolidation + eval ──────────
Hack-Deed-Maker-3B (Gran, 3B)     ─── pending consolidation + eval ──────────
Atlas-Granite-30B (Gran, 30B)     ─── pending cook ──────────────
```

### Atlas-70B per-bucket detail (from post-cook assistant-only eval)

```
BUCKET                       RECORDS    TOKENS         LOSS      ACC
underwriting_calc                697   1,033,948     1.1579    71.64%
ic_memo                           75      15,260     1.5756    71.38%   ← weakest loss
comp_market                      189      39,156     1.4941    70.88%
other (lease extraction)          32       7,128     0.8560    85.48%   ← BEST · structured JSON
other (agent mode)                 3         631     1.3574    77.34%   (tiny sample)
─────────────────────────────────────────────────────────────────────────
TOTAL                            996   1,096,123     1.1739    71.70%
```

**Atlas excels** at structured JSON extraction (lease abstraction).
**Atlas struggles relatively** with narrative-heavy buckets (IC memos · comp/market analysis)
where answer-space entropy is higher. *The Granite-30B cook on Block-1-v2 should narrow the
narrative-bucket gap — the new corpus has 30K SwarmJudge CRE evaluation pairs and 95K
SwarmRefinery doctrine pairs that directly target this weakness.*

---

## Token accuracy on the holdout (the customer-felt metric)

```
                              step 200   step 400   step 600   step 800   step 1000   step 1177   final
Atlas-70B (Llama, 70B)        ?          ?          ?          ?          ?           ?           pending log parse
Bookmaker-8B (Granite, 8B)    77.65%     85.79%     86.90%     87.30%     87.45%      87.46%      87.46% ✓
Hack-Deed-Maker-3B (Gran, 3B) 75.17%     84.17%     85.64%     86.09%     86.27%      86.29%      86.29% ✓
```

(Atlas-70B token accuracy not directly logged at the same checkpoints; will
back-fill from final manifest review.)

---

## The strategic finding · LOCKED 2026-05-06

> **Granite-4.1-8B beats Llama-3.3-70B on the Royal Jelly CRE corpus.**
>
> At step 600, the 8B's eval loss of 0.4983 is below Atlas-70B's eventual best
> of 0.5018 (which the 70B reached at step 1000).
>
> By step 1177 (final), the 8B is at **0.467 — 0.035 below Atlas-70B's best.**
>
> Same data. Same recipe. **One-ninth the parameters. One-eighth the cook time.
> One-eighteenth the electrons.**

This is the empirical receipt for the Granite pivot decision made on the same
day the cooks launched. See `granite_pivot_2026_05.md` in our internal memory
for the strategic doctrine that follows from this finding.

---

## What this means for our product line

```
PRODUCT             BRAIN                                BACKED BY (eval evidence)
HACKER ($250)       Hack-Deed-Maker-3B (Granite 4.1)    86.29% token acc · 0.5383 final
HACKER-PRO ($599)   Bookmaker-8B (Granite 4.1)          87.46% token acc · 0.467 final · BEATS 70B
HACKER-AGX ($2K)    Atlas-Granite-30B (Granite 4.1)     LIVE · expected 0.40-0.45 / ~89% acc
Datacenter          Atlas-Granite-30B OR Atlas-70B       decided after 30B cook completes
```

**The IQ-vs-cost frontier is mathematically validated, not marketing.**

A $250 HACKER box delivers 86%+ token accuracy on broker-grade output. A $599
HACKER-PRO delivers 87%+. The customer-felt delta is ~1 percentage point —
invisible on routine underwriting tasks. That's the receipt for our pricing
tier story.

---

## Why we publish this

Three reasons.

1. **Auditability.** Every customer of Atlas OS — every brokerage CTO, every
   family-office counsel, every sponsor's diligence officer — can read this
   table and verify the substrate claim. The numbers are receipts, not
   marketing.

2. **Reproducibility.** The recipe + corpus + sha256 are all anchored. Any
   third party with access to the base models (all Apache 2.0 except Llama)
   could replicate within ~5% on the same hardware.

3. **Discipline.** "Verified · Vetted · Virtu" requires that we publish what
   actually happened, not what we wished happened. If a future cook does
   *worse* than we expected, the table stays honest. The standard isn't
   "looks good on paper" — it's "something we'd put our own name on."

---

## Pending fills (this doc updates as cooks land)

- [ ] Atlas-Granite-30B full trajectory (LIVE · ETA ~2026-05-08 07:00 UTC)
- [ ] Atlas-70B token accuracy back-fill from log parse
- [ ] Bookmaker-8B post-cook assistant-only eval
- [ ] Hack-Deed-Maker-3B post-cook assistant-only eval
- [ ] Final summary chart · fleet IQ-vs-cost frontier (after all 4 cooks land)

---

## Hardware-vs-cook-time receipt (the cost side of the frontier)

```
COOK                    HARDWARE              WALL-CLOCK   $/HOUR (electricity)*  TOTAL
Atlas-70B               2× PRO 6000 FSDP      73.57 hr     ~$0.50/hr peers        ~$37
Bookmaker-8B            1× RTX 5090            8.89 hr     ~$0.20/hr              ~$2
Hack-Deed-Maker-3B      1× RTX 5090            5.20 hr     ~$0.20/hr              ~$1.20
Atlas-Granite-30B       2× PRO 6000 FSDP      ~35 hr       ~$0.50/hr              ~$15-20

* Approximate · sovereign compute on owned silicon · power costs only ·
  excludes capex amortization.
```

The 8B Granite cook produced a model that beats the 70B Llama for **~$2 in
electrons.** That's the labor-business unit economics in microcosm.
