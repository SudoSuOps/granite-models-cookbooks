# Correction Loop Findings · Bookmaker-8B

What qualitative dev-tester sessions surface that loss curves don't.

The Bookmaker-8B (Granite-4.1-8B + Royal Jelly CRE Block-0 LoRA) post-cook eval
gave us 0.467 / 87.46% (cook methodology) and 0.7051 / 80.17% (assistant-only).
Those are the math receipts. The discipline of qualitative testing is asking
**which 12-20% the model is wrong about** — and whether that wrongness is the
kind a broker can live with.

This doc captures findings from live correction-loop sessions (Donovan dropping
real IC-memo prompts in the local chat UI, evaluating responses, giving the model
specific corrections, observing whether it absorbs them).

---

## Session 1 · 2026-05-06 · IC memo on a multifamily acquisition

### What the cook handled well

Self-corrected when given numeric discipline rules (no fighting back, no doubling
down on the wrong frame):

- Changed recommendation from over-confident *"Proceed with acquisition"* to
  measured *"Conditional approval — proceed to diligence"*
- Separated going-in cap rate from stabilized yield-on-cost (after correction)
- Identified the CapEx funding gap independently
- Required validation steps: rent comp validation, contractor bids,
  insurance/tax review, full 5-year cash-flow model

This is the broker-level judgment dial working. The model knows where the seams
between "approve" and "kill" sit, and holds the line when given specific rules.

### Three clamps required for the next cook (v2)

**Clamp 1 · Cap-rate vocabulary discipline**
- ❌ Currently: labels assumed exit / reversion / valuation cap as *"stabilized cap rate"*
- ✅ Required: three distinct terms with specific definitions
  - **Going-in cap rate** = trailing 12-month NOI ÷ purchase price (the entry yield)
  - **Stabilized yield-on-cost** = stabilized NOI ÷ all-in basis (purchase + CapEx + carry)
  - **Exit / reversion / valuation cap** = assumed cap at hold-period sale (an underwriting
    assumption, not a measured number)
- Cook-time fix: corpus pairs that force the model to use the right term in context

**Clamp 2 · Multifamily cash-flow modeling**
- ❌ Currently: applies lease-term framing (5-year, 7-year, NN) to multifamily flows
- ✅ Required: multifamily uses ANNUAL rent reset cycles · not lease-term cycles
  - Underwriting framework: T-12 actual → year-1 underwritten (with mark-to-market) →
    annual rent growth assumption → vacancy + concession allowance → operating expense
    growth → reversion cap × terminal NOI
  - The "lease term" on a multifamily property is a 12-month tenant lease, NOT
    a cash-flow modeling unit
- Cook-time fix: corpus pairs that demonstrate the per-asset-class cash-flow vocabulary
  (multifamily / office / industrial / retail / STNL / hospitality each have their
  own modeling conventions and the model needs to switch correctly)

**Clamp 3 · IRR without full model = refuse**
- ❌ Currently: produces an IRR estimate when key inputs are missing
- ✅ Required: refuse and enumerate the missing inputs
  - Required inputs for IRR: rent growth assumption · vacancy assumption · expense
    growth · CapEx schedule · debt terms (rate, amort, IO period, fees) · hold period
    · exit cap · transaction costs at sale · equity split (if JV)
  - Refusal template: *"Cannot quote IRR until the full model is built. Missing inputs:
    [enumerate]. Provide these and I'll run the model with explicit assumptions."*
- Cook-time fix: corpus pairs where the assistant explicitly refuses + lists missing
  inputs · rather than producing an unsupported IRR number

---

## How these findings feed downstream work

```
IMMEDIATE (chat-UI prompt-level clamps · before any re-cook)
  Add the three clamps to the "Underwriter" and "IC memo" persona system prompts.
  Test that prompt-level clamps catch the failure modes from Session 1.

NEAR-TERM (Block-1-v3 corpus additions for next 8B re-cook)
  ~500 pairs targeting cap-rate vocab discipline (3 terms, in-context use, mismatched
  scenarios where the model must pick the right one).
  ~500 pairs targeting per-asset-class cash-flow vocabulary (MF / office / industrial /
  retail / STNL / hospitality · each with its own modeling conventions).
  ~300 pairs targeting refusal-when-inputs-missing (IRR · cap rate at sale ·
  loan-sizing without DSCR target · sensitivity tables without sensitivity ranges).

POST-COOK EVAL (testing whether the next cook absorbed the clamps)
  Hold-out test prompts that specifically trigger each failure mode · score the
  response against a rubric (refused-correctly / used-right-term / used-right-modeling).
  This becomes a "doctrine eval" alongside the loss-curve eval.

INDEPENDENT ARTIFACT (this doc)
  Append every correction-loop session here as a dated entry. Each entry = the find,
  the requirement, the cook-time fix. Over time this becomes the operational doctrine
  document for the brokerage, not just for the AI cook.
```

---

## Why this matters more than another decimal place on eval_loss

A model that scores 0.467 but quotes IRR with no model is not deployable. A model
that scores 0.50 but refuses to quote IRR until inputs are present is. The eval
loss measures average next-token correctness · it doesn't measure whether the
model knows when to STOP.

The correction loop is how we measure judgment. Loss curves are how we measure
absorption. Both have to land for the cook to ship.

**Verified · Vetted · Virtu** — and the V's only mean something if a broker has
sat down with the model and confirmed it doesn't bluff.

---

## Append future sessions below

(Date · Persona tested · Prompt summary · What handled well · Clamps required ·
Cook-time fix proposed)
