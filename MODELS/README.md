# MODELS · the Granite 4.1 family + companions

Per-model reference for every Granite-derived checkpoint we use across the
HACKER product line and the AtlasOS network.

---

## The full family

| Model | Params | License | Role | Cooked here? |
|---|---|---|---|---|
| `granite-4.1-3b-base` | 3B | Apache 2.0 | Pre-train output | No (we use instruct) |
| `granite-4.1-3b` | 3B | Apache 2.0 | **Hack-Deed-Maker base** · HACKER ($250) | ✓ in flight |
| `granite-4.1-8b-base` | 8B | Apache 2.0 | Pre-train output | No (we use instruct) |
| `granite-4.1-8b` | 8B | Apache 2.0 | **Bookmaker base** · HACKER-PRO ($599) | ✓ in flight |
| `granite-4.1-30b-base` | 30B | Apache 2.0 | Pre-train output | No (we use instruct) |
| `granite-4.1-30b` | 30B | Apache 2.0 | **Branch / candidate doctrine model** · HACKER-AGX ($2K) | ⏳ queued |
| `granite-docling-258M` | 258M | Apache 2.0 | **Document parser** (HACKER eyes) | No fine-tune (stock) |
| `granite-guardian-3.3-8b` | 8B | Apache 2.0 | **Safety classifier** (AIOV sidecar) | No fine-tune (stock) |

Plus stock companions (not Granite but in the runtime stack):

| Model | Params | License | Role |
|---|---|---|---|
| Whisper base | 74M | MIT | Speech-to-text · HACKER ears |
| Piper TTS | ~60M | MIT | Text-to-speech · HACKER mouth |

---

## How to use any Granite 4.1 model (basic inference)

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = "ibm-granite/granite-4.1-8b"  # or 3b · 30b · -base variants
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
model.eval()

chat = [
    {"role": "user", "content": "What is the cap rate of an STNL with $200K NOI at $3.5M ask?"}
]
prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
input_tokens = tokenizer(prompt, return_tensors="pt").to(model.device)
output = model.generate(**input_tokens, max_new_tokens=200)
print(tokenizer.batch_decode(output))
```

For tool-calling, structured output, multilingual use cases — see the per-model
docs in this dir.

---

## Architecture commonalities (Granite 4.1 family)

All three sizes share:

```
Decoder-only dense transformer
GQA (Grouped Query Attention) · efficient KV cache
SwiGLU MLP activation
RMSNorm
Rotary Position Embedding (RoPE)
Tied input/output embeddings    ← important for LoRA target_module selection
512K context window (with long-context extension)
~15T tokens pre-training (5-phase: pre-train · mid-train · long-context)
Native multilingual support (12+ languages including English · Arabic · German ·
   Spanish · French · Japanese · Portuguese · Czech · Italian · Korean · Dutch ·
   Chinese)
Native tool-calling format (OpenAI-compatible)
Native structured JSON output
RL-aligned post-training for instruct variants
```

Key per-size differences in the individual model docs (`granite-4.1-3b.md` etc).

---

## License summary

```
All Granite 4.1 models    Apache 2.0
Granite-Docling           Apache 2.0
Granite-Guardian          Apache 2.0
Whisper                   MIT
Piper TTS                 MIT
```

Clean for commercial use across the entire stack. The cooked LoRA adapters
on top of these models are proprietary to Swarm and Bee LLC — see
`atlasOS/CORPUS.md` and `atlasOS/MODELS.md` for the IP boundary.

---

## Disclosures

IBM publishes a 155-175KB JSON disclosure per model card at
`github.com/ibm-granite/granite-4.1-language-models/disclosures/`. Each
disclosure covers data sources, governance review, risk evaluation, and
compliance check. **This is the IBM-tier transparency standard.**

We mirror this pattern for our cooked adapters: every cook produces a
manifest with sha256s, recipe, eval results, and Defendable anchor. Customers
can audit IBM's base-model disclosure AND our adapter manifest to walk the
full provenance chain from pre-training to production deployment.

---

## File index

```
MODELS/
├── README.md                       this file
├── granite-4.1-3b.md               Hack-Deed-Maker base (HACKER $250)
├── granite-4.1-8b.md               Bookmaker base (HACKER-PRO $599)
├── granite-4.1-30b.md              Branch / candidate doctrine (HACKER-AGX $2K · next cook)
├── granite-docling-258M.md         Document parser (every HACKER tier · the eyes)
└── granite-guardian.md             Safety classifier (AIOV sidecar)
```

Individual model docs are added commit-by-commit. Initial commit ships this
README plus the three cook-relevant models (3B, 8B, 30B); Docling and Guardian
follow.
