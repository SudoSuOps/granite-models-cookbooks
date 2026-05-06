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

## Session 3 · 2026-05-06 · 5-test batch · Numeric Gate doctrine locked

After Session 2 confirmed numeric-discipline absorption at the system-prompt layer,
Donovan ran a 5-test stress batch covering: cap-rate math under uncertainty, missing-
data refusal discipline, comp weighting numeric consistency, document conflict tribunal,
and multifamily category-leak detection.

**The big finding:** Bookmaker-8B fails *predictably*. Not like a hallucinating chatbot.
Like a junior analyst who knows the memo language but needs a spreadsheet checker sitting
behind it. **That predictability is what makes a deterministic Numeric Gate sufficient.**

### Test results matrix

```
TEST                                       VERDICT       FAILURE MODE
1. Dollar General retest (cap math)        FAIL          Cap-range value direction reversed +
                                                          weighted-cap arithmetic error +
                                                          risk-adjustment direction backwards
2. Missing NOI retail (refusal discipline) FAIL          Acknowledged missing data, then produced
                                                          value/ask/proceed anyway · violated refusal
3. Retail comp weighting (range math)      FAIL          Cap-rate range → value range direction
                                                          reversed (higher cap should give lower value)
4. Document tribunal (conflict adjud.)     PASS          Correct source hierarchy: T-12 > rent-roll > OM
                                                          Did NOT average · used T-12 as primary
                                                          (small typo: "TERRIBLIS" should be "TRIBUNAL")
5. Multifamily category-leak               MIXED         First-order math correct (cap, YOC, value-add)
                                                          BUT recommendation contradicted own numbers
                                                          ("$16.32M < $14.2M" — factually wrong)
```

### Three production blockers identified

```
BLOCKER 1 · Cap-rate value-range direction
  Model output:                Selected cap range 6.50%-6.75% → Value range $1.917M-$1.960M
  Correct math:                $132,000 / 0.0650 = $2,030,769  (lower cap → higher value)
                               $132,000 / 0.0675 = $1,955,556  (higher cap → lower value)
  So range:                    $1.96M - $2.03M  (NOT $1.917M-$1.960M)
  Failure class:               Direction error · the model has the formula but applies it inverted
  Root cause:                  Likely from training pairs that report cap-then-value as fixed
                               anchors rather than functional inverse relationship

BLOCKER 2 · Refusal under missing data
  Test setup:                  Retail asset · NOI missing · T-12 missing · partial rent roll
  Correct behavior:            "No defensible value opinion can be provided. Ask cannot be
                                validated without NOI/T-12/full rent roll. Recommendation:
                                HOLD / INSUFFICIENT DATA."
  Model output:                "VALUE: $8,900,000  RECOMMENDED VALUE: $8,900,000  ASK: $8,900,000
                                PASS/PROCEED: PROCEED" (after acknowledging missing inputs)
  Plus invented conditionals:  "If NOI is $2.5M+, value: $8.5M-$9.5M" → on $8.9M ask that's
                                a 28% cap rate. Numerically absurd.
  Failure class:               Refusal-discipline collapse under partial data + invented
                               conditional projections that fail sanity-check

BLOCKER 3 · Self-contradiction in recommendation
  Multifamily test computed:   Implied stabilized value = $16.32M
                               Purchase price          = $14.20M
  Recommendation said:         "Implied stabilized value ($16.32M) < purchase price ($14.2M)"
  Reality:                     $16.32M is GREATER than $14.20M
  Failure class:               The model's narrative layer contradicts its own arithmetic
                               output · no fact-check loop on its own numbers
```

### What WORKS · keep these strengths

```
1. CRE memo language          structure, vocabulary, recommendation calibration discipline
2. Document conflict tribunal Honey/Jelly/Propolis source hierarchy applied correctly
3. First-order ratios         going-in cap, stabilized YOC, debt service, cash-flow math
4. Calibrated recommendation  uses CONDITIONAL/PROCEED/HOLD/REJECT not just yes/no
5. Refusal of IRR             refused with enumerated missing inputs · the cleanest gate
```

### The architectural lock · Numeric Gate is mandatory

The 5-stage AIOV pipeline (locked in Session 2) becomes operationally specific:

