"""Read-only checks plus an optional JSON report restricted to preview/."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

from manifest_tools import ROOT, EXPECTED, DURATIONS, load_manifest, frames_of, local_path, png_info, sha256


def verify(manifest: dict, require_complete: bool = False) -> dict:
    errors, warnings = [], []
    frames = frames_of(manifest)
    groups, hashes = defaultdict(list), defaultdict(list)
    registration = manifest.get("registration", {})
    if registration.get("method") != "shared_camera_root":
        errors.append("registration.method 必须为 shared_camera_root；不得最低像素贴地。")
    for flag in ("perFrameBboxScaling", "lowestPixelGrounding"):
        if registration.get(flag) is not False:
            errors.append(f"registration.{flag} 必须显式为 false。")
    global_scale = registration.get("globalScale")
    if not isinstance(global_scale, (int, float)) or isinstance(global_scale, bool) or global_scale <= 0:
        errors.append("registration.globalScale 必须是统一且大于零的尺度。")
    root = registration.get("rootAnchor")
    if not isinstance(root, list) or len(root) != 2 or not all(isinstance(v, (int, float)) for v in root):
        errors.append("registration.rootAnchor 必须记录统一虚拟地面根锚点 [x,y]。")
    if manifest.get("canvas") != {"width": 1024, "height": 1024, "mode": "RGBA"}:
        errors.append("canvas 必须明确为 1024×1024 RGBA。")
    ids = Counter()
    scales = set()
    for position, frame in enumerate(frames):
        label = frame.get("id", f"frames[{position}]")
        ids[label] += 1
        action, direction = frame.get("action"), frame.get("direction")
        if action not in EXPECTED or direction not in EXPECTED.get(action, {}):
            errors.append(f"{label}: 动作/方向无效 {action}/{direction}")
            continue
        groups[(action, direction)].append(frame)
        index = frame.get("index")
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < EXPECTED[action][direction]:
            errors.append(f"{label}: index 必须采用 0 起始并落在当前组范围内。")
        expected_ms = DURATIONS[action]
        if action == "run" and manifest.get("timing"):
            schedule = manifest["timing"]["E" if direction == "E" else "otherRunDirections"]
            expected_ms = schedule[index] if isinstance(index, int) and 0 <= index < len(schedule) else None
        if frame.get("durationMs") != expected_ms:
            errors.append(f"{label}: durationMs 应为 {expected_ms}。")
        if frame.get("isPlaceholder") or frame.get("mirrored") or frame.get("interpolated"):
            errors.append(f"{label}: 不得使用占位、镜像或插值帧。")
        transform = frame.get("transform", {})
        if transform.get("scale") is not None:
            scales.add(transform["scale"])
            if transform["scale"] != global_scale:
                errors.append(f"{label}: 逐帧尺度与统一 globalScale 不同。")
        for flag in ("perFrameBboxScaling", "lowestPixelGrounding"):
            if frame.get(flag) or transform.get(flag):
                errors.append(f"{label}: 检测到禁止处理 {flag}。")
        if frame.get("rootAnchor") is not None and frame["rootAnchor"] != root:
            errors.append(f"{label}: 根锚点不同于统一虚拟根锚点；腾空应表现在画布中。")
        for path_key, sha_key, is_native in (("path", "sha256", False), ("nativePath", "nativeSha256", True)):
            value = frame.get(path_key, frame.get("file") if path_key == "path" else None)
            expected_digest = frame.get(sha_key, "")
            if is_native and frame.get("nativeProvenance"):
                native = frame["nativeProvenance"]
                value = native.get("historicalPath")
                expected_digest = native.get("sha256", "")
                if native.get("disposition") == "removed_after_verified_export":
                    try:
                        ledger = json.loads((ROOT / "review" / "cleanup-ledger.json").read_text(encoding="utf-8"))
                        prior = json.loads((ROOT / "review" / "pre-cleanup-structure-report.json").read_text(encoding="utf-8"))
                        source = json.loads(local_path(native["generationRecord"]).read_text(encoding="utf-8-sig"))
                        archived = {x["path"]: x["sha256"] for x in ledger["removed"]}
                        if archived.get(value) != expected_digest or not prior["passed"] or not native.get("verifiedBeforeCleanup"):
                            errors.append(f"{label}: 原生图清理证据不完整。")
                        if [native.get("width"), native.get("height"), native.get("mode")] != [1254, 1254, "RGBA"]:
                            errors.append(f"{label}: 原生图尺寸/模式历史证据不正确。")
                        if source.get("sha256") and source["sha256"].lower() != expected_digest:
                            errors.append(f"{label}: 原生来源记录 SHA 不匹配。")
                    except (OSError, ValueError, KeyError) as exc:
                        errors.append(f"{label}: 读取原生清理记录失败 {exc}")
                    continue
            if not value:
                errors.append(f"{label}: 缺少 {path_key}，不能证明正式帧或原生输入。")
                continue
            try:
                path = local_path(value)
                info = png_info(path)
                if info["mode"] != "RGBA":
                    errors.append(f"{label}/{path_key}: 实际 {info['mode']}，要求 RGBA。")
                if info.get("alphaExtrema", [0, 255])[1] == 0:
                    errors.append(f"{label}/{path_key}: 全透明空图。")
                if info.get("alphaExtrema", [0, 255])[0] == 255:
                    errors.append(f"{label}/{path_key}: 全不透明，需人物透明背景。")
                if not info.get("decoded"):
                    warnings.append(f"{label}/{path_key}: 未安装 Pillow，仅检查 PNG 头，未完整解码。")
                if is_native and min(info["width"], info["height"]) < 1024:
                    errors.append(f"{label}: 原生单帧小于 1024；不能把小格放大计为高清帧。")
                if not is_native and (info["width"], info["height"]) != (1024, 1024):
                    errors.append(f"{label}: 导出尺寸为 {info['width']}×{info['height']}，要求 1024×1024。")
                digest = sha256(path)
                if expected_digest.lower() != digest:
                    errors.append(f"{label}: {sha_key} 缺失或与文件不符。")
                if not is_native:
                    hashes[digest].append(label)
            except (OSError, ValueError, TypeError) as exc:
                errors.append(f"{label}/{path_key}: {exc}")
        record = frame.get("sourceRecord")
        try:
            if not record or not local_path(record).is_file():
                errors.append(f"{label}: 缺少有效逐图来源记录 sourceRecord。")
        except (TypeError, ValueError) as exc:
            errors.append(f"{label}/sourceRecord: {exc}")
    if any(count > 1 for count in ids.values()):
        errors.append("帧 id 重复。")
    if len(scales) > 1:
        errors.append("存在逐帧独立缩放。")
    for digest, names in hashes.items():
        if len(names) > 1:
            errors.append(f"同内容帧重复 {', '.join(names)}；不同槽位不能靠复制凑数。")
    counts = {}
    for action, directions in EXPECTED.items():
        for direction, expected in directions.items():
            group = groups[(action, direction)]
            indices = [f.get("index") for f in group]
            if len(set(indices)) != len(indices):
                errors.append(f"{action}/{direction}: index 重复。")
            counts[f"{action}/{direction}"] = {"present": len(group), "expected": expected,
                "visualApproved": sum(f.get("visualApproved") is True for f in group),
                "exported": sum(f.get("status") == "exported" for f in group)}
            if len(group) != expected:
                (errors if require_complete else warnings).append(f"{action}/{direction}: {len(group)}/{expected} 帧。")
            if require_complete and any(f.get("visualApproved") is not True for f in group):
                errors.append(f"{action}/{direction}: 尚有帧未声明视觉通过。")
            if require_complete and any(f.get("status") != "exported" for f in group):
                errors.append(f"{action}/{direction}: 尚有帧未声明正式导出。")
    return {"characterId": manifest.get("characterId"), "passed": not errors, "requireComplete": require_complete,
            "totalFrames": len(frames), "targetFrames": 196, "groups": counts, "errors": errors, "warnings": warnings,
            "limits": ["结构检查不能证明解剖、身份、动作连续性或独立绘制。", "统一根锚点与尺度声明仍需视觉验收及来源审计。", "有 Pillow 时完整解码并检查 Alpha 范围；透明边缘是否干净仍需目检。"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--report", action="store_true", help="Write preview/structure-report.json")
    args = parser.parse_args()
    try:
        report = verify(load_manifest(), args.require_complete)
    except (OSError, ValueError, TypeError) as exc:
        print(f"未能读取真实 manifest.json: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    if args.report:
        (ROOT / "preview").mkdir(exist_ok=True)
        (ROOT / "preview" / "structure-report.json").write_text(output + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
