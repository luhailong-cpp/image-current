#!/usr/bin/env python3
"""Read-only image audit; writes manifests and an offline inspection page only.

Never generates, retouches, moves, aligns, duplicates, or interpolates images.
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

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parents[3]
CONTRACT = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = {"E": "敌方 · 右下斜正面", "W": "我方 · 左上真正斜背面"}
EXPECTED_COUNT = 68
SIZE = (1024, 1024)
EXPORT_OPERATION = {"type": "sourceNormalizedTo980Square", "resize": [980, 980],
                    "offset": [22, 0], "canvas": [1024, 1024], "perFrameAlignment": False}
ACCEPTED_NATIVE_SIZES = [[1254, 1254], [1024, 1024]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def local_reference(value: str, sidecar: Path) -> Path | None:
    """Only resolve paths inside Image; never inspect sibling/client sources."""
    if not isinstance(value, str) or not value or "://" in value:
        return None
    source = Path(value)
    candidates = [source] if source.is_absolute() else [ROOT / source, sidecar.parent / source, PROJECT_ROOT / source]
    allowed = [p.resolve() for p in candidates if p.resolve().is_relative_to(PROJECT_ROOT)]
    return next((p for p in allowed if p.is_file()), allowed[0] if allowed else None)


def textual_paths(value):
    """Receipt/evidence may be a path, a list, or nested path-bearing objects."""
    if isinstance(value, str):
        if not "://" in value and Path(value).suffix.lower() in {".json", ".txt", ".log", ".receipt"}:
            yield value
    elif isinstance(value, list):
        for item in value:
            yield from textual_paths(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from textual_paths(item)


def generated_source_reference(value, receipt_value, sidecar):
    """Permit only a tool-output cache path explicitly named in its saved receipt."""
    within_image = local_reference(value, sidecar)
    if within_image:
        return within_image
    if not isinstance(value, str):
        return None
    candidate = Path(value).resolve()
    cache = (Path.home() / '.codex' / 'generated_images').resolve()
    receipt_path = local_reference(receipt_value, sidecar)
    if not candidate.is_relative_to(cache):
        return None
    def strings(node):
        if isinstance(node, str): yield node
        elif isinstance(node, dict):
            for item in node.values(): yield from strings(item)
        elif isinstance(node, list):
            for item in node: yield from strings(item)
    needle = str(candidate).replace('\\', '/').lower()
    receipts = [receipt_path] if receipt_path and receipt_path.is_file() else list((ROOT / 'receipts').glob('*.json'))
    for receipt_path in receipts:
        receipt = load_json(receipt_path)
        if any(needle in re.sub('/+', '/', s.replace('\\', '/')).lower() for s in strings(receipt)):
            return candidate
    return None


def validate_record(path: Path, frame: dict, error, warn) -> dict | None:
    if not path.is_file():
        error("missing_generation_record", "缺少逐图 generation.json")
        return None
    try:
        record = load_json(path)
        if not isinstance(record, dict):
            raise ValueError("顶层必须为对象")
    except (ValueError, OSError) as exc:
        error("invalid_generation_record", str(exc))
        return None
    required = ["file", "sha256", "generatedAt", "width", "height", "format", "tool", "route",
                "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references"]
    for key in required:
        if key not in record:
            error("record_missing_field", key)
    if record.get("sha256") != frame["sha256"]:
        error("record_sha_mismatch", "生成记录 SHA256 与当前 PNG 不符")
    recorded_file = local_reference(record.get("file"), path)
    if recorded_file != (ROOT / frame["file"]).resolve():
        error("record_file_mismatch", "file 未指向本帧")
    for key in ("width", "height"):
        if record.get(key) != frame[key]:
            error("record_size_mismatch", f"{key} 未等于当前导出尺寸；原生尺寸请另记 nativeWidth/nativeHeight")
    if str(record.get("format", "")).upper() != "PNG":
        error("record_format_mismatch", "format 必须为 PNG")
    try:
        stamp = datetime.fromisoformat(str(record.get("generatedAt", "")).replace("Z", "+00:00"))
        if stamp.utcoffset() is None:
            raise ValueError("必须含时区")
    except ValueError as exc:
        error("invalid_generated_at", str(exc))
    config = record.get("configSnapshot")
    if not isinstance(config, dict) or any(not config.get(key) for key in ("model", "quality", "builtin_product", "verified_on", "sources")):
        error("incomplete_config_snapshot", "必须保存当次配置快照的五项字段")
    submitted = record.get("submittedParameters")
    if not isinstance(submitted, dict) or any(key not in submitted for key in ("model", "quality")):
        error("incomplete_submitted_parameters", "model/quality 未提供时也必须显式 null")
    if (record.get("actualModel") is None or record.get("actualQuality") is None) and not record.get("unverifiedReason"):
        error("missing_unverified_reason", "未确认实际型号或质量时必须说明原因")
    if not record.get("tool") or not record.get("route"):
        error("missing_route", "tool 与 route 必须非空")
    prompt = local_reference(record.get("prompt"), path)
    if not prompt or not prompt.is_file():
        error("missing_prompt", "prompt 必须指向保留的实际提示词文件")
    else:
        try:
            if not prompt.read_text(encoding="utf-8-sig").strip():
                error("empty_prompt", "提示词文件为空")
        except (UnicodeError, OSError) as exc:
            error("unreadable_prompt", str(exc))
    receipts = list(textual_paths(record.get("evidence")))
    if not receipts:
        error("missing_receipt_reference", "evidence 必须引用保留的原始工具输出 receipt/文字证据")
    for receipt in receipts:
        resolved = local_reference(receipt, path)
        if not resolved or not resolved.is_file() or resolved.stat().st_size == 0:
            error("missing_evidence_file", receipt)
    refs = record.get("references")
    if not isinstance(refs, list) or not refs:
        error("missing_references", "references 必须逐一列出身份和风格参考路径与用途")
    else:
        for ref in refs:
            ref_path = ref.get("path", ref.get("file")) if isinstance(ref, dict) else ref
            resolved = generated_source_reference(ref_path, ref.get('generationRecord') if isinstance(ref,dict) else None, path)
            if not resolved or not resolved.is_file():
                error("missing_reference_file", str(ref_path))
            if not isinstance(ref, dict) or not (ref.get("purpose") or ref.get("role")):
                error("missing_reference_purpose", str(ref_path))
            if isinstance(ref, dict) and ref.get("sha256") and resolved and resolved.is_file() and sha256(resolved) != ref["sha256"]:
                error("reference_sha_mismatch", str(ref_path))
    if record.get("derivedFrom") and not record.get("operation"):
        error("missing_derived_operation", "派生图必须记录 operation")
    operation = record.get("operation")
    if not isinstance(operation, dict) or any(operation.get(key) != value for key, value in EXPORT_OPERATION.items()):
        error("export_operation_mismatch", "必须以sourceNormalizedTo980Square整画布resize980×980后offset[22,0]导出1024；禁止逐帧定位")
    elif operation.get("sourceSize") not in ACCEPTED_NATIVE_SIZES:
        error("unexpected_native_source_size", "本批原生尺寸合同接受1254×1254或1024×1024，operation.sourceSize需如实记录")
    if not record.get("derivedFrom"):
        error("missing_derived_source", "统一缩放导出必须关联derivedFrom原生图片及来源记录")
    if record.get("derivedFrom"):
        ancestors = record["derivedFrom"] if isinstance(record["derivedFrom"], list) else [record["derivedFrom"]]
        for ancestor in ancestors:
            if not isinstance(ancestor, dict) or not re.fullmatch(r"[a-fA-F0-9]{64}", str(ancestor.get("sha256", ""))):
                error("invalid_derived_source", "derivedFrom 必须保留源图路径、SHA256 与 generationRecord")
                continue
            ancestor_name = ancestor.get("path", ancestor.get("file"))
            ancestor_path = generated_source_reference(ancestor_name, ancestor.get('generationRecord', ancestor.get('generationReceipt')), path)
            if not ancestor_name or not ancestor_path:
                error("invalid_derived_source_path", str(ancestor_name))
            elif ancestor_path.is_file() and sha256(ancestor_path) != ancestor["sha256"]:
                error("derived_source_sha_mismatch", str(ancestor_name))
            elif not ancestor_path.is_file():
                # Deleted intermediate images are permitted only with an explicit cleanup trail.
                cleanup = local_reference(ancestor.get("cleanupRecord"), path)
                if not (ancestor.get("removed") or ancestor.get("deleted")) or not cleanup or not cleanup.is_file():
                    error("missing_derived_source", f"{ancestor_name}；已删除原图须记 removed=true 与 cleanupRecord")
            ancestor_record = local_reference(ancestor.get("generationRecord", ancestor.get("generationReceipt")), path)
            if not ancestor_record or not ancestor_record.is_file():
                error("missing_derived_generation_record", str(ancestor.get("generationRecord")))
    if record.get("actualModel") is not None or record.get("actualQuality") is not None:
        warn("declared_model_evidence_needs_review", "仅校验了证据文件存在；实际型号/质量声明需人工核对 receipt 对应字段")
    return record


def audit() -> tuple[dict, dict]:
    errors, warnings, frames, sequences = [], [], [], []
    file_hashes, visible_hashes, content_hashes = defaultdict(list), defaultdict(list), defaultdict(list)
    expected_paths = set()
    for action, (count, duration) in CONTRACT.items():
        for direction, direction_text in DIRECTIONS.items():
            sequence = {"id": f"{action}-{direction}", "action": action, "direction": direction,
                        "directionDescription": direction_text, "frameCount": count, "durationMs": duration,
                        "totalDurationMs": count * duration, "frames": [], "visualStatus": "unreviewed_by_tool"}
            for index in range(1, count + 1):
                relative = f"runtime/{action}/{direction}/{index:02d}.png"
                expected_paths.add(relative)
                path = ROOT / relative
                record_path = path.with_name(path.name + ".generation.json")
                frame = {"file": relative, "action": action, "direction": direction, "frame": index,
                         "durationMs": duration, "width": None, "height": None, "mode": None, "format": None,
                         "pivot": [0.5, 0.08], "pivotCoordinateSystem": "normalized_bottom_left",
                         "anchorTopLeftPixels": [512, 942], "event": None,
                         "sha256": None, "generationRecord": record_path.relative_to(ROOT).as_posix(),
                         "present": path.is_file(), "visualStatus": "unreviewed_by_tool", "issues": []}

                def error(code, message):
                    issue = {"file": relative, "code": code, "message": message}
                    errors.append(issue)
                    frame["issues"].append({"severity": "error", "code": code, "message": message})

                def warn(code, message):
                    issue = {"file": relative, "code": code, "message": message}
                    warnings.append(issue)
                    frame["issues"].append({"severity": "warning", "code": code, "message": message})

                if not frame["present"]:
                    error("missing_frame", "预期帧不存在；未以任何占位图补齐")
                else:
                    frame["sha256"] = sha256(path)
                    file_hashes[frame["sha256"]].append(relative)
                    try:
                        with Image.open(path) as im:
                            im.load()
                            frame.update(width=im.width, height=im.height, mode=im.mode, format=im.format)
                            if im.size != SIZE:
                                error("wrong_size", f"实际 {im.width}×{im.height}，应为 1024×1024")
                            if im.format != "PNG" or im.mode != "RGBA":
                                error("wrong_format", f"实际 {im.format}/{im.mode}，应为 PNG/RGBA")
                            if im.mode == "RGBA":
                                alpha = im.getchannel("A")
                                histogram = alpha.histogram()
                                bbox = alpha.getbbox()
                                frame["alpha"] = {"min": alpha.getextrema()[0], "max": alpha.getextrema()[1],
                                                  "transparentPixels": histogram[0], "partialPixels": sum(histogram[1:255]),
                                                  "opaquePixels": histogram[255], "bbox": list(bbox) if bbox else None}
                                if histogram[0] == 0:
                                    error("no_transparent_pixels", "没有完全透明像素")
                                if bbox is None:
                                    error("empty_frame", "整帧完全透明")
                                else:
                                    if bbox[0] == 0 or bbox[1] == 0 or bbox[2] == im.width or bbox[3] == im.height:
                                        warn("content_touches_canvas", "非零 alpha 接触画布边缘，需肉眼排除裁切")
                                    # Zero hidden RGB and premultiply alpha for visible-pixel identity checks.
                                    channels = [ImageChops.multiply(im.getchannel(ch), alpha) for ch in "RGB"]
                                    canonical = Image.merge("RGBA", (*channels, alpha))
                                    frame["visiblePixelSha256"] = hashlib.sha256(canonical.tobytes()).hexdigest()
                                    cropped = canonical.crop(bbox)
                                    size_header = f"{cropped.width}x{cropped.height}:".encode("ascii")
                                    frame["visibleContentSha256"] = hashlib.sha256(size_header + cropped.tobytes()).hexdigest()
                                    visible_hashes[frame["visiblePixelSha256"]].append(relative)
                                    content_hashes[frame["visibleContentSha256"]].append(relative)
                    except (OSError, ValueError) as exc:
                        error("unreadable_image", str(exc))
                    record = validate_record(record_path, frame, error, warn)
                    if record:
                        frame["generationRecordSha256"] = sha256(record_path)
                        frame["source"] = {key: record.get(key) for key in ("tool", "route", "generatedAt", "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "unverifiedReason", "evidence", "prompt", "references", "derivedFrom", "operation")}
                        retained_texts = [record.get("prompt"), *textual_paths(record.get("evidence"))]
                        frame["source"]["retainedTextSha256"] = {name: sha256(resolved) for name in retained_texts
                                                                 if isinstance(name, str) and (resolved := local_reference(name, record_path)) and resolved.is_file()}
                frames.append(frame)
                sequence["frames"].append(relative)
            sequence["presentCount"] = sum((ROOT / file).is_file() for file in sequence["frames"])
            sequences.append(sequence)
    duplicate_groups = {"fileBytes": [v for v in file_hashes.values() if len(v) > 1],
                        "visiblePixels": [v for v in visible_hashes.values() if len(v) > 1],
                        "visibleContentIgnoringTranslation": [v for v in content_hashes.values() if len(v) > 1]}
    for kind, groups in duplicate_groups.items():
        for group in groups:
            issue = {"file": group[0], "code": "duplicate_" + kind, "message": "内容重复，需检查独立姿态", "files": group}
            errors.append(issue)
            for frame in frames:
                if frame["file"] in group:
                    frame["issues"].append({"severity": "error", "code": issue["code"], "message": issue["message"]})
    actual_paths = {p.relative_to(ROOT).as_posix() for p in (ROOT / "runtime").rglob("*.png")} if (ROOT / "runtime").is_dir() else set()
    for extra in sorted(actual_paths - expected_paths):
        errors.append({"file": extra, "code": "unexpected_runtime_png", "message": "不在六组 68 帧合同内"})
    stamp = datetime.now(timezone.utc).isoformat()
    present = sum(frame["present"] for frame in frames)
    record_count = sum("source" in frame for frame in frames)
    passed = not errors and present == EXPECTED_COUNT
    report = {"schemaVersion": 1, "generatedAt": stamp, "expectedCount": EXPECTED_COUNT,
              "presentCount": present, "readableGenerationRecordCount": record_count,
              "technicalPassed": passed, "errorCount": len(errors), "warningCount": len(warnings),
              "errors": errors, "warnings": warnings, "duplicates": duplicate_groups,
              "artisticReview": "not_performed_by_this_tool", "motionReview": "not_performed_by_this_tool",
              "clientIntegration": "not_performed", "independentPoseProof": "this audit detects exact duplicates only; anatomical continuity and non-interpolated provenance require visual/tool-receipt review"}
    manifest = {"schemaVersion": 1, "character": "灵玥", "slug": "legacy-ling-yue", "generatedAt": stamp,
                "contract": {"expectedCount": EXPECTED_COUNT, "width": 1024, "height": 1024, "mode": "RGBA", "format": "PNG",
                             "pivot": [0.5, 0.08], "anchorTopLeftPixels": [512, 942],
                             "anchorNote": "合同原点；0.08×1024=81.92，自顶部为942.08，整数脚点942为约定取整。工具不重新定位任何脚点。",
                             "directionDefinitions": DIRECTIONS},
                "exportPolicy": {"E": dict(EXPORT_OPERATION), "W": dict(EXPORT_OPERATION),
                                 "nativeExpectedSize": [1254, 1254], "acceptedNativeSizes": ACCEPTED_NATIVE_SIZES,
                                 "basis": "parent-declared whole native square normalized to 980x980 then pasted at [22,0]; scale is 980/sourceWidth, never based on per-frame feet",
                                 "perFrameAlignment": False, "verifiedAgainstNativeSources": False},
                "technicalPassed": passed, "artisticReview": "not_performed_by_this_tool", "motionReview": "not_performed_by_this_tool",
                "clientIntegration": "not_performed", "releaseReady": False, "sequences": sequences, "frames": frames}
    return manifest, report


def task_output(value: str) -> Path:
    candidate = (ROOT / value).resolve()
    if not candidate.is_relative_to(ROOT):
        raise ValueError("输出必须位于灵玥任务目录内")
    return candidate


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="只读检查，不写任何文件")
    parser.add_argument("--manifest", default="manifest.json", help="任务目录内输出位置")
    parser.add_argument("--report", default="technical-validation.json", help="任务目录内输出位置")
    parser.add_argument("--preview", default="preview.html", help="任务根的预览，必须为 preview.html")
    args = parser.parse_args()
    manifest, report = audit()
    if not args.check_only:
        # Paths are resolved before any write; no image file is an allowed output.
        output_manifest, output_report, output_preview = map(task_output, (args.manifest, args.report, args.preview))
        if output_manifest.suffix != ".json" or output_report.suffix != ".json" or output_preview != ROOT / "preview.html":
            parser.error("manifest/report 须为 JSON；preview 只允许任务根 preview.html")
        if output_manifest == output_report:
            parser.error("manifest 与 report 不能覆盖同一文件")
        template = (ROOT / "tools" / "preview.template.html").read_text(encoding="utf-8")
        data = json.dumps({"manifest": manifest, "report": report}, ensure_ascii=False).replace("<", "\\u003c")
        write_json(output_manifest, manifest)
        write_json(output_report, report)
        output_preview.write_text(template.replace("/*__DELIVERY_DATA__*/", data), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("expectedCount", "presentCount", "readableGenerationRecordCount", "technicalPassed", "errorCount", "warningCount")}, ensure_ascii=False))
    return 0 if report["technicalPassed"] else 1


if __name__ == "__main__":
    sys.exit(main())
