# AIOV Numeric Gate · Stage 2 Spec

The deterministic validator that sits between the cooked LLM (stage 1 · Bookmaker)
and the Tribunal (stage 3). Catches the bounded failure modes that LLMs produce
predictably under domain-specific number work.

**Locked: 2026-05-06 by Donovan after Session 3 of the Bookmaker-8B correction loop.**

---

## Why this exists

LLMs cooked on a CRE corpus produce broker-grade narrative but fail predictably on:

1. Cap-rate value-range direction (gets the inverse relationship backwards)
2. Refusal discipline under missing data (invents value when math is unsupported)
3. Recommendation cohere (states things that contradict its own arithmetic)
4. Source hierarchy collapses (averages T-12 / rent-roll / OM instead of using T-12)
5. Range sanity (implies absurd cap rates from mismatched asking + NOI)

These failures are **bounded** (a finite list) and **detectable** (each one is one
deterministic Python check). The Numeric Gate is the spreadsheet checker that sits
behind the model. Without it, AIOV cannot ship. With it, AIOV ships.

---

## Architecture

```
LLM draft → Numeric Gate validator → if PASS: forward to Tribunal (stage 3)
                                   → if FAIL: reroute to Bookmaker with specific
                                              correction prompt + retry (max 2 retries)
                                              → if still FAIL: hard reject + log
                                                              for human review
```

The validator is a Python module that:
- Parses every numeric claim in the LLM draft
- Re-computes against source inputs
- Verifies labels match definitions
- Verifies recommendation language is consistent with computed values
- Verifies refusal discipline when inputs are absent
- Returns `{passed: bool, errors: list, corrections: list}` for the next stage

---

## Validation rules

### Rule 1 · Cap-rate value-range direction

**For every value opinion that includes a cap-rate range and a value range:**

```python
# Given: cap_range = (cap_low, cap_high) where cap_low < cap_high
# Given: value_range = (value_low, value_high) where value_low < value_high
# Given: NOI

# CORRECT direction (must hold):
assert NOI / cap_low > NOI / cap_high          # lower cap → higher value
assert value_high == approx(NOI / cap_low)      # high end of value matches low cap
assert value_low  == approx(NOI / cap_high)     # low end of value matches high cap

# Tolerance: ±1% of computed value (rounding)
```

Failure → flag: `cap_direction_inverted`. Send back to LLM with: *"Your cap range
{cap_low}%-{cap_high}% should yield a value range of ${NOI/cap_high:,.0f} - ${NOI/cap_low:,.0f}.
Lower cap rate produces HIGHER value, higher cap rate produces LOWER value. Recompute."*

### Rule 2 · Missing data refusal

**Required-data presence check before allowing any value opinion:**

```python
REQUIRED_FOR_VALUE_OPINION = [
    "NOI" or "T-12 actual" or "T-3 annualized",     # must have at least one
    "rent_roll_complete",                            # full rent roll or explicit "stabilized"
    "expense_detail" or "operating_expense_total",   # at minimum total opex
]

if not all_present(REQUIRED_FOR_VALUE_OPINION):
    # NO value opinion allowed
    # NO recommended value
    # NO ask/floor
    # Output MUST be one of:
    #   - "INSUFFICIENT DATA · cannot validate ask"
    #   - "CONDITIONAL only on supplied data"
    #   - "HOLD pending [list missing inputs]"
    pass
```

Failure → flag: `refusal_discipline_violation`. The LLM produced a value/ask/proceed
when required inputs were missing. Reroute with: *"Required inputs missing:
{missing_list}. You acknowledged this. Therefore output MUST be 'INSUFFICIENT DATA'.
You may not produce a value opinion. Rewrite."*

### Rule 3 · Recommendation cohere

**The recommendation narrative must not contradict computed numbers in the same draft:**

```python
# Pull every numeric fact stated in the draft
# Pull every comparative claim in the recommendation section
# Cross-check

# Examples of failures we've seen:
#   Draft computes: implied_value = $16.32M, purchase_price = $14.20M
#   Recommendation: "implied value ($16.32M) < purchase price ($14.2M)"
#   FAIL: 16.32 > 14.20 · narrative contradicts computed numbers

# Check class:
for claim in extract_comparative_claims(recommendation):
    actual = lookup_in_computed_values(claim.subjects)
    if not claim.relationship_holds(actual):
        flag("recommendation_contradicts_arithmetic", claim)
```

Failure → flag: `recommendation_contradicts_arithmetic`. Send back with the specific
contradiction: *"Your recommendation claims X < Y but the computed values show X > Y.
Restate the recommendation consistent with the arithmetic in this draft."*

### Rule 4 · Source hierarchy

**When multiple sources for the same metric exist, the gate enforces the hierarchy:**

