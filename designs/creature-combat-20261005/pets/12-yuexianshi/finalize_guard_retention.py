"""Annotate removed repair pixels without changing historical generation evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def normalize(value):
    path = Path(value)
    return str((path if path.is_absolute() else ROOT / path).resolve()).casefold()

def main():
    cleanup = read(ROOT / "cleanup-guardfix.json")
    removed = {normalize(item["path"]): item for item in cleanup["items"]}
    assert len(removed) == cleanup["deletedCount"]
    assert all(not Path(item["path"]).exists() for item in removed.values())
    assert len(list((ROOT / "runtime").rglob("*.png"))) == 68
    updated = 0
    paths = list((ROOT / "records").rglob("*.generation.json"))
    paths += list((ROOT / "repair-inputs").glob("*.input.json"))
    for path in paths:
        record = read(path)
        references = [record.get("file"), record.get("derivedFrom", {}).get("path")]
        references += [reference.get("path") for reference in record.get("references", [])]
        affected = sorted({normalize(value) for value in references if value} & removed.keys())
        if not affected:
            continue
        record["repairSourceRetention"] = {
            "state": "pixels-deleted-after-final-export-and-reference-verification",
            "completedAt": cleanup["completedAt"],
            "cleanupRecord": "cleanup-guardfix.json",
            "sources": [{"path": removed[key]["path"], "sha256": removed[key]["sha256"]} for key in affected],
            "preserved": "Original generation parameters, prompts, receipts, source hashes, final runtime pixels and current identity/style references.",
        }
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        updated += 1
    print(json.dumps({"deletedRepairPixels": len(removed), "annotatedProvenanceRecords": updated}))

if __name__ == "__main__":
    main()