```
1. Bookmaker drafts            LLM produces draft narrative + math
2. Numeric Gate                ← THIS SESSION · new spec drafted
   ├── cap-rate direction      lower cap MUST yield higher value (and vice versa)
   ├── missing-data refusal    no NOI/T-12/rent-roll = no value opinion
   ├── recommendation cohere   no statement contradicting own arithmetic
   ├── source hierarchy        T-12 > rent-roll > OM (no averaging)
   ├── status enum             only [PASS / REJECT / PROCEED-TO-DILIGENCE /
                                CONDITIONAL-APPROVAL / APPROVE / INSUFFICIENT-DATA]
   └── range sanity            implied cap rates must fall in plausible
                                asset-class bounds (e.g. retail 5-10% not 28%)
3. Tribunal validates          multi-judge eval scores draft+gate output
4. AIOV renders                customer-facing PDF/HTML, only after rails pass
5. Receipt anchors             Hedera-anchored Defendable receipt
```

Full Numeric Gate spec is in `COOKS/aiov-numeric-gate-spec.md` (Apache 2.0 · public).

### Why the failure shape matters

The Bookmaker-8B fails *predictably*. The errors are:
- **Bounded** (5 specific failure classes, not arbitrary hallucinations)
- **Detectable** (every error is a deterministic check away from validation)
- **Correctable** (Numeric Gate can flag and reroute for regeneration)

A model that fails arbitrarily is undeployable. A model that fails along a known
shape is a *component* — and we have a component spec.

### Verdict for the cook itself

```
SHIP-READY?                    Not yet · gated on Numeric Gate stage being built
COOK QUALITY?                  Strong · 87.46% / 80.17% holds up qualitatively
                               for narrative/structure/conflict/first-order math
RE-COOK NEEDED?                Not for these blockers · they're addressable
                               at gate layer (stage 2), not cook layer (stage 1)
NEXT CORPUS PASS?              Block-1-v3 should add ~500 pairs of the
                               *correct* cap-direction examples to harden
                               at training time too · belt and suspenders
30B IMPLICATIONS?              The 30B will likely have similar shape failures
                               but at lower frequency · same gate catches both
```

---

## Session 4 · 2026-05-06 · Hack-Deed-Maker-3B 8-test batch · ROLE REDEFINED

The 3B was tested with the same correction-loop discipline as the 8B (Sessions 1-3),
on a wider 8-test batch covering deed extraction, missing-data refusal, STNL cap math,
lease economics extraction, tribunal conflict, receipt metadata, legal-safe deed
explanation, and final consistency checking.

**The strategic finding:** the 3B is NOT a smaller version of the 8B for valuation.
It's a different tier entirely — an **intake brain**, not an underwriting brain.

### Test results matrix

```
TEST                                       VERDICT       NOTES
1. Deed/package extraction                 PARTIAL PASS  Fields extracted correctly · JSON
                                                          boundary failed (output polluted by
                                                          other answers mid-JSON)
2. Missing NOI refusal                     PASS          Correctly refused · used [x] checked
                                                          boxes (formatting fix needed)
3. STNL cap-rate math                      FAIL          Cap-direction reversed + ask/floor
                                                          unsupported by own cap range
4. Lease extraction JSON                   FAIL          ti_allowance_total = 45.0 (got the
                                                          $/PSF · should be 4,250 × $45 =
                                                          $191,250) · security_deposit = 2800
                                                          (should be $28,000)
5. Tribunal conflict source hierarchy      FAIL          INVERTED hierarchy:
                                                          said rent-roll=propolis · T-12=jelly
                                                          should be: T-12=HONEY · rent-roll=JELLY
                                                          · OM=PROPOLIS
                                                          Also misattributed $992K to rent roll
                                                          (was T-12)
6. Receipt metadata privacy                PASS          Clean · no address / NOI / tenant /
                                                          deal facts in receipt JSON · only
                                                          metadata · perfectly aligned with AIOV
                                                          public-receipt principle
7. Legal-safe deed explanation             PASS          "Special warranty guarantees only the
                                                          grantor's ownership period" · careful,
                                                          concise, did not overclaim
8. Final consistency checker               PARTIAL PASS  Caught draft cap-math failure correctly
                                                          but ended with "All components consistent"
                                                          AFTER saying draft failed · self-
                                                          contradiction in summary line
```