```
For NOI / income / cash flow:
  T-12 actual              = HIGHEST authority · use as primary
  T-3 annualized           = MEDIUM authority · use as run-rate confirmation
  Rent roll (current)      = MEDIUM authority · use as run-rate confirmation
  Broker OM / pro-forma    = LOWEST authority · marketing claim · do not use unless
                             reconciled against T-12 or rent roll

NEVER average across the hierarchy.
NEVER use OM number alone.
```

Failure → flag: `source_hierarchy_violated`. Reroute with: *"You used [OM number] as
primary when T-12 is available. Use T-12 as primary. Flag [OM number] as marketing
claim discrepancy if it diverges by >10% from T-12."*

### Rule 5 · Status enum

**Final recommendation status must be exactly one of:**

```python
ALLOWED_STATUSES = {
    "INSUFFICIENT-DATA",      # required inputs missing
    "REJECT",                 # deal does not pencil
    "HOLD",                   # waiting on specific information (specify)
    "PROCEED-TO-DILIGENCE",   # initial yes, full diligence required
    "CONDITIONAL-APPROVAL",   # approved subject to specific conditions (specify)
    "APPROVE",                # full approval
}
```

No other status strings allowed. "Maybe", "Looks good", "Worth a look", "Let's discuss"
all → flag: `non_canonical_status`.

### Rule 6 · Range sanity

**Implied cap rates from price + NOI must fall within asset-class bounds:**

```python
ASSET_CLASS_CAP_BOUNDS = {
    "multifamily":     (4.0, 8.5),
    "industrial":      (4.5, 8.0),
    "office":          (5.5, 12.0),    # post-2024 office is wide
    "retail_grocery":  (5.0, 8.5),
    "retail_strip":    (6.0, 10.0),
    "stnl_invest":     (5.0, 8.0),
    "stnl_credit":     (4.5, 6.5),
    "hospitality":     (6.0, 12.0),
    "self_storage":    (5.0, 8.0),
    "data_center":     (5.0, 8.5),
}

for value_opinion in draft:
    implied_cap = NOI / value_opinion
    bounds = ASSET_CLASS_CAP_BOUNDS[asset_class]
    if not bounds[0] <= implied_cap * 100 <= bounds[1]:
        flag("range_sanity_violation", implied_cap, bounds)
```

Failure → flag: `range_sanity_violation`. Reroute with: *"Your value opinion of ${X}
on NOI of ${Y} implies a {Z}% cap rate. {Asset class} caps in 2026 fall in
{bounds}. Reconsider value or check NOI."*

---

## Implementation notes

### Primary parser
- LLM output is structured against a known IC-memo template (defined in
  `atlasOS/templates/ic_memo_v1.md`)
- Numeric claims tagged via regex: `\$[\d,]+(?:,\d{3})*(?:\.\d+)?`, `\d+(?:\.\d+)?%`
- Cap-rate claims paired by proximity to value claims in the structured template
- Source claims tagged by phrasing: "T-12", "rent roll", "OM", "broker"

### Retry loop
- On any failure flag: send LLM back with a structured correction prompt that includes:
  - The specific failure class
  - The numeric claim that failed validation
  - The expected value or required behavior
- Max 2 retries per draft
- After 2 failed retries: hard reject, log to `aiov_gate_failures.jsonl` for human
  review and corpus addition (each failure becomes a training pair for v3)

### Logging
- Every gate pass logs: `{deal_id, draft_sha, gate_pass: bool, retries: int, latency_ms}`
- Hedera anchor (stage 5) parent-anchors the gate-pass receipt as part of provenance

### Versioning
- Numeric Gate ruleset is versioned (semver). Current: `v0.1.0` (this spec).
- Receipt at stage 5 includes `gate_version` so any audit can trace which ruleset
  validated which draft.

---

## What this is NOT

The Numeric Gate is **not** a second LLM judging the first one. That would just
relocate the failure. It's a **deterministic Python validator** with explicit rules
sourced from broker doctrine. The validator is auditable, reproducible, and
extensible to new failure classes as we identify them.

Future failure classes will surface from continued correction-loop sessions. Each
becomes a new rule. The ruleset grows. The cook stays the same.

---

## Why this is the moat

```
What anyone can replicate:
  - Fine-tune a 30B model on CRE pairs (the cook)
  - Bind it to a chat UI
  - Call it an AI underwriter

What only Swarm & Bee can replicate:
  - The Numeric Gate ruleset, calibrated by an actual broker who's closed $8B
  - The Tribunal rubrics, written from real IC-memo experience
  - The AIOV rendering format, calibrated by what brokerage clients trust
  - The Hedera anchoring that makes the receipt portable
  - The 5 stages running together, with each stage's failures caught by the next

The cooked LLM is one component. The product is the pipeline.
```

**Verified · Vetted · Virtu** — the V's only mean something when every numeric
claim has been re-checked by a deterministic component the broker himself wrote
the rules for.
