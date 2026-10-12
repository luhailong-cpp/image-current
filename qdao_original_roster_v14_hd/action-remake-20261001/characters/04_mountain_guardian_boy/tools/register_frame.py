#!/usr/bin/env python3
"""Register one generated native frame and export its whole canvas to 1024 RGBA.

Only this character directory is writable. This does not draw, repair, align,
crop, mirror, interpolate poses, approve art, or remove the native source.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from timing_profile import RUN_FRAME_MS

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[3]
PROVENANCE = ROOT / "provenance"
CONFIG = WORKSPACE / "config" / "image-generation.json"
SPECS = {
    "run": (16, ("N", "NE", "E", "SE", "S", "SW", "W", "NW"), RUN_FRAME_MS),
    "hit": (6, ("E", "W"), 40),
    "attack": (12, ("E", "W"), 30),
    "cast": (16, ("E", "W"), 45),
}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def local_path(value: str | Path, allowed: Path, *, must_exist: bool = True) -> Path:
    path = Path(value).resolve()
    if not path.is_relative_to(allowed.resolve()):
        raise ValueError(f"路径越出允许目录 {allowed}: {path}")
    if must_exist and not path.is_file():
        raise ValueError(f"文件不存在: {path}")
    return path


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"必须为 JSON 对象: {path}")
    return payload


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def evidence_file(path: Path) -> dict:
    return {"path": relative(path), "sha256": digest(path)}


def timestamp(value) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return value if parsed.tzinfo is not None else None


def receipt_host_source(receipt: dict, source: Path) -> bool:
    # A host-generated source must be named by the supplied receipt, not merely
    # happen to live somewhere beneath generated_images.
    text = json.dumps(receipt, ensure_ascii=False).replace("\\\\", "/").replace("\\", "/").lower()
    return source.as_posix().lower() in text


def register(args) -> dict:
    count, directions, duration = SPECS[args.action]
    if args.direction not in directions or not 1 <= args.frame <= count:
        raise ValueError(f"非法帧槽: {args.action}/{args.direction}/{args.frame}")
    prompt_path = local_path(args.prompt, PROVENANCE)
    receipt_path = local_path(args.receipt, PROVENANCE)
    receipt = read_json(receipt_path)
    if not receipt_path.name.endswith(".receipt.json"):
        raise ValueError("回执须命名为 *.receipt.json，以绑定同名 *.submission.json")
    submission_path = local_path(receipt_path.with_name(receipt_path.name.removesuffix(".receipt.json") + ".submission.json"), PROVENANCE)
    submission = read_json(submission_path)
    submitted = submission.get("submittedParameters")
    if not isinstance(submitted, dict):
        raise ValueError("submission 缺少 submittedParameters 对象")
    prompt = prompt_path.read_text(encoding="utf-8-sig")
    if prompt.strip() != str(submitted.get("prompt", "")).strip():
        raise ValueError("提示词文件与真实提交中的 prompt 不一致")
    result = receipt.get("result")
    if not isinstance(result, dict) or not (result.get("image_url") or result.get("output_hint")):
        raise ValueError("回执不包含成功图像结果")

    source = Path(args.source).resolve()
    if not source.is_file():
        raise ValueError(f"原生源不存在: {source}")
    inside_provenance = source.is_relative_to(PROVENANCE.resolve())
    host_roots = [Path.home() / ".codex" / "generated_images"]
    if os.environ.get("CODEX_HOME"):
        host_roots.append(Path(os.environ["CODEX_HOME"]) / "generated_images")
    host_allowed = any(source.is_relative_to(root.resolve()) for root in host_roots)
    if not inside_provenance and not (host_allowed and receipt_host_source(receipt, source)):
        raise ValueError("原生源只能位于本角色 provenance，或位于宿主 generated_images 且由当前回执明确指向")
    source_sha = digest(source)
    with Image.open(source) as opened:
        opened.load()
        if opened.format != "PNG" or opened.mode != "RGBA":
            raise ValueError(f"源必须为真实 RGBA PNG，当前 {opened.format}/{opened.mode}")
        width, height = opened.size
        if width != height or min(width, height) < 1024:
            raise ValueError(f"原生必须为至少 1024 的方形单帧，当前 {width}x{height}")
        alpha_extrema = list(opened.getchannel("A").getextrema())
        if alpha_extrema[0] == 255 or alpha_extrema[1] == 0:
            raise ValueError("源没有真实背景透明度，或整张为空")
        # Whole-canvas scaling only: no bbox/foot adjustment and no cropping.
        exported = opened.copy() if opened.size == (1024, 1024) else opened.resize((1024, 1024), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        exported.save(buffer, format="PNG")
        output_bytes = buffer.getvalue()
        output_alpha = list(exported.getchannel("A").getextrema())

    refs = submitted.get("referenced_image_paths")
    if not isinstance(refs, list) or not refs:
        raise ValueError("submission 没有可核实的参考图路径")
    references = []
    for index, value in enumerate(refs, 1):
        ref = local_path(value, WORKSPACE)
        with Image.open(ref) as opened:
            ref_size = list(opened.size)
        references.append({"inputIndex": index, "path": ref.as_posix(), "sha256": digest(ref), "pixelDimensions": ref_size, "roleEvidence": "实际用途见提交 prompt 对 reference 序号的描述"})

    frame_name = f"frame_{args.frame:02d}"
    output = local_path(ROOT / "frames" / args.action / args.direction / f"{frame_name}.png", ROOT, must_exist=False)
    sidecar = output.with_suffix(".generation.json")
    replacement = None
    if output.exists() or sidecar.exists():
        if not args.replace_sha256 or not output.is_file() or not sidecar.is_file():
            raise ValueError(f"拒绝覆盖已有登记，须显式提供经核对的旧 SHA: {output}")
        if digest(output) != args.replace_sha256:
            raise ValueError("旧帧 SHA 已变化，拒绝替换")
        previous = read_json(sidecar)
        if previous.get("sha256") != args.replace_sha256:
            raise ValueError("旧帧来源记录与像素 SHA 不一致")
        retired = PROVENANCE / args.action / f"{args.direction}_{args.frame:02d}_retired_{args.replace_sha256[:12]}.generation.json"
        replacement = {"oldFrameSha256": args.replace_sha256, "retiredRecord": relative(retired)}
    elif args.replace_sha256:
        raise ValueError("提供了替换 SHA 但旧帧不存在")
    native_path = source if inside_provenance else local_path(PROVENANCE / args.action / f"{args.direction}_{args.frame:02d}_native_{source_sha[:12]}.png", PROVENANCE, must_exist=False)
    if native_path != source and native_path.exists() and digest(native_path) != source_sha:
        raise ValueError(f"宿主源复制目的地已有不同文件: {native_path}")
    config_snapshot = read_json(CONFIG)
    exported_at = datetime.now(timezone.utc).isoformat()
    generated_at = timestamp(receipt.get("generatedAt")) or timestamp(result.get("generatedAt"))
    native_info = {"path": relative(native_path), "sha256": source_sha, "width": width, "height": height, "format": "PNG", "mode": "RGBA", "alphaExtrema": alpha_extrema}
    record = {
        "schemaVersion": 1, "character": ROOT.name, "action": args.action,
        "direction": args.direction, "frame": args.frame,
        "file": relative(output), "sha256": hashlib.sha256(output_bytes).hexdigest(),
        "generatedAt": generated_at,
        "generationTimeEvidence": {"startedAt": timestamp(submission.get("startedAt")), "completedAt": timestamp(receipt.get("completedAt")), "note": "仅返回生成时间字段才填 generatedAt；提交/完成时间是调用边界，不能冒充精确出图时刻。"},
        "exportedAt": exported_at, "width": 1024, "height": 1024, "format": "PNG", "mode": "RGBA", "alphaExtrema": output_alpha,
        "tool": submission.get("tool"), "route": "builtin",
        "configSnapshot": config_snapshot,
        "configSnapshotTiming": "导出登记时读取当前配置；当次已保存目标另见 submissionConfigTarget，不回写或补造历史配置。",
        "submissionConfigTarget": submission.get("configTarget"),
        "submittedParameters": {"model": submitted.get("model"), "quality": submitted.get("quality"), "transparent_background": submitted.get("transparent_background"), "referenced_image_paths": refs, "prompt": relative(prompt_path)},
        "actualModel": None, "actualQuality": None,
        "unverifiedReason": "宿主管理；工具未披露可核实 model/quality，目标值不能当作实际版本或质量。",
        "prompt": evidence_file(prompt_path), "references": references,
        "evidence": {"submission": evidence_file(submission_path), "receipt": evidence_file(receipt_path), "originalHostSource": source.as_posix() if not inside_provenance else None},
        "nativeSource": native_info, "derivedFrom": [native_info],
        "operation": {"type": "whole_canvas_uniform_resize" if width != 1024 else "whole_canvas_png_export", "sourceSize": [width, height], "targetSize": [1024, 1024], "scaleX": 1024 / width, "scaleY": 1024 / height, "translation": [0, 0], "resample": "LANCZOS" if width != 1024 else None, "crop": None, "bboxAlignment": False, "footAlignment": False, "mirroring": False, "poseInterpolation": False},
        "rootAnchor": {"x": 512, "y": 928, "units": "export_canvas_pixels", "status": "declared_layout_target_not_pixel_verified"},
        "frameDurationMs": duration,
        "review": {"status": args.review_status, "automaticallyApproved": False, "note": "尺寸与哈希登记不等于美术通过；review-status 是调用者显式声明。"},
        "clientIntegration": "not_integrated",
        "replacement": replacement,
    }
    # Validate every input before making the first write.
    if native_path != source and not native_path.exists():
        native_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, native_path)
    if replacement:
        retired.parent.mkdir(parents=True, exist_ok=True)
        if retired.exists() and digest(retired) != digest(sidecar):
            raise ValueError("退役文字记录冲突，拒绝覆盖")
        shutil.copy2(sidecar, retired)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(output_bytes)
    sidecar.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"output": str(output), "record": str(sidecar), "nativeSize": [width, height], "sourceSha256": source_sha, "exportSha256": record["sha256"], "reviewStatus": args.review_status}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--action", required=True, choices=tuple(SPECS))
    parser.add_argument("--direction", required=True)
    parser.add_argument("--frame", required=True, type=int)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--review-status", default="candidate_pending_visual", choices=("candidate_pending_visual", "needs_revision", "visual_passed"))
    parser.add_argument("--replace-sha256", help="明确核对的被替换帧 SHA；先读取所有参考后再写新帧，保留旧来源文字记录")
    args = parser.parse_args()
    try:
        print(json.dumps(register(args), ensure_ascii=False, indent=2))
    except (OSError, ValueError, SyntaxError) as error:
        parser.exit(1, f"登记失败: {error}\n")


if __name__ == "__main__":
    main()
