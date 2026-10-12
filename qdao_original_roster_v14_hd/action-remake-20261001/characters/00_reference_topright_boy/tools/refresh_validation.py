"""Bind current technical checks and review limitations to the actual exported snapshot."""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report_path = ROOT / "review/technical_report.json"
    report = read(report_path)
    manifest = read(ROOT / "manifest.json")
    sources = read(ROOT / "sources.json")
    notes = read(ROOT / "review/visual-notes.json")
    previous = read(ROOT / "review/current-validation.json")
    manifest_mismatches, source_mismatches, selection_mismatches = [], [], []
    by_file = {f["file"]: f for f in manifest["frames"]}
    for f in manifest["frames"]:
        path = ROOT / f["file"]
        actual = sha(path)
        if actual != f["sha256"]:
            manifest_mismatches.append(f["file"])
        if actual != sources["frames"][f["file"].removeprefix("frames/")]["export_sha256"]:
            source_mismatches.append(f["file"])
    for f in read(ROOT / "selected-new.json"):
        key = f"frames/{f['action']}/{f['direction']}/{f['frame']:02d}.png"
        exported = by_file.get(key)
        if not exported or sha(ROOT / f["source"]) != exported["derivedFrom"]["sha256"]:
            selection_mismatches.append(key)
    report_mismatches = []
    for f in report["frames"]:
        if f["exists"]:
            current = sha(ROOT / "frames" / f["key"])
            if current != f.get("sha256"):
                report_mismatches.append(f["key"])
    integrity = not (manifest_mismatches or source_mismatches or selection_mismatches or report_mismatches)
    technical = dict(report["summary"])
    for key in ("duplicate_file_groups", "duplicate_pixel_groups", "unexpected_pngs"):
        technical[key] = report[key]
    technical.update(manifest_png_sha_mismatches=manifest_mismatches,
                     sources_export_sha_mismatches=source_mismatches,
                     selection_source_mismatches=selection_mismatches,
                     technical_report_sha_mismatches=report_mismatches,
                     snapshot_integrity_pass=integrity)
    old_browser = previous.get("preview", {}).get("browser_check", {})
    old_browser["historical_attempt"] = True
    old_browser["note"] = "历史本地file页面导航被策略拒绝；本次未绕过。不能把旧尝试写成新节奏页已实播。"
    timing_path = ROOT / "review/timing-grounding/review-data.json"
    timing = read(timing_path) if timing_path.exists() else {}
    timing_sources_match = all(sha(ROOT / f["file"]) == f["sha256"] for f in timing.get("sources", [])) if timing else False
    state = {
        "character": "00_reference_topright_boy",
        "validated_at": datetime.now(timezone(timedelta(hours=-4))).isoformat(),
        "timezone": "America/New_York",
        "status": "complete_candidates_technical_pass_art_pending" if technical["fully_measured_technical_pass"] and integrity else "candidates_technical_or_snapshot_checks_pending",
        "snapshot": {"technical_report_generated_at": report["generated_at"], "technical_report_sha256": sha(report_path),
                     "manifest_sha256": sha(ROOT / "manifest.json"), "selection_sha256": sha(ROOT / "selected-new.json"),
                     "scope": "仅绑定本次实际PNG和来源SHA；修改任意选帧后须重跑。"},
        "technical": technical,
        "sequences": report["sequence_summary"],
        "preview": {"path": "review/index.html", "browser_check": old_browser,
                    "dynamic_visual_playback_verified": False,
                    "player_logic_verification": read(ROOT / "review/player-validation.json") if (ROOT / "review/player-validation.json").exists() else None,
                    "encoded_animation_verification": read(ROOT / "review/animations/timing-validation.json") if (ROOT / "review/animations/timing-validation.json").exists() else None,
                    "run_timing": {"path": "review/timing-grounding/index.html", "cycles_ms": [960],
                                          "uniform_frame_ms": 60, "phase_weights_applied": False,
                                          "source_hashes_current": timing_sources_match, "final_timing_adopted": True, "adoption_scope": "offline_only", "adopted_timing": manifest["runTiming"]},
                    "combat_frame_ms": {"hit": 40, "attack": 30, "cast": 45}},
        "art": {"fully_approved_sequences": 0, "final_approved_frames": 0, "dynamic_art_approved": False,
                "client_run": False, "static_findings": notes["frames"], "run_review": notes["actions"]["run"],
                "pending": ["正常显示尺寸的接地、摆臂、首尾和跨方向连续性实播", "可信根点与世界地面校准", "客户端位移速度和滑步检查"]},
        "notes": ["196个槽位齐全与美术完成分别统计。", "新修订为内置图像工具原生编辑；导出仅每方向固定整画布变换。", "未披露模型和质量继续为null；不按配置推定实际返回。", ("本机客户端目录现已存在；本素材任务未接入、未运行。" if Path('D:/work/mmorpg-client').exists() else "本机未发现客户端目录；未接入、未运行。")]
    }
    target = ROOT / "review/current-validation.json"
    temporary = target.with_suffix(".write-tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    print(json.dumps({"technical": technical, "timing_sources_current": timing_sources_match}))
    return 0 if technical["fully_measured_technical_pass"] and integrity else 1


if __name__ == "__main__":
    raise SystemExit(main())
