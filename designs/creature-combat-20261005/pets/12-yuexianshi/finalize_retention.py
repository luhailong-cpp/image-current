"""Record completed source-image cleanup without changing generation evidence."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def key(value):
    return str(Path(value).resolve()).casefold()

cleanup = read(ROOT / "cleanup.json")
deleted = {key(entry["path"]): entry for entry in cleanup["items"]}
assert cleanup["deletedCount"] == 78
assert all(not Path(entry["path"]).exists() for entry in cleanup["items"])
updated = 0
for path in (ROOT / "records").rglob("*.generation.json"):
    record = read(path)
    sources = [record.get("file"), record.get("derivedFrom", {}).get("path")]
    removed = [value for value in sources if value and key(value) in deleted]
    historical = [ref["path"] for ref in record.get("references", []) if key(ref["path"]) in deleted]
    if removed or historical:
        record["sourceRetention"] = {
            "state": "deleted-after-final-export-verification",
            "completedAt": cleanup["completedAt"],
            "cleanupRecord": "cleanup.json",
            "removedNativeSources": removed,
            "removedHistoricalGenerationInputs": historical,
            "note": "User-confirmed final-assets-only retention; original identity/style references, final runtime frames, generation parameters, prompts, receipts and SHA evidence retained. Historical generation fields remain unchanged."
        }
        save(path, record)
        updated += 1

review_path = ROOT / "records" / "cast-W" / "REVIEW.json"
review = read(review_path)
review["sourceRetention"] = "Completed: parent removed 78 exact recorded native/candidate PNG files after all 68 final frames and current references passed validation; see cleanup.json. Final runtime, previews, original identity/style references and textual provenance retained."
save(review_path, review)

readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8")
old = "按项目素材保留规则，最终导出和当前引用核实后只保留正式帧、预览与文字证据；宿主原生图及拒稿按清理记录删除，不建立图片备份。跨窗口旧身份和主要画法源不删除。"
new = "按项目素材保留规则，68 张正式帧及当前身份/画法引用核实后，已删除本批次 78 张宿主原生图、拒稿与中间图，详见 [清理记录](cleanup.json)。保留 68 张正式 PNG、6 张联系表、12 个 APNG 预览及完整文字证据；旧身份与主要画法源继续保留。记录中的历史原生路径仅用于溯源，已清理文件不再是运行或预览依赖。"
if old in readme:
    readme_path.write_text(readme.replace(old, new), encoding="utf-8")

status_path = ROOT / "STATUS.md"
status = status_path.read_text(encoding="utf-8")
line = "- 清理：最终帧及当前引用通过校验后，已删除本批次78张宿主原生/拒稿/中间PNG；正式68帧、预览和逐图文字证据保留，详见 cleanup.json。\n"
if line not in status:
    status = status.replace("- Git：", line + "- Git：")
    status_path.write_text(status, encoding="utf-8")
print(json.dumps({"updatedGenerationRecords": updated, "removedNativeFiles": cleanup["deletedCount"]}))
