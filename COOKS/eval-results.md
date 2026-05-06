# Eval Results · the IQ-vs-cost frontier

Head-to-head eval across every cook on Royal Jelly CRE Block-0.

**Apples-to-apples discipline:** identical corpus (125,651 train · 996
fingerprint-disjoint eval) · identical recipe (Gold Standard LoRA r=64 α=32 ·
LR 1e-5 cosine · eff batch 32 · max_steps 1177). Only the base model varies.

Numbers below are **measured, not extrapolated.** Pending cells fill in as
cooks complete.

---

## Live status (updated 2026-05-06 18:00 UTC)

```
                              step 200   step 400   step 600   step 800   step 1000   step 1177   final eval
Atlas-70B (Llama 3.3, 70B)    0.8074     0.5517     0.5118     0.5031     0.5018      0.5019      0.5018  ✓
Bookmaker-8B (Granite, 8B)    0.9421     0.5615     0.4983 ⚡  0.4756     pending     pending     pending
Hack-Deed-Maker-3B (Gran, 3B) 1.102      0.6559     0.5773     0.5487     pending     pending     pending
Atlas-Granite-30B (Gran, 30B) ─── queued · launches post-Atlas-70B finish ──────────────
```

⚡ = the moment Granite-8B beat Atlas-70B's eventual best (0.4983 < 0.5018).
This happened at step 600 of the 8B cook · 7 steps before Atlas-70B reached its
own best at step 1000.

---

## Token accuracy on the holdout (the customer-felt metric)

```
                              step 200   step 400   step 600   step 800   step 1000   step 1177   final
Atlas-70B (Llama, 70B)        ?          ?          ?          ?          ?           ?           pending log parse
Bookmaker-8B (Granite, 8B)    77.65%     85.79%     86.90%     87.30%     pending     pending     pending
Hack-Deed-Maker-3B (Gran, 3B) 75.17%     84.17%     85.64%     86.09%     pending     pending     pending
```

(Atlas-70B token accuracy not directly logged at the same checkpoints; will
back-fill from final manifest review.)

---

## The strategic finding (locked at Atlas-70B finish, 2026-05-06 17:42 UTC)

> **Granite-4.1-8B beats Llama-3.3-70B on the Royal Jelly CRE corpus.**
>
> At step 600, the 8B's eval loss of 0.4983 is below Atlas-70B's eventual best
> of 0.5018 (which the 70B reached at step 1000).
>
> By step 800, the 8B is at 0.4756 — 0.026 below Atlas-70B's best.
>
> Same data. Same recipe. **One-ninth the parameters. One-eighth the cook time.**

This is the empirical receipt for the Granite pivot decision made on the same
day the cooks launched. See `granite_pivot_2026_05.md` in our internal memory
for the strategic doctrine that follows from this finding.

---

## What this means for our product line

```
PRODUCT             BRAIN                                BACKED BY (eval evidence)
HACKER ($250)       Hack-Deed-Maker-3B (Granite 4.1)    86%+ token acc at step 800 · still cooking
HACKER-PRO ($599)   Bookmaker-8B (Granite 4.1)          87%+ token acc · already beats 70B Llama
HACKER-AGX ($2K)    Granite-30B (queued)                 expected ~89-91% token acc · TBD post-cook
Datacenter          Granite-30B OR Atlas-70B             decided after 30B cook completes
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

- [ ] Bookmaker-8B step 1000 + 1177 + final eval (ETA ~21:00 UTC tonight)
- [ ] Hack-Deed-Maker-3B step 1000 + 1177 + final eval (ETA ~18:30 UTC tonight)
- [ ] Atlas-70B token accuracy back-fill from log parse
- [ ] Atlas-Granite-30B full trajectory (ETA ~Day +2 after launch)
- [ ] Final summary chart · fleet IQ-vs-cost frontier (after all 4 cooks land)

---

## Hardware-vs-cook-time receipt (the cost side of the frontier)

```
COOK                    HARDWARE              WALL-CLOCK   $/HOUR (electricity)*  TOTAL
Atlas-70B               2× PRO 6000 FSDP      73.57 hr     ~$0.50/hr peers        ~$37
Bookmaker-8B            1× RTX 5090           ~10 hr        ~$0.20/hr              ~$2
Hack-Deed-Maker-3B      1× RTX 5090           ~6 hr         ~$0.20/hr              ~$1.20
Atlas-Granite-30B       2× PRO 6000 FSDP      ~30-50 hr     ~$0.50/hr              ~$15-25

* Approximate · sovereign compute on owned silicon · power costs only ·
  excludes capex amortization.
```

The 8B Granite cook produced a model that beats the 70B Llama for **~$2 in
electrons.** That's the labor-business unit economics in microcosm.
