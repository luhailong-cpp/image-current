"""Retire obsolete image QA snapshots; preserve their text and hashes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
note = "> 历史快照（2026-10-05）：本记录保留原验收经过，不能代表2026-10-08修后的当前像素。当前验收及SHA以根目录README、qa/final-visual-review.json为准。原接触图已清理，当前全帧图位于qa/contact。\n\n"
for name in ("qa/attack/DELIVERY.md", "qa/attack/E-static-review.md", "qa/attack/W-static-review.md", "qa/attack/W-handoff.md", "qa/cast/E-visual-review.md"):
    p = ROOT / name
    content = p.read_text(encoding="utf-8-sig")
    if not content.startswith(note):
        p.write_text(note + content, encoding="utf-8")
p = ROOT / "qa/attack/review-20261008.md"
content = p.read_text(encoding="utf-8-sig")
repair_note = "> 历史修前检查：本记录指出的W09→10问题已完成定点修复；当前结论以final-static-review-20261008.md和根目录qa/final-visual-review.json为准。\n\n"
if not content.startswith(repair_note):
    p.write_text(repair_note + content, encoding="utf-8")
for name in ("qa/attack/W-technical.json", "qa/cast/E-technical.json", "qa/cast/W/technical-check.json", "qa/cast/W/static-review.json"):
    p = ROOT / name
    value = json.loads(p.read_text(encoding="utf-8-sig"))
    if isinstance(value, dict):
        value["historicalSnapshotOnly"] = True
        value["supersededBy"] = "qa/final-visual-review.json"
        p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

report_path = ROOT / "qa/obsolete-preview-cleanup.json"
rows = json.loads(report_path.read_text(encoding="utf-8"))["files"] if report_path.exists() else []
for name in ("qa/attack/E-contact-sheet.png", "qa/attack/W-contact-sheet.png", "qa/cast/E-contact-sheet.png", "qa/cast/W/contact.png"):
    p = (ROOT / name).resolve()
    assert p.is_relative_to(ROOT.resolve()) and p.parent.is_relative_to((ROOT / "qa").resolve())
    if p.exists():
        rows.append({"file": name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "deleted": True,
                     "reason": "Superseded or duplicate QA raster; final runtime and current qa/contact retained."})
        p.unlink()
report_path.write_text(json.dumps({"recordedAt": datetime.now(timezone.utc).isoformat(), "files": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"retiredQaImages": len(rows)}))