### Production blockers for 3B (DIFFERENT from the 8B blockers)

The 8B's failures (Session 3) were valuation-engine failures: cap direction · refusal
under data scarcity · self-contradiction in recommendations. The 3B has those same
failures PLUS unique-to-3B failures that disqualify it from valuation work entirely:

```
3B-SPECIFIC BLOCKERS · disqualify 3B from running valuation as primary

A. JSON BOUNDARY DISCIPLINE
   When asked for JSON only, 3B leaks surrounding text and may merge outputs from
   other tasks into one JSON. This is a structural output-format failure, not a
   numeric one. The 8B doesn't do this.

B. LEASE ECONOMICS NUMERIC EXTRACTION
   3B got TI allowance and security deposit wrong by ORDERS OF MAGNITUDE
   ($45 vs $191,250 · $2,800 vs $28,000). These are simple multiplications the
   8B handled correctly. Smaller capacity = less cross-attention to which
   number-with-units goes where.

C. SOURCE HIERARCHY DOCTRINE
   3B INVERTED the Royal Jelly tier hierarchy on the conflict-tribunal test:
   said rent-roll=propolis (lowest tier · marketing claim) when the doctrine is
   T-12=HONEY (highest), rent-roll=JELLY (medium), OM=PROPOLIS (lowest).
   The 8B passed this same test correctly. This is a doctrine-level memorization
   gap that's hard to fix at prompt-level alone — the model needs to be re-cooked
   with stronger source-hierarchy supervision.

D. SELF-CONTRADICTION IN SUMMARY LINES
   3B said "draft failed" then concluded "All components consistent." Same class
   of error the 8B has but at higher frequency in the 3B.

8B-INHERITED BLOCKERS · also present in 3B but at higher frequency
   - Cap-rate value-range direction (still reversed)
   - Ask/floor unsupported by own cap range
   - Refusal-discipline formatting (checked-box [x] looks like completed diligence)
```

### What the 3B PASSED — the new product role

```
A. RECEIPT METADATA · PRIVACY-CLEAN
   Built a clean receipt JSON with model name, parser, timestamps, request/response
   sizes, requestor wallet — and CRITICALLY zero deal facts. No address, no NOI,
   no tenant name. Perfectly aligned with the AIOV public-receipt principle.
   This is exactly what should anchor at aiov.defendable.eth/<deal_id> publicly.

B. LEGAL-SAFE DEED EXPLANATIONS
   "A special warranty deed guarantees the grantor only owned the property during
   the grantor's ownership — not before." Concise. Accurate. Does not overclaim.
   This is plain-English transaction explainer work · low downside · valuable to
   the broker's client at every tier.

C. MISSING-DATA REFUSAL DISCIPLINE
   Refused to value when NOI was missing. Listed the required diligence items.
   The discipline holds. Just needs formatting cleanup (unchecked bullets, not
   checked boxes that look like done-diligence).

D. PARTIAL DEED FIELD EXTRACTION
   Grantor, grantee, address, consideration, instrument-type all extracted right.
   Basic field-extraction is in scope. The JSON-boundary discipline needs a clamp
   but the underlying extraction works.
```

### The product reframe · 3B is INTAKE, not UNDERWRITING

**Old product framing (Sessions 1-2):**
```
HACKER ($250)       Hack-Deed-Maker-3B (Granite 4.1)    everyday underwriting brain
HACKER-PRO ($599)   Bookmaker-8B (Granite 4.1)          compositional narrative + IC memos
HACKER-AGX ($2K)    Atlas-Granite-30B                    branch-tier doctrine model
```

