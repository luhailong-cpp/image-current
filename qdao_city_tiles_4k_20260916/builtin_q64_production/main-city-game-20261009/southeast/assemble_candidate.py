#!/usr/bin/env python3
"""Assemble only r13_c13's sixteen active native patches; never accept a tile.

Requires Python, Pillow and NumPy. Default / --check is read-only preflight.
Pass --assemble explicitly to write candidate/ and review/ under r13_c13.
No source resizing, generation, progress updates, or formal acceptance occurs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


ZONE = Path(__file__).resolve().parent
PROJECT = ZONE.parent
TILE_ID = "r13_c13"
TILE = ZONE / TILE_ID
NATIVE = TILE / "native"
ACTIVE_MAP = TILE / "active-native-map.json"
CONTRACT = PROJECT / "production-contract.json"
CANDIDATE = TILE / "candidate"
REVIEW = TILE / "review"
GRID, CORE, HALO = 4, 1024, 115
PATCH, OVERLAP, FINAL, ASSEMBLED = 1254, 230, 4096, 4326
ORIGIN = (49152, 49152)
FEATHER_RADIUS = 2.0
EXPECTED_IDS = [f"p{r:02d}_{c:02d}" for r in range(1, 5) for c in range(1, 5)]


class RejectedInput(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RejectedInput(message)


def successful_generation_receipt(status: object) -> bool:
    """Generation success permits candidate assembly, never art/geometry acceptance."""
    if not isinstance(status, str):
        return False
    normalized = status.strip().lower()
    if "rejected" in normalized or "failed" in normalized:
        return False
    return normalized == "succeeded" or re.fullmatch(
        r"succeeded_pending_[a-z0-9]+(?:_[a-z0-9]+)*", normalized
    ) is not None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    require(path.is_file(), f"Missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"Expected JSON object: {path}")
    return value


def recorded_path(value: object) -> Path:
    require(isinstance(value, str) and bool(value), "Missing recorded path")
    path = Path(value)
    return (path if path.is_absolute() else TILE / path).resolve()


def checked_hash(path: Path, expected: object, guards: dict[str, str]) -> str:
    require(isinstance(expected, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected) is not None,
            f"Missing/invalid SHA-256: {path}")
    require(path.is_file(), f"Missing source: {path}")
    actual = sha256(path)
    require(actual == expected.lower(), f"SHA-256 mismatch: {path}")
    guards[str(path.resolve())] = actual
    return actual


def remember(path: Path, guards: dict[str, str]) -> str:
    require(path.is_file(), f"Missing evidence: {path}")
    digest = sha256(path)
    guards[str(path.resolve())] = digest
    return digest


def coordinates(logical_id: str) -> dict:
    row, column = int(logical_id[1:3]), int(logical_id[4:6])
    x, y = ORIGIN[0] + (column - 1) * CORE, ORIGIN[1] + (row - 1) * CORE
    return {"id": logical_id, "row": row, "column": column,
            "coreBox": [x, y, x + CORE, y + CORE],
            "contextBox": [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO],
            "nativeExpected": [PATCH, PATCH],
            "coreCropExpected": [HALO, HALO, HALO + CORE, HALO + CORE]}


def preflight() -> tuple[list[list[np.ndarray]], list[dict], dict[str, str], dict, dict]:
    """Validate every input before creating any output directory or file."""
    guards: dict[str, str] = {}
    contract = load_json(CONTRACT)
    remember(CONTRACT, guards)
    require(contract.get("artCanvasPixels") == [65536, 65536]
            and contract.get("formalTilePixels") == [FINAL, FINAL]
            and contract.get("rows") == 16 and contract.get("columns") == 16,
            "Production contract artwork coordinates changed")
    require(contract.get("builtinOnly") is True and contract.get("paidApiAllowed") is False,
            "Production route contract changed")
    plan = contract.get("nativePatchPlan", {})
    require(plan.get("corePixels") == CORE and plan.get("haloPixels") == HALO
            and plan.get("expectedNativePixels") == PATCH
            and plan.get("subrows") == GRID and plan.get("subcolumns") == GRID
            and plan.get("resizeFinalArtAllowed") is False,
            "Native patch plan changed; do not resize inputs to make them fit")
    active = load_json(ACTIVE_MAP)
    remember(ACTIVE_MAP, guards)
    missing = sorted(set(EXPECTED_IDS) - set(active))
    extra = sorted(set(active) - set(EXPECTED_IDS))
    require(not missing and not extra,
            f"Exactly 16 logical patches required; missing={missing}; unexpected={extra}")
    require(all(isinstance(v, str) for v in active.values()), "Active map values must be version names")
    require(len(set(active.values())) == 16, "A native version is assigned to multiple logical patches")
    required_files = [NATIVE / f"{active[key]}{suffix}" for key in EXPECTED_IDS
                      for suffix in (".png", ".png.generation.json")]
    absent = [str(path) for path in required_files if not path.is_file()]
    require(not absent, f"Missing native images or generation records: {absent}")
    sources, pixels = [], []
    source_hashes: set[str] = set()
    for logical_id in EXPECTED_IDS:
        version = active[logical_id]
        require(re.fullmatch(re.escape(logical_id) + r"(?:_[A-Za-z0-9][A-Za-z0-9_-]*)?", version) is not None,
                f"Unsafe or mismatched version name: {logical_id} -> {version}")
        native = NATIVE / f"{version}.png"
        record_path = NATIVE / f"{version}.png.generation.json"
        record = load_json(record_path)
        record_sha = remember(record_path, guards)
        status = str(record.get("status", "")).strip().lower()
        require(bool(status) and "rejected" not in status and "failed" not in status,
                f"Rejected, failed, or missing source status: {version}: {status}")
        require(record.get("id") == version and recorded_path(record.get("file")) == native.resolve(),
                f"Native identity/path mismatch: {version}")
        require(record.get("tool") == "image_gen.imagegen" and record.get("route") == "builtin",
                f"Non-builtin generation source: {version}")
        require(record.get("resizedAfterGeneration") is False and record.get("finalArtUpscaled") is False,
                f"Missing explicit no-resize/no-upscale evidence: {version}")
        require([record.get("width"), record.get("height")] == [PATCH, PATCH]
                and record.get("format") == "PNG", f"Recorded dimensions/format differ: {version}")
        expected_coordinates = coordinates(logical_id)
        require(record.get("coordinates") == expected_coordinates, f"Wrong global coordinates: {version}")
        native_sha = checked_hash(native, record.get("sha256"), guards)
        require(native_sha not in source_hashes, f"Duplicate native pixels/file used twice: {version}")
        source_hashes.add(native_sha)
        with Image.open(native) as image:
            image.load()
            require(image.format == "PNG" and image.size == (PATCH, PATCH)
                    and image.mode in ("RGB", "RGBA"), f"Actual native image invalid: {version}")
            require(image.mode == record.get("mode"), f"Native mode differs from record: {version}")
            require(image.mode != "RGBA" or image.getextrema()[3] == (255, 255),
                    f"Transparent/unpainted source pixels: {version}")
            pixels.append(np.asarray(image.convert("RGB")).copy())
        evidence = record.get("evidence", {})
        require(evidence.get("originalSha256") == native_sha, f"Original-output hash mismatch: {version}")
        original = recorded_path(evidence.get("originalOutputPath"))
        original_present = original.is_file()
        if original_present:
            checked_hash(original, native_sha, guards)
        prompt_path = recorded_path(record.get("prompt"))
        checked_hash(prompt_path, record.get("promptSha256"), guards)
        prompt_text = prompt_path.read_text(encoding="utf-8-sig")
        require(bool(prompt_text.strip()), f"Empty generation prompt: {version}")
        receipt_path = recorded_path(evidence.get("receipt"))
        request_path = recorded_path(evidence.get("request"))
        receipt, request = load_json(receipt_path), load_json(request_path)
        receipt_sha, request_sha = remember(receipt_path, guards), remember(request_path, guards)
        require(successful_generation_receipt(receipt.get("status"))
                and receipt.get("tool") == "image_gen.imagegen",
                f"Missing successful builtin receipt: {version}: {receipt.get('status')}")
        require(isinstance(request.get("prompt"), str)
                and request["prompt"].strip() == prompt_text.strip(), f"Prompt/request mismatch: {version}")
        require(request.get("transparent_background") is False, f"Opaque map request required: {version}")
        references = record.get("references")
        require(isinstance(references, list) and bool(references), f"Missing references: {version}")
        reference_paths = []
        for reference in references:
            path = recorded_path(reference.get("path"))
            checked_hash(path, reference.get("sha256"), guards)
            with Image.open(path) as ref_image:
                require(list(ref_image.size) == reference.get("dimensions"),
                        f"Reference dimensions changed: {path}")
            require(bool(reference.get("role")), f"Missing reference role: {path}")
            reference_paths.append(path)
        submitted = record.get("submittedParameters", {})
        for origin, listed in (("request", request.get("referenced_image_paths")),
                               ("generation record", submitted.get("referenced_image_paths"))):
            require(isinstance(listed, list) and [recorded_path(p) for p in listed] == reference_paths,
                    f"Reference order/path mismatch in {origin}: {version}")
        # Preserve unknown model/quality values exactly; configuration targets are not actual values.
        sources.append({"logicalId": logical_id, "activeVersion": version,
                        "native": str(native), "nativeSha256": native_sha,
                        "measuredSize": [PATCH, PATCH], "generationRecord": str(record_path),
                        "generationRecordSha256": record_sha, "generationRecordSnapshot": record,
                        "promptText": prompt_text, "receiptSha256": receipt_sha,
                        "receiptSnapshot": receipt, "requestSha256": request_sha,
                        "requestSnapshot": request, "originalFilePresentAndVerified": original_present,
                        "originalEvidenceNote": ("Original bytes verified" if original_present else
                            "Original output absent; preserved native hash matches recorded original SHA-256"),
                        "coordinates": expected_coordinates})
    remember(Path(__file__), guards)
    return [pixels[r * GRID:(r + 1) * GRID] for r in range(GRID)], sources, guards, active, contract


def verify_unchanged(guards: dict[str, str]) -> None:
    for filename, expected in guards.items():
        path = Path(filename)
        require(path.is_file() and sha256(path) == expected, f"Input changed during assembly: {path}")


def minimum_vertical_seam(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Existing seam_helpers.py algorithm, embedded to avoid external import writes."""
    difference = left.astype(np.float32) - right.astype(np.float32)
    cost = np.mean(difference * difference, axis=2)
    height, width = cost.shape
    center = (width - 1) / 2.0
    normalized = np.abs((np.arange(width, dtype=np.float32) - center) / max(center, 1.0))
    typical = float(np.median(cost)) + 1.0
    cost += (normalized ** 4)[None, :] * typical * 0.16
    margin = min(24, max(1, width // 12))
    cost[:, :margin] += typical * 8.0
    cost[:, -margin:] += typical * 8.0
    previous = cost[0].copy()
    backtrack = np.zeros((height, width), dtype=np.int8)
    infinity = np.float32(np.finfo(np.float32).max / 16.0)
    for y in range(1, height):
        from_left, from_right = np.empty_like(previous), np.empty_like(previous)
        from_left[0], from_right[-1] = infinity, infinity
        from_left[1:], from_right[:-1] = previous[:-1], previous[1:]
        candidates = np.stack((from_left, previous, from_right), axis=0)
        choices = np.argmin(candidates, axis=0)
        backtrack[y] = choices.astype(np.int8) - 1
        previous = cost[y] + np.take_along_axis(candidates, choices[None, :], axis=0)[0]
    seam = np.empty(height, dtype=np.int32)
    seam[-1] = int(np.argmin(previous))
    for y in range(height - 1, 0, -1):
        seam[y - 1] = seam[y] + int(backtrack[y, seam[y]])
    return seam


def append_patch(base: np.ndarray, patch: np.ndarray, label: str,
                 seam_arrays: dict[str, np.ndarray]) -> tuple[np.ndarray, dict]:
    require(base.shape[0] == patch.shape[0], f"Overlap height mismatch: {label}")
    left, right = base[:, -OVERLAP:], patch[:, :OVERLAP]
    seam = minimum_vertical_seam(left, right)
    mask = np.uint8(np.arange(OVERLAP)[None, :] >= seam[:, None]) * 255
    alpha = np.asarray(Image.fromarray(mask).filter(ImageFilter.GaussianBlur(FEATHER_RADIUS)))
    weight = alpha.astype(np.uint32)[..., None]
    blended = ((left.astype(np.uint32) * (255 - weight) + right.astype(np.uint32) * weight + 127)
               // 255).astype(np.uint8)
    same = np.all(left == right, axis=2)
    require(np.array_equal(blended[same], left[same]), f"Identical overlap pixels changed: {label}")
    seam_arrays[label + "_path"] = seam
    seam_arrays[label + "_alpha"] = alpha
    difference = np.abs(left.astype(np.int16) - right.astype(np.int16))
    metric = {"label": label, "overlapPixels": OVERLAP, "seamLength": len(seam),
              "seamMin": int(seam.min()), "seamMax": int(seam.max()),
              "beforeBlendMeanAbsoluteDifference": float(difference.mean()),
              "beforeBlendP95AbsoluteDifference": float(np.percentile(difference, 95)),
              "beforeBlendMaxAbsoluteDifference": int(difference.max()),
              "identicalInputPixelsPreserved": True,
              "visualAcceptance": "pending; numeric error does not prove geometric continuity"}
    return np.concatenate((base[:, :-OVERLAP], blended, patch[:, OVERLAP:]), axis=1), metric


def write_png(image: Image.Image, path: Path) -> dict:
    temporary = path.with_name(path.stem + ".writing.png")
    image.save(temporary, format="PNG")
    with Image.open(temporary) as saved:
        saved.load()
        require(saved.size == image.size and np.array_equal(np.asarray(saved), np.asarray(image)),
                f"Saved PNG differs from intended pixels: {path}")
    temporary.replace(path)
    return {"file": path.relative_to(TILE).as_posix(), "size": list(image.size), "sha256": sha256(path)}


def write_json(value: dict, path: Path) -> None:
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def assemble(rows: list[list[np.ndarray]], sources: list[dict], guards: dict[str, str],
             active: dict, contract: dict) -> dict:
    seam_arrays: dict[str, np.ndarray] = {}
    seams, strips = [], []
    for row, patches in enumerate(rows, 1):
        strip = patches[0]
        for column, patch in enumerate(patches[1:], 2):
            strip, metric = append_patch(strip, patch, f"row{row:02d}_c{column-1:02d}_c{column:02d}", seam_arrays)
            seams.append(metric)
        require(strip.shape == (PATCH, ASSEMBLED, 3), "Incorrect assembled row size")
        strips.append(strip)
    combined = strips[0].transpose(1, 0, 2)
    for row, strip in enumerate(strips[1:], 2):
        combined, metric = append_patch(combined, strip.transpose(1, 0, 2),
                                        f"rows_r{row-1:02d}_r{row:02d}", seam_arrays)
        seams.append(metric)
    combined = combined.transpose(1, 0, 2)
    require(combined.shape == (ASSEMBLED, ASSEMBLED, 3), "Incorrect context assembly size")
    final = Image.fromarray(combined[HALO:HALO + FINAL, HALO:HALO + FINAL].copy())
    require(final.size == (FINAL, FINAL), "Incorrect final size")
    verify_unchanged(guards)
    # No output directories are made before all sixteen sources and composition pass.
    CANDIDATE.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    review_items = []
    rectangles = {}
    for position in (CORE, 2 * CORE, 3 * CORE):
        rectangles[f"vertical-x{position}-full-height"] = (position - 256, 0, position + 256, FINAL)
        rectangles[f"horizontal-y{position}-full-width"] = (0, position - 256, FINAL, position + 256)
    for y in (CORE, 2 * CORE, 3 * CORE):
        for x in (CORE, 2 * CORE, 3 * CORE):
            rectangles[f"junction-x{x}-y{y}"] = (x - 450, y - 450, x + 450, y + 450)
    rectangles.update({"edge-north": (0, 0, FINAL, 256), "edge-south": (0, FINAL - 256, FINAL, FINAL),
                       "edge-west": (0, 0, 256, FINAL), "edge-east": (FINAL - 256, 0, FINAL, FINAL)})
    for label, box in rectangles.items():
        item = write_png(final.crop(box), REVIEW / f"{label}-100pct.png")
        item.update({"kind": "native-pixel-crop", "cropBoxIn4096": list(box), "resized": False})
        review_items.append(item)
    overview = write_png(final.resize((1024, 1024), Image.Resampling.LANCZOS), REVIEW / "overview-preview-only.png")
    overview.update({"kind": "downsampled-preview-only", "resized": True})
    review_items.append(overview)
    masks_path = REVIEW / "seam-paths-and-alpha.npz"
    masks_temporary = REVIEW / "seam-paths-and-alpha.writing.npz"
    np.savez_compressed(masks_temporary, **seam_arrays)
    masks_temporary.replace(masks_path)
    context_output = write_png(Image.fromarray(combined), CANDIDATE / f"{TILE_ID}-context-4326.png")
    output = write_png(final, CANDIDATE / f"{TILE_ID}-4k-candidate.png")
    verify_unchanged(guards)
    manifest = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "tileId": TILE_ID, "status": "candidate_pending_internal_and_external_visual_review",
        "formalAccepted": False, "runtimeIntegration": False, "capacity5000Validated": False,
        "contractSnapshot": contract, "activeNativeMapSnapshot": active,
        "verifiedInputHashes": guards, "nativeSources": sources,
        "parameters": {"grid": [GRID, GRID], "origin": "top-left", "order": "row-major",
                       "tileGlobalCoreBox": [49152, 49152, 53248, 53248],
                       "tileGlobalContextBox": [49037, 49037, 53363, 53363],
                       "nativePixels": [PATCH, PATCH], "corePixels": CORE, "haloPerSide": HALO,
                       "adjacentOverlap": OVERLAP, "assembledSize": [ASSEMBLED, ASSEMBLED],
                       "finalCropBox": [HALO, HALO, HALO + FINAL, HALO + FINAL],
                       "method": "minimum-error seam; horizontal row joins, then vertical strip joins",
                       "seamAlgorithmOrigin": "tianyong_festival_hd_20260910/seam_helpers.py:_minimum_vertical_seam",
                       "featherRadiusPixels": FEATHER_RADIUS,
                       "blendArithmetic": "(left*(255-alpha)+right*alpha+127)//255, uint32",
                       "sourceResampling": False, "sourceUpscaling": False, "registration": False,
                       "colorMatching": False, "globalBlur": False, "sharpening": False,
                       "layoutOnlyPixelsComposited": False},
        "seamMetrics": seams, "seamPathsAndAlpha": {"file": masks_path.relative_to(TILE).as_posix(),
            "sha256": sha256(masks_path), "arrayKeys": sorted(seam_arrays)},
        "contextOutput": context_output, "output": output, "reviewImages": review_items,
        "visualReview": {"status": "pending", "fullVerticalSeamBands": 3, "fullHorizontalSeamBands": 3,
                         "junctionCrops": 9, "externalEdgeCrops": 4,
                         "required": "Inspect all at 100%; repaint geometry mismatches; review neighboring tile context before formal acceptance"},
    }
    manifest_path = CANDIDATE / "assembly-manifest.json"
    write_json(manifest, manifest_path)
    return {"status": manifest["status"], "nativeSourceCount": len(sources),
            "candidate": str(CANDIDATE / f"{TILE_ID}-4k-candidate.png"),
            "manifest": str(manifest_path), "formalAccepted": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Read-only source preflight (default)")
    mode.add_argument("--assemble", action="store_true", help="Write candidate and review only after all 16 sources validate")
    args = parser.parse_args()
    try:
        rows, sources, guards, active, contract = preflight()
        if args.assemble:
            result = assemble(rows, sources, guards, active, contract)
        else:
            verify_unchanged(guards)
            result = {"status": "sources_ready_candidate_not_written", "nativeSourceCount": len(sources),
                      "tileId": TILE_ID, "formalAccepted": False}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (RejectedInput, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "refused", "error": str(error), "formalAccepted": False},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
