"""Promote a SHA-bound 128-frame run position plan; never regenerate deleted natives.

Check (read-only):
  python tools/promote-position-run.py --check
Accept externally after visual review, using check's selectionSha256/preimageSha256:
  {"accepted": true, "selectionSha256": "...", "preimageSha256": "...",
   "clientValidated": false}
Promote (only when explicitly authorized):
  python tools/promote-position-run.py --promote

All sources, source sidecars and original rows are cached before the first write.
Old evidence is preserved as text, without image backups. Each file replacement is
atomic; caught write/verification failures restore the original run files from
memory. This is not a filesystem-wide atomic transaction across process crashes.
Preview rebuilding and cleanup remain the caller's responsibility.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DIRS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
EVIDENCE = "provenance/ground-contact-20261004"
DEFAULT_PLAN = EVIDENCE + "/position-selection-all.json"
DEFAULT_ACCEPTANCE = EVIDENCE + "/position-acceptance.json"
DEFAULT_REPORT = EVIDENCE + "/position-promotion.json"
TOP_FILES = ("final-selection.json", "final/manifest.json",
             "registration.json", "animation-timing.json")


class PromotionError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise PromotionError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def canonical_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def decode(data, label):
    try:
        return json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PromotionError(f"{label}: invalid UTF-8 JSON: {exc}") from exc


def inside(relative):
    require(isinstance(relative, str) and relative and
            not Path(relative).is_absolute(), f"Expected relative path: {relative!r}")
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT.resolve()), f"Path escapes character root: {relative}")
    return path


def read_bytes(relative):
    try:
        return inside(relative).read_bytes()
    except OSError as exc:
        raise PromotionError(f"Cannot read {relative}: {exc}") from exc


def safe_png_check(data, label):
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.load()
            require(im.format == "PNG" and im.size == (1024, 1024) and im.mode == "RGBA",
                    f"{label}: expected native delivery PNG 1024x1024 RGBA")
            alpha = im.getchannel("A")
            require(alpha.getextrema() == (0, 255), f"{label}: invalid alpha range")
            border = max(alpha.crop(box).getextrema()[1] for box in
                         ((0, 0, 1024, 1), (0, 1023, 1024, 1024),
                          (0, 0, 1, 1024), (1023, 0, 1024, 1024)))
            require(border == 0, f"{label}: nontransparent delivery border")
    except OSError as exc:
        raise PromotionError(f"{label}: cannot read PNG: {exc}") from exc


def validate_lineage(meta, data, label, direction, registration, expected_native=None):
    require(meta.get("file") == label, f"{label}: sidecar file field does not match source")
    require(meta.get("sha256") == sha(data), f"{label}: sidecar SHA mismatch")
    source, generation = meta.get("source", {}), meta.get("sourceGeneration", {})
    native = source.get("sha256")
    require(isinstance(native, str) and len(native) == 64, f"{label}: native SHA missing")
    require(native == generation.get("sha256"), f"{label}: embedded native lineage SHA mismatch")
    if expected_native is not None:
        require(native == expected_native, f"{label}: planned native SHA mismatch")
    require(isinstance(source.get("file"), str) and source["file"],
            f"{label}: native source path missing")
    require(min(source.get("nativeSize", [0, 0])) >= 1024,
            f"{label}: native source dimensions below 1024")
    require(meta.get("actualModel") is None and meta.get("actualQuality") is None,
            f"{label}: actual model/quality evidence must remain undisclosed/null")
    transform = meta.get("transform", {})
    require(transform.get("globalScale") == registration["globalScale"] == 0.65,
            f"{label}: common scale mismatch")
    require(transform.get("sourceRoot") == registration["sequences"]["run/" + direction]["sourceRoot"],
            f"{label}: direction root mismatch")
    require(transform.get("targetRoot") == registration["targetRoot"] == [512, 942],
            f"{label}: target root mismatch")
    require(transform.get("perFrameNormalization") is False,
            f"{label}: per-frame normalization is forbidden")
    return native


def collect(plan_relative):
    plan_data = read_bytes(plan_relative)
    value = decode(plan_data, plan_relative)
    plan = value.get("directionSelections") if isinstance(value, dict) else value
    require(isinstance(plan, list) and len(plan) == 128,
            "Position plan must contain exactly 128 rows (array or directionSelections array)")
    top = {name: read_bytes(name) for name in TOP_FILES}
    rows = decode(top["final-selection.json"], "final-selection.json")
    manifest = decode(top["final/manifest.json"], "final/manifest.json")
    registration = decode(top["registration.json"], "registration.json")
    timing = decode(top["animation-timing.json"], "animation-timing.json")
    require(len(rows) == 196 and manifest.get("frames") == rows,
            "Current final-selection and manifest must agree on all 196 frames")
    require(timing["run"]["frameMs"] == 75 and timing["run"]["cycleMs"] == 1200
            and timing["run"]["uniform"] is True, "Run timing must remain 16 x 75ms = 1200ms")
    require(registration["globalScale"] == 0.65 and registration["targetRoot"] == [512, 942],
            "Registration must remain global scale 0.65, target [512,942]")
    current, by_file, cache, artifacts = {}, {}, {}, []
    for row in rows:
        key = (row["action"], row["direction"], row["frame"])
        require(key not in current, f"Duplicate current slot {key}")
        require(row["file"] not in by_file, f"Duplicate current file {row['file']}")
        expected = f"final/{key[0]}/{key[1]}/{key[2]:02}.png"
        require(row["file"] == expected and row["generationRecord"] == expected + ".generation.json",
                f"Unexpected current delivery path for {key}")
        image_data = read_bytes(row["file"])
        record_data = read_bytes(row["generationRecord"])
        meta = decode(record_data, row["generationRecord"])
        require(sha(image_data) == row["sha256"] == meta.get("sha256"),
                f"Current PNG or sidecar SHA mismatch: {row['file']}")
        require(meta.get("source", {}).get("sha256") == row["nativeSha256"]
                == meta.get("sourceGeneration", {}).get("sha256"),
                f"Current native lineage mismatch: {row['file']}")
        require(meta["source"]["file"] == row["nativeSourceFile"],
                f"Current source path mismatch: {row['file']}")
        require(meta["file"] == row["file"], f"Current sidecar path mismatch: {row['file']}")
        safe_png_check(image_data, row["file"])
        current[key] = {"row": deepcopy(row), "meta": meta}
        by_file[row["file"]] = current[key]
        cache[row["file"]] = image_data
        cache[row["generationRecord"]] = record_data
        artifacts.append({"file": row["file"], "sha256": sha(image_data),
                          "generationRecord": row["generationRecord"],
                          "generationRecordSha256": sha(record_data),
                          "nativeSha256": row["nativeSha256"]})
    expected_slots = {("run", d, f) for d in DIRS for f in range(1, 17)}
    run_slots = {key for key in current if key[0] == "run"}
    require(run_slots == expected_slots and len(rows) - len(run_slots) == 68,
            "Current delivery must have all 128 run slots and 68 combat slots")
    bindings, sources, seen_slots, source_files, source_shas = [], [], set(), set(), set()
    for item in plan:
        require(isinstance(item, dict), "Plan rows must be objects")
        d, frame = item.get("direction"), item.get("targetFrame")
        require(item.get("action") == "run" and d in DIRS
                and type(frame) is int and 1 <= frame <= 16,
                f"Invalid planned slot: {item.get('action')}/{d}/{frame}")
        key = ("run", d, frame)
        require(key not in seen_slots, f"Duplicate planned target {d}/{frame:02}")
        seen_slots.add(key)
        expected_leg = "RIGHT" if frame <= 8 else "LEFT"
        require(item.get("supportLeg") == expected_leg, f"{d}/{frame:02}: wrong supportLeg")
        require(item.get("positionSegment") == ((frame - 1) % 8) // 2 + 1
                and item.get("pairOrdinal") == (frame - 1) % 2 + 1,
                f"{d}/{frame:02}: position segment/pair ordinal mismatch")
        file, record = item.get("sourceFile"), item.get("sourceGenerationRecord")
        require(isinstance(file, str) and
                (file.startswith(f"final/run/{d}/") or file.startswith(f"staging/run/{d}/")),
                f"{d}/{frame:02}: source must be from same run direction in final or staging")
        require(record == file + ".generation.json", f"{file}: source sidecar path mismatch")
        require(file not in source_files, f"Source file reused for multiple slots: {file}")
        source_files.add(file)
        data = cache[file] if file in cache else read_bytes(file)
        record_data = cache[record] if record in cache else read_bytes(record)
        actual_sha = sha(data)
        require(actual_sha == item.get("sha256"), f"{file}: planned source SHA mismatch")
        require(actual_sha not in source_shas, f"Duplicate planned PNG bytes: {file}")
        source_shas.add(actual_sha)
        if item.get("sourceGenerationRecordSha256") is not None:
            require(sha(record_data) == item["sourceGenerationRecordSha256"],
                    f"{record}: planned sidecar SHA mismatch")
        meta = decode(record_data, record)
        native = validate_lineage(meta, data, file, d, registration, item.get("nativeSha256"))
        require(item.get("nativeSha256") == native, f"{file}: planned native SHA missing/mismatch")
        safe_png_check(data, file)
        original_source_row = deepcopy(by_file[file]["row"]) if file in by_file else None
        if file.startswith("final/"):
            require(original_source_row is not None, f"{file}: final source absent from current selection")
        bindings.append({"file": file, "sha256": actual_sha, "generationRecord": record,
                         "generationRecordSha256": sha(record_data), "nativeSha256": native})
        sources.append({"item": deepcopy(item), "data": data, "recordData": record_data,
                        "meta": meta, "sourceSelectionRow": original_source_row})
    require(seen_slots == expected_slots, "Plan does not cover exactly all 128 target slots")
    combat = [row for row in rows if row["action"] != "run"]
    final_native = [source["meta"]["source"]["sha256"] for source in sources] + [r["nativeSha256"] for r in combat]
    final_sha = [sha(source["data"]) for source in sources] + [r["sha256"] for r in combat]
    require(len(set(final_native)) == 196, "Prospective 196 outputs do not have unique native SHA values")
    require(len(set(final_sha)) == 196, "Prospective 196 outputs do not have unique PNG SHA values")
    snapshot = {"schemaVersion": 1,
                "topFiles": {name: sha(data) for name, data in sorted(top.items())},
                "currentArtifacts": sorted(artifacts, key=lambda x: x["file"]),
                "plannedSources": sorted(bindings, key=lambda x: x["file"])}
    return {"plan": plan, "planPath": plan_relative, "planData": plan_data,
            "planSha": sha(plan_data), "top": top, "rows": rows, "manifest": manifest,
            "registration": registration, "current": current, "cache": cache,
            "sources": sources, "snapshot": snapshot, "preimageSha": sha(canonical_bytes(snapshot))}


def verify_unchanged(state):
    expected = {name: sha(data) for name, data in state["top"].items()}
    expected.update({name: sha(data) for name, data in state["cache"].items()})
    expected[state["planPath"]] = state["planSha"]
    for source in state["sources"]:
        expected[source["item"]["sourceFile"]] = sha(source["data"])
        expected[source["item"]["sourceGenerationRecord"]] = sha(source["recordData"])
    for name, expected_sha in expected.items():
        require(sha(read_bytes(name)) == expected_sha, f"Preimage changed during check: {name}")


def atomic_write(relative, data):
    path = inside(relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".position-", suffix=".tmp",
                                         dir=path.parent, delete=False) as stream:
            temp_path = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def promote(state, acceptance_relative, report_relative):
    acceptance_data = read_bytes(acceptance_relative)
    acceptance = decode(acceptance_data, acceptance_relative)
    require(acceptance.get("accepted") is True, "Acceptance guard: accepted must be true")
    require(acceptance.get("clientValidated") is False,
            "Acceptance guard: clientValidated must be false (offline promotion only)")
    require(acceptance.get("selectionSha256") == state["planSha"],
            "Acceptance guard: selectionSha256 does not bind this exact plan")
    require(acceptance.get("preimageSha256") == state["preimageSha"],
            "Acceptance guard: preimageSha256 does not match current bytes/sidecars/metadata")
    require(report_relative.startswith(EVIDENCE + "/"), "Promotion report must stay in current evidence directory")
    history_relative = EVIDENCE + "/position-superseded-records-" + state["planSha"][:12] + ".json"
    require(not inside(report_relative).exists(), f"Promotion report already exists: {report_relative}; inspect before retrying")
    require(not inside(history_relative).exists(), f"Old-record evidence already exists: {history_relative}; inspect before retrying")
    now = datetime.now(timezone.utc).isoformat()
    new_rows = deepcopy(state["rows"])
    target_rows = {(r["action"], r["direction"], r["frame"]): r for r in new_rows}
    writes = {}
    for source in state["sources"]:
        item, meta = source["item"], deepcopy(source["meta"])
        d, frame = item["direction"], item["targetFrame"]
        target = f"final/run/{d}/{frame:02}.png"
        record = target + ".generation.json"
        position = {"positionSegment": item["positionSegment"], "pairOrdinal": item["pairOrdinal"]}
        if item.get("phase") is not None:
            position["phase"] = item["phase"]
        meta.update(file=target, sha256=sha(source["data"]),
                    status="offline_artwork_accepted_client_pending",
                    finalVisualPassed=True, clientValidated=False,
                    offlineAcceptance=acceptance_relative,
                    stancePosition=position, supportLeg=item["supportLeg"],
                    positionPromotion={"promotedAt": now, "selection": state["planPath"],
                                       "selectionSha256": state["planSha"],
                                       "sourceFile": item["sourceFile"],
                                       "sourceSha256": sha(source["data"]),
                                       "sourceFileRole": "prepromotion_path_not_live_after_reorder",
                                       "sourceGenerationRecord": item["sourceGenerationRecord"],
                                       "sourceGenerationRecordSha256": sha(source["recordData"])})
        row = target_rows[("run", d, frame)]
        row.update(file=target, generationRecord=record, sha256=meta["sha256"],
                   nativeSourceFile=meta["source"]["file"], nativeSha256=meta["source"]["sha256"],
                   visualStatus=item.get("visualNotes", "连续八帧四位置接地离线复核通过；客户端未验收"),
                   finalVisualPassed=True, clientValidated=False,
                   stancePosition=position, supportLeg=item["supportLeg"])
        # If a future row schema embeds lineage, take it from the source, never the old target slot.
        for field in ("source", "sourceGeneration", "nativeSourceRecord", "actualModel", "actualQuality"):
            if field in row:
                row[field] = deepcopy(meta.get(field))
        writes[target] = source["data"]
        writes[record] = json_bytes(meta)
    combat_before = [r for r in state["rows"] if r["action"] != "run"]
    require([r for r in new_rows if r["action"] != "run"] == combat_before,
            "Internal error: combat rows were changed")
    manifest = deepcopy(state["manifest"])
    manifest.update(frames=new_rows, artworkUpdatedAt=now,
                    status="offline_artwork_complete_client_pending",
                    latestVisualAcceptance=acceptance_relative,
                    latestRunPositionSelection=state["planPath"])
    writes["final-selection.json"] = json_bytes(new_rows)
    writes["final/manifest.json"] = json_bytes(manifest)
    history = {"capturedAt": now, "selectionSha256": state["planSha"],
               "preimageSha256": state["preimageSha"], "preimageSnapshot": state["snapshot"],
               "previousFinalSelection": state["rows"], "previousFinalManifest": state["manifest"],
               "previousRegistration": state["registration"],
               "supersededRunRecords": [{"selectionRow": value["row"], "generationRecord": value["meta"]}
                                        for key, value in state["current"].items() if key[0] == "run"],
               "sourceRecords": [{"planRow": s["item"], "originalSelectionRow": s["sourceSelectionRow"],
                                  "generationRecord": s["meta"]} for s in state["sources"]],
               "imageBackupsCreated": False}
    result = {"status": "in_progress", "startedAt": now, "selection": state["planPath"],
              "selectionSha256": state["planSha"], "preimageSha256": state["preimageSha"],
              "acceptance": acceptance_relative, "acceptanceSha256": sha(acceptance_data),
              "oldTextRecords": history_relative, "plannedRunFrames": 128,
              "combatFramesUntouched": 68, "clientValidated": False}
    verify_unchanged(state)
    require(sha(read_bytes(acceptance_relative)) == sha(acceptance_data), "Acceptance changed before promotion")
    # Every source image/record and original source row is already cached above.
    atomic_write(history_relative, json_bytes(history))
    atomic_write(report_relative, json_bytes(result))
    written = []
    try:
        for name, data in writes.items():
            atomic_write(name, data)
            written.append(name)
        for name, data in writes.items():
            require(sha(read_bytes(name)) == sha(data), f"Postwrite SHA mismatch: {name}")
        for name in ("registration.json", "animation-timing.json"):
            require(read_bytes(name) == state["top"][name], f"Forbidden metadata change: {name}")
        for row in combat_before:
            for name in (row["file"], row["generationRecord"]):
                require(read_bytes(name) == state["cache"][name], f"Forbidden combat change: {name}")
        result.update(status="complete", completedAt=datetime.now(timezone.utc).isoformat(),
                      promotedRunFrames=128, finalFrames=196, uniqueNativeFrames=196,
                      uniqueFinalFrames=196, registrationUnchanged=True, timingUnchanged=True,
                      finalSelectionSha256=sha(writes["final-selection.json"]),
                      finalManifestSha256=sha(writes["final/manifest.json"]),
                      outputs=[{"file": r["file"], "sha256": r["sha256"],
                                "generationRecord": r["generationRecord"],
                                "generationRecordSha256": sha(writes[r["generationRecord"]]),
                                "nativeSha256": r["nativeSha256"]}
                               for r in new_rows if r["action"] == "run"])
        atomic_write(report_relative, json_bytes(result))
        return result
    except Exception as exc:
        rollback_errors = []
        for name in reversed(written):
            try:
                old = state["top"][name] if name in state["top"] else state["cache"][name]
                atomic_write(name, old)
            except Exception as rollback_exc:
                rollback_errors.append(f"{name}: {rollback_exc}")
        result.update(status="failed_rollback_incomplete" if rollback_errors else "failed_rolled_back",
                      failedAt=datetime.now(timezone.utc).isoformat(), error=str(exc),
                      rollbackErrors=rollback_errors)
        try:
            atomic_write(report_relative, json_bytes(result))
        except Exception as report_exc:
            rollback_errors.append(f"Could not write failure report: {report_exc}")
        raise PromotionError(f"Promotion failed: {exc}; rollback errors: {rollback_errors or 'none'}") from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true", help="Read-only plan/preimage validation; emit acceptance SHA bindings")
    modes.add_argument("--promote", action="store_true", help="Requires externally written SHA-bound accepted:true record")
    parser.add_argument("--selection", default=DEFAULT_PLAN, help="Character-relative 128-row plan")
    parser.add_argument("--acceptance", default=DEFAULT_ACCEPTANCE, help="Character-relative acceptance JSON")
    parser.add_argument("--report", default=DEFAULT_REPORT, help="Character-relative promotion result JSON (promote only)")
    args = parser.parse_args()
    state = collect(args.selection)
    verify_unchanged(state)
    if args.check:
        output = {"status": "check_passed", "selection": args.selection,
                  "selectionSha256": state["planSha"], "preimageSha256": state["preimageSha"],
                  "sourceFrames": 128, "uniqueSourceFiles": 128, "uniqueSourcePngHashes": 128,
                  "prospectiveFinalFrames": 196, "prospectiveUniqueNativeHashes": 196,
                  "prospectiveUniquePngHashes": 196, "combatFramesUntouched": 68,
                  "readOnly": True, "clientValidated": False,
                  "acceptanceRequired": ["accepted:true", "selectionSha256", "preimageSha256", "clientValidated:false"]}
    else:
        result = promote(state, args.acceptance, args.report)
        output = {key: value for key, value in result.items() if key != "outputs"}
        output["report"] = args.report
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PromotionError, KeyError, TypeError, ValueError, OSError) as exc:
        print(f"promote-position-run: ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)