**New product framing (Session 4 lock):**
```
HACKER ($250)        Hack-Deed-Maker-3B (Granite 4.1)
                     INTAKE BRAIN · deed extraction · receipt metadata · legal-safe
                     explanations · missing-data refusal checklist
                     NOT a valuation engine · NOT a primary AIOV renderer

HACKER-PRO ($599)    Bookmaker-8B (Granite 4.1)
                     ANALYST BRAIN · AIOV first-pass valuation · lease economics ·
                     IC memo language · comp framing · narrative discipline
                     The valuation tier · runs against Numeric Gate before sealing

Numeric Gate         Stage 2 deterministic validator (mandatory before AIOV render)
                     The spreadsheet checker behind every memo · 6+ rules
                     See COOKS/aiov-numeric-gate-spec.md

Tribunal             Stage 3 multi-judge conflict adjudicator · honey/jelly/propolis
                     hierarchy enforced · seals the final AIOV before render

HACKER-AGX ($2K)     Atlas-Granite-30B (Granite 4.1)
                     PREMIUM TIER · doctrine model · escalation / second opinion /
                     IC review on hard deals · pending cook completion
```

### The locked taxonomy

```
HACKER-3B  collects and protects the deal.
Bookmaker-8B  values it.
The Numeric Gate  seals it.
Atlas-Granite-30B  reviews it on the hard ones.
Hedera  anchors the receipt.
```

That's the product. Five components. Each has a job a bigger or smaller component
shouldn't try to do.

### What this means for the cookbook & next cooks

```
NEXT 3B RE-COOK (deferred · not blocking ship)
  Cook on a corpus weighted toward INTAKE work:
    - deed/title field extraction (clean JSON-only output)
    - lease economic field extraction (with multiplication: RSF × PSF)
    - receipt metadata templates (privacy-clean by construction)
    - legal-safe transaction explainers (no overclaim discipline)
    - source hierarchy doctrine (HONEY > JELLY > PROPOLIS · explicit pairs)
    - missing-data refusal templates (unchecked bullet format)
  Skip valuation pairs for the 3B re-cook · leave that to the 8B / 30B.

NEXT 8B RE-COOK (deferred · not blocking ship)
  Cook on Block-1-v3 with valuation pairs that hit the 8B's specific blockers:
    - cap-rate value-range direction examples (~500 pairs)
    - missing-data refusal under partial data (~300 pairs)
    - recommendation-cohere fact-check examples (~300 pairs)
    - asset-class implied-cap sanity examples (~200 pairs)

CHAT UI v9 · 3B persona set rewrite
  Replace Underwriter / IC memo personas (which fail on 3B) with intake personas:
    - Deed Extractor (JSON-only output · no surrounding text)
    - Package Intake Classifier (deed / lease / OM / financials / other)
    - Receipt Metadata Builder (privacy-clean by construction)
    - Legal-Safe Transaction Explainer (special warranty · grant deed · estoppel)
    - Missing-Data Refusal (with proper unchecked bullet format)
  Disable Underwriter / IC memo on the 3B UI · banner says "route to Bookmaker-8B".

PIPELINE INTEGRATION
  AIOV pipeline now explicitly routes intake to 3B and valuation to 8B:

  customer uploads deal package
    → HACKER-3B (intake) classifies + extracts deed/lease/OM fields → JSON
    → router validates JSON-only output via deterministic gate
    → Bookmaker-8B (valuation) consumes structured fields + writes IC memo
    → Numeric Gate validates 8B output
    → Tribunal scores final draft against rubric
    → AIOV renders customer-facing PDF
    → Hedera anchors receipt at aiov.defendable.eth/<deal_id>
```

### Why this finding is more bullish than it sounds

The 3B not being the valuation brain is **good news** for the product, not bad:

```
1. The 3B has a CLEAN role · intake / extraction / receipts · which is exactly
   what every customer needs and what runs at $250 hardware.
2. The 8B's failure modes are bounded and Numeric-Gate-addressable. The 3B's
   failure modes were unbounded enough to disqualify it from valuation. Now that
   we know that, the 3B's job description is honest.
3. Pipeline tier-routing is now explicit: intake → 3B (cheap) · valuation → 8B
   (the brain) · review → 30B (premium). Each tier earns its slot.
4. The line "HACKER-3B collects and protects the deal · Bookmaker-8B values it ·
   the Numeric Gate seals it" is a one-sentence brand articulation that maps
   perfectly to the deployment architecture. Every word is a component with a
   defined responsibility.

The eval numbers said the 3B trails 8B by 1.92pp · which sounded like "almost
the same brain, smaller." Session 4 showed that 1.92pp lives precisely in the
shape of valuation work that disqualifies the 3B from valuation. Same number,
different meaning · which is exactly why the correction loop matters.
```

