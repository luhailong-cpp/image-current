"""Normalize recorded native evidence without changing any sprite pixels."""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, data: dict) -> None:
    assert path.resolve().is_relative_to(ROOT)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    before_runtime = {p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / "runtime/attack").rglob("*.png")}
    before_sidecars = {p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / "runtime/attack").rglob("*.generation.json")}
    edits = []
    plans = []
    for direction, count in (("E", 12), ("W", 6)):
        for frame in range(1, count + 1):
            record = ROOT / f"provenance/attack/{direction}/{frame:02}.generation.json"
            data = load(record)
            if data.get("recordNormalization", {}).get("kind") == "native_record_restored_from_existing_evidence":
                continue
            original_record_sha = sha(record)
            source = data["derivedFrom"]
            native_path = Path(source["path"])
            native_sha = source["sha256"]
            receipt_path = ROOT / data["evidence"]["receipt"]
            receipt = load(receipt_path)
            assert native_path.name in receipt["output_hint"], record
            assert receipt["output_hint"] == data["evidence"]["output_hint"], record
            assert native_path.exists() and sha(native_path) == native_sha, record
            native_info = data["native"]
            with Image.open(native_path) as image:
                assert list(image.size) == [native_info["width"], native_info["height"]], record
                assert image.mode == native_info["mode"] and image.format == native_info["format"], record
            runtime = ROOT / f"runtime/attack/{direction}/{frame:02}.png"
            sidecar = load(Path(str(runtime) + ".generation.json"))
            assert data["sha256"] == sidecar["sha256"] == sha(runtime), record
            assert sidecar["derivedFrom"]["sha256"] == native_sha, record
            assert (ROOT / sidecar["derivedFrom"]["generationRecord"]).resolve() == record, record
            assert Path(sidecar["derivedFrom"]["path"]).resolve() == native_path.resolve(), record
            assert data["actualModel"] is None and data["actualQuality"] is None, record
            assert data["submittedParameters"]["model"] is None and data["submittedParameters"]["quality"] is None, record
            # Keep the prior export fields as history; this record becomes the native
            # generation endpoint already expected by the unmodified runtime sidecar.
            export_keys = ("file", "sha256", "width", "height", "format", "mode", "alphaExtrema", "alphaBbox", "derivedFrom", "operation", "durationMs", "pivot", "event", "visualReview")
            archived = {key: copy.deepcopy(data[key]) for key in export_keys if key in data}
            for key in export_keys:
                data.pop(key, None)
            data.update(file=str(native_path), sha256=native_sha, **{key: native_info[key] for key in ("width", "height", "format", "mode")})
            data["recordNormalization"] = {
                "kind": "native_record_restored_from_existing_evidence",
                "normalizedAt": updated_at,
                "priorRecordSha256": original_record_sha,
                "reason": "The runtime sidecar points to this native record, but its former top-level fields repeated the export and left derivedFrom without a generation record. Native path/hash/dimensions come from the original recorded source and were verified against the receipt and native file; no new generation is claimed.",
                "unchangedRuntimeSidecar": Path(str(runtime) + ".generation.json").relative_to(ROOT).as_posix(),
                "previousExportFields": archived,
            }
            plans.append((record, data))
            edits.append({"record": record.relative_to(ROOT).as_posix(), "nativePath": str(native_path), "nativeSha256": native_sha, "runtime": runtime.relative_to(ROOT).as_posix(), "runtimeSha256": sidecar["sha256"], "receipt": receipt_path.relative_to(ROOT).as_posix()})

    rejected = ROOT / "provenance/cast/E03-rejected-early-effect.generation.json"
    rejected_data = load(rejected)
    old_pointer = rejected_data["evidence"]["receipt"]
    correct_pointer = "provenance/cast/E03-rejected-early-effect.job.json"
    job = load(ROOT / correct_pointer)
    assert Path(job["source"]).resolve() == Path(rejected_data["source"]).resolve()
    assert job["receipt"]["output_hint"] == rejected_data["evidence"]["output_hint"]
    if old_pointer != correct_pointer:
        rejected_data["evidence"]["receipt"] = correct_pointer
        rejected_data["receiptLinkCorrection"] = {"correctedAt": updated_at, "previousPointer": old_pointer, "reason": "Historical job was retained under its rejected name; source path and output_hint match exactly."}
        plans.append((rejected, rejected_data))
    for record, data in plans:
        write(record, data)

    assert before_runtime == {p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / "runtime/attack").rglob("*.png")}
    assert before_sidecars == {p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / "runtime/attack").rglob("*.generation.json")}
    report = {"checkedAt": updated_at, "normalizedRecords": edits, "correctedRejectedReceipt": correct_pointer, "runtimeAttackPngHashesUnchanged": before_runtime, "runtimeAttackSidecarHashesUnchanged": before_sidecars, "scope": "No sprite pixels, runtime sidecars, cast/W/06, final manifest, README, STATUS, or MERGE_HANDOFF changed."}
    write(ROOT / "provenance/provenance-finalize-evidence.json", report)
    print(json.dumps({"normalizedNativeRecords": len(edits), "receiptPointerCorrected": old_pointer != correct_pointer, "attackPngUnchanged": len(before_runtime), "attackSidecarsUnchanged": len(before_sidecars)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
