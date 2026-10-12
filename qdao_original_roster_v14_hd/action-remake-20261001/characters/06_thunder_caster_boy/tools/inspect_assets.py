#!/usr/bin/env python3
"""Read-only PNG/provenance audit for 06; only the JSON report is written.

Usage: python tools/inspect_assets.py [--stdout] [--strict]
Default report: review/technical.json. No PNG is generated or modified.
Declared native dimensions are evidence claims, never inferred from export size.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "run": {"directions": ("N", "NE", "E", "SE", "S", "SW", "W", "NW"), "count": 16, "duration_ms": 60},
    "hit": {"directions": ("E", "W"), "count": 6, "duration_ms": 40},
    "attack": {"directions": ("E", "W"), "count": 12, "duration_ms": 30},
    "cast": {"directions": ("E", "W"), "count": 16, "duration_ms": 45},
}
NATIVE_KEYS = {
    "native",
    "nativesourcedimensions", "nativedimensions", "nativesize",
    "nativeframesize", "nativeframesizedimensions", "nativeinputsize",
    "nativeinputdimensions", "originaldimensions", "originalsize",
    "nativeperslotdimensions", "nativeperframedimensions",
}
SOURCE_KEYS = {"derivedfrom", "sources", "source", "sourcereferences", "sourcefiles"}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def normalize(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def dimensions(value) -> list[int] | None:
    if isinstance(value, (list, tuple)) and len(value) == 2:
        if all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in value):
            return list(value)
    if isinstance(value, dict):
        return dimensions([value.get("width"), value.get("height")])
    return None


def named_values(value, accepted: set[str], prefix: str = "") -> list[dict]:
    """Retain JSON locations so differently shaped generation records remain auditable."""
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            location = f"{prefix}.{key}" if prefix else key
            if normalize(key) in accepted:
                found.append({"json_field": location, "value": child})
            found.extend(named_values(child, accepted, location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(named_values(child, accepted, f"{prefix}[{index}]"))
    return found


def load_records(paths: list[Path]) -> dict[str, dict]:
    records = {}
    for path in paths:
        item = {"path": relative(path), "sha256": None, "issues": []}
        try:
            item["sha256"] = digest(path)
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(payload, dict):
                raise ValueError("generation record must be a JSON object")
            item["data"] = payload
            item["native_dimensions_claims"] = named_values(payload, NATIVE_KEYS)
            item["source_claims"] = named_values(payload, SOURCE_KEYS)
            item["configured_target"] = named_values(payload, {"configsnapshot", "configurationtarget", "configtarget", "targetmodel", "targetquality"})
            item["submitted_parameters"] = named_values(payload, {"submittedparameters", "actualsubmittedparameters"})
            item["reported_actual_model_quality"] = named_values(payload, {"actualmodel", "actualquality", "returnedmodel", "returnedquality"})
        except Exception as error:
            item["issues"].append(f"无法读取来源记录：{type(error).__name__}: {error}")
        records[relative(path)] = item
    return records


def associated_record(path: Path, records: dict[str, dict]) -> dict | None:
    # Prefer exact sidecars; never guess a relationship from the basename alone.
    for candidate in (Path(str(path) + ".generation.json"), path.with_suffix(".generation.json")):
        if relative(candidate) in records:
            return records[relative(candidate)]
    matches = []
    for record in records.values():
        payload = record.get("data", {})
        declared = payload.get("file") or payload.get("path") or payload.get("output_file")
        if not isinstance(declared, str):
            continue
        declared_path = Path(declared.replace("\\", "/"))
        possibilities = [declared_path] if declared_path.is_absolute() else [ROOT / declared_path, (ROOT / record["path"]).parent / declared_path]
        if any(candidate.resolve() == path.resolve() for candidate in possibilities):
            matches.append(record)
    return matches[0] if len(matches) == 1 else None


def inspect_png(path: Path, records: dict[str, dict], slot: dict | None) -> dict:
    item = {"path": relative(path), "area": path.relative_to(ROOT).parts[0], "slot": slot,
            "sha256": None, "decoded_rgba_sha256": None, "size": None, "format": None,
            "mode": None, "alpha": None, "technical_issues": [], "provenance_issues": [],
            "visual_approval": "unreviewed", "native_input_verified": False}
    try:
        item["sha256"] = digest(path)
        with Image.open(path) as frame:
            frame.load()
            item.update(size=list(frame.size), format=frame.format, mode=frame.mode)
            if frame.format != "PNG":
                item["technical_issues"].append("扩展名为 PNG，但解码格式不是 PNG")
            if frame.mode != "RGBA":
                item["technical_issues"].append(f"像素模式为 {frame.mode}，正式帧要求 RGBA")
            rgba = frame.convert("RGBA")
            pixel_hash = hashlib.sha256(f"{rgba.width}x{rgba.height}:RGBA:".encode("ascii"))
            pixel_hash.update(rgba.tobytes())
            item["decoded_rgba_sha256"] = pixel_hash.hexdigest()
            alpha = rgba.getchannel("A")
            histogram = alpha.histogram()
            item["alpha"] = {
                "extrema": list(alpha.getextrema()), "transparent_pixels": histogram[0],
                "opaque_pixels": histogram[255], "partial_pixels": sum(histogram[1:255]),
                "visible_bbox": list(alpha.getbbox()) if alpha.getbbox() else None,
                "total_pixels": frame.width * frame.height,
                "has_encoded_alpha": frame.mode in ("RGBA", "LA") or "transparency" in frame.info,
            }
            if histogram[0] == frame.width * frame.height:
                item["technical_issues"].append("图片完全透明")
            if histogram[255] == frame.width * frame.height:
                item["technical_issues"].append("图片完全不透明，需检查背景")
            if item["area"] == "runtime" and frame.size != (1024, 1024):
                item["technical_issues"].append("正式单帧尺寸不是 1024×1024")
    except Exception as error:
        item["technical_issues"].append(f"图片读取失败：{type(error).__name__}: {error}")

    record = associated_record(path, records)
    item["generation_record"] = record["path"] if record else None
    item["declared_native_dimensions"] = record.get("native_dimensions_claims", []) if record else []
    item["source_claims"] = record.get("source_claims", []) if record else []
    item["native_dimensions_note"] = "记录中声明的原生尺寸；不能仅凭声明或导出尺寸确认原生单帧分辨率。"
    if record is None:
        item["provenance_issues"].append("没有可明确关联的逐图生成记录")
    elif record["issues"]:
        item["provenance_issues"].extend(record["issues"])
    else:
        declared_sha = record["data"].get("sha256")
        item["generation_record_sha_matches"] = declared_sha.lower() == item["sha256"] if isinstance(declared_sha, str) else None
        if declared_sha and item["generation_record_sha_matches"] is False:
            item["provenance_issues"].append("生成记录 SHA 与当前 PNG 不一致")
        valid_claims = [dimensions(claim["value"]) for claim in item["declared_native_dimensions"]]
        valid_claims = [claim for claim in valid_claims if claim]
        if not valid_claims:
            item["provenance_issues"].append("未记录明确原生单帧尺寸；当前画布尺寸不可替代来源证据")
        elif any(min(claim) < 1024 for claim in valid_claims):
            item["provenance_issues"].append("存在低于 1024 的原生尺寸声明，须人工确认单帧来源")
    item["technical_ok"] = not item["technical_issues"]
    return item


def build_report() -> dict:
    files = sorted(p for area in ("runtime", "work") for p in (ROOT / area).rglob("*") if p.is_file())
    pngs = [p for p in files if p.suffix.lower() == ".png"]
    records = load_records([p for p in files if p.name.endswith(".generation.json")])
    expected = {}
    sequences = []
    for action, spec in SPECS.items():
        for direction in spec["directions"]:
            paths = [f"runtime/{action}/{direction}/{index:02d}.png" for index in range(spec["count"])]
            sequence = {"action": action, "direction": direction, "expected_count": spec["count"],
                        "frame_duration_ms": spec["duration_ms"], "cycle_duration_ms": spec["duration_ms"] * spec["count"],
                        "slots": paths, "missing": [], "present": []}
            sequences.append(sequence)
            for index, name in enumerate(paths):
                expected[name] = {"action": action, "direction": direction, "number": index}
    assets = [inspect_png(path, records, expected.get(relative(path))) for path in pngs]
    by_path = {item["path"]: item for item in assets}
    for sequence in sequences:
        sequence["present"] = [name for name in sequence["slots"] if name in by_path]
        sequence["missing"] = [name for name in sequence["slots"] if name not in by_path]
    sha_groups = defaultdict(list)
    pixel_groups = defaultdict(list)
    for asset in assets:
        if asset["sha256"]:
            sha_groups[asset["sha256"]].append(asset["path"])
        if asset["decoded_rgba_sha256"]:
            pixel_groups[asset["decoded_rgba_sha256"]].append(asset["path"])
    related_records = {asset["generation_record"] for asset in assets if asset["generation_record"]}
    # Raw records remain on disk; report selected facts only (prompts may be large).
    compact_records = [{key: value for key, value in record.items() if key != "data"} for record in records.values()]
    return {
        "schema_version": 1, "character_id": ROOT.name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(ROOT), "scan_areas": ["runtime", "work"],
        "expected_total": len(expected), "present_slot_count": sum(name in by_path for name in expected),
        "missing_slot_count": sum(name not in by_path for name in expected),
        "png_count": len(assets), "generation_record_count": len(records),
        "technical_ok_slot_count": sum(by_path[name]["technical_ok"] for name in expected if name in by_path),
        "unexpected_runtime_files": [asset["path"] for asset in assets if asset["area"] == "runtime" and asset["slot"] is None],
        "duplicate_file_sha256": [{"sha256": key, "paths": values} for key, values in sha_groups.items() if len(values) > 1],
        "duplicate_decoded_rgba_sha256": [{"sha256": key, "paths": values} for key, values in pixel_groups.items() if len(values) > 1],
        "unassociated_generation_records": [name for name in records if name not in related_records],
        "visual_approval": "unreviewed", "client_status": "not_integrated",
        "notes": ["只读检查现有 PNG 和逐图 JSON；不生成、复制、镜像、缩放、对齐或修改图片。",
                  "SHA 不同、文件齐全、RGBA 或技术通过均不代表美术通过。",
                  "work 是在制稿，不自动计入正式槽位。缺帧保持为空。",
                  "原生尺寸声明与解码画布尺寸分列；未自动证实原生输入、手脚连续性或根锚点。",
                  "重复 SHA 只是事实提示；work 与 runtime 的交付副本可能合法重复，须结合用途审核。"],
        "sequences": sequences, "assets": assets, "generation_records": compact_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", action="store_true", help="完整 JSON 输出到 stdout，不写报告文件")
    parser.add_argument("--strict", action="store_true", help="存在缺帧、技术或来源问题时返回 1（不宣告美术结论）")
    args = parser.parse_args()
    report = build_report()
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.stdout:
        print(serialized, end="")
    else:
        output = ROOT / "review" / "technical.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(serialized, encoding="utf-8")
        print(json.dumps({"report": str(output), "present": report["present_slot_count"],
                          "expected": report["expected_total"], "png_count": report["png_count"],
                          "generation_record_count": report["generation_record_count"],
                          "visual_approval": "unreviewed"}, ensure_ascii=False))
    failed = report["missing_slot_count"] or report["unexpected_runtime_files"] or any(asset["technical_issues"] or asset["provenance_issues"] for asset in report["assets"]) or any(record["issues"] for record in report["generation_records"])
    return int(bool(args.strict and failed))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