---

## Session 5 · 2026-05-06 · Bookmaker-8B deed extraction + missing-NOI refusal · ANALYST TIER LOCK

After Session 4 redefined the 3B as the intake brain, Donovan ran the same kind of
extraction + refusal tasks against the Bookmaker-8B to confirm whether the 8B actually
performs the analyst-tier work the 3B was disqualified from. The result: the 8B
materially outperforms the 3B on deed/package extraction AND on missing-data refusal
discipline.

### What the 8B passed (cleanly)

```
EXTRACTION
  ✓ Clean valid JSON object · no boundary leak (vs 3B's mid-JSON pollution)
  ✓ Grantor / grantee / parcel / consideration / instrument / county / date all correct
  ✓ Tenant / lease type / base rent / expiration / renewal options / exceptions captured
  ✓ All output well-formed and consumable by downstream pipeline stages

REFUSAL DISCIPLINE
  ✓ Refused to produce a hard value opinion without rent or NOI
  ✓ Correctly stated $3.8M asking price cannot be validated without income data
  ✓ Did not invent a value (the 3B's Session 4 failure mode)
  ✓ Refusal was structured and actionable, not just "I don't know"
```

### Minor issues · four new clamps for the 8B Bookmaker persona

```
ISSUE 1 · ZIP code dropping
  Output: address as "1840 Indiantown Road, Jupiter, FL"
  Required: address as "1840 Indiantown Road, Jupiter, FL 33458"
  Class: extraction completeness · ZIP is a required field for title/lender
         downstream consumers
  Clamp: "When extracting addresses, preserve EVERY address component including
         ZIP code. Do not abbreviate, normalize, or drop fields."

ISSUE 2 · Hypothetical scenarios when not asked
  Output: included "if NOI were $X, value would be $Y" speculation despite the
         user explicitly providing no NOI
  Required: refuse cleanly · do not generate hypothetical scenarios unless the
         user explicitly requests them
  Class: refusal-discipline scope creep · the model was right to flag missing
         data but then weakened the refusal by appending speculation
  Clamp: "If rent/NOI is missing, do NOT provide hypothetical value ranges
         unless the user EXPLICITLY requests them. State INSUFFICIENT-DATA and
         stop."

ISSUE 3 · Tenant credit rating asserted without source
  Output: stated tenant has BBB credit rating without that being in the source
         document
  Required: never assert specific credit ratings unless the source provides them
  Class: hallucination at the data-attribution boundary · invented a fact and
         attributed it to nothing
  Clamp: "Do NOT state exact tenant credit ratings (BBB / Baa2 / etc.) unless
         the rating is explicitly present in the source document."

ISSUE 4 · Wrong language for unverified credit
  Output: language asserting credit rather than recommending validation
  Required: use "validate tenant credit profile" not "the tenant has BBB credit"
  Class: tone discipline at intake · always recommend validation, never assert
         what hasn't been verified
  Clamp: "When the source doesn't provide a credit rating but credit assessment
         is relevant, write 'validate tenant credit profile via S&P/Moody's/Fitch'
         · do NOT assert a rating."
```

### What this session locks · the analyst-tier role for the 8B

Combined with Session 1-3 findings (numeric discipline, IRR refusal, source
hierarchy) and now Session 5 (extraction + refusal discipline), the 8B's full
job description in the AIOV pipeline is:

