"""Finalize this character's source retention after export and visual review.

Default: read-only preflight. Pass --apply to record the plan in cleanup.json,
remove only verified work/**/*.png and provenance/**/contact-sheet.jpg,
and mark the retained evidence. This never regenerates images or deletes
external generated_images, shared identity/style inputs, or preview files.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
PROVENANCE = ROOT / "provenance"
SPECS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve(value):
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def inside(path, directory=ROOT):
    return path.is_relative_to(directory.resolve()) and path != directory.resolve()


def relative(path):
    require(inside(path), f"Outside character directory: {path}")
    return path.relative_to(ROOT).as_posix()


def save(path, value):
    path = path.resolve()
    require(inside(path), f"Refusing external metadata write: {path}")
    # A same-directory temporary text file permits atomic replacement.
    temporary = path.with_name(path.name + ".retention-tmp")
    require(not temporary.exists(), f"Unresolved metadata temporary file: {temporary}")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def deletion_allowed(path):
    resolved = path.resolve()
    require(inside(resolved), f"Deletion target escapes this character: {resolved}")
    require(not path.is_symlink(), f"Refusing symbolic link: {path}")
    return ((inside(resolved, WORK) and resolved.suffix.lower() == ".png")
            or (inside(resolved, PROVENANCE) and resolved.name == "contact-sheet.jpg"))


def verify_delivery():
    manifest_path = ROOT / "manifest.json"
    validation_path = ROOT / "validation.json"
    manifest = load(manifest_path)
    validation = load(validation_path)
    require(manifest.get("expectedFrames") == manifest.get("presentFrames") == 68,
            "Manifest is not a complete 68-frame delivery")
    require(manifest.get("technicalStatus") == validation.get("technicalStatus") == "passed",
            "Export/validation must pass before source cleanup")
    require(validation.get("presentFrames") == 68 and not validation.get("errors")
            and not validation.get("missingFrames"), "Validation reports missing or invalid frames")
    frames = manifest.get("frames", [])
    require(len(frames) == 68, "Manifest frames must contain exactly 68 entries")
    by_id = {frame["id"]: frame for frame in frames}
    require(len(by_id) == 68, "Duplicate manifest frame IDs")
    expected_ids = {f"{action}/{direction}/{n:02}" for action, (count, _) in SPECS.items()
                    for direction in ("E", "W") for n in range(1, count + 1)}
    require(set(by_id) == expected_ids, "Manifest frame IDs do not match six required groups")
    groups = manifest.get("groups", [])
    require(len(groups) == 6, "Expected six groups")
    for action, (count, duration) in SPECS.items():
        for direction in ("E", "W"):
            matches = [g for g in groups if g.get("id") == f"{action}-{direction}"]
            require(len(matches) == 1, f"Missing/duplicate group {action}-{direction}")
            group = matches[0]
            require(group.get("presentFrames") == group.get("expectedFrames") == count
                    and group.get("durationMs") == duration and group.get("complete"),
                    f"Incomplete group {group['id']}")
            require(group.get("frames") == [by_id[f"{action}/{direction}/{n:02}"]
                                            for n in range(1, count + 1)],
                    f"Group/frame records disagree: {group['id']}")
    sums = {}
    for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        sha, name = line.split(maxsplit=1)
        name = name.lstrip("*")
        require(name not in sums, f"Duplicate SHA256SUMS path: {name}")
        sums[name] = sha
    runtime_names = {f"runtime/{key}.png" for key in expected_ids}
    require(set(sums) == runtime_names, "SHA256SUMS does not match all 68 runtime paths")
    actual_runtime = {relative(p.resolve()) for p in (ROOT / "runtime").rglob("*.png")}
    require(actual_runtime == runtime_names, "Runtime PNG set differs from the manifest")
    protected = {manifest_path: digest(manifest_path), validation_path: digest(validation_path),
                 ROOT / "SHA256SUMS.txt": digest(ROOT / "SHA256SUMS.txt")}
    current_sources = {}
    exports = {}
    for key in sorted(expected_ids):
        frame = by_id[key]
        expected_runtime = f"runtime/{key}.png"
        require(frame.get("file") == expected_runtime, f"Unexpected runtime path: {key}")
        runtime = resolve(expected_runtime)
        require(inside(runtime, ROOT / "runtime") and runtime.is_file(), f"Invalid runtime: {runtime}")
        current_hash = digest(runtime)
        require(current_hash == frame.get("sha256") == sums[expected_runtime], f"Runtime SHA mismatch: {key}")
        with Image.open(runtime) as image:
            require(image.mode == "RGBA" and image.size == (1024, 1024), f"Runtime dimensions/mode: {key}")
            require(image.getchannel("A").getextrema() == (0, 255), f"Runtime alpha: {key}")
            require(hashlib.sha256(image.tobytes()).hexdigest() == frame.get("pixelSha256"),
                    f"Decoded pixel SHA mismatch: {key}")
        generation_path = resolve(f"provenance/{key}.json")
        export_path = resolve(f"provenance/export/{key}.json")
        require(frame.get("generationRecord") == relative(generation_path)
                and frame.get("exportRecord") == relative(export_path), f"Unexpected evidence path: {key}")
        generation = load(generation_path)
        exported = load(export_path)
        source = resolve(generation["file"])
        require(inside(source, WORK), f"Current generation source is outside work: {key}")
        require(exported.get("file") == expected_runtime and exported.get("sha256") == current_hash,
                f"Export/runtime mismatch: {key}")
        derived = exported.get("derivedFrom", {})
        require(resolve(derived.get("file", "")) == source
                and generation.get("sha256") == frame.get("sourceSha256") == derived.get("sha256"),
                f"Generation/export source mismatch (rebuild required): {key}")
        require(source.is_file() and digest(source) == generation["sha256"],
                f"Native source unavailable or mismatched before cleanup: {key}")
        prompt = resolve(generation.get("prompt", ""))
        receipt = resolve(generation.get("evidence", {}).get("receipt", ""))
        require(inside(prompt) and prompt.is_file() and inside(receipt) and receipt.is_file(),
                f"Prompt/receipt unavailable: {key}")
        protected[runtime] = current_hash
        protected[prompt] = digest(prompt)
        protected[receipt] = digest(receipt)
        current_sources[source] = {"runtime": expected_runtime, "sha256": generation["sha256"]}
        exports[export_path] = exported
    # Preserve every preview and every prompt/receipt, including historical text.
    for folder in (ROOT / "preview", ROOT / "prompts"):
        for path in folder.rglob("*"):
            if path.is_file():
                require(inside(path.resolve()), f"Protected file escapes character root: {path}")
                protected[path.resolve()] = digest(path)
    for path in PROVENANCE.rglob("*.receipt.json"):
        protected[path.resolve()] = digest(path)
    return current_sources, exports, protected


def make_plan(current_sources, exports, protected):
    records = {}
    by_source_hash = {}
    original_record_hashes = {}
    for action in SPECS:
        for direction in ("E", "W"):
            for path in sorted((PROVENANCE / action / direction).glob("*.json")):
                data = load(path)
                if not isinstance(data, dict) or not all(k in data for k in ("file", "sha256", "prompt", "submittedParameters")):
                    continue
                path = path.resolve()
                records[path] = data
                original_record_hashes[path] = digest(path)
                source = resolve(data["file"])
                # External source evidence is preserved verbatim; never inspect or remove it.
                if inside(source, WORK):
                    require(source.is_file() and digest(source) == data["sha256"],
                            f"Historical source record mismatch: {relative(path)} -> {source}")
                    by_source_hash.setdefault(data["sha256"], []).append((source, path))
                for value in (data.get("prompt"), data.get("evidence", {}).get("receipt")):
                    require(value, f"Missing retained text evidence: {relative(path)}")
                    retained = resolve(value)
                    require(inside(retained) and retained.is_file(), f"Missing retained text: {value}")
                    protected[retained] = digest(retained)
    targets = []
    for path in sorted(WORK.rglob("*.png")):
        require(deletion_allowed(path), f"Target not permitted: {path}")
        source = path.resolve()
        sha = digest(source)
        evidence = [relative(p) for candidate, p in by_source_hash.get(sha, []) if candidate == source]
        require(evidence, f"Unrecorded work image will not be removed: {source}")
        targets.append({"path": relative(source), "absolutePath": str(source), "sha256": sha,
                        "reason": "exported-native-source" if source in current_sources else "historical-rejected-source",
                        "generationRecords": evidence, "status": "planned"})
    for path in sorted(PROVENANCE.rglob("contact-sheet.jpg")):
        require(deletion_allowed(path), f"Target not permitted: {path}")
        targets.append({"path": relative(path.resolve()), "absolutePath": str(path.resolve()),
                        "sha256": digest(path), "reason": "redundant-working-contact-sheet; formal-preview-retained",
                        "status": "planned"})
    target_paths = {resolve(item["path"]) for item in targets}
    require(set(current_sources).issubset(target_paths), "Not all current native sources appear in cleanup plan")
    require(not (target_paths & set(protected)), "Cleanup plan includes a protected file")
    updated = {}
    remaps = []
    stamp = now()
    for path, original in records.items():
        record = copy.deepcopy(original)
        for ref in record.get("references", []):
            old_path = resolve(ref["path"])
            expected_sha = ref.get("sha256")
            require(expected_sha, f"Reference SHA missing: {relative(path)}")
            if not inside(old_path, WORK):
                # Shared/external identities and styles remain outside the write surface.
                continue
            if not old_path.is_file() or digest(old_path) != expected_sha:
                candidates = by_source_hash.get(expected_sha, [])
                require(candidates, f"No historical source matches reference SHA: {relative(path)} -> {ref['path']}")
                # Prefer a rejected/attempt record over an unrelated equal-hash path.
                candidate, source_record = sorted(candidates,
                    key=lambda pair: (not any(s in pair[0].name for s in ("rejected", "attempt")), str(pair[0])))[0]
                submitted_path = ref.get("submittedPath", ref["path"])
                remaps.append({"record": relative(path), "submittedPath": submitted_path,
                               "oldMetadataPath": ref["path"], "resolvedHistoricalPath": str(candidate),
                               "sha256": expected_sha, "sourceGenerationRecord": relative(source_record)})
                ref["submittedPath"] = submitted_path
                ref["path"] = str(candidate)
                ref["sourceGenerationRecord"] = relative(source_record)
                ref["pathRole"] = "historical-source-resolved-by-sha; submittedPath preserves original tool input"
                old_path = candidate
            require(old_path in target_paths, f"Internal reference not covered by cleanup evidence: {old_path}")
            ref["availability"] = "removed-after-final-export"
            ref["retentionRecord"] = "cleanup.json"
        source = resolve(record["file"])
        if source in target_paths:
            record["sourceAvailability"] = "removed-after-final-export"
            record["retentionRecord"] = "cleanup.json"
            record["sourceRemovedAt"] = stamp
        require(record.get("submittedParameters") == original.get("submittedParameters"),
                f"Submitted parameters would be changed: {relative(path)}")
        if record != original:
            updated[path] = record
    for path, original in exports.items():
        updated[path] = copy.deepcopy(original)
        updated[path]["sourceAvailability"] = "removed-after-final-export"
        updated[path]["retentionRecord"] = "cleanup.json"
        original_record_hashes[path] = digest(path)
    plan = {"schemaVersion": 1, "plannedAt": stamp, "status": "planned",
            "root": str(ROOT), "policy": "Keep runtime, formal preview, design and all textual generation evidence; no image backups",
            "verifiedRuntimeFrames": 68, "deletedImages": targets, "referenceRemaps": remaps,
            "metadataFiles": [relative(path) for path in sorted(updated)],
            "untouched": ["runtime/**", "preview/**", "prompts/**", "all receipt text", "external generated_images", "shared identity/style references"],
            "limitations": "Historical source SHA and pre-cleanup verification survive; deleted AI pixels cannot be reconstructed from text."}
    return plan, updated, original_record_hashes


def check_unchanged(files):
    for path, sha in files.items():
        require(path.is_file() and digest(path) == sha, f"File changed during cleanup preparation: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write cleanup evidence, then perform the verified scoped cleanup")
    args = parser.parse_args()
    cleanup_path = ROOT / "cleanup.json"
    require(not cleanup_path.exists(), "cleanup.json already exists; inspect its transaction state before any further cleanup")
    sources, exports, protected = verify_delivery()
    plan, updates, record_hashes = make_plan(sources, exports, protected)
    check_unchanged(protected)
    check_unchanged(record_hashes)
    summary = {"mode": "apply" if args.apply else "read-only-preflight", "runtimeVerified": 68,
               "imageTargets": len(plan["deletedImages"]), "referenceRemaps": len(plan["referenceRemaps"]),
               "metadataUpdates": len(updates)}
    if not args.apply:
        print(json.dumps({**summary, "plan": plan}, ensure_ascii=False, indent=2))
        return
    # Full plan and every target SHA are committed to text before the first unlink.
    save(cleanup_path, plan)
    try:
        for item in plan["deletedImages"]:
            target = resolve(item["path"])
            require(str(target) == item["absolutePath"] and deletion_allowed(target),
                    f"Target changed or escaped scope: {target}")
            require(target.is_file() and digest(target) == item["sha256"], f"Target changed before removal: {target}")
            target.unlink()
            item["status"] = "removed"
            item["removedAt"] = now()
            save(cleanup_path, plan)
        check_unchanged(protected)
        check_unchanged(record_hashes)
        for path, record in updates.items():
            save(path, record)
        check_unchanged(protected)
        require(all(not resolve(item["path"]).exists() for item in plan["deletedImages"]), "Some deletion targets remain")
        plan["status"] = "completed"
        plan["completedAt"] = now()
        plan["retainedRuntimeAndTextHashesVerified"] = True
        save(cleanup_path, plan)
    except Exception as error:
        plan["status"] = "incomplete"
        plan["error"] = str(error)
        plan["stoppedAt"] = now()
        save(cleanup_path, plan)
        raise
    print(json.dumps({**summary, "status": "completed", "cleanupRecord": str(cleanup_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
