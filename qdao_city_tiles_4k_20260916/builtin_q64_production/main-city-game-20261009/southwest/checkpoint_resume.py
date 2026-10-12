"""Checkpoint live native production without changing art, selections, or records.

Run with the bundled Python runtime. Counts are a snapshot of concurrent writers,
not a claim that production stopped. The 2026-10-10 resume baseline is immutable.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from PIL import Image


BASE = Path(__file__).resolve().parent
PROGRESS = BASE / "progress.json"
BASELINE = BASE / "pipeline-tools/progress-baseline-20261010T090648.json"
SNAPSHOT = BASE / "pipeline-tools/live-counts-20261010.json"
BASELINE_TIME = "2026-10-10T09:06:48.945394+00:00"
BASELINE_COUNTS = {
    "generatedNativeCount": 36,
    "rejectedNativeCount": 6,
    "failedBuiltinCallCount": 2,
}
PATCH_IDS = [f"p{row:02}_{col:02}" for row in range(1, 5) for col in range(1, 5)]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")), digest(raw)


def atomic_json(path, value):
    """Replace only the requested checkpoint file, never a production source."""
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def preserve_baseline():
    """Exclusive creation preserves the original progress bytes on every rerun."""
    if not BASELINE.exists():
        original = PROGRESS.read_bytes()
        parsed = json.loads(original.decode("utf-8-sig"))
        if parsed.get("updatedAtUtc") != BASELINE_TIME or any(parsed.get(k) != v for k, v in BASELINE_COUNTS.items()):
            raise RuntimeError("Original resume baseline changed before backup; refusing to invent or overwrite a baseline.")
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with BASELINE.open("xb") as handle:
                handle.write(original)
        except FileExistsError:
            pass
    parsed, checksum = read_json(BASELINE)
    if parsed.get("updatedAtUtc") != BASELINE_TIME or any(parsed.get(k) != v for k, v in BASELINE_COUNTS.items()):
        raise RuntimeError("Immutable baseline does not match the authorized 36/6/2 resume baseline.")
    return parsed, checksum


def tile_paths():
    return sorted(p for p in BASE.glob("r??_c??") if p.is_dir() and 9 <= int(p.name[1:3]) <= 16 and 1 <= int(p.name[5:7]) <= 8)


def receipt_paths():
    # Historical receipts remain in the original receipts/refinement/repairs
    # folders. These namespaces were created only after this resume baseline.
    paths = set()
    repair_roots = set()
    for tile in tile_paths():
        paths.update((tile / "pipeline/receipts").glob("*.json"))
        for root in tile.glob("refinement-resume20261010*"):
            repair_roots.add(root)
        repair_roots.update(root for root in tile.glob("*-repair") if root.is_dir())
        repair_roots.update(root for root in tile.glob("repairs*20261011*") if root.is_dir())
        repair_roots.update(root for root in tile.glob("repairs*20261012*") if root.is_dir())
    repair_roots.update(root for root in (BASE / "pipeline-tools").glob("*-repair") if root.is_dir())
    repair_roots.update(root for root in (BASE / "pipeline-tools").glob("*repair*20261011*") if root.is_dir())
    repair_roots.update(root for root in (BASE / "pipeline-tools").glob("crossedge-stair-restored-20261011*") if root.is_dir())
    repair_roots.update(root for root in BASE.glob("*-repair") if root.is_dir())
    for root in repair_roots:
        # Workers may save receipts directly beside the request/native files,
        # or in a receipts folder. Both forms are real generation evidence.
        paths.update(root.glob("**/*.receipt.json"))
        paths.update(root.glob("**/receipt.json"))
        paths.update(root.glob("**/failure-receipt-*.json"))
        for candidate in root.glob("**/tool-result.json"):
            evidence, _ = read_json(candidate)
            if evidence.get("tool") == "image_gen.imagegen" and evidence.get("status"):
                paths.add(candidate)
        for receipts in root.glob("**/receipts"):
            paths.update(receipts.glob("*.json"))
    return sorted(paths)


def image_info(path, cache):
    key = str(path).lower()
    if key not in cache:
        with Image.open(path) as image:
            image.load()
            info = {"file": str(path), "pixels": list(image.size), "mode": image.mode}
        info["sha256"] = digest(path.read_bytes())
        cache[key] = info
    return cache[key]


def source_output(receipt):
    explicit = receipt.get("sourceOutputPath") or receipt.get("outputFile") or receipt.get("sourceOutput") or receipt.get("generatedSourcePath")
    if explicit:
        return Path(explicit)
    hint = receipt.get("output_hint") or receipt.get("rawOutputHint") or receipt.get("metadata", {}).get("output_hint") or ""
    match = re.search(r" as (.+?\.png) by default", hint)
    return Path(match.group(1)) if match else None


def supplemental_receipt_evidence(path, receipt, cache):
    """Link alternate-schema repair receipts to actual native records/reviews.

    Production-result totals are never added to counts. They only supply an
    explicit rejection disposition for the individual receipt/native ID.
    """
    work_root = path.parent.parent if path.parent.name == "receipts" else path.parent
    evidence, rejected, verified = [], False, False
    verified_natives = {}
    receipt_sha = digest(path.read_bytes())
    output = source_output(receipt)
    direct_native = receipt.get("native", {})
    if isinstance(direct_native, dict) and direct_native.get("file") and direct_native.get("sha256") and output:
        native = image_info(Path(direct_native["file"]), cache)
        returned = image_info(output, cache)
        if native["pixels"] == [1254,1254] and native["sha256"] == direct_native["sha256"] == returned["sha256"]:
            verified = True
            verified_natives[str(Path(direct_native["file"])).lower()] = native["sha256"]
            evidence.append({"file": str(path), "sha256": receipt_sha, "kind": "receipt-embedded-native-verified-against-actual-output", "native": native})
    native_records = set((work_root / "native").glob("*.generation.json")) | set(work_root.glob("*.generation.json"))
    for record in native_records:
        data, checksum = read_json(record)
        linked = data.get("receipt") or data.get("evidence", {}).get("toolReceipt")
        if not linked or Path(linked) != path:
            continue
        expected_receipt = data.get("receiptSha256") or data.get("evidence", {}).get("toolReceiptSha256")
        native_path = data.get("file") or data.get("path")
        if not native_path or expected_receipt != receipt_sha:
            continue
        native = image_info(Path(native_path), cache)
        if native["pixels"] != [1254, 1254] or native["sha256"] != data.get("sha256"):
            continue
        if output and image_info(output, cache)["sha256"] == native["sha256"]:
            verified = True
            verified_natives[str(Path(native_path)).lower()] = native["sha256"]
        native_rejected = "rejected" in str(data.get("status", "")).lower() or str(data.get("candidateUse", "")).lower().startswith("rejected")
        rejected = rejected or native_rejected
        evidence.append({"file": str(record), "sha256": checksum, "kind": "native-record-linked-to-receipt", "native": native, "explicitRejection": native_rejected})
    for result in work_root.glob("production-result*.json"):
        data, checksum = read_json(result)
        rid = receipt.get("id")
        native = data.get("newNative", {})
        linked_receipt = data.get("receipt")
        raw_native = data.get("rawNative")
        if linked_receipt and Path(linked_receipt) == path and data.get("receiptSha256") == receipt_sha and raw_native:
            native_info = image_info(Path(raw_native), cache)
            if native_info["pixels"] == [1254,1254] and native_info["sha256"] == data.get("rawNativeSha256") and output and image_info(output, cache)["sha256"] == native_info["sha256"]:
                verified = True
                verified_natives[str(Path(raw_native)).lower()] = native_info["sha256"]
                evidence.append({"file": str(result), "sha256": checksum, "kind": "receipt-linked-raw-native-production-record", "native": native_info})
        if rid and (rid in data.get("rejectedNativeIds", []) or (native.get("id") == rid and "rejected" in str(native.get("status", "")).lower()) or (data.get("id") == rid and str(data.get("status", "")).startswith("rejected"))):
            rejected = True
            evidence.append({"file": str(result), "sha256": checksum, "kind": "explicit-rejected-native-id", "id": rid})
    disposition_path = work_root / "disposition.json"
    if disposition_path.exists():
        disposition, checksum = read_json(disposition_path)
        ref = disposition.get("native", {})
        if isinstance(ref, dict) and verified_natives.get(str(Path(ref.get("file", ""))).lower()) == ref.get("sha256") and ref.get("sha256"):
            explicit = disposition.get("explicitlyRejected") is True or disposition.get("explicitRejected") is True
            rejected = rejected or explicit
            evidence.append({"file":str(disposition_path),"sha256":checksum,"kind":"hash-linked-native-disposition","explicitRejection":explicit})
    historically_rejected = rejected
    # A parent may salvage a rejected worker output through a different local
    # composition. Preserve the rejection evidence but use the explicit current
    # patch contributor disposition, without changing historical records.
    for ancestor in work_root.parents:
        if ancestor == BASE or BASE not in ancestor.parents:
            break
        for result in ancestor.glob("production-result*.json"):
            data, checksum = read_json(result)
            for patch in data.get("patches", []):
                native = patch.get("nativeSource", {})
                native_path = native.get("path") or native.get("file")
                if native_path and verified_natives.get(str(Path(native_path)).lower()) == native.get("sha256"):
                    rejected = False
                    evidence.append({"file": str(result), "sha256": checksum, "kind": "current-parent-patch-contributor-supersedes-worker-rejection", "patchId": patch.get("id"), "nativeSource": native})
    return {"nativeReturnVerified": verified, "explicitlyRejected": rejected, "historicallyRejected": historically_rejected, "evidence": evidence}


def run(production_lines, generation_worker=None, generation_tile=None, support_note=None):
    started = utc_now()
    baseline, baseline_sha = preserve_baseline()
    captured_paths = receipt_paths()
    cache, receipts, errors, warnings = {}, [], [], []
    seen_outputs = {}
    # Capture receipts before native slots so a concurrently completed slot with
    # a not-yet-captured receipt cannot inflate this snapshot's spatial count.
    for path in captured_paths:
        try:
            data, checksum = read_json(path)
            output = source_output(data)
            is_repair = "pipeline/receipts/" not in path.as_posix()
            supplement = supplemental_receipt_evidence(path, data, cache) if is_repair else {}
            status = data.get("status")
            status_evidence = "explicit receipt status"
            if not status and data.get("error"):
                status, status_evidence = "tool_error", "explicit receipt error"
            elif not status and supplement.get("nativeReturnVerified") and ("image_gen" in str(data.get("tool", "")) or data.get("mode") == "builtin_imagegen") and not data.get("error"):
                status, status_evidence = "returned_image", "nested tool output metadata plus receipt-linked native record and matching actual output hash"
            disposition = data.get("rejectionReason") or data.get("visualDisposition")
            item = {
                "receipt": str(path), "receiptSha256": checksum,
                "status": status, "rawStatus": data.get("status"), "statusEvidence": status_evidence,
                "sourceOutputPath": str(output) if output else None,
                "recordedAtUtc": data.get("recordedAtUtc") or data.get("returnedAtUtc") or data.get("completedAtUtc") or data.get("receivedAt") or data.get("reviewedAtUtc") or data.get("atUtc"),
                "error": data.get("error"), "disposition": disposition,
                "explicitlyRejected": data.get("explicitRejected") is True or data.get("explicitlyRejected") is True or bool(data.get("rejectionReason")) or (data.get("accepted") is False and bool(data.get("reason"))) or str(data.get("visualDisposition", "")).lower().startswith("rejected") or supplement.get("explicitlyRejected", False),
                "supplementalEvidence": supplement.get("evidence", []),
                "historicallyRejectedBeforeParentReuse": supplement.get("historicallyRejected", False) and not supplement.get("explicitlyRejected", False),
                "workType": "repair_without_new_spatial_coverage" if is_repair else "spatial_patch_attempt",
                "group": str(path.parent.relative_to(BASE)),
                "selectedDirectNativeSlot": False,
            }
            if item["status"] == "returned_image":
                key = str(output).lower() if output else str(path).lower()
                if key in seen_outputs:
                    item["duplicateOf"] = seen_outputs[key]
                else:
                    seen_outputs[key] = str(path)
                if output:
                    try:
                        item["returnedImage"] = image_info(output, cache)
                    except (OSError, ValueError) as exc:
                        warnings.append({"file": str(path), "error": "Returned output is unavailable: " + str(exc)})
                else:
                    warnings.append({"file": str(path), "error": "Returned-image receipt has no parseable output path."})
            receipts.append(item)
        except (OSError, ValueError) as exc:
            errors.append({"file": str(path), "error": "Receipt was unreadable during snapshot: " + str(exc)})

    by_receipt = {item["receipt"].lower(): item for item in receipts}
    captured_keys = set(by_receipt)
    tiles, partial_outputs, complete_outputs = [], [], []
    for tile in tile_paths():
        raw_records = {path.name[:6]: path for path in (tile / "native").glob("p??_??.png.generation.json")}
        selection_file = tile / "refinement/selection.json"
        selection = read_json(selection_file)[0] if selection_file.exists() else {}
        valid, native_records = [], []
        for patch, raw_record in sorted(raw_records.items()):
            record = tile / selection[patch] if patch in selection else raw_record
            try:
                data, record_sha = read_json(record)
                info = image_info(Path(data["file"]), cache)
                receipt = data.get("evidence", {}).get("toolReceipt") or data.get("receiptFile") or data.get("receipt")
                if not receipt:
                    raise ValueError("Native record has no receipt evidence")
                receipt_path = Path(receipt)
                if "pipeline/receipts/" in receipt_path.as_posix() and str(receipt_path).lower() not in captured_keys:
                    warnings.append({"file": str(record), "error": "Concurrent new native skipped until its receipt is captured next run."})
                    continue
                receipt_data, receipt_sha = read_json(receipt_path)
                if receipt_data.get("status") != "returned_image":
                    raise ValueError("Native receipt is not returned_image")
                expected_receipt_sha = data.get("evidence", {}).get("toolReceiptSha256")
                if expected_receipt_sha and expected_receipt_sha != receipt_sha:
                    raise ValueError("Native receipt hash mismatch")
                if info["pixels"] != [1254, 1254] or info["sha256"] != data.get("sha256"):
                    raise ValueError("Native dimensions/hash mismatch")
                valid.append(patch)
                if str(receipt_path).lower() in by_receipt:
                    by_receipt[str(receipt_path).lower()]["selectedDirectNativeSlot"] = True
                native_records.append({"patch": patch, "record": str(record), "recordSha256": record_sha, "receipt": receipt, "verifiedNative1254": True, **info})
            except (OSError, ValueError, KeyError) as exc:
                errors.append({"file": str(record), "error": str(exc)})

        full_outputs = []
        for root in (tile / "output", tile / "pipeline/output", tile / "repairs/output"):
            for path in root.glob("**/*.png"):
                if "context" in path.name:
                    continue
                try:
                    with Image.open(path) as image:
                        size = image.size
                    if size == (4096, 4096):
                        full_outputs.append(image_info(path, cache))
                except (OSError, ValueError) as exc:
                    errors.append({"file": str(path), "error": str(exc)})
        for path in (tile / "pipeline/output").glob("**/assembly.json"):
            try:
                data, assembly_sha = read_json(path)
                output = data.get("output", {})
                if not output.get("file"):
                    continue
                info = image_info(Path(output["file"]), cache)
                if info["sha256"] != output.get("sha256"):
                    raise ValueError("Assembly output hash mismatch")
                if info["pixels"][0] == 4096 and info["pixels"][1] in (1024, 2048, 3072):
                    if not set(data.get("usedPatchIds", [])).issubset(valid):
                        raise ValueError("Assembly includes an unverified native slot")
                    partial_outputs.append({"tile": tile.name, "assembly": str(path), "assemblySha256": assembly_sha, "createdAtUtc": data.get("createdAtUtc", ""), "coreWorldBox": data.get("outputWorldBox") or data.get("selectedCoreWorldBox"), **info})
                elif info["pixels"] == [4096, 4096] and len(valid) == 16:
                    complete_outputs.append({"tile": tile.name, "assembly": str(path), "assemblySha256": assembly_sha, "createdAtUtc": data.get("createdAtUtc", ""), "coreWorldBox": data.get("outputWorldBox") or data.get("selectedCoreWorldBox"), "kind": "native-full-candidate", "internalPassed": False, "formalAccepted": False, **info})
            except (OSError, ValueError, KeyError) as exc:
                errors.append({"file": str(path), "error": str(exc)})
        # Composite review outputs may be the current candidate while retaining
        # the native selection. Map them separately without granting QA passes.
        for result_path in tile.glob("refinement-resume20261010*/full-tile-review/production-result.json"):
            try:
                result, result_sha = read_json(result_path)
                core = result.get("outputs", {}).get("core", {})
                info = image_info(Path(core.get("path") or core["file"]), cache)
                if info["pixels"] != [4096, 4096] or info["sha256"] != core.get("sha256") or len(valid) != 16:
                    raise ValueError("Full composite dimensions/hash/native coverage mismatch")
                assembly_path = Path(result["assembly"])
                assembly, assembly_sha = read_json(assembly_path)
                if assembly_sha != result.get("assemblySha256"):
                    raise ValueError("Composite assembly hash mismatch")
                review_path = Path(result["visualReview"])
                review, review_sha = read_json(review_path)
                if review_sha != result.get("visualReviewSha256"):
                    raise ValueError("Composite visual review hash mismatch")
                origin = assembly["tileWorldOrigin"]
                complete_outputs.append({"tile": tile.name, "kind": "reviewed-composite-candidate", "productionResult": str(result_path), "productionResultSha256": result_sha, "assembly": str(assembly_path), "assemblySha256": assembly_sha, "createdAtUtc": assembly.get("createdAtUtc", ""), "coreWorldBox": [origin[0], origin[1], origin[0] + 4096, origin[1] + 4096], "internalPassed": result.get("internalPassed") is True, "formalAccepted": False, "qaStatus": result.get("status"), "visualReview": str(review_path), "geometryIssueCount": result.get("geometryIssueCount"), "materialIssueCount": result.get("materialIssueCount"), **info})
                full_outputs.append(info)
            except (OSError, ValueError, KeyError) as exc:
                errors.append({"file": str(result_path), "error": str(exc)})
        for assembly_path in tile.glob("refinement-resume20261010*/integrated-v*/assembly.json"):
            try:
                assembly, assembly_sha = read_json(assembly_path)
                output = assembly["output"]
                info = image_info(Path(output.get("file") or output["path"]), cache)
                context = assembly["context"]
                context_info = image_info(Path(context.get("file") or context["path"]), cache)
                if len(valid) != 16 or info["pixels"] != [4096,4096] or info["sha256"] != output.get("sha256"):
                    raise ValueError("Integrated candidate output hash/dimensions/native coverage mismatch")
                if context_info["pixels"] != [4326,4326] or context_info["sha256"] != context.get("sha256"):
                    raise ValueError("Integrated candidate context hash/dimensions mismatch")
                manifest_sources = [assembly["sourceContext"], *assembly.get("proposals", [])]
                for patch in assembly.get("patches", []):
                    manifest_sources.extend(patch[key] for key in ("patch", "mask", "nativeSource") if key in patch)
                for source in manifest_sources:
                    source_path = Path(source.get("file") or source["path"])
                    if digest(source_path.read_bytes()) != source["sha256"]:
                        raise ValueError("Integrated candidate manifest source hash mismatch: " + str(source_path))
                review_path = assembly_path.parent / "qa-review.json"
                review, review_sha = ({}, None)
                review_status = "pending_geometry_and_material_review"
                if review_path.exists():
                    review, review_sha = read_json(review_path)
                    review_status = review.get("status", "review_saved")
                    for field, actual in (("output", info), ("context", context_info)):
                        reviewed = review.get(field, {})
                        if not isinstance(reviewed, dict) or reviewed.get("sha256") != actual["sha256"]:
                            raise ValueError("Integrated candidate QA " + field + " hash mismatch or missing")
                geometry_passed = review.get("geometryPassed") is True
                # The owner's acceptance counters are intentionally separate.
                # Geometry alone cannot set whole-internal or formal acceptance.
                internal_passed = review.get("internalPassed") is True
                origin = [(int(tile.name[5:7])-1)*4096, (int(tile.name[1:3])-1)*4096]
                complete_outputs.append({"tile": tile.name, "kind": "integrated-repair-candidate", "priority": 10, "assembly": str(assembly_path), "assemblySha256": assembly_sha, "createdAtUtc": assembly.get("createdAtUtc", ""), "coreWorldBox": [origin[0],origin[1],origin[0]+4096,origin[1]+4096], "context": context_info, "geometryPassed": geometry_passed, "internalPassed": internal_passed, "formalAccepted": False, "qaStatus": review_status, "visualReview": str(review_path), "visualReviewSha256": review_sha, "visualReviewPresent": review_path.exists(), "manifestSourceHashesVerified": True, **info})
                full_outputs.append(info)
            except (OSError, ValueError, KeyError) as exc:
                errors.append({"file": str(assembly_path), "error": str(exc)})
        tiles.append({"tile": tile.name, "directNativeSlots": len(raw_records), "verifiedSelectedSpatialSlots": len(valid), "selectedIds": valid, "missingIds": [patch for patch in PATCH_IDS if patch not in valid], "full16NativeSlots": len(valid) == 16, "full4096OutputFiles": full_outputs, "has4096Output": bool(full_outputs), "complete4kCandidate": len(valid) == 16 and bool(full_outputs), "nativeRecords": native_records})

    catalog_path = BASE / "current-candidates.json"
    if catalog_path.exists():
        try:
            catalog, catalog_sha = read_json(catalog_path)
            for tile_name, entry in catalog.get("tiles", {}).items():
                candidate = entry["candidate"]
                info = image_info(Path(candidate["file"]), cache)
                context = entry["context"]
                context_info = image_info(Path(context["file"]), cache)
                tile_status = next(t for t in tiles if t["tile"] == tile_name)
                if info["sha256"] != candidate["sha256"] or info["pixels"] != [4096, 4096] or context_info["sha256"] != context["sha256"] or context_info["pixels"] != [4326, 4326] or not tile_status["full16NativeSlots"]:
                    raise ValueError("Current candidate catalog dimensions/hash/coverage mismatch: " + tile_name)
                if catalog.get("schemaVersion", 1) >= 2:
                    assembly_path = Path(entry.get("assembly") or (Path(candidate["file"]).parent / "assembly.json"))
                    assembly_sha = digest(assembly_path.read_bytes())
                    created_at = catalog.get("updatedAtUtc")
                    tile_row, tile_col = int(tile_name[1:3]), int(tile_name[5:7])
                    world_box = entry.get("coreWorldBox", [(tile_col-1)*4096, (tile_row-1)*4096, tile_col*4096, tile_row*4096])
                else:
                    assembly_path = Path(catalog["assembly"]["file"])
                    assembly_sha = catalog["assembly"]["sha256"]
                    if digest(assembly_path.read_bytes()) != assembly_sha:
                        raise ValueError("Current candidate catalog assembly hash mismatch")
                    created_at = catalog["createdAtUtc"]
                    world_box = entry["coreWorldBox"]
                complete_outputs.append({"tile": tile_name, "kind": "cross-tile-integrated-candidate", "priority": 20, "assembly": str(assembly_path), "assemblySha256": assembly_sha, "createdAtUtc": created_at, "coreWorldBox": world_box, "context": context_info, "geometryPassed": False, "internalPassed": False, "formalAccepted": False, "qaStatus": catalog.get("status", "pending_visual_QA"), "catalog": str(catalog_path), "catalogSha256": catalog_sha, **info})
        except (OSError, ValueError, KeyError, StopIteration) as exc:
            errors.append({"file": str(catalog_path), "error": str(exc)})

    unique = [item for item in receipts if item["status"] == "returned_image" and not item.get("duplicateOf")]
    failures = [item for item in receipts if item["status"] and ("error" in item["status"] or "fail" in item["status"] or "blocked" in item["status"] or item["status"] == "rejected_by_safety_system")]
    rejected = [item for item in unique if item["explicitlyRejected"]]
    slots = sum(tile["verifiedSelectedSpatialSlots"] for tile in tiles)
    complete = sum(tile["complete4kCandidate"] for tile in tiles)
    started_tiles = sum(tile["verifiedSelectedSpatialSlots"] > 0 for tile in tiles)
    counts = {
        "generatedNativeCount": 36 + len(unique), "rejectedNativeCount": 6 + len(rejected), "failedBuiltinCallCount": 2 + len(failures),
        "selectedNativePatchCount": slots, "usableNativeCount": slots,
        "selectedLocalRepairCount": 2, "selectedNativeSourceCount": slots + 2, "refinedNativeCount": 8,
        "complete4kCandidateCount": complete, "fullyCovered4kCount": complete,
        "nativeCoverageCompleteTileCount": sum(tile["full16NativeSlots"] for tile in tiles),
        "internalPassed4kCount": 0 if catalog_path.exists() else 1, "historicalInternalPassed4kCount": 1, "externalPassed4kCount": 0, "formalAcceptedCount": 0,
        "partialTileCount": sum(tile["verifiedSelectedSpatialSlots"] > 0 and not tile["complete4kCandidate"] for tile in tiles),
        "untouchedTileCount": 64 - started_tiles, "remainingTilesWithout4kCandidates": 64 - complete,
        "missingFullTileCount": 64 - complete, "remainingCorePatchCount": 1024 - slots,
        "newImageGenCallsSinceResume": len(unique) + len(failures),
    }
    completed = utc_now()
    snapshot = {
        "schemaVersion": 2, "snapshotStartedAtUtc": started, "snapshotCompletedAtUtc": completed,
        "isLiveSnapshotNotFinal": True, "productionInProgress": True,
        "baseline": {"file": str(BASELINE), "sha256": baseline_sha, "updatedAtUtc": baseline["updatedAtUtc"], **BASELINE_COUNTS},
        "recommendedProgressFieldsBeforeRepairIntegration": counts,
        "sinceBaseline": {"successfulBuiltinReturns": len(unique), "selectedNewSpatialSlots": sum(item["selectedDirectNativeSlot"] for item in unique), "explicitRejectedReturns": len(rejected), "repairReturnsWithoutNewSpatialCoverage": sum(item["workType"] == "repair_without_new_spatial_coverage" for item in unique), "failedCalls": len(failures), "quotaErrors": sum("quota" in str(item["error"]).lower() or "usage limit" in str(item["error"]).lower() for item in failures), "uniqueNativeOutputsVerified1254Square": sum(item.get("returnedImage", {}).get("pixels") == [1254, 1254] for item in unique), "groupSuccessCounts": dict(Counter(item["group"] for item in unique))},
        "countingNotes": ["Counts are a live snapshot of captured receipts and verified native slots; concurrent production may advance immediately afterward.", "Successful receipts include rejected and repair outputs; image output paths are deduplicated. Derived contexts, crops and overlays are never additional native generations.", "A complete tile requires both 16 verified native slots and an actual 4096x4096 output. Native coverage alone is reported separately.", "Baseline local repair count 2 and refined count 8 are historical counters; the current integrated assembly records newer repair contributors.", "Current integrated candidates have internal pass count 0; the historical internal pass count 1 is recorded separately. Formal acceptance remains 0. This script does not perform visual acceptance."],
        "tiles": tiles, "partialOutputs": partial_outputs, "completeOutputs": complete_outputs,
        "successfulAndFailedReceiptInventory": receipts, "rejectedDetails": rejected, "failedDetails": failures,
        "verificationIssues": errors, "warnings": warnings,
        "endInventoryChangeDetected": receipt_paths() != captured_paths,
    }
    if errors:
        # An interrupted concurrent write must not erase previously verified
        # progress. The diagnostic snapshot is still useful; rerun once the
        # source write has completed.
        snapshot["progressUpdated"] = False
        atomic_json(SNAPSHOT, snapshot)
        print(json.dumps({"countsSnapshotUtc": completed, "snapshot": str(SNAPSHOT), "progressUpdated": False, "verificationIssues": errors}, ensure_ascii=False, indent=2))
        return 1
    # Reread at commit time to preserve unrelated progress fields changed while
    # the audit ran. Only documented count/status/partial fields are updated.
    progress, previous_progress_sha = read_json(PROGRESS)
    progress.update(counts)
    progress.update({"updatedAtUtc": completed, "countsSnapshotUtc": completed, "productionInProgress": True, "status": "native_production_in_progress", "inFlightStatus": "parallel_production_in_progress", "holdNewImageGeneration": False, "finalCityComplete": False, "countsSnapshot": str(SNAPSHOT), "countsBaseline": str(BASELINE), "countsVerificationIssueCount": len(errors), "countsSnapshotMayHaveAdvanced": snapshot["endInventoryChangeDetected"]})
    if production_lines is not None:
        worker_status = dict(progress.get("workerStatus", {}))
        worker_status.update({"productionLines": production_lines, "reportedAtUtc": completed, "source": "Parent-reported active generation lines; QA/statistics assistance is not counted as image generation."})
        if generation_worker is not None:
            worker_status["activeGenerationWorkers"] = [generation_worker]
        if generation_tile is not None:
            worker_status["activeGenerationTiles"] = [generation_tile]
        if support_note is not None:
            worker_status["supportActivities"] = support_note
        progress["workerStatus"] = worker_status
    active_tile = progress.get("activeTile", "r11_c05")
    active_partials = [output for output in partial_outputs if output["tile"] == active_tile]
    if active_partials:
        latest = max(active_partials, key=lambda output: (output["pixels"][1], output["createdAtUtc"]))
        progress.update({"partial": latest["file"], "partialSha256": latest["sha256"], "partialPixels": latest["pixels"], "partialCoreWorldBox": latest["coreWorldBox"], "partialAssembly": latest["assembly"]})
    active_complete = [output for output in complete_outputs if output["tile"] == active_tile]
    if active_complete:
        latest = max(active_complete, key=lambda output: (output.get("priority", 0), output["createdAtUtc"]))
        progress.update({"activeCandidate": latest["file"], "activeCandidateSha256": latest["sha256"], "activeCandidatePixels": latest["pixels"], "activeCandidateCoreWorldBox": latest["coreWorldBox"], "activeCandidateAssembly": latest["assembly"], "activeCandidateAssemblySha256": latest["assemblySha256"], "activeCandidateKind": latest["kind"], "activeCandidateGeometryPassed": latest.get("geometryPassed", False), "activeCandidateInternalPassed": latest["internalPassed"], "activeCandidateFormalAccepted": False, "activeCandidateVisualReview": latest.get("visualReview"), "activeCandidateVisualReviewSha256": latest.get("visualReviewSha256"), "activeCandidateQaStatus": latest.get("qaStatus", "pending_visual_QA"), "partialIsHistorical": True})
    snapshot["previousProgressSha256"] = previous_progress_sha
    snapshot["progressUpdated"] = True
    atomic_json(SNAPSHOT, snapshot)
    atomic_json(PROGRESS, progress)
    print(json.dumps({"countsSnapshotUtc": completed, "progress": str(PROGRESS), "snapshot": str(SNAPSHOT), "baseline": str(BASELINE), "counts": counts, "partial": {key: progress.get(key) for key in ("partial", "partialPixels", "partialCoreWorldBox")}, "verificationIssues": errors, "warnings": warnings, "endInventoryChangeDetected": snapshot["endInventoryChangeDetected"]}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-lines", type=int, default=None, help="Parent-reported current production lines; omitted preserves existing workerStatus.")
    parser.add_argument("--generation-worker", default=None, help="Explicit parent-reported sole active image-generation worker.")
    parser.add_argument("--generation-tile", default=None, help="Explicit parent-reported active image-generation tile.")
    parser.add_argument("--support-note", default=None, help="Preserve a distinction between non-generation assistance and image-generation lines.")
    args = parser.parse_args()
    if args.production_lines is not None and args.production_lines < 1:
        parser.error("--production-lines must be positive")
    raise SystemExit(run(args.production_lines, args.generation_worker, args.generation_tile, args.support_note))
