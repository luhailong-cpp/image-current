"""List unselected generation PNGs. No deletion without --apply.

After final merge/export: --save-plan --sw-finalized; inspect plan; then --apply.
The fixed plan and result files live in review/. Text evidence is never removed.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = (ROOT / "generation").resolve()
PLAN = ROOT / "review/final-cleanup-plan.json"
RESULT = ROOT / "review/final-cleanup-executed.json"
SNAPSHOTS = ("selected-new.json", "sources.json", "manifest.json")


def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(value):
    p = Path(str(value).replace("\\", "/"))
    return (p if p.is_absolute() else ROOT / p).resolve()


def inspect(sw_finalized):
    snapshot = {name: sha(ROOT / name) for name in SNAPSHOTS}
    selected, sources, manifest = [read(ROOT / name) for name in SNAPSHOTS]
    assert len(selected) == 145 and len(manifest["frames"]) == 196
    current, proposed, skipped = set(), [], []
    by_file = {row["file"]: row for row in manifest["frames"]}
    assert len(by_file) == 196 and len(sources["frames"]) == 196
    for row in manifest["frames"]:
        export = resolve(row["file"])
        assert export.is_relative_to(ROOT / "frames") and sha(export) == row["sha256"]
        native = resolve(row["derivedFrom"]["file"])
        native_sha = sha(native)
        assert native_sha == row["derivedFrom"]["sha256"]
        index = sources["frames"][row["file"].removeprefix("frames/")]
        assert resolve(index["source_path"]) == native
        assert index["source_sha256"] == native_sha and index["export_sha256"] == row["sha256"]
        current.add(native)
    selected_paths = set()
    selected_slots = {}
    for row in selected:
        native = resolve(row["source"])
        assert native.is_relative_to(GEN) and native.is_file()
        selected_paths.add(native)
        key = f'frames/{row["action"]}/{row["direction"]}/{row["frame"]:02d}.png'
        assert resolve(by_file[key]["derivedFrom"]["file"]) == native
        selected_slots[(row["action"], row["direction"], row["frame"])] = native
    assert len(selected_paths) == 145
    current.update(selected_paths)
    # Before merge, preserve proposed final selections as well as current exports.
    for path in sorted((ROOT / "generation/run").glob("*/selection-middle4-side2-20261004.json")):
        document = read(path)
        rows = document if isinstance(document, list) else document["frames"]
        for row in rows:
            native = resolve(row["source"])
            assert native.is_relative_to(GEN)
            current.add(native)
            if sw_finalized:
                direction = row.get("direction", path.parent.name)
                assert selected_slots[("run", direction, row["frame"])] == native, "Direction selections are not merged; do not finalize cleanup"
    for path in sorted(GEN.rglob("*.png")):
        if path.is_symlink():
            skipped.append({"file": path.relative_to(ROOT).as_posix(), "reason": "Symbolic link requires manual review"})
            continue
        absolute = path.resolve()
        assert absolute.is_relative_to(GEN) and absolute.is_relative_to(ROOT)
        if absolute in current:
            continue
        if not sw_finalized and absolute.is_relative_to(GEN / "run/SW"):
            skipped.append({"file": path.relative_to(ROOT).as_posix(), "reason": "SW work in progress protected"})
            continue
        record_path = Path(str(path) + ".generation.json")
        if not record_path.is_file() or read(record_path).get("sha256") != sha(path):
            skipped.append({"file": path.relative_to(ROOT).as_posix(), "reason": "Missing or mismatched text source record; manual review"})
            continue
        proposed.append({"file": path.relative_to(ROOT).as_posix(), "absolutePath": absolute.as_posix(),
                         "sha256": sha(path), "bytes": path.stat().st_size,
                         "retainedRecord": record_path.relative_to(ROOT).as_posix(),
                         "recordSha256": sha(record_path)})
    assert snapshot == {name: sha(ROOT / name) for name in SNAPSHOTS}, "Indices changed during inventory"
    return {"createdAtUtc": datetime.now(timezone.utc).isoformat(), "scopeRoot": ROOT.as_posix(),
            "snapshot": snapshot, "swFinalized": sw_finalized, "currentNativeSourcesProtected": 145,
            "formalExportsProtected": 196, "proposed": proposed, "skipped": skipped,
            "note": "Only listed unselected generation PNG files; no recursive deletion, no other files, no text evidence, no exports, no external directories."}


def save(path, value):
    temp = path.with_name(path.name + ".write-tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def main():
    if not __debug__:
        raise RuntimeError("Do not run cleanup with Python optimization; safety assertions must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-plan", action="store_true", help="Save current read-only plan to review/final-cleanup-plan.json")
    parser.add_argument("--apply", action="store_true", help="Apply the existing exact plan after all snapshot and file checks pass")
    parser.add_argument("--sw-finalized", action="store_true", help="Explicitly mark SW work complete when creating a fresh plan; requires all direction selections merged")
    args = parser.parse_args()
    if args.apply:
        assert not args.save_plan and not args.sw_finalized, "Apply only the existing reviewed plan, without rebuilding it"
        plan = read(PLAN)
        assert plan["scopeRoot"] == ROOT.as_posix()
        assert plan["snapshot"] == {name: sha(ROOT / name) for name in SNAPSHOTS}, "Stale cleanup plan; rebuild after final merge/export"
        fresh = inspect(plan["swFinalized"])
        assert fresh["snapshot"] == plan["snapshot"] and fresh["proposed"] == plan["proposed"], "Plan/files changed; rebuild"
        for item in plan["proposed"]:
            target = resolve(item["file"])
            assert target.is_relative_to(GEN) and target.is_relative_to(ROOT) and target.suffix.lower() == ".png"
            assert target.as_posix() == item["absolutePath"] and sha(target) == item["sha256"]
            assert sha(resolve(item["retainedRecord"])) == item["recordSha256"]
        # Every absolute target has been checked before any deletion; no shell or recursion.
        result = {"atUtc": datetime.now(timezone.utc).isoformat(), "snapshot": plan["snapshot"], "removed": [], "status": "in_progress"}
        save(RESULT, result)
        for item in plan["proposed"]:
            assert plan["snapshot"] == {name: sha(ROOT / name) for name in SNAPSHOTS}, "Indices changed during deletion; stop"
            target = resolve(item["file"])
            assert target.is_relative_to(GEN) and sha(target) == item["sha256"], "Target changed; stop"
            target.unlink()
            result["removed"].append(item)
            save(RESULT, result)
        result["status"] = "complete"
        save(RESULT, result)
        print(json.dumps({"removedPngs": len(result["removed"]), "textRecordsPreserved": True}))
    else:
        plan = inspect(args.sw_finalized)
        if args.save_plan:
            save(PLAN, plan)
        print(json.dumps({"proposedPngs": len(plan["proposed"]), "bytes": sum(r["bytes"] for r in plan["proposed"]),
                          "skipped": len(plan["skipped"]), "swProtected": not args.sw_finalized,
                          "files": [r["file"] for r in plan["proposed"]], "planSaved": args.save_plan}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
