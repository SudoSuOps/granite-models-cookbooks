#!/usr/bin/env python3
"""
Royal Jelly CRE · Block-1-v2 corpus builder · for Atlas-Granite-30B.

Block-1-v2 is the forward-looking cook corpus (2026 vintage):
  - KEEPS Block-0's 6 capital-markets sources (apples-to-apples on those buckets)
  - UPGRADES canonical_cre_volume (651K dedup) → cre_honey_volume (810K honey-graded · cap 120K)
  - NEW · stream_blockchain (5,046 RWA / Hedera / security tokens / DeFi-CRE)
  - NEW · swarmgrant_train (43,689 federal grants · OZ / NMTC / HUD / USDA / EDA / EB-5)
  - NEW · legal_consumer_stamped (9,160 lease / LOI / estoppel / tenant default)
  - NEW · creditsniper_train (79,910 → cap 30K · CRE credit + debt covenant)
  - PREMIUM · arc/honey + jelly + propolis (276 + 2,020 + 1,347 Royal Jelly graded)

Eval holdout = same 996 records as Block-0 (so eval is comparable across cooks).

Output:
  /data2/atlas-granite-30b/train.jsonl
  /data2/atlas-granite-30b/eval.jsonl   (copy from /data2/atlas-70b/eval.jsonl · same sha)
  /data2/atlas-granite-30b/MANIFEST_SLICE.json
"""
import json
import hashlib
import time
import glob
import os
import shutil
import random
from pathlib import Path

random.seed(42)

OUT_DIR = Path("/data2/atlas-granite-30b")
OUT_DIR.mkdir(parents=True, exist_ok=True)

EVAL_SOURCE = "/data2/atlas-70b/eval.jsonl"
EVAL_DEST = OUT_DIR / "eval.jsonl"
TRAIN_DEST = OUT_DIR / "train.jsonl"
MANIFEST = OUT_DIR / "MANIFEST_SLICE.json"

# Block-0 reference (for compares_to receipt)
BLOCK_0_TRAIN_SHA = "d63b05d9e36b0e0d1113ee2fcf9c4681dbb95133a44889319bf1df2f7ad90f39"
BLOCK_0_RECORDS = 125651

# Filters (same as Block-0)
JELLY_THRESHOLD = 75
MIN_MESSAGES = 2

