#!/usr/bin/env python3
"""
Atlas-Granite-30B · cook script · Royal Jelly CRE Block-1-v2.

Same Gold Standard recipe as Atlas-70B / Bookmaker-8B / Hack-Deed-Maker-3B:
  LoRA r=64 alpha=32 · LR 1e-5 cosine · eff batch 32 · max_steps 1177 · max_seq 4096.

Granite-specific changes vs the 70B Llama cook:
  - base path           → /data2/granite-4.1-30b
  - FSDP wrap class      → GraniteDecoderLayer (set in accelerate_fsdp_granite.yaml)
  - target_modules       → exclude embed/lm_head (tied weights)
  - tokenizer chat       → apply_chat_template (handles BOS quirk · bos==eos)

Hardware:
  swarmrails 2× RTX PRO 6000 Blackwell 96GB · FSDP_FULL_SHARD · sharded state dict.

Launch:
  accelerate launch \\
    --config_file /data2/atlas-granite-30b/scripts/accelerate_fsdp_granite.yaml \\
    /data2/atlas-granite-30b/scripts/train_atlas_granite_30b.py [--smoke-test]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer

# ─────────────────────────────────── PATHS ───────────────────────────────────
BUILD_DIR = Path("/data2/atlas-granite-30b")
BASE_PATH = "/data2/granite-4.1-30b"
TRAIN_FILE = BUILD_DIR / "train.jsonl"
EVAL_FILE = BUILD_DIR / "eval.jsonl"
OUT_DIR = BUILD_DIR / "lora-adapter"
HEARTBEAT = Path("/tmp/atlas-granite-30b.heartbeat")
NAS_MIRROR = Path("/mnt/swarm/model_archives/atlas-granite-30b")  # optional · auto-skipped if NAS unavailable

# ─────────────────────────────────── RECIPE ───────────────────────────────────
# IDENTICAL to Atlas-70B / Bookmaker-8B / Hack-Deed-Maker-3B (apples-to-apples on recipe)

LORA_R = 64
LORA_ALPHA = 32
LORA_DROPOUT = 0.0
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
# Note: NOT including embed_tokens / lm_head because Granite has tie_word_embeddings=true.
# A LoRA adapter on tied embeds would create a double-LoRA conflict on save/load.

LEARNING_RATE = 1.0e-5
LR_SCHEDULER_TYPE = "cosine"
WARMUP_RATIO = 0.05
WEIGHT_DECAY = 0.01

PER_DEVICE_BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 32        # eff_batch = 2 procs × 1 × 32 = 64
MAX_STEPS = 1177             # apples-to-apples with 70B/8B/3B
MAX_SEQ_LEN = 4096

EVAL_STEPS = 200
SAVE_STEPS = 200
SAVE_TOTAL_LIMIT = 7
SEED = 42


def heartbeat(state):
    HEARTBEAT.write_text(
        f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {state}\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true",
                        help="Tiny slice + 20 steps to validate pipeline before real cook")
    args = parser.parse_args()

    is_smoke = args.smoke_test
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    heartbeat("starting")

    print(f"\n{'=' * 80}")
    print(f"  Atlas-Granite-30B · Royal Jelly CRE Block-1-v2")
    print(f"  base: {BASE_PATH}")
    print(f"  recipe: LoRA r={LORA_R} α={LORA_ALPHA} · LR {LEARNING_RATE} cosine · "
          f"eff batch 64 · max_steps {MAX_STEPS} · max_seq {MAX_SEQ_LEN}")
    if is_smoke:
        print(f"  *** SMOKE TEST · 20 steps · 500 train / 50 eval ***")
    print(f"{'=' * 80}\n", flush=True)

    # 1. Tokenizer
    print("[1/6] Loading tokenizer...", flush=True)
    tok = AutoTokenizer.from_pretrained(BASE_PATH)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    print(f"      vocab_size={tok.vocab_size} · pad={tok.pad_token_id} · "
          f"bos={tok.bos_token_id} · eos={tok.eos_token_id}", flush=True)

    # 2. Datasets · stream from JSONL
    print("[2/6] Loading datasets...", flush=True)
    train_ds = load_dataset("json", data_files=str(TRAIN_FILE), split="train")
    eval_ds = load_dataset("json", data_files=str(EVAL_FILE), split="train")
    if is_smoke:
        train_ds = train_ds.select(range(min(500, len(train_ds))))
        eval_ds = eval_ds.select(range(min(50, len(eval_ds))))
    print(f"      train: {len(train_ds):,} · eval: {len(eval_ds):,}", flush=True)

    def format_chat(example):
        msgs = example["messages"]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
        return {"text": text}

    train_ds = train_ds.map(format_chat, remove_columns=train_ds.column_names)
    eval_ds = eval_ds.map(format_chat, remove_columns=eval_ds.column_names)

    # 3. Base model · BF16 · FSDP-managed
    print("[3/6] Loading base model in BF16 · FSDP will shard across 2 cards...", flush=True)
    t = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        BASE_PATH,
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
        use_cache=False,                              # required when grad checkpointing on
    )
    model.config.use_cache = False
    print(f"      base loaded · {time.time() - t:.1f}s", flush=True)

    # Sanity-check tied embeddings
    if getattr(model.config, "tie_word_embeddings", False):
        print(f"      tie_word_embeddings=True (confirmed) · LoRA targets exclude embed/lm_head", flush=True)

    # 4. LoRA adapter
    print("[4/6] Attaching LoRA adapter...", flush=True)
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        target_modules=LORA_TARGET_MODULES,
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    trainable, total = 0, 0
    for p in model.parameters():
        total += p.numel()
        if p.requires_grad:
            trainable += p.numel()
    print(f"      trainable: {trainable:,} / {total:,} ({100 * trainable / total:.3f}%)", flush=True)

    # 5. SFT config + trainer
    print("[5/6] Building trainer...", flush=True)
    sft = SFTConfig(
        output_dir=str(OUT_DIR),
        num_train_epochs=1,                            # max_steps takes precedence
        max_steps=20 if is_smoke else MAX_STEPS,
        per_device_train_batch_size=PER_DEVICE_BATCH_SIZE,
        per_device_eval_batch_size=PER_DEVICE_BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,
        gradient_checkpointing=False,                  # FSDP YAML handles activation checkpointing
                                                       # · TRL 0.24 default is True · must explicitly disable
        learning_rate=LEARNING_RATE,
        lr_scheduler_type=LR_SCHEDULER_TYPE,
        warmup_ratio=WARMUP_RATIO,
        weight_decay=WEIGHT_DECAY,
        optim="adamw_torch",
        bf16=True,
        max_length=MAX_SEQ_LEN,                        # TRL 0.24 renamed from max_seq_length
        dataset_text_field="text",
        completion_only_loss=False,                    # match prior cooks' methodology (whole-seq loss · cook-canonical)
        eval_strategy="steps",
        eval_steps=10 if is_smoke else EVAL_STEPS,
        save_strategy="steps",
        save_steps=10 if is_smoke else SAVE_STEPS,
        save_total_limit=SAVE_TOTAL_LIMIT,
        logging_steps=5 if is_smoke else 25,
        report_to="none",
        seed=SEED,
        data_seed=SEED,
        dataloader_num_workers=2,
        remove_unused_columns=False,
        ddp_find_unused_parameters=False,
        # save_safetensors removed in TRL 0.24 · safetensors is the default and not configurable
    )

    trainer = SFTTrainer(
        model=model,
        args=sft,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        processing_class=tok,
    )

    # 6. Cook
    print(f"[6/6] Cooking · {'smoke 20 steps' if is_smoke else f'full {MAX_STEPS} steps'}...", flush=True)
    heartbeat("cooking")
    t_cook = time.time()
    trainer.train()
    cook_elapsed = time.time() - t_cook

    # Save final adapter
    print(f"\n  cook elapsed: {cook_elapsed / 3600:.2f}h", flush=True)
    print(f"  saving adapter to {OUT_DIR}...", flush=True)
    trainer.save_model(str(OUT_DIR))
    heartbeat("done" if not is_smoke else "smoke-done")

    # NAS mirror (best-effort)
    try:
        if NAS_MIRROR.parent.exists():
            print(f"  mirroring to NAS at {NAS_MIRROR}...", flush=True)
            NAS_MIRROR.mkdir(parents=True, exist_ok=True)
            os.system(f"rsync -a {OUT_DIR}/ {NAS_MIRROR}/")
            print(f"  NAS mirror complete", flush=True)
    except Exception as e:
        print(f"  WARN · NAS mirror skipped: {e}", flush=True)

    # Manifest stamp
    manifest = {
        "build": "Atlas-Granite-30B",
        "step": "cook",
        "block_version": "Block-1-v2",
        "smoke_test": is_smoke,
        "base": BASE_PATH,
        "out_dir": str(OUT_DIR),
        "recipe": {
            "lora_r": LORA_R,
            "lora_alpha": LORA_ALPHA,
            "target_modules": LORA_TARGET_MODULES,
            "learning_rate": LEARNING_RATE,
            "lr_scheduler": LR_SCHEDULER_TYPE,
            "warmup_ratio": WARMUP_RATIO,
            "max_steps": 20 if is_smoke else MAX_STEPS,
            "max_seq_len": MAX_SEQ_LEN,
            "per_device_batch_size": PER_DEVICE_BATCH_SIZE,
            "gradient_accumulation_steps": GRAD_ACCUM_STEPS,
            "effective_batch_size": 2 * PER_DEVICE_BATCH_SIZE * GRAD_ACCUM_STEPS,
        },
        "cook_elapsed_hours": round(cook_elapsed / 3600, 3),
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    manifest_path = BUILD_DIR / ("MANIFEST_SMOKE.json" if is_smoke else "MANIFEST_COOK.json")
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"  manifest: {manifest_path}", flush=True)
    print(f"\n  DONE", flush=True)


if __name__ == "__main__":
    main()
