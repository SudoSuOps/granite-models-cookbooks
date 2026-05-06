# Granite-4.1-3B · desk-edge brain · Hack-Deed-Maker base

The 3-billion-parameter dense decoder in the Granite 4.1 family. The base for
our **Hack-Deed-Maker** cook — the brain that ships inside every $250 HACKER
box at every brokerage Hack desk.

---

## Identity

```
Hugging Face        ibm-granite/granite-4.1-3b
Variant             instruct (RL-aligned post-training)
Base variant        ibm-granite/granite-4.1-3b-base (pre-train only)
License             Apache 2.0
Released            April 29, 2026
Disclosure          github.com/ibm-granite/granite-4.1-language-models/disclosures/granite_4.1_3b_disclosure.json
```

---

## Architecture

```
Type                Decoder-only dense transformer
Parameters          3B (verified ~3.4B effective)
Layers              40 (same as 8B · just smaller hidden)
Hidden size         2560
Attention heads     40
KV heads            8 (GQA 5:1 · slightly different ratio than 8B/30B's 4:1)
Head dim            64
MLP intermediate    8192
Vocab size          100,352 (same family vocab)
Activation          SwiGLU
Normalization       RMSNorm
Position encoding   RoPE
Context window      131,072 (128K)
Embedding tying     yes
Precision           BF16 native
```

---

## VRAM math (the desk-edge constraint matters here)

```
BF16 (training)         ~6 GB weights · LoRA adds ~1.5 GB · acts ~3-5 GB
                        Total ~10-15 GB · trivially fits 32GB RTX 5090

INT8 inference          ~3 GB weights · fits any 6GB+ GPU

INT4 Q4_K_M deployment  ~2.1 GB weights
                        Fits Jetson Orin Nano 8GB (HACKER $250 box)
                        Coexists with Granite-Docling (700MB) + Whisper (500MB) +
                        Piper (100MB) + framework overhead — total ~4.5 GB ·
                        leaves ~3.5 GB headroom on the 8 GB box
```

This VRAM math is what makes the $250 HACKER product line viable. The 3B at
INT4 is the largest brain that fits with vision (Docling) + audio (Whisper +
Piper) + memory (Honey ledger SQLite) all running concurrently on Orin Nano 8GB.

---

## Performance (Jetson Orin Nano 8GB · validated 2026-05-06)

Stock Granite-4.1-3B at Q4_K_M on `signal-edge-01` (our reference HACKER):

```
Cold load                ~5 sec
Warm latency (TTFT)      ~500 ms
Generation throughput    13.5 tok/s sustained
Prompt eval              ~400 tok/s
300-token answer         ~22 sec
500-token answer         ~37 sec
RAM peak (3B + Docling)  ~4.5 GB / 7.4 GB available
Power draw (estimated)   10-15W (within 25W max)
```

Live during a phone call, the model generates faster than a broker can read it.
That's the desk-edge experience we promise customers.

---

## Capabilities (per IBM benchmarks · 3B variant)

```
MMLU 5-shot                       67.02
MMLU-Pro 5-shot, CoT              49.83
BBH 3-shot, CoT                   75.83
AGI EVAL 0-shot, CoT              65.16
IFEval Avg                        82.30
GSM8K 8-shot                      86.88
HumanEval pass@1                  81.71
MBPP pass@1                       71.16
BFCL v3                           60.80
```

The 3B trades off frontier reasoning (GPQA 31.70 · MMLU-Pro 49.83) for
desk-edge runtime characteristics. **For our use case — daily broker-vocab
underwriting · cap rate / DSCR / IRR math · LOI drafting · pass-or-proceed
verdicts — these scores predict adequate-to-strong production performance.**

The actual eval on our corpus (next section) confirms it.

---

## Empirical receipt on Royal Jelly Block-0

Our Hack-Deed-Maker cook on this base · in flight as of 2026-05-06 · step 800
of 1177:

```
step       eval_loss     token_acc
────────────────────────────────────
   200     1.102         75.17%
   400     0.6559        84.17%
   600     0.5773        85.64%
   800     0.5487        86.09%   ← still cooking · cosine tail kicking in
  1000     pending
  1177     pending
```

**86% token accuracy on a 996-record fingerprint-disjoint broker holdout · at
$250 hardware.** That's the receipt for the HACKER pricing thesis. The gap
to the Bookmaker-8B at the same step is only ~1.21 percentage points —
smaller than the noise floor on most broker-grade output tasks.

---

## Cook reference

Documentation at `COOKS/hack-deed-maker-3b.md`. Recipe at
`atlasOS/recipes/hack-deed-maker-3b.yml`. Same Gold Standard as the 8B and 70B
cooks · single-GPU bf16 LoRA on RTX 5090 · ~5-6 hour cook.

```
Status              IN FLIGHT · step ~800/1177 · ETA ~18:30 UTC tonight
Deployed to         HACKER ($250 box) at Q4_K_M quant
Receipt             hack-deed-maker.defendable.eth/<id>
```

---

## Why this is the right size for the desk

The HACKER ($250) ships at Orin Nano 8GB. The 3B Q4_K_M is the largest brain
that fits with the full multimodal companion stack (Docling eyes · Whisper
ears · Piper mouth · Honey ledger memory · Defendable receipt module). Going
larger means dropping a companion. Going smaller means losing broker-grade
output quality.

**The 3B at INT4 is the floor of the production stack.** Below this size, the
desk-edge product story doesn't hold. Above this size, the $250 hardware tier
doesn't hold. The intersection is here.

That's why the 3B is the Hack-Deed-Maker brain. Architecture, not marketing.

---

## See also

- `COOKS/hack-deed-maker-3b.md` · our cook on this base
- `COOKS/eval-results.md` · live head-to-head trajectory
- `MODELS/granite-4.1-8b.md` · the same family at HACKER-PRO size
- `MODELS/granite-docling-258M.md` · the eyes that coexist with this brain on the box
- `atlasOS/PRODUCTS.md` · HACKER ($250) product positioning
- `atlasOS/hacker_box_atlasos_product.md` (memory) · the box that hosts this brain
