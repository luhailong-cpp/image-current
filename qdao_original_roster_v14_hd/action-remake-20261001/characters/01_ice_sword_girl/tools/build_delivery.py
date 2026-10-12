#!/usr/bin/env python3
"""Read-only PNG audit + offline animation preview for 01_ice_sword_girl.

No PNG is created, resized, mirrored, re-anchored, or changed. The only outputs
are manifest.json, validation.json, and index.html under --output-dir
(preview/legacy-audit). The active grounding preview is built separately.
Run --help for the supported source metadata and anchor declaration formats.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import zlib
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CHARACTER = "01_ice_sword_girl"
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
SPECS = {
    "run": {"label": "跑步", "directions": DIRECTIONS, "count": 16, "frame_ms": 75},
    "hit": {"label": "受击", "directions": ("E", "W"), "count": 6, "frame_ms": 40},
    "attack": {"label": "普攻", "directions": ("E", "W"), "count": 12, "frame_ms": 30},
    "cast": {"label": "施法", "directions": ("E", "W"), "count": 16, "frame_ms": 45},
}
PATH_KEYS = ("file", "path", "output_path", "outputPath", "image_path", "imagePath")
try:
    from PIL import Image
except ImportError:
    Image = None


def inside(path: Path) -> Path:
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"路径越出本角色目录：{path}")
    return path


def relative(path: Path) -> str:
    return inside(path).relative_to(ROOT).as_posix()


def pick(data: dict, *keys):
    return next((data[k] for k in keys if k in data), None)


def size_pair(value):
    if isinstance(value, dict):
        value = (value.get("width"), value.get("height"))
    if isinstance(value, (list, tuple)) and len(value) == 2:
        if all(isinstance(x, int) and not isinstance(x, bool) and x > 0 for x in value):
            return list(value)
    return None


def path_key(value, record_file: Path):
    if not isinstance(value, str) or not value.lower().endswith(".png"):
        return None
    path = Path(value.replace("\\", "/"))
    candidates = [path] if path.is_absolute() else [ROOT / path, record_file.parent / path]
    for candidate in candidates:
        try:
            safe = inside(candidate)
        except ValueError:
            continue
        if safe.exists():
            return relative(safe)
    try:
        return relative(candidates[0])
    except ValueError:
        return None


def load_sources():
    """Index explicit file entries only; never interpret reference images as outputs."""
    index, summaries, errors = {}, {}, []
    directory = ROOT / "sources"
    files = sorted(directory.rglob("*.json")) if directory.is_dir() else []
    # Sidecar records are supported as well as sources/*.json.
    for stage in ("drafts", "final"):
        base = ROOT / stage
        if base.is_dir():
            files.extend(sorted(base.rglob("*.png.generation.json")))
    skip = {"references", "reference", "derivedFrom", "derived_from", "configSnapshot", "config_snapshot", "evidence", "submittedParameters", "submitted_parameters"}

    def walk(node, source_file, inherited, pointer):
        if isinstance(node, list):
            for n, child in enumerate(node):
                walk(child, source_file, inherited, f"{pointer}/{n}")
            return
        if not isinstance(node, dict):
            return
        common = dict(inherited)
        # Frame-level values replace batch values, including explicit nulls.
        for key, value in node.items():
            if not isinstance(value, (list, dict)) or key in skip or key in {
                "native_size", "nativeSize", "nativeFrameSize", "native_frame_size",
                "visualReview", "visual_review", "anchor", "root_anchor", "output",
            }:
                common[key] = value
        path = next((path_key(node[k], source_file) for k in PATH_KEYS
                     if k in node and path_key(node[k], source_file)), None)
        if path:
            record_id = relative(source_file) + "#" + (pointer or "/")
            entry = {"id": record_id, "file": path, "data": common}
            index.setdefault(path, []).append(entry)
            summaries[record_id] = {
                "record": relative(source_file), "pointer": pointer or "/",
                "file": path, "sha256": pick(common, "sha256", "sha"),
                "generated_at": pick(common, "generatedAt", "generated_at"),
                "config_target": pick(common, "configSnapshot", "config_snapshot"),
                "submitted_parameters": pick(common, "submittedParameters", "submitted_parameters"),
                "actual_model": pick(common, "actualModel", "actual_model"),
                "actual_quality": pick(common, "actualQuality", "actual_quality"),
                "unverified_reason": pick(common, "unverifiedReason", "unverified_reason"),
            }
        for key, child in node.items():
            if key not in skip and isinstance(child, (dict, list)):
                walk(child, source_file, common, f"{pointer}/{key}")

    for file in files:
        try:
            file = inside(file)
            walk(json.loads(file.read_text(encoding="utf-8-sig")), file, {}, "")
        except (ValueError, OSError) as exc:
            errors.append({"file": str(file), "error": str(exc)})
    return index, summaries, errors


def inspect_png(path: Path):
    result = {"path": relative(path), "errors": [], "warnings": []}
    try:
        raw = inside(path).read_bytes()
        result["bytes"] = len(raw)
        result["sha256"] = hashlib.sha256(raw).hexdigest()
        if raw[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("不是 PNG 签名")
        cursor, ihdr, end, idat = 8, None, False, False
        while cursor + 12 <= len(raw):
            length = struct.unpack(">I", raw[cursor:cursor + 4])[0]
            kind = raw[cursor + 4:cursor + 8]
            if cursor + 12 + length > len(raw):
                raise ValueError("PNG chunk 截断")
            data = raw[cursor + 8:cursor + 8 + length]
            crc = struct.unpack(">I", raw[cursor + 8 + length:cursor + 12 + length])[0]
            if zlib.crc32(kind + data) & 0xFFFFFFFF != crc:
                raise ValueError(f"PNG CRC 错误：{kind!r}")
            if kind == b"IHDR":
                if ihdr is not None or length != 13 or cursor != 8:
                    raise ValueError("PNG IHDR 无效")
                ihdr = struct.unpack(">IIBBBBB", data)
            if kind == b"acTL":
                result["errors"].append("正式单帧不能是 APNG")
            if kind == b"IDAT":
                idat = True
            cursor += length + 12
            if kind == b"IEND":
                end = True
                break
        if ihdr is None or not end or not idat:
            raise ValueError("PNG 缺少 IHDR/IDAT/IEND")
        width, height, depth, color, compression, filtering, interlace = ihdr
        result.update(width=width, height=height, bit_depth=depth, color_type=color,
                      mode="RGBA" if color == 6 else {0: "L", 2: "RGB", 3: "P", 4: "LA"}.get(color, "unknown"),
                      pixel_sha256=None, alpha_checked=False)
        if (width, height) != (1024, 1024):
            result["errors"].append(f"画布 {width}×{height}，正式要求 1024×1024")
        if color != 6:
            result["errors"].append("不是 PNG RGBA color_type=6")
        if depth not in (8, 16) or compression != 0 or filtering != 0 or interlace not in (0, 1):
            result["errors"].append("PNG 头参数不符合 RGBA PNG 规范")
        if Image is not None:
            with Image.open(path) as im:
                im.load()
                result["decoded_mode"] = im.mode
                result["pixel_sha256"] = hashlib.sha256(im.tobytes()).hexdigest()
                if im.mode == "RGBA":
                    alpha = im.getchannel("A")
                    result.update(alpha_checked=True, alpha_extrema=list(alpha.getextrema()),
                                  content_bbox=alpha.getbbox())
                    if alpha.getextrema()[0] != 0:
                        result["errors"].append("没有 Alpha=0 的完全透明背景像素")
                    if alpha.getbbox() is None:
                        result["errors"].append("全图透明，没有角色像素")
                    if alpha.getbbox() and (alpha.getbbox()[0] == 0 or alpha.getbbox()[1] == 0
                                           or alpha.getbbox()[2] == width or alpha.getbbox()[3] == height):
                        result["warnings"].append("非透明像素触及画布边界，请检查鞋尖/发饰/剑尖裁切")
        else:
            result["warnings"].append("缺少 Pillow：已检查 PNG 结构，未解码 Alpha 与像素；不能视为完整技术检查")
    except (ValueError, OSError, struct.error, Image.DecompressionBombError if Image else ValueError) as exc:
        result["errors"].append(str(exc))
    result["technical_passed"] = not result["errors"] and result.get("alpha_checked", False)
    return result


def provenance(records, png):
    if not records:
        return {"source_ids": [], "status": "missing", "native_frame_size": None,
                "native_hd_confirmed": False, "visual_passed": False, "issues": ["无逐图来源记录"]}
    matching = [r for r in records if str(pick(r["data"], "sha256", "sha") or "").lower() == png.get("sha256")]
    if not matching:
        return {"source_ids": [r["id"] for r in records], "status": "sha_unbound",
                "native_frame_size": None, "native_hd_confirmed": False, "visual_passed": False,
                "issues": ["来源记录缺少当前文件 SHA256 或 SHA 不符"]}
    data, selected = matching[-1]["data"], matching[-1]["id"]
    issues = []
    derived = pick(data, "derivedFrom", "derived_from")
    native = size_pair(pick(data, "nativeFrameSize", "native_frame_size"))
    if native is None and not derived:
        native = size_pair(pick(data, "native_size", "nativeSize")) or size_pair([data.get("width"), data.get("height")])
    native_ok = bool(native and min(native) >= 1024)
    if not native_ok:
        issues.append("真实单帧原生尺寸未确认 ≥1024；图集总尺寸不能证明单格高清")
    if derived:
        # Derived records must preserve their original record link; model fields
        # belong to that original, never inferred from the current configuration.
        if not pick(data, "operation", "operations"):
            issues.append("派生图缺少 operation")
        origin_items = derived if isinstance(derived, list) else [derived]
        for origin in origin_items:
            if not isinstance(origin, dict) or not pick(origin, "file", "path") or not origin.get("sha256") or not pick(origin, "generation_record", "generationRecord", "record", "source_record"):
                issues.append("派生来源须逐项包含原图路径、SHA256 与 generation_record；未验证完整来源链")
                break
            link = pick(origin, "generation_record", "generationRecord", "record", "source_record")
            try:
                if not isinstance(link, str):
                    raise ValueError("generation_record 必须是本角色目录中的 JSON 路径")
                linked = inside(ROOT / link.split("#", 1)[0])
                json.loads(linked.read_text(encoding="utf-8-sig"))
            except (ValueError, OSError) as exc:
                issues.append(f"派生生成记录不可读取：{exc}")
    else:
        required = (
            ("generatedAt", "generated_at"), ("tool",), ("route",),
            ("configSnapshot", "config_snapshot"), ("submittedParameters", "submitted_parameters"),
            ("actualModel", "actual_model"), ("actualQuality", "actual_quality"),
            ("evidence",), ("prompt",), ("references",),
        )
        for aliases in required:
            if not any(key in data for key in aliases):
                issues.append(f"来源字段缺失：{aliases[0]}")
        submitted = pick(data, "submittedParameters", "submitted_parameters")
        if not isinstance(submitted, dict) or not all(key in submitted for key in ("model", "quality")):
            issues.append("实际提交 model/quality 必须显式记录；无选择器填 null")
        if (pick(data, "actualModel", "actual_model") is None or pick(data, "actualQuality", "actual_quality") is None) and not pick(data, "unverifiedReason", "unverified_reason"):
            issues.append("实际型号/质量未确认时必须记录 unverifiedReason")
    visual = pick(data, "visualReview", "visual_review")
    visual_passed = bool(isinstance(visual, dict) and visual.get("status") == "passed"
                         and str(visual.get("sha256", "")).lower() == png.get("sha256")
                         and visual.get("reviewer") and (visual.get("reviewedAt") or visual.get("reviewed_at")))
    return {"source_ids": [r["id"] for r in matching], "selected_source_id": selected,
            "status": "recorded" if not issues else "incomplete", "issues": issues,
            "native_frame_size": native, "native_hd_confirmed": native_ok,
            "visual_passed": visual_passed,
            "visual_review": visual if isinstance(visual, dict) else None,
            "anchor": pick(data, "anchor", "root_anchor"),
            "events": data.get("events", []),
            "derived_from": derived}


def load_anchor():
    path = ROOT / "anchor.json"
    if not path.exists():
        return {"status": "unconfirmed", "canvas": [1024, 1024], "root_anchor": None,
                "virtual_ground_y": None, "note": "未提供锚点声明；预览不自动贴地或归一化"}
    try:
        data = json.loads(inside(path).read_text(encoding="utf-8-sig"))
        point = data.get("root_anchor")
        valid = size_pair(data.get("canvas")) == [1024, 1024] and isinstance(point, list) and len(point) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) and 0 <= x <= 1024 for x in point)
        if not valid:
            raise ValueError("anchor.json 要求 canvas=[1024,1024] 与 root_anchor=[x,y]")
        return {**data, "status": "declared", "record": "anchor.json",
                "note": "锚点为人工声明；本工具不据此自动移动图片，也不代替逐帧视觉检查"}
    except (ValueError, OSError, AttributeError) as exc:
        return {"status": "invalid", "canvas": [1024, 1024], "root_anchor": None, "error": str(exc)}


def build(frame_base):
    source_index, sources, source_errors = load_sources()
    # The selected E sequence has real contact events at slots 1 and 8;
    # use the user-selected uniform 75 ms instead of old fast timings.
    selected_timing = None
    selection_file = ROOT / "review/run-E-selection.json"
    if selection_file.exists():
        selection = json.loads(selection_file.read_text(encoding="utf-8-sig"))
        candidate_timing = selection.get("timing", {}).get("frameDurationsMs")
        if (selection.get("characterId") != CHARACTER or selection.get("direction") != "E"
                or not isinstance(candidate_timing, list) or len(candidate_timing) != 16
                or any(isinstance(n, bool) or not isinstance(n, (int, float)) or n <= 0
                       for n in candidate_timing)):
            raise ValueError("E向选择清单的角色、方向或16个正帧时长无效")
        selected_timing = candidate_timing
    slots = []
    for action, spec in SPECS.items():
        for direction in spec["directions"]:
            for frame in range(spec["count"]):
                slots.append({"id": f"{action}/{direction}/{frame:03d}", "action": action,
                              "direction": direction, "frame": frame,
                              "duration_ms": selected_timing[frame] if action == "run" and direction == "E" and selected_timing else spec["frame_ms"],
                              "draft": None, "final": None})
    lookup = {(s["action"], s["direction"], s["frame"]): s for s in slots}
    unassigned, groups, duplicates = [], {}, []
    for stage in ("drafts", "final"):
        directory = ROOT / stage
        if not directory.is_dir():
            continue
        for file in sorted(directory.rglob("*.png")):
            try:
                local = inside(file).relative_to(directory.resolve())
                if len(local.parts) != 3:
                    raise ValueError("路径应为 <action>/<direction>/<frame>.png")
                action, direction, filename = local.parts
                if action not in SPECS or direction not in SPECS[action]["directions"]:
                    raise ValueError("动作或方向不在本批规格内")
                match = re.fullmatch(r"(?:frame[_-]?)?(\d+)\.png", filename, re.IGNORECASE)
                if not match:
                    raise ValueError("帧名须为数字或 frame_数字，例如 000.png")
                groups.setdefault((stage, action, direction), []).append((int(match.group(1)), file))
            except ValueError as exc:
                unassigned.append({"path": str(file), "reason": str(exc)})
    for (stage, action, direction), items in groups.items():
        numbers = {n for n, _ in items}
        count = SPECS[action]["count"]
        base = frame_base
        if base == "auto":
            if 0 in numbers and count not in numbers:
                base = "0"
            elif count in numbers and 0 not in numbers:
                base = "1"
            else:
                for _, file in items:
                    unassigned.append({"path": relative(file), "reason": "编号起点不明确；请显式传 --frame-base 0 或 1"})
                continue
        for number, file in items:
            frame = number - int(base)
            slot = lookup.get((action, direction, frame))
            if slot is None:
                unassigned.append({"path": relative(file), "reason": "帧编号越界"})
                continue
            key = "draft" if stage == "drafts" else "final"
            if slot[key] is not None:
                duplicates.append({"slot": slot["id"], "stage": stage, "paths": [slot[key]["path"], relative(file)]})
                slot[key]["errors"].append("同一槽位存在多个 PNG；未作替换选择")
                slot[key]["technical_passed"] = False
                continue
            png = inspect_png(file)
            png["provenance"] = provenance(source_index.get(png["path"], []), png)
            slot[key] = png
    hashes = {}
    for slot in slots:
        for key in ("draft", "final"):
            png = slot[key]
            if png:
                identity = png.get("pixel_sha256") or png.get("sha256")
                if identity:
                    hashes.setdefault(identity, []).append({"slot": slot["id"], "stage": key, "path": png["path"]})
    repeated = [items for items in hashes.values() if len({item["slot"] for item in items}) > 1]
    for group in repeated:
        for item in group:
            png = next(s for s in slots if s["id"] == item["slot"])[item["stage"]]
            png["errors"].append("与其他槽位像素/文件完全相同；不能计作独立姿态")
            png["technical_passed"] = False
    anchor = load_anchor()
    for slot in slots:
        for key in ("draft", "final"):
            png = slot[key]
            if not png:
                continue
            declared = png["provenance"].get("anchor")
            if isinstance(declared, dict):
                declared = declared.get("root_anchor")
            if declared is not None and anchor.get("root_anchor") is not None and declared != anchor["root_anchor"]:
                png["errors"].append("逐图根锚点与全局 anchor.json 不一致")
                png["technical_passed"] = False
    summary = {"expected": 196, "draft_present": 0, "final_present": 0,
               "final_technical_passed": 0, "final_native_hd_confirmed": 0,
               "final_source_recorded": 0, "final_visual_passed": 0,
               "final_ready_for_handoff": 0, "client_status": "not_integrated_not_tested"}
    for slot in slots:
        summary["draft_present"] += slot["draft"] is not None
        png = slot["final"]
        if png is None:
            continue
        p = png["provenance"]
        summary["final_present"] += 1
        summary["final_technical_passed"] += bool(png["technical_passed"])
        summary["final_native_hd_confirmed"] += p["native_hd_confirmed"]
        summary["final_source_recorded"] += p["status"] == "recorded"
        summary["final_visual_passed"] += p["visual_passed"]
        summary["final_ready_for_handoff"] += bool(png["technical_passed"] and p["native_hd_confirmed"] and p["status"] == "recorded" and p["visual_passed"] and anchor["status"] == "declared")
    summary["missing_final"] = 196 - summary["final_present"]
    summary["all_frames_ready_for_handoff"] = bool(summary["final_ready_for_handoff"] == 196 and not source_errors and not unassigned and not duplicates)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest = {"schema_version": 1, "character": CHARACTER, "generated_at": timestamp,
                "generator": "tools/build_delivery.py", "frame_index_base": 0,
                "canvas": [1024, 1024], "anchor": anchor, "specs": SPECS,
                "summary": summary, "slots": slots, "sources": sources,
                "notes": ["工具只读图片，未镜像/复制/缩放/扭曲/插值补帧。", "缺失槽位为 null；文件齐全或 SHA 不同不等于美术通过。", "视觉通过仅从当前 SHA 绑定的人工 visualReview 读取。", "客户端未接入、未运行验收。"]}
    validation = {"generated_at": timestamp, "summary": summary,
                  "source_errors": source_errors, "unassigned_pngs": unassigned,
                  "slot_collisions": duplicates, "identical_pixels_or_files": repeated,
                  "missing_slots": [s["id"] for s in slots if s["final"] is None],
                  "issues": [{"slot": s["id"], "stage": key, "path": s[key]["path"],
                              "errors": s[key]["errors"], "warnings": s[key]["warnings"],
                              "source_issues": s[key]["provenance"]["issues"]}
                             for s in slots for key in ("draft", "final") if s[key] is not None],
                  "automatic_audit_limit": "不证明手脚、握持、身份、根锚点运动、朝向、动作阶段和循环衔接的美术正确性；必须实际看图与动态验收。"}
    return manifest, validation


HTML = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>冰剑少女 · 动作验收</title>
<style>
:root{font-family:system-ui,"Microsoft YaHei",sans-serif;color:#1f3d3b;background:#f4f0e5}body{margin:0 auto;padding:22px;max-width:1500px}h1{font-size:24px;margin:0 0 8px}p{line-height:1.6}.muted{color:#5c6b67;font-size:14px}.bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;padding:14px 0}select,button,input{font:inherit}select,button{border:1px solid #b4a67f;border-radius:9px;background:#fffdf6;color:#17483e;padding:9px 12px}button{cursor:pointer}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #247b6a;outline-offset:2px}button.primary{background:#246451;color:white}main{display:grid;grid-template-columns:minmax(360px,1fr) minmax(300px,400px);gap:20px}.viewport{overflow:auto;border:1px solid #bbab86;border-radius:14px;background:#dcdedc;min-height:300px}.stage{position:relative;width:512px;height:512px;margin:auto;background-color:#f8f9f7;background-image:linear-gradient(45deg,#dce3df 25%,transparent 25%),linear-gradient(-45deg,#dce3df 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#dce3df 75%),linear-gradient(-45deg,transparent 75%,#dce3df 75%);background-size:32px 32px;background-position:0 0,0 16px,16px -16px,-16px 0}canvas{width:100%;height:100%;display:block}.empty{position:absolute;inset:0;display:grid;place-content:center;text-align:center;background:#f4f0e5b8;font-size:23px;pointer-events:none}.empty[hidden]{display:none}.card{padding:16px;border:1px solid #c9bc9e;border-radius:14px;background:#fffcf3;margin-bottom:12px}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:5px}.frame{padding:8px 2px;border:1px solid #d0c6b1;background:transparent}.frame.available{background:#dcf0e7}.frame.active{outline:3px solid #246451}.status{font-size:14px;white-space:pre-wrap;overflow-wrap:anywhere}.warning{color:#974318}.meter{width:100%}code{font-size:12px}a{color:#1b6358}@media(max-width:850px){main{grid-template-columns:1fr}.stage{max-width:none}}
</style>
<h1>冰剑少女 · 动作验收</h1><div id="summary" class="muted"></div>
<p class="muted">查看透明边缘、左右手握持、腿脚交替、朝向和首尾衔接。未生成槽位保持空白；播放不会跳过缺帧。画布固定 1024×1024，显示倍率统一作用于整张画布。</p>
<div class="bar"><label>版本 <select id="stage"><option value="draft">当前在制</option><option value="final">正式导出</option></select></label><label>动作 <select id="action"></select></label><label>方向 <select id="direction"></select></label><label>背景 <select id="background"><option value="checker">透明格</option><option value="#fff">白色</option><option value="#172429">深色</option></select></label><label>显示 <select id="zoom"><option value="0.5">50%</option><option value="0.75">75%</option><option value="1">100%</option></select></label><label><input id="anchor" type="checkbox" checked>显示全局锚点</label></div>
<main><section><div class="viewport"><div class="stage" id="surface"><canvas id="canvas" width="1024" height="1024"></canvas><div class="empty" id="empty">此槽位未生成</div></div></div><div class="bar"><button class="primary" id="play">播放</button><button id="prev">← 上一帧</button><button id="next">下一帧 →</button><select id="speed" aria-label="播放速度"><option value="1">正常速度</option><option value="0.25">慢速 ¼</option></select><label><input type="checkbox" id="loop" checked>循环</label><span id="counter"></span></div><input class="meter" id="seek" type="range" min="0" value="0" aria-label="逐帧滑块"><p class="muted" id="timing"></p><div class="grid" id="frames"></div></section><aside><div class="card"><strong>当前帧与验收状态</strong><p class="status" id="detail"></p><div id="links"></div></div><div class="card"><strong>全局锚点</strong><p class="status" id="anchorInfo"></p><p class="muted">不做最低像素贴地、包围盒缩放、自动居中或方向镜像。根锚点声明不能代替动态检查。</p></div><div class="card"><strong>检查范围</strong><p class="muted">文件检查不证明美术通过。视觉状态仅引用与当前 SHA 对应的人工记录；客户端未接入、未验收。</p><p><a href="manifest.json">清单 JSON</a> · <a href="validation.json">检查 JSON</a></p></div></aside></main>
<script id="manifest" type="application/json">__MANIFEST__</script>
<script>
'use strict';
const data=JSON.parse(document.getElementById('manifest').textContent),$=id=>document.getElementById(id),ctx=$('canvas').getContext('2d');
const imagePrefix=__IMAGE_PREFIX__, sourcePrefix=__SOURCE_PREFIX__, cache=new Map();
let sequence=[], frame=0, running=false, timer=null, drawToken=0, selectionToken=0;
function option(value,label){const o=document.createElement('option');o.value=value;o.textContent=label;return o;}
Object.entries(data.specs).forEach(([k,v])=>$('action').append(option(k,v.label)));
$('action').value='run';
$('summary').textContent=`正式 ${data.summary.final_present}/196 · 当前在制 ${data.summary.draft_present}/196 · 正式视觉通过 ${data.summary.final_visual_passed}/196 · 正式技术通过 ${data.summary.final_technical_passed}/196 · 客户端未接入`;
$('anchorInfo').textContent=data.anchor.root_anchor?`已声明根锚点：(${data.anchor.root_anchor.join(', ')})\n虚拟地面：${data.anchor.virtual_ground_y??'未指定'}\n${data.anchor.note}`:'锚点未确认。当前预览保持图像原始像素位置。';
function url(path){return imagePrefix+path.split('/').map(encodeURIComponent).join('/');}
function stop(){running=false;clearTimeout(timer);timer=null;$('play').textContent='播放';}
function schedule(){if(!running)return;timer=setTimeout(()=>{if(frame===sequence.length-1&&!$('loop').checked){stop();return;}frame=(frame+1)%sequence.length;render();schedule();},sequence[frame].duration_ms/Number($('speed').value));}
function rebuildDirections(){const current=$('direction').value;$('direction').replaceChildren(...data.specs[$('action').value].directions.map(d=>option(d,d)));if(data.specs[$('action').value].directions.includes(current))$('direction').value=current;else $('direction').value=data.specs[$('action').value].directions.includes('E')?'E':data.specs[$('action').value].directions[0];select();}
function select(){stop();const token=++selectionToken;frame=0;sequence=data.slots.filter(s=>s.action===$('action').value&&s.direction===$('direction').value);$('seek').max=sequence.length-1;$('frames').replaceChildren(...sequence.map((s,i)=>{const b=document.createElement('button');b.className='frame';b.textContent=String(i).padStart(3,'0');b.title=s.id;b.onclick=()=>{stop();frame=i;render();};return b;}));$('play').disabled=true;$('play').textContent='加载中';render();Promise.allSettled(sequence.map(s=>s[$('stage').value]).filter(Boolean).map(p=>load(p.path))).then(()=>{if(token!==selectionToken)return;$('play').disabled=false;$('play').textContent='播放';});}
function load(path){if(!cache.has(path)){cache.set(path,new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(new Error('读取失败'));im.src=url(path);}));}return cache.get(path);}
function overlay(){if(!$('anchor').checked||!data.anchor.root_anchor)return;const [x,y]=data.anchor.root_anchor;ctx.save();ctx.strokeStyle='#ea5454';ctx.lineWidth=2;ctx.setLineDash([8,6]);ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,1024);ctx.moveTo(0,y);ctx.lineTo(1024,y);ctx.stroke();ctx.setLineDash([]);ctx.beginPath();ctx.arc(x,y,10,0,Math.PI*2);ctx.stroke();if(typeof data.anchor.virtual_ground_y==='number'){ctx.strokeStyle='#1684bb';ctx.beginPath();ctx.moveTo(0,data.anchor.virtual_ground_y);ctx.lineTo(1024,data.anchor.virtual_ground_y);ctx.stroke();}ctx.restore();}
async function render(){const token=++drawToken,s=sequence[frame],p=s[$('stage').value];ctx.clearRect(0,0,1024,1024);$('seek').value=frame;$('counter').textContent=`${frame+1}/${sequence.length}`;$('timing').textContent=`${s.duration_ms} ms/帧 · ${sequence.reduce((sum,slot)=>sum+slot.duration_ms,0)} ms/完整动作 · 编号从 000 开始 · 预览定时受浏览器调度影响`;$('empty').hidden=!!p;$('empty').textContent='此槽位未生成';Array.from($('frames').children).forEach((b,i)=>{b.className='frame'+(sequence[i][$('stage').value]?' available':'')+(i===frame?' active':'');});$('links').replaceChildren();
if(!p){$('detail').textContent=s.id+'\n缺失，未生成图像。';overlay();return;}
const v=p.provenance;$('detail').textContent=`${p.path}\n${p.width??'?'}×${p.height??'?'} ${p.mode??'?'}\n技术检查：${p.technical_passed?'通过':'待处理'}\n真实原生单帧：${v.native_frame_size?.join('×')??'未确认'}\n来源：${v.status}\n视觉验收：${v.visual_passed?'人工记录通过':'未通过或未记录'}\n实际型号/质量：${data.sources[v.selected_source_id]?.actual_model??'未确认'} / ${data.sources[v.selected_source_id]?.actual_quality??'未确认'}\nSHA256：${p.sha256??'无'}\n${[...p.errors,...p.warnings,...v.issues].join('\n')}`;
const a=document.createElement('a');a.href=url(p.path);a.target='_blank';a.textContent='打开原始 PNG';$('links').append(a);v.source_ids.forEach(id=>{const r=data.sources[id];if(r){const div=document.createElement('div'),link=document.createElement('a');link.href=sourcePrefix+r.record.split('/').map(encodeURIComponent).join('/');link.target='_blank';link.textContent=r.record;div.append(link);$('links').append(div);}});
try{const im=await load(p.path);if(token!==drawToken)return;ctx.drawImage(im,0,0);overlay();}catch(e){if(token!==drawToken)return;$('empty').hidden=false;$('empty').textContent='PNG 无法加载';overlay();}}
$('play').onclick=()=>{if(running)stop();else{running=true;$('play').textContent='暂停';schedule();}};$('prev').onclick=()=>{stop();frame=(frame+sequence.length-1)%sequence.length;render();};$('next').onclick=()=>{stop();frame=(frame+1)%sequence.length;render();};$('seek').oninput=()=>{stop();frame=Number($('seek').value);render();};$('action').onchange=rebuildDirections;$('direction').onchange=select;$('stage').onchange=select;$('speed').onchange=()=>{clearTimeout(timer);schedule();};$('anchor').onchange=render;$('zoom').onchange=()=>{const size=1024*Number($('zoom').value);$('surface').style.width=size+'px';$('surface').style.height=size+'px';};$('background').onchange=()=>{const val=$('background').value;$('surface').style.backgroundImage=val==='checker'?'':'none';$('surface').style.backgroundColor=val==='checker'?'':val;};
document.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON'].includes(document.activeElement.tagName))return;if(e.key==='ArrowLeft'){$('prev').click();e.preventDefault();}if(e.key==='ArrowRight'){$('next').click();e.preventDefault();}if(e.code==='Space'){$('play').click();e.preventDefault();}});
rebuildDirections();
</script></html>'''


def atomic_text(path, text):
    path = inside(path)
    temporary = path.with_name(path.name + ".tmp")
    inside(temporary).write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''编号推荐 000.png 起；--frame-base 1 可读取 001.png 起。
--frame-base auto 只在出现 0 或该动作最大帧号时推断；部分序列不猜编号。
来源：sources/*.json 的独立记录或 outputs/artifacts 数组，使用 file/path + sha256。
原生尺寸：nativeFrameSize: [1024,1024]；直接生成图亦支持 width/height。
派生图必须记录 derivedFrom 与 operation；图集总尺寸不等于单格原生尺寸。
视觉验收：visualReview: {status:"passed",sha256:"当前SHA",reviewer:"人工验收者",reviewedAt:"含时区时间"}。
全局锚点：角色根目录 anchor.json，含 canvas:[1024,1024],root_anchor:[x,y],virtual_ground_y:y。
检查不会新增图片；缺槽为 null；来源和视觉状态不会自动补成已通过。
Pillow 可选：有 Pillow 时解码图片检查透明度及像素重复；没有时不判技术通过。''')
    parser.add_argument("--frame-base", choices=("0", "1", "auto"), default="0")
    parser.add_argument("--output-dir", default="preview/legacy-audit", help="角色目录内的输出目录；默认 preview/legacy-audit，避免覆盖当前接地预览")
    parser.add_argument("--check-only", action="store_true", help="只输出摘要，不写任何文件")
    parser.add_argument("--strict", action="store_true", help="196 正式槽未全部可交接则退出码 2")
    args = parser.parse_args()
    if ROOT.name != CHARACTER:
        parser.error("本脚本仅限 01_ice_sword_girl 专属目录")
    output = inside(ROOT / args.output_dir)
    if output == ROOT / "preview":
        parser.error("preview/index.html由当前接地预览维护；请使用preview/legacy-audit等独立目录")
    if output == ROOT or any(output == ROOT / p or (ROOT / p) in output.parents for p in ("drafts", "final", "sources")):
        parser.error("输出须为独立预览目录，不能写角色根目录或覆盖 drafts/final/sources")
    manifest, validation = build(args.frame_base)
    print(json.dumps(manifest["summary"], ensure_ascii=False, indent=2))
    if not args.check_only:
        output.mkdir(parents=True, exist_ok=True)
        prefix = Path(os.path.relpath(ROOT, output)).as_posix().rstrip("/") + "/"
        embedded = json.dumps(manifest, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
        page = HTML.replace("__MANIFEST__", embedded).replace("__IMAGE_PREFIX__", json.dumps(prefix)).replace("__SOURCE_PREFIX__", json.dumps(prefix))
        atomic_text(output / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        atomic_text(output / "validation.json", json.dumps(validation, ensure_ascii=False, indent=2) + "\n")
        atomic_text(output / "index.html", page)
        print(f"预览：{output / 'index.html'}")
    return 2 if args.strict and not manifest["summary"]["all_frames_ready_for_handoff"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
