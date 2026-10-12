"""Audit the selected axis repairs and unchanged exports without inventing native reads.

Run only after the final candidates and manifest have been selected.  The earlier
native PNGs were intentionally retired; their unchanged exports use the frozen
pre-revision audit and retirement hashes.  Changed frames must still have their
actual native PNGs, and must match full-canvas LANCZOS resizing pixel for pixel.
Only review/delivery-provenance.json is written by this script.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import sys

from PIL import Image


R = Path(__file__).resolve().parents[1]
PRIOR_MANIFEST = "review/manifest-before-full-axis-20261005.json"
PRIOR_PROOF = "review/delivery-provenance-before-full-axis-20261005.json"
RETIREMENT = "review/retired-image-sources-before-full-axis-20261005.json"
TARGETS = {v["file"] for v in json.loads((R / "review/full-axis-revision-selection-20261005.json").read_text(encoding="utf-8"))["changes"]}
SPEC = {
    "run": (("S", "SE", "E", "NE", "N", "NW", "W", "SW"), 16, 60),
    "hit": (("E", "W"), 6, 40),
    "attack": (("E", "W"), 12, 30),
    "cast": (("E", "W"), 16, 45),
}
EXPECTED_PATHS = {
    f"candidate/{action}/{direction}/{i:02}.png"
    for action, (directions, count, _) in SPEC.items()
    for direction in directions
    for i in range(1, count + 1)
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local(path):
    result = (R / path).resolve()
    require(result.is_relative_to(R), f"Local evidence path escapes character directory: {path}")
    return result


def relative(path):
    return Path(path).resolve().relative_to(R).as_posix()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def normalized(path):
    return str(Path(path).resolve()).casefold()


def index_unique(rows, key, label):
    counts = Counter(row[key] for row in rows)
    repeats = sorted(path for path, count in counts.items() if count != 1)
    require(not repeats, f"Duplicate {label} paths: {repeats}")
    return {row[key]: row for row in rows}


def inventory(manifest, label, run_ms=60):
    rows = [f for sequence in manifest["sequences"] for f in sequence["frames"]]
    indexed = index_unique(rows, "path", label)
    require(set(indexed) == EXPECTED_PATHS,
            f"{label} inventory mismatch; missing={sorted(EXPECTED_PATHS-set(indexed))}; "
            f"unexpected={sorted(set(indexed)-EXPECTED_PATHS)}")
    require(len(manifest["sequences"]) == 14, f"{label} must have exactly 14 sequences")
    seen_sequences = set()
    for sequence in manifest["sequences"]:
        action, direction = sequence["action"], sequence["direction"]
        require(action in SPEC, f"{label}: unexpected action {action}")
        directions, count, ms = SPEC[action]
        if action == "run": ms = run_ms
        require(direction in directions, f"{label}: unexpected {action}/{direction}")
        key = (action, direction)
        require(key not in seen_sequences, f"{label}: repeated sequence {key}")
        seen_sequences.add(key)
        require(sequence["frameMs"] == ms and sequence["cycleMs"] == count * ms,
                f"{label}: timing mismatch for {action}/{direction}")
        require(len(sequence["frames"]) == count, f"{label}: frame count mismatch for {key}")
        for i, frame in enumerate(sequence["frames"], 1):
            require(frame["path"] == f"candidate/{action}/{direction}/{i:02}.png"
                    and frame["frame"] == i and frame["durationMs"] == ms,
                    f"{label}: frame order/duration mismatch for {key} at {i}")
    return indexed


def source_record(derived):
    source = local(derived.get("file") or derived["path"])
    record_path = local(derived["generationRecord"])
    record = read(record_path)
    require(record["sha256"] == derived["sha256"], f"Native generation SHA differs: {record_path}")
    require(normalized(local(record["file"])) == normalized(source),
            f"Native generation file differs from derivedFrom: {record_path}")
    if derived.get("generationRecordSha256"):
        require(digest(record_path) == derived["generationRecordSha256"],
                f"Native generation record hash mismatch: {record_path}")
    return source, record_path, record


def receipt_and_prompt(record, *, new):
    evidence = record["evidence"]
    receipt_path = local(evidence["receipt"])
    require(digest(receipt_path) == evidence["receiptSha256"],
            f"Receipt SHA mismatch: {receipt_path}")
    receipt = read(receipt_path)
    prompt_path = local(record["prompt"])
    require(prompt_path.is_file(), f"Missing retained prompt: {prompt_path}")
    prompt = prompt_path.read_text(encoding="utf-8-sig")
    require(bool(prompt.strip()), f"Empty prompt: {prompt_path}")
    if new:
        require(record.get("generatedAt"), f"Missing native generation time: {record['file']}")
        require(record.get("route") == "builtin" and record.get("tool") == "image_gen__imagegen",
                f"Unexpected new native generation route/tool: {record['file']}")
        for name, item in (("native record", record), ("receipt", receipt)):
            require("actualModel" in item and item["actualModel"] is None
                    and "actualQuality" in item and item["actualQuality"] is None,
                    f"{name} improperly claims disclosed model/quality: {record['file']}")
        submitted = receipt["submittedParameters"]
        require(submitted.get("transparent_background") is True,
                f"New receipt lacks submitted transparent_background=true: {receipt_path}")
        require(submitted["prompt"].rstrip("\r\n") == prompt.rstrip("\r\n"),
                f"Saved prompt does not match receipt submission: {prompt_path}")
        references = record["references"]
        require(bool(references), f"New native has no reference evidence: {record['file']}")
        submitted_paths = [normalized(p) for p in submitted["referenced_image_paths"]]
        record_paths = [normalized(p) for p in record["submittedParameters"]["referenced_image_paths"]]
        reference_paths = [normalized(ref["file"]) for ref in references]
        require(submitted_paths == record_paths == reference_paths,
                f"Submitted reference path/order differs from native record: {record['file']}")
    returned = receipt.get("output", {}).get("toolReturnedPath")
    if not returned:
        hint = receipt.get("toolResult", {}).get("output_hint", "")
        match = re.search(r"as (C:\\[^\r\n]+?\.png) by default", hint)
        if match:
            returned = match.group(1)
    return receipt_path, prompt_path, returned


def audit():
    issues, rows, references = [], [], []
    result = {
        "schemaVersion": 2,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "expectedFrames": 196,
        "expectedChangedFrames": sorted(TARGETS),
        "checked": 0,
        "passed": False,
        "issues": issues,
        "frames": rows,
        "historicalReferences": references,
        "clientRuntimeVerified": False,
        "verificationScope": "Current 196 exports re-read; changed native pixels re-read; "
                             "unchanged retired natives rely on frozen prior proof, never a new native read.",
        "checks": [
            "196 exact expected candidate paths and original sequence timing/order",
            "all current candidate SHA, 1024 RGBA, alpha 0..255 and unique decoded pixels",
            "Unchanged export/native bindings against frozen successful prior proof and retirement SHA",
            "Changed native PNGs exactly 1254 RGBA and exact whole-canvas LANCZOS export pixels",
            "retained source generation, receipt SHA and prompt evidence",
            "new references checked as live bytes or explicit SHA-bound historical candidate records",
            "unique selected native SHA and disclosed tool output path",
        ],
    }
    try:
        manifest = read(local("manifest.json"))
        current = inventory(manifest, "current manifest")
        prior_manifest = read(local(PRIOR_MANIFEST))
        prior = inventory(prior_manifest, "prior manifest", run_ms=75)
        proof = read(local(PRIOR_PROOF))
        require(proof.get("passed") is True and proof.get("checked") == 196,
                "Frozen prior proof is not a successful 196-frame audit")
        prior_rows = index_unique(proof["frames"], "file", "prior proof")
        require(set(prior_rows) == EXPECTED_PATHS and all(row.get("passed") is True for row in prior_rows.values()),
                "Frozen prior proof lacks a passed row for each expected frame")
        retirement = read(local(RETIREMENT))
        require(retirement.get("status") == "applied", "Retirement log is not applied")
        require(normalized(retirement["scope"]) == normalized(R), "Retirement log scope differs from character")
        retired = index_unique(retirement["removedFiles"], "file", "retired-image")
        result["priorProof"] = {"file": PRIOR_PROOF, "sha256": digest(local(PRIOR_PROOF)),
                                "checkedAt": proof.get("checkedAt")}
        result["priorManifest"] = {"file": PRIOR_MANIFEST, "sha256": digest(local(PRIOR_MANIFEST))}
        result["retirementProof"] = {"file": RETIREMENT, "sha256": digest(local(RETIREMENT))}
        result["manifest"] = {"file": "manifest.json", "sha256": digest(local("manifest.json"))}
        revision_path = local("review/full-axis-revision-selection-20261005.json")
        revision = read(revision_path)
        selected = index_unique(revision["changes"], "file", "revision selection")
        require(set(selected) == TARGETS, "Revision target set changed during audit")
        approval_ref = revision["approvalEvidence"]
        require(digest(local(approval_ref["file"])) == approval_ref["sha256"], "Approved native evidence SHA differs")
        approved = read(local(approval_ref["file"]))
        require(approved["passed"] and not approved["remainingRequiredRepairs"], "Native art review remains incomplete")
        approved_rows = index_unique(approved["reviewedDrafts"], "path", "approved native")
        result["revisionSelection"] = {"file": relative(revision_path), "sha256": digest(revision_path)}
        result["approvedNativeEvidence"] = approval_ref
        for path, selection in selected.items():
            require(selection["oldSha256"] == prior[path]["sha256"], f"Selected previous export mismatch: {path}")
            require(selection["sha256"] == current[path]["sha256"], f"Selected current export mismatch: {path}")
            require(selection["source"] == current[path]["nativeSource"], f"Selected native path mismatch: {path}")
            approved_row = approved_rows[selection["source"]]
            require(approved_row["passed"] and approved_row["sha256"] == selection["nativeSha256"], f"Selected native not approved: {path}")
        changed = {path for path in current if current[path]["sha256"] != prior[path]["sha256"]}
        result["actualChangedFrames"] = sorted(changed)
        if changed != TARGETS:
            issues.append({"stage": "replacement_scope", "error": "Actual replacement set differs from explicit revision frame list",
                           "missingChanges": sorted(TARGETS - changed), "unexpectedChanges": sorted(changed - TARGETS)})

        def check_historical_binding(path, historical_record):
            old = prior[path]
            evidence = prior_rows[path]
            require(evidence["passed"] is True and historical_record["sha256"] == old["sha256"] == evidence["sha256"],
                    f"Historical candidate SHA is not the passed prior export: {path}")
            derived = historical_record["derivedFrom"]
            native_path, _, native_record = source_record(derived)
            native = relative(native_path)
            require(native == old["nativeSource"] == evidence["native"],
                    f"Historical native source binding changed: {path}")
            require(native in retired and retired[native]["sha256"] == derived["sha256"] == native_record["sha256"],
                    f"Historical native SHA missing/mismatched in retirement log: {path}; native={native}")
            require(historical_record["nativeFrameSize"] == evidence["nativeSize"]
                    == native_record["nativeFrameSize"], f"Historical native size binding differs: {path}")
            return evidence

        def check_reference(ref, frame):
            path = Path(ref["file"]).resolve()
            expected_sha = ref["sha256"]
            current_sha = digest(path) if path.is_file() else None
            evidence_row = {"frame": frame, "reference": str(path), "recordedSha256": expected_sha,
                            "currentSha256": current_sha}
            history = None
            if ref.get("generationRecord"):
                history_path = local(ref["generationRecord"])
                require(history_path.is_relative_to(local("sources/reference-history")),
                        f"Reference history record is outside sources/reference-history: {history_path}")
                require(history_path.name == expected_sha + ".generation.json",
                        f"Reference history filename not bound to expected image SHA: {history_path}")
                require(ref.get("generationRecordSha256") == digest(history_path),
                        f"Reference history record SHA mismatch: {history_path}")
                history = read(history_path)
                require(history["sha256"] == expected_sha, f"Historical reference image SHA differs: {history_path}")
                require(normalized(local(history["file"])) == normalized(path),
                        f"Historical reference file binding differs: {history_path}")
                evidence_row.update({"historicalRecord": relative(history_path),
                                     "historicalRecordSha256": digest(history_path)})
            if current_sha == expected_sha:
                evidence_row.update(status="live_reference_bytes_verified", historicalImageBytesReverified=True)
            else:
                require(path.is_relative_to(local("candidate")),
                        f"New native requires live reference bytes; missing/changed non-candidate reference: {path}")
                require(history is not None,
                        f"Replaced candidate reference lacks explicit SHA-bound generationRecord: {path}")
                old_path = relative(path)
                require(old_path in prior, f"Historical candidate reference absent from prior manifest: {old_path}")
                check_historical_binding(old_path, history)
                evidence_row.update(status="historical_candidate_reference_superseded",
                                    historicalImageBytesReverified=False,
                                    verificationMethod="Explicit saved generation record SHA + prior passed export SHA + retired native SHA")
            references.append(evidence_row)

        pixel_seen, file_seen, native_seen, output_seen = {}, {}, {}, {}
        for path, frame in current.items():
            row = {"file": path, "sha256": frame["sha256"], "native": frame.get("nativeSource"),
                   "nativeSize": None, "receipt": None, "passed": False}
            stage = "current_export"
            try:
                destination = local(path)
                export_sha = digest(destination)
                require(export_sha == frame["sha256"], f"Current PNG SHA differs from manifest: {path}")
                record_path = local(frame["generationRecord"])
                exported_record = read(record_path)
                require(normalized(local(exported_record["file"])) == normalized(destination)
                        and exported_record["sha256"] == export_sha, f"Current export generation binding differs: {path}")
                with Image.open(destination) as image:
                    image.load()
                    require(image.format == "PNG" and image.mode == "RGBA" and image.size == (1024, 1024),
                            f"Current image must be 1024x1024 RGBA PNG: {path}; got {image.format}/{image.mode}/{image.size}")
                    require(image.getchannel("A").getextrema() == (0, 255), f"Current alpha range is not 0..255: {path}")
                    pixels = image.tobytes()
                pixel_sha = hashlib.sha256(pixels).hexdigest()
                require(pixel_sha not in pixel_seen, f"Duplicate decoded pixels: {path} matches {pixel_seen.get(pixel_sha)}")
                require(export_sha not in file_seen, f"Duplicate PNG bytes: {path} matches {file_seen.get(export_sha)}")
                pixel_seen[pixel_sha], file_seen[export_sha] = path, path
                row["pixelSha256"] = pixel_sha
                row["generationRecord"] = relative(record_path)
                row["generationRecordSha256"] = digest(record_path)
                derived = exported_record["derivedFrom"]
                native_path, native_record_path, native_record = source_record(derived)
                native = relative(native_path)
                row.update(native=native, nativeSha256=derived["sha256"], nativeSize=exported_record["nativeFrameSize"],
                           nativeGenerationRecord=relative(native_record_path), nativeGenerationRecordSha256=digest(native_record_path))
                if path in selected:
                    require(selected[path]["source"] == native and selected[path]["nativeSha256"] == derived["sha256"],
                            f"Selected native SHA/path differs from live export derivation: {path}")
                require(frame["nativeSource"] == native, f"Manifest native source differs from derivedFrom: {path}")
                require(derived["sha256"] not in native_seen,
                        f"Duplicate selected native SHA: {path} matches {native_seen.get(derived['sha256'])}")
                native_seen[derived["sha256"]] = path
                stage = "source_receipt_prompt"
                receipt_path, prompt_path, returned = receipt_and_prompt(native_record, new=path in changed)
                row.update(receipt=relative(receipt_path), receiptSha256=digest(receipt_path),
                           prompt=relative(prompt_path), promptSha256=digest(prompt_path))
                if returned:
                    key = normalized(returned)
                    require(key not in output_seen, f"Duplicate tool output path: {path} matches {output_seen.get(key)}")
                    output_seen[key] = path
                    row["toolReturnedPath"] = returned
                if path not in changed:
                    stage = "unchanged_prior_proof_and_retirement"
                    old_evidence = check_historical_binding(path, exported_record)
                    require(row["receipt"] == old_evidence["receipt"], f"Retained receipt path differs from prior proof: {path}")
                    row.update(verificationMethod="unchanged_export_rechecked_native_previously_verified",
                               priorProof={"file": PRIOR_PROOF, "sha256": result["priorProof"]["sha256"], "frame": path},
                               nativePixelBytesReadThisAudit=False, nativeToExportPixelsCheckedThisAudit=False,
                               nativeToExportPixelsPreviouslyVerified=True,
                               retiredNativeSha256=retired[native]["sha256"])
                else:
                    stage = "changed_native_pixels"
                    require(path in TARGETS, f"Unexpected changed frame requires explicit scope review: {path}")
                    require(native_path.is_file(), f"Changed frame has no live native PNG: {native_path}")
                    require(digest(native_path) == derived["sha256"], f"Live native PNG SHA mismatch: {native_path}")
                    with Image.open(native_path) as image:
                        image.load()
                        require(image.format == "PNG" and image.mode == "RGBA" and image.size == (1254, 1254),
                                f"Changed native must be 1254x1254 RGBA PNG: {native_path}; got {image.format}/{image.mode}/{image.size}")
                        require(image.getchannel("A").getextrema() == (0, 255), f"Native alpha range is not 0..255: {native_path}")
                        require(exported_record["nativeFrameSize"] == native_record["nativeFrameSize"] == [1254, 1254],
                                f"Native size records differ from live image: {path}")
                        require(image.resize((1024, 1024), Image.Resampling.LANCZOS).tobytes() == pixels,
                                f"Current export is NOT an exact full-canvas LANCZOS resize of native pixels: {path}")
                    stage = "changed_reference_evidence"
                    for reference in native_record["references"]:
                        check_reference(reference, path)
                    row.update(verificationMethod="changed_native_and_export_pixels_rechecked",
                               nativePixelBytesReadThisAudit=True, nativeToExportPixelsCheckedThisAudit=True,
                               nativeToExportPixelsPreviouslyVerified=False)
                row["passed"] = True
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
                issues.append({"file": path, "stage": stage, "error": row["error"]})
            rows.append(row)
        result["checked"] = len(rows)
        result["passedFrameCount"] = sum(row["passed"] for row in rows)
        result["unchangedExportsRechecked"] = sum(row.get("verificationMethod") == "unchanged_export_rechecked_native_previously_verified" for row in rows)
        result["changedNativesAndExportsRechecked"] = sum(row.get("verificationMethod") == "changed_native_and_export_pixels_rechecked" for row in rows)
        result["passed"] = (len(rows) == 196 and result["passedFrameCount"] == 196 and not issues
                            and result["unchangedExportsRechecked"] == 196 - len(TARGETS) and result["changedNativesAndExportsRechecked"] == len(TARGETS))
    except Exception as exc:
        issues.append({"stage": "audit_setup", "error": f"{type(exc).__name__}: {exc}"})
    output = local("review/delivery-provenance.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result.get(key) for key in (
        "checked", "expectedFrames", "passed", "unchangedExportsRechecked", "changedNativesAndExportsRechecked", "issues"
    )}, ensure_ascii=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(audit())