SOURCES = [
    # ─────── TIER 1 · APEX DOCTRINE (smallest · highest signal · process first) ───────
    {"label": "signal_platinum",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/signal/signal_platinum_20260309.jsonl",
     "cap":   None,
     "category": "doctrine · SwarmCapitalMarkets institutional analyst · PLATINUM tier"},
    {"label": "board_member_500",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/grants/board_member_500.jsonl",
     "cap":   None,
     "category": "doctrine · strategic advisor to Swarm & Bee · governance"},

    # ─────── TIER 2 · DOCTRINE BACKBONE (the bee-hive corpus we missed) ───────
    {"label": "bee_hive_train_data",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/bee-hive/train_data.jsonl",
     "cap":   None,
     "category": "doctrine · SwarmRefinery · Defendable CCIR operational intelligence engine"},
    {"label": "judge_cre_30k",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/judge/judge_cre_30k.jsonl",
     "cap":   None,
     "category": "evaluation · SwarmJudge CRE · A/B/C grading · tool-calling discipline"},

    # ─────── TIER 3 · AGENT COORDINATION (tool calling reliability) ───────
    {"label": "bee_hive_agent",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/bee-hive/agent_train_v1.jsonl",
     "cap":   None,
     "category": "agent · SwarmAgent conductor · tool dispatch · multi-turn"},
    {"label": "bee_hive_router",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/bee-hive/router_train_v1.jsonl",
     "cap":   None,
     "category": "agent · router bee · arena dispatch · tool calling"},
    {"label": "bee_hive_scout",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/bee-hive/scout_train_v1.jsonl",
     "cap":   None,
     "category": "agent · scout bee · exploration · breadth"},
    {"label": "bee_hive_peeta",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/bee-hive/peeta_train_v1.jsonl",
     "cap":   None,
     "category": "agent · SwarmPeeta · 4B stabilizer · repair"},

    # ─────── TIER 4 · USER-REQUESTED NEW BUCKETS (blockchain · grants · legal) ───────
    {"label": "stream_blockchain",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/capital-markets/stream_blockchain.jsonl",
     "cap":   None,
     "category": "blockchain · RWA tokenization · Hedera · stablecoin settlement"},
    {"label": "swarmgrant_train",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/grants/swarmgrant_train.jsonl",
     "cap":   None,
     "category": "grants · OZ / NMTC / HUD / USDA / EDA / EB-5"},
    {"label": "legal_consumer_stamped",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/legal/legal_consumer_stamped_openrouter_20260317_111349.jsonl",
     "cap":   None,
     "category": "legal · lease / LOI / estoppel / tenant default · FDCPA debt defense"},
    {"label": "creditsniper_train",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/legal/creditsniper_train.jsonl",
     "cap":   30000,
     "category": "legal · CRE credit + debt covenant + IRAC reasoning"},

    # ─────── TIER 5 · FINANCE TRIO (CRE-credit depth) ───────
    {"label": "finance_creditor_collector",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/finance/creditor_collector_branching.jsonl",
     "cap":   None,
     "category": "finance · creditor vs debt collector branching logic"},
    {"label": "finance_debt_validation",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/finance/swarm_cooks_creditsniper_cook__debt_validation.jsonl",
     "cap":   None,
     "category": "finance · FDCPA debt defense strategist"},
    {"label": "finance_rating_agency",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/finance/swarm-honey_finance-propolis__propolis.jsonl",
     "cap":   None,
     "category": "finance · credit analyst at major rating agency · sovereign + corporate"},

    # ─────── TIER 6 · BLOCK-0 SMALL SPECIALTY (preserved · process before superset) ───────
    {"label": "maturity_wall_workflow",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/capital-markets/stream_debt_maturity.jsonl",
     "cap":   None},
    {"label": "macro_energy",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/capital-markets/stream_energy.jsonl",
     "cap":   None},
    {"label": "streams",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/capital-markets/swarmcapital_streams__shard_*.jsonl",
     "cap":   None,
     "multi_shard": True},

    # ─────── TIER 7 · BLOCK-0 MEDIUM CAPITAL MARKETS ───────
    {"label": "capital_markets_stamped",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/capital-markets/r2_capital_stamped.jsonl",
     "cap":   None},
    {"label": "capital_markets_neweconomy",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/capital-markets/r2_neweconomy_stamped.jsonl",
     "cap":   None},

    # ─────── TIER 8 · ATLAS-V1 FOUNDATION (large CRE superset · process late) ───────
    {"label": "atlas_v1_foundation",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/capital-markets/swarmcapitalmarkets_train.jsonl",
     "cap":   None},

    # ─────── TIER 9 · OCEAN · cre_honey_volume (810K → 120K cap · LAST) ───────
    {"label": "cre_honey_volume",
     "path":  "/mnt/swarm/swarm-and-bee-datasets/cre/cre_honey_stamped.jsonl",
     "cap":   120000,
     "replaces": "canonical_cre_volume (Block-0)"},

    # DROPPED from this build:
    # · arc/honey_pairs + jelly_pairs + propolis_pairs (ARC-AGI puzzle solver telemetry · wrong domain)
    # · bee-hive/instruction_following.jsonl (549K · too general · would dilute CRE specificity)
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fingerprint(rec):
    """Hash concatenated message contents for cross-source dedup."""
    msgs = rec.get("messages", [])
    parts = []
    for m in msgs:
        role = m.get("role", "")
        content = m.get("content") or ""
        parts.append(role + ":" + content[:5000])
    return hashlib.md5("\n".join(parts).encode("utf-8")).hexdigest()


def jelly_score(rec):
    """Pull a verification score if one exists. Returns None if absent."""
    for key in ("verification_score", "jelly_score", "rj_score"):
        if key in rec and isinstance(rec[key], (int, float)):
            return float(rec[key])
    meta = rec.get("metadata") or rec.get("meta") or {}
    if isinstance(meta, dict):
        for key in ("verification_score", "jelly_score", "rj_score"):
            if key in meta and isinstance(meta[key], (int, float)):
                return float(meta[key])
    return None


def main():
    t_start = time.time()
    print("=" * 80)
    print("  Royal Jelly CRE · Block-1-v2 build · for Atlas-Granite-30B")
    print("=" * 80)

    # 1. Read eval fingerprints (so we exclude any train record that matches)
    print("\n[1/4] Reading eval set fingerprints...")
    eval_fingerprints = set()
    with open(EVAL_SOURCE) as f:
        for line in f:
            line = line.strip()
            if line:
                eval_fingerprints.add(fingerprint(json.loads(line)))
    print(f"      {len(eval_fingerprints)} eval fingerprints loaded")

    shutil.copy(EVAL_SOURCE, EVAL_DEST)
    eval_sha = sha256_file(EVAL_DEST)
    print(f"      eval.jsonl copied · sha256 {eval_sha[:16]}...")

    # 2. Stream sources · filter · dedup · cap
    print("\n[2/4] Reading sources + filtering + dedup + cap...")
    seen_fingerprints = set(eval_fingerprints)
    sources_meta = []
    all_train_records = []

    for src in SOURCES:
        label = src["label"]
        cap = src.get("cap")

        if src.get("multi_shard"):
            paths = sorted(glob.glob(src["path"]))
        else:
            paths = [src["path"]]

        if not paths or not all(os.path.exists(p) for p in paths):
            print(f"      WARN  {label}: file(s) missing for {src['path']}")
            sources_meta.append({
                "label": label, "path": src["path"], "cap": cap,
                "raw_count": 0, "kept_after_cap": 0,
                "sha256": None, "error": "file_not_found",
            })
            continue

        raw_count = 0
        kept = []
        drop_dup = 0
        drop_score = 0
        drop_minmsg = 0
        drop_invalid = 0

        for p in paths:
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        drop_invalid += 1
                        continue
                    raw_count += 1

                    msgs = rec.get("messages", [])
                    if len(msgs) < MIN_MESSAGES:
                        drop_minmsg += 1
                        continue

                    score = jelly_score(rec)
                    if score is not None and score < JELLY_THRESHOLD:
                        drop_score += 1
                        continue

                    fp = fingerprint(rec)
                    if fp in seen_fingerprints:
                        drop_dup += 1
                        continue

                    seen_fingerprints.add(fp)
                    kept.append(rec)

        kept_after_filter = len(kept)
        if cap is not None and len(kept) > cap:
            random.shuffle(kept)
            kept = kept[:cap]

        if src.get("multi_shard"):
            h = hashlib.sha256()
            for p in paths:
                h.update(sha256_file(p).encode())
            source_sha = "multi-shard:" + h.hexdigest()[:32]
        else:
            source_sha = sha256_file(paths[0])

        sources_meta.append({
            "label": label,
            "path": src["path"],
            "shards": len(paths),
            "cap": cap,
            "raw_count": raw_count,
            "drop_invalid_json": drop_invalid,
            "drop_minmsg": drop_minmsg,
            "drop_score_below_75": drop_score,
            "drop_fingerprint_duplicate": drop_dup,
            "kept_after_filter_dedup": kept_after_filter,
            "kept_after_cap": len(kept),
            "sha256": source_sha,
            "category": src.get("category"),
            "replaces": src.get("replaces"),
        })

        cap_note = f" cap→{cap}" if cap else ""
        print(f"      {label:30s}  raw {raw_count:>7} | kept {len(kept):>6}{cap_note} | "
              f"drop dup {drop_dup} score {drop_score} minmsg {drop_minmsg}")

        for r in kept:
            r["_source_bucket"] = label
        all_train_records.extend(kept)

    # 3. Shuffle and write train.jsonl
    print("\n[3/4] Shuffling + writing train.jsonl...")
    random.shuffle(all_train_records)

    by_source = {}
    with open(TRAIN_DEST, "w") as f:
        for r in all_train_records:
            bucket = r.pop("_source_bucket", "unknown")
            by_source[bucket] = by_source.get(bucket, 0) + 1
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    train_sha = sha256_file(TRAIN_DEST)
    train_size_mb = TRAIN_DEST.stat().st_size / (1024 * 1024)
    print(f"      train.jsonl · {len(all_train_records):,} records · {train_size_mb:.1f} MB · sha256 {train_sha[:16]}...")

    # 4. Manifest
    print("\n[4/4] Writing MANIFEST_SLICE.json...")
    manifest = {
        "build": "Atlas-Granite-30B",
        "step": "slice",
        "block_version": "Block-1-v2",
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": round(time.time() - t_start, 2),
        "sources": sources_meta,
        "filters": {
            "jelly_threshold_verification_score": JELLY_THRESHOLD,
            "fingerprint_dedup": True,
            "min_messages": MIN_MESSAGES,
        },
        "train": {
            "path": str(TRAIN_DEST),
            "sha256": train_sha,
            "records": len(all_train_records),
            "size_mb": round(train_size_mb, 1),
            "by_source": by_source,
        },
        "eval": {
            "path": str(EVAL_DEST),
            "sha256": eval_sha,
            "records": len(eval_fingerprints),
            "note": "Same eval as Block-0 cooks (Atlas-70B / Bookmaker-8B / Hack-Deed-Maker-3B). Comparable across cooks.",
        },
        "compares_to_block_0": {
            "manifest_path": "/data2/atlas-70b/MANIFEST_SLICE.json",
            "block_0_train_sha256": BLOCK_0_TRAIN_SHA,
            "block_0_records": BLOCK_0_RECORDS,
            "delta_records": len(all_train_records) - BLOCK_0_RECORDS,
            "delta_pct": round(100 * (len(all_train_records) - BLOCK_0_RECORDS) / BLOCK_0_RECORDS, 1),
        },
        "doctrine": (
            "Block-1-v2 breaks corpus apples-to-apples with prior cooks but PRESERVES recipe + base apples-to-apples. "
            "The 30B cook is a forward-looking production-doctrine cook on 2026-vintage CRE corpus (blockchain · grants · "
            "legal layered on top of the proven Block-0 base). The 70B / 8B / 3B remain the substrate-comparison frontier "
            "on Block-0; the 30B is the production candidate."
        ),
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"      manifest written · {MANIFEST}")

    # Summary
    print()
    print("=" * 80)
    print(f"  BUILD COMPLETE · {time.time() - t_start:.1f}s")
    print("=" * 80)
    print(f"  train.jsonl:    {len(all_train_records):>7,} records · sha256 {train_sha[:32]}...")
    print(f"  eval.jsonl:     {len(eval_fingerprints):>7,} records · sha256 {eval_sha[:32]}...")
    print(f"  vs Block-0:     {len(all_train_records) - BLOCK_0_RECORDS:+,} records "
          f"({round(100 * len(all_train_records) / BLOCK_0_RECORDS, 1)}% of Block-0)")
    print(f"\n  Records by source bucket:")
    for bucket, count in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"    {bucket:30s} {count:>7,}")
    print()


if __name__ == "__main__":
    main()
