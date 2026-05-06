# Cooks · our training runs on Royal Jelly CRE Block-0

The actual cooks. Recipes, hardware, eval numbers, manifests, anchors.

**The rule:** same corpus (Royal Jelly CRE Block-0) · same recipe (Gold Standard
LoRA r=64 α=32 · LR 1e-5 cosine · eff batch 32 · max_steps 1177) · same eval
holdout (996 fingerprint-disjoint records). Only the base model changes.
*That's how we know what we got — apples-to-apples.*

---

## Status as of 2026-05-06 18:00 UTC

| Cook | Base | Hardware | Status | Final eval | Notes |
|---|---|---|---|---|---|
| **Atlas-70B** | Llama-3.3-70B-Instruct | 2× PRO 6000 FSDP | ✓ COMPLETE | **0.5018** | 73.57h cook · the Llama comparator |
| **Bookmaker-8B** | Granite-4.1-8B | 1× RTX 5090 | in flight (step ~800) | 0.4756 @ 800 (best yet) | already beat 70B at step 600 |
| **Hack-Deed-Maker-3B** | Granite-4.1-3B | 1× RTX 5090 | in flight (step ~800) | 0.5487 @ 800 | desk-edge brain · 86% token acc |
| **Atlas-Granite-30B** | Granite-4.1-30B | 2× PRO 6000 FSDP | QUEUED · post-Atlas | TBD | next cook · launches when swarmrails frees |

See `eval-results.md` for the full head-to-head trajectory across all checkpoints.

---

## The four-cook fleet pattern

The four cooks together form a complete IQ-vs-cost frontier on identical data:

```
                        params      cook time     hardware              role
Hack-Deed-Maker-3B       3B          ~6 hr         RTX 5090 single GPU   HACKER ($250 box) · daily desk underwriting
Bookmaker-8B             8B          ~10 hr        RTX 5090 single GPU   HACKER-PRO ($599 box) · OS-tier reasoning
Atlas-Granite-30B        30B         ~30-50 hr     2× PRO 6000 FSDP      HACKER-AGX ($2K) · candidate doctrine model
Atlas-70B                70B         73.57 hr      2× PRO 6000 FSDP      Llama comparator · current doctrine (under review)
```

When the 8B and 3B finish (tonight) we have 3 of 4 cooks landed. The 30B cook
is the final piece · once it lands, we have a 4-point measured curve and the
strategic decision on which model becomes the production doctrine model.

---

## What's in each cook doc

Per-cook docs in this directory follow a fixed template:

```
1. Identity              name · base model · status · location of artifacts
2. The recipe            full hyperparameters · why these choices · YAML link
3. The data              corpus reference · sha256s · diversity stats
4. The hardware          GPUs · sharding strategy · power · time
5. The trajectory        eval at every checkpoint · loss + token_acc
6. The manifest          path · sha256 · Hedera anchor · subdomains
7. The deployment        how this cook gets served · which HACKER tier · what role
8. Notes                 anything operational learned during the cook
```

This template makes every cook auditable and reproducible.

---

## File index

```
COOKS/
├── README.md                    this file
├── atlas-70b.md                 Llama-3.3-70B-Instruct + Royal Jelly Block-0 · COMPLETE
├── bookmaker-8b.md              Granite-4.1-8B + Royal Jelly Block-0 · in flight
├── hack-deed-maker-3b.md        Granite-4.1-3B + Royal Jelly Block-0 · in flight
├── atlas-granite-30b.md         Granite-4.1-30B + Royal Jelly Block-0 · queued (next)
└── eval-results.md              head-to-head trajectory · the IQ-vs-cost frontier
```

---

## Why we cook on the same corpus every time

Donovan's directive (2026-05-06):

> *"We cook Granite 30B on the same datasets we cooked Llama-70B on — that's
> how we know what we got the full cook."*

Variable isolation. If we change the corpus AND the base model, we can't
attribute the difference to either. By holding the corpus + recipe constant
across the family scaling curve, every cook is a clean controlled experiment
on **base model substrate quality**. That's the experiment that matters for
substrate selection.

The Royal Jelly CRE Block-0 corpus itself is documented at
`atlasOS/CORPUS.md` (in our `atlasOS` repo). Sha256 anchors:

- train.jsonl: `d63b05d9e36b0e0d1113ee2fcf9c4681dbb95133a44889319bf1df2f7ad90f39`
- eval.jsonl:  `7f025a264210174a75c5bad30c5f255011e133272ed33a1917798b3085f075cc`

Block-1 (vertical Hack pairs) and Block-2 (distress-cycle) are in queue but
not used for substrate-comparison cooks. Those will be specialization cooks
on top of the substrate winner.