```
BOOKMAKER-8B · ANALYST TIER (HACKER-PRO $599)

EXTRACTION (Session 5)
  ✓ Detailed deed/title field extraction (with ZIP and all components preserved)
  ✓ Lease economics extraction (TI · security deposit · base rent · escalations)
  ✓ Operating statement parsing (T-12 NOI · OpEx detail · GEI)

VALUATION (Sessions 1-3)
  ✓ Going-in cap rate (T-12 NOI / purchase price)
  ✓ Stabilized yield-on-cost (stabilized NOI / all-in basis)
  ✓ Assumed Stabilized Valuation Cap Rate (when computing implied value)
  ✓ Exit/reversion cap (sale-year NOI / sale price · for IRR)
  ✓ DSCR · cash-on-cash · CapEx funding gap analysis

REFUSAL DISCIPLINE (Sessions 2-5)
  ✓ INSUFFICIENT-DATA when NOI/T-12/rent-roll missing
  ✓ Refusal to quote IRR without all model inputs
  ✓ No hypothetical scenarios when refusal is the answer
  ✓ No asserted credit ratings without source

IC MEMO LANGUAGE (Session 2)
  ✓ Structured Deal Summary / Sponsor / Property / Market / Underwriting / Debt /
    Risk / Recommendation sections
  ✓ Calibrated recommendation: APPROVE / CONDITIONAL / PROCEED-TO-DILIGENCE /
    HOLD / REJECT / INSUFFICIENT-DATA (no fuzzy phrasings)

CONFLICT TRIBUNAL (Session 1)
  ✓ Source hierarchy: T-12 = HONEY (highest) > T-3/rent-roll = JELLY > OM = PROPOLIS
  ✓ Never averages across the hierarchy
  ✓ Flags discrepancies between sources rather than silently picking one
```

### Locked product roles after Session 5

```
HACKER ($250 · 3B brain · "the cheap intake bee on the desk")
  intake · receipt metadata · basic deed summary · missing-data checklist
  package classification · legal-safe explainers
  NOT the analyst · NOT the extractor at production accuracy

HACKER-PRO ($599 · 8B brain · "the AIOV browser-side analyst")
  detailed extraction (deed + lease + OM) · lease economics · valuation ·
  AIOV pre-broker analysis · refusal discipline · IC memo drafting
  THE analyst tier · gated by Numeric Gate before AIOV render

(Stage 2) Numeric Gate
  cap-rate math direction · TI math · security deposit math · ask/floor support ·
  range sanity · status-enum compliance · recommendation cohere

(Stage 3) Tribunal
  conflict source hierarchy enforcement · honey/jelly/propolis grading · final seal

HACKER-AGX ($2K · 30B brain · COOK IN FLIGHT)
  premium escalation · second opinion · IC committee tier review
```

**The brand-locked tagline:**

> *"HACKER-3B is the cheap intake bee on the desk. Bookmaker-8B is the analyst
> brain in the browser. The Numeric Gate is the spreadsheet checker. Atlas-30B
> is the IC committee."*

That's the SKU stack. Each tier has a job a different bee was built to do.

### Why "the cheap intake bee on the desk" is the right framing

The original framing pitched the $250 HACKER as "underwriting brain in a small
box" — which sounded like a step DOWN from the $599 HACKER-PRO. The Session 4
correction-loop showed that framing was wrong (the 3B can't do underwriting).

The new framing pitches the $250 HACKER as "intake bee on every desk" — which
is a step UP for what every brokerage actually needs at the desk-edge:

```
Every broker desk needs intake automation:
  - Deal package arrives (PDF / images / lease + financials)
  - Classify documents · extract basic fields · build receipt · refuse if
    incomplete · hand off to the analyst tier with structured JSON
  - This is high-frequency, low-margin work · running on $250 hardware is the
    right cost structure
  - Every desk gets one · 4 brokers in an office = 4 boxes = $1,000 in hardware

The 8B / Bookmaker tier is the analyst brain that sits behind the intake bees.
You don't need one per desk · you need one per office (or in the datacenter).
The 3B feeds it pre-cleaned structured data, the analyst does the real work.

That's a brokerage office in a box. The desks have intake bees. The analyst
sits in the back office (or in the cloud). The committee (30B) reviews the
hard ones. Every layer earns its tier.
```

### Three sessions of receipts, three of strengths · the cooks know who they are

Five correction-loop sessions across two cooks have produced:
- 4 Bookmaker-8B sessions (1, 2, 3, 5) → analyst tier locked, 7 clamps applied
- 1 Hack-Deed-Maker-3B session (4) → intake tier locked, 5 personas defined

The cookbook now has both *what each cook does* AND *what each cook does NOT do*.
That's the receipt for shipping. **Cooks that know their job ship. Cooks that
think they do everything fail in production.**

---

## Append future sessions below

(Date · Persona tested · Prompt summary · What handled well · Clamps required ·
Cook-time fix proposed)
