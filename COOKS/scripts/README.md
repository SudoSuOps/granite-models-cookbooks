# Atlas-Granite-30B · cook scripts

The three artifacts that build and run the Atlas-Granite-30B cook on
Royal Jelly CRE Block-1-v2.

```
build_block1_v2.py            Deterministic corpus builder · seed 42
                              · 19 sources tiered apex→ocean
                              · fingerprint dedup against eval set + cross-source
                              · Royal Jelly score filter (≥75)
                              · sha256 every source · MANIFEST_SLICE.json output
                              · ran in 78s · 407,076 train records produced

train_atlas_granite_30b.py    The cook itself · TRL 0.24 SFTTrainer
                              · LoRA r=64 α=32 · LR 1e-5 cosine
                              · 1177 steps · max_seq 4096 · eff batch 64
                              · save_steps 200 · save_total_limit 7
                              · NAS auto-mirror best-effort
                              · MANIFEST_COOK.json on completion

accelerate_fsdp_granite.yaml  FSDP config · 2× RTX PRO 6000 96GB
                              · transformer_layer_cls_to_wrap=GraniteDecoderLayer
                              · activation_checkpointing=true (replaces gradient_checkpointing)
                              · SHARDED_STATE_DICT (post-cook consolidation required)
```

---

## Run order

```bash
# 1. Build the corpus (~80s · once)
python3 build_block1_v2.py

# 2. Smoke test (--smoke-test · 20 steps · 500/50 slice · ~25 min)
accelerate launch \
  --config_file accelerate_fsdp_granite.yaml \
  train_atlas_granite_30b.py --smoke-test

# 3. Full cook (1177 steps · ~35h · 30B base on Block-1-v2)
accelerate launch \
  --config_file accelerate_fsdp_granite.yaml \
  train_atlas_granite_30b.py

# 4. Post-cook consolidation (FSDP-shard → standard PEFT format)
#    See atlasOS/scripts/consolidate_atlas_lora.py · adapt for the 30B path
python3 consolidate_atlas_lora.py \
  --shard /data2/atlas-granite-30b/lora-adapter \
  --out   /data2/atlas-granite-30b/consolidated-adapter
```

---

## TRL 0.24 / transformers 5.5 reconciliation notes

The cook script was originally cribbed from the Atlas-70B Llama cook (which ran on
TRL 0.20 and transformers 4.53). Six smoke iterations were needed to bring it up
to the current stack. The lessons in case you're cooking on a different stack:

```
1. SFTConfig · max_seq_length renamed to max_length (TRL 0.20 → 0.24)
2. SFTConfig · save_safetensors removed (now default · not configurable)
3. SFTConfig · gradient_checkpointing default flipped to True (TRL 0.24)
4. transformers 5.5+ · enforces "pick one" between fsdp activation_checkpointing
   and trainer gradient_checkpointing · setting both raises ValueError
5. FSDP2 · backward_prefetch unsupported (warning only · ignored)
6. HF datasets · heterogeneous schema across source files causes pa_table cast
   failures · MUST strip records to {"messages": [...]} only before training
```

The smoke logs at `/data2/atlas-granite-30b/smoke_v{1..6}_*.log` on swarmrails
are preserved as the receipt for each fix.

---

## Granite-specific things to know

```
1. FSDP transformer wrap class      GraniteDecoderLayer (NOT LlamaDecoderLayer)
2. tie_word_embeddings              true → exclude embed/lm_head from LoRA targets
3. init_method                      mup (Maximum Update Parameterization)
4. Architectural multipliers        attn 0.0078125 · resid 0.175 · embed 12.0 · logits 16.0
                                    (read automatically from config.json by HF transformers)
5. bos_token_id == eos_token_id     100257 → don't manually prepend BOS · apply_chat_template handles
6. rope_theta                       50,000,000 (128K context capable)
7. vocab_size                       100,352
8. Chat template tokens             <|start_of_role|>system<|end_of_role|> ... <|end_of_text|>
                                    <tool_call>...</tool_call> for tool dispatch
```

---

## Receipt sha256s (for reproducibility)

```
build_block1_v2.py      run 2026-05-06 19:35 UTC · seed 42
train.jsonl             4d90e676442738c4...  407,076 records · 2.17 GB
eval.jsonl              7f025a264210174a...  996 records · 6.3 MB · IDENTICAL to Block-0
config.json (base)      384f1935366f0b0f...  ibm-granite/granite-4.1-30b
tokenizer.json (base)   e2bad66439538cb4...
chat_template.jinja     fed2756d2d24e127...
```

All of these are pinned in `/data2/atlas-granite-30b/MANIFEST_SLICE.json` on swarmrails.
