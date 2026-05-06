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

## Session 2 · 2026-05-06 · Numeric Discipline Compliance Layer · PASSED

After Session 1's three clamps were applied at the system-prompt layer (chat UI v6 ·
Underwriter + IC memo personas), the same Bookmaker-8B was re-tested against a
72-unit garden-apartment acquisition memo: purchase price, current NOI, stabilized NOI,
debt service, and CapEx requirement provided as inputs.

### Test deal facts

```
72-unit garden apartment
Purchase price                  $9,400,000
Current (T-12) NOI               $548,000
Stabilized NOI                   $675,000
Debt service                     $436,200/yr
CapEx requirement                $750,000
Implied stabilized value         $11,250,000
```

### Passed checks

- ✅ **Going-in cap rate** computed correctly:
  $548,000 / $9,400,000 = **5.83%**
- ✅ **Stabilized yield-on-cost** computed correctly:
  $675,000 / $9,400,000 = **7.18%**
- ✅ **Assumed exit / valuation cap** computed correctly:
  $675,000 / $11,250,000 = **6.00%**
- ✅ **Annual cash flow before CapEx** computed correctly:
  $548,000 − $436,200 = **$111,800**
- ✅ **CapEx funding gap flagged correctly** as a red flag:
  $750,000 CapEx ÷ $111,800 annual cash flow = **6.7 years of current cash flow**
  → equity reserve call required, properly identified
- ✅ **Refused to compute IRR** due to missing assumptions:
  hold period · exit cap confirmation · cash-flow schedule · CapEx timing ·
  debt amortization · sale assumptions — all enumerated correctly in the refusal
- ✅ **Recommendation properly constrained**:
  *"Proceed to diligence — conditional approval"* (not approve · not reject)

### Verdict

**Numeric discipline compliance achieved.** The three clamps from Session 1 (cap-rate
vocabulary · multifamily cash-flow framing · IRR refusal pattern) were absorbed via
the system-prompt layer alone — no re-cook required.

### One remaining label clamp

The model wrote:
```
Stabilized Cap Rate (assumed): $675,000 NOI / $11,250,000 value = 6.00%
```

Mathematically fine, but the label "Stabilized Cap Rate" risks blending with
"stabilized yield-on-cost" in ambiguous prompts. Rename to:

```
Assumed Stabilized Valuation Cap Rate: $675,000 / $11,250,000 = 6.00%
```

This keeps four distinct terms in clean separation:

```
1. Going-in cap rate                       T-12 NOI / purchase price          (entry yield, measured)
2. Stabilized yield-on-cost                stabilized NOI / all-in basis      (return on invested cap, measured)
3. Assumed Stabilized Valuation Cap Rate   stabilized NOI / assumed stab val  (assumption used to compute implied value)
4. Exit / reversion cap                    sale-year NOI / sale price         (assumption used in IRR exit math)
```

The fourth-term distinction matters because Term 2 (yield-on-cost) and Term 3
(valuation cap) can be NUMERICALLY similar but are CONCEPTUALLY different:
- Yield-on-cost answers: *what return am I earning on every dollar I put in?*
- Valuation cap answers: *what cap rate am I assuming to compute the property's value?*

### Product implication

This Session 2 result locks the architecture for the **AIOV rendering pipeline**:

```
Bookmaker drafts        →  the cooked LLM generates draft narrative + math
Numeric rails clamp     →  deterministic check pass on every number / label
Tribunal validates      →  multi-judge eval scores the draft against rubrics
AIOV renders            →  customer-facing IC memo / valuation report
Receipt anchors         →  Hedera-anchored Defendable receipt for the output
```

**Bookmaker-8B can generate broker-grade IC memo language**, but the final AIOV
rendering must require a **deterministic numeric-discipline pass** before output is
sealed and receipt-anchored. The LLM produces the draft. The rails enforce the math.
The Tribunal scores the framing. AIOV renders the artifact. Hedera anchors the
receipt. Five distinct stages, five distinct responsibilities — and only the Bookmaker
is the LLM.

### Cook-time vs serve-time discipline

Session 2 confirms a doctrinal point: **clamps that work at the system-prompt layer
do not require a re-cook.** The 8B already has the underlying capability — it just
needed the right framing rules. We add the fourth-term clarification to the persona
prompts (no re-cook · ships immediately) and proceed.

The corpus pairs queued for Block-1-v3 (~1,300 pairs · cap-rate vocab + per-asset-class
cash flow + refusal patterns) become **defensive depth** rather than mandatory ·
worth doing for the v2 8B re-cook but not gating any current product release.

---

## Append future sessions below

(Date · Persona tested · Prompt summary · What handled well · Clamps required ·
Cook-time fix proposed)
