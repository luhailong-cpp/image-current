"""Exact native crops and bounded four-side quilting for r10_c05 local repairs.

Crop: --input FILE --candidate-box L T R B --output crop.png [--preflight]
Apply: --input FILE --record repair.json --output repaired.png [--preflight]
Batch: --input FILE --selection r10_c05/repairs/selection.json --output repaired.png
Omitting record/box/selection reads the default repairs/selection.json list.
Preflight computes and validates in memory; it never creates output files.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
T = ROOT / "r10_c05"
DEFAULT_INPUT = T / "output" / "r10_c05.candidate.png"
DEFAULT_OUTPUT = T / "output" / "r10_c05.repaired.candidate.png"
DEFAULT_SELECTION = T / "repairs" / "selection.json"
ORIGIN = (16384, 36864)
FINAL, PATCH, HALO, CORE = 4096, 1254, 115, 1024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return digest(path.read_bytes())


def read(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def tile_path(value: str | Path) -> Path:
    """Paths inside records/selections are relative to the tile, unless absolute."""
    path = Path(value)
    return path.resolve() if path.is_absolute() else (T / path).resolve()


def check_file(path: Path, checked: dict[str, str], expected: str | None = None) -> str:
    path = path.resolve()
    require(path.is_file(), f"Missing source/provenance file: {path}")
    value = sha(path)
    if expected is not None:
        require(isinstance(expected, str) and value == expected.lower(), f"SHA-256 mismatch: {path}")
    if str(path) in checked:
        require(value == checked[str(path)], f"Source changed while reading: {path}")
    checked[str(path)] = value
    return value


def load_png_bytes(data: bytes, size: tuple[int, int], label: str) -> np.ndarray:
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        require(image.format == "PNG" and image.size == size, f"{label} must be a {size} PNG.")
        require(image.mode in ("RGB", "RGBA"), f"{label} must contain RGB or opaque RGBA pixels.")
        require(image.mode != "RGBA" or image.getextrema()[3] == (255, 255),
                f"{label} contains transparent/unpainted pixels.")
        return np.array(image.convert("RGB"), dtype=np.uint8)


def encode_png(pixels: np.ndarray) -> bytes:
    stream = io.BytesIO()
    Image.fromarray(pixels).save(stream, format="PNG", optimize=True)
    encoded = stream.getvalue()
    require(np.array_equal(load_png_bytes(encoded, (pixels.shape[1], pixels.shape[0]), "Encoded result"), pixels),
            "PNG encoding changed pixels.")
    return encoded


def validate_box(box: list[int] | tuple[int, ...]) -> list[int]:
    require(isinstance(box, (list, tuple)) and len(box) == 4
            and all(type(value) is int for value in box), "candidateBox must contain four integer coordinates.")
    left, top, right, bottom = box
    require(0 <= left < right <= FINAL and 0 <= top < bottom <= FINAL,
            "candidateBox lies outside the 4096 candidate; padding is forbidden.")
    require(right - left == PATCH and bottom - top == PATCH, "candidateBox must cover exactly 1254x1254 pixels.")
    return list(box)


def world_box(box: list[int]) -> list[int]:
    return [box[0] + ORIGIN[0], box[1] + ORIGIN[1], box[2] + ORIGIN[0], box[3] + ORIGIN[1]]


def validate_contract(checked: dict[str, str]) -> dict:
    path = ROOT.parent / "production-contract.json"
    value = check_file(path, checked)
    contract = read(path)
    require(contract["artCanvasPixels"] == [65536, 65536]
            and contract["formalTilePixels"] == [FINAL, FINAL], "Artwork coordinate contract changed.")
    require(contract["nativePatchPlan"]["resizeFinalArtAllowed"] is False,
            "This tool requires the no-resize artwork contract.")
    return {"file": str(path), "sha256": value}


def minimum_error_path(old: np.ndarray, new: np.ndarray, radius: int) -> np.ndarray:
    """Constrained minimum squared-error path in an Hx115 border strip.

    Seams stay far enough from both strip edges that the bounded feather never
    changes the outermost border or intrudes into the strict 1024-pixel core.
    """
    require(old.shape == new.shape and old.shape[1] == HALO, "Invalid halo strip.")
    difference = old.astype(np.float64) - new.astype(np.float64)
    cost = np.mean(difference * difference, axis=2)
    height, width = cost.shape
    margin = radius + 1
    cost[:, :margin] = np.inf
    cost[:, width - margin:] = np.inf
    previous = cost[0].copy()
    backtrack = np.zeros((height, width), dtype=np.int8)
    for row in range(1, height):
        alternatives = np.stack((np.r_[np.inf, previous[:-1]], previous, np.r_[previous[1:], np.inf]))
        choices = np.argmin(alternatives, axis=0)
        backtrack[row] = choices.astype(np.int8) - 1
        previous = cost[row] + np.take_along_axis(alternatives, choices[None, :], axis=0)[0]
    require(bool(np.isfinite(previous).any()), "No bounded seam exists.")
    seam = np.empty(height, dtype=np.int32)
    seam[-1] = int(np.argmin(previous))
    for row in range(height - 1, 0, -1):
        seam[row - 1] = seam[row] + int(backtrack[row, seam[row]])
    require(bool(np.all((seam >= margin) & (seam < width - margin))), "Seam escaped its halo.")
    return seam


def inclusion_mask(seam: np.ndarray, radius: int) -> np.ndarray:
    distance = np.arange(HALO, dtype=np.int32)[None, :] - seam[:, None]
    if radius == 0:
        return np.uint8(distance >= 0) * 255
    weight = np.clip(distance + radius, 0, radius * 2) * 255
    return ((weight + radius) // (radius * 2)).astype(np.uint8)


def repair_alpha(old: np.ndarray, new: np.ndarray, radius: int) -> tuple[np.ndarray, list[dict]]:
    require(radius in (0, 1, 2), "Maximum seam feather radius is two pixels.")
    require(old.shape == new.shape == (PATCH, PATCH, 3), "Quilting requires two native 1254-square RGB arrays.")
    strips = {
        "left": (old[:, :HALO], new[:, :HALO]),
        "right": (old[:, -HALO:][:, ::-1], new[:, -HALO:][:, ::-1]),
        "top": (old[:HALO].transpose(1, 0, 2), new[:HALO].transpose(1, 0, 2)),
        "bottom": (old[-HALO:][::-1].transpose(1, 0, 2), new[-HALO:][::-1].transpose(1, 0, 2)),
    }
    masks, records = {}, []
    for side, (before, after) in strips.items():
        seam = minimum_error_path(before, after, radius)
        masks[side] = inclusion_mask(seam, radius)
        absolute = np.abs(before.astype(np.int16) - after.astype(np.int16))
        records.append({"side": side, "haloPixels": HALO,
                        "seamCoordinates": "distance from named outer edge; top/bottom indexed by x, left/right by y",
                        "seamDistances": seam.tolist(), "seamMin": int(seam.min()), "seamMax": int(seam.max()),
                        "beforeBlendMeanAbsoluteDifference": float(absolute.mean()),
                        "beforeBlendP95AbsoluteDifference": float(np.percentile(absolute, 95)),
                        "featherRadiusPixels": radius})
    alpha = np.full((PATCH, PATCH), 255, dtype=np.uint8)
    alpha[:, :HALO] = np.minimum(alpha[:, :HALO], masks["left"])
    alpha[:, -HALO:] = np.minimum(alpha[:, -HALO:], masks["right"][:, ::-1])
    alpha[:HALO] = np.minimum(alpha[:HALO], masks["top"].T)
    alpha[-HALO:] = np.minimum(alpha[-HALO:], masks["bottom"].T[::-1])
    require(bool(np.all(alpha[HALO:-HALO, HALO:-HALO] == 255)), "Repair mask touched the strict core.")
    require(not bool(alpha[0].any() or alpha[-1].any() or alpha[:, 0].any() or alpha[:, -1].any()),
            "Repair mask changes the outermost border.")
    return alpha, records


def quilt(old: np.ndarray, new: np.ndarray, radius: int) -> tuple[np.ndarray, dict]:
    alpha, seams = repair_alpha(old, new, radius)
    weight = alpha.astype(np.uint32)[..., None]
    result = ((old.astype(np.uint32) * (255 - weight) + new.astype(np.uint32) * weight + 127) // 255).astype(np.uint8)
    require(np.array_equal(result[HALO:-HALO, HALO:-HALO], new[HALO:-HALO, HALO:-HALO]),
            "New native core was not preserved exactly.")
    border = np.zeros((PATCH, PATCH), dtype=bool)
    border[[0, -1]] = True
    border[:, [0, -1]] = True
    require(np.array_equal(result[border], old[border]), "Outer boundary pixels changed.")
    identical = np.all(old == new, axis=2)
    require(np.array_equal(result[identical], old[identical]), "Identical native samples changed while blending.")
    return result, {"seams": seams, "alphaSha256Uint8RowMajor": digest(alpha.tobytes()),
                    "coreNativePixelsPreserved": True, "outerBoundaryPixelsPreserved": True,
                    "coreBoxInRepair": [HALO, HALO, PATCH - HALO, PATCH - HALO],
                    "cornerRule": "minimum/intersection of the four side inclusion masks",
                    "cornerLimitation": "Independent four-side minimum-error paths are not a globally optimized closed seam; inspect all four corners visually.",
                    "sourceResampling": False, "resize": False, "blur": False, "colorAdjustment": False,
                    "maximumFeatherRadiusPixels": radius, "feather": "bounded linear; only within halo",
                    "blendArithmetic": "uint32 rounded /255, once per pixel"}


def validate_repair(record_path: Path, current_hash: str, checked: dict[str, str]) -> tuple[np.ndarray, dict]:
    record_hash = check_file(record_path, checked)
    record = read(record_path)
    require(isinstance(record, dict), "Repair record must be a JSON object.")
    require(record.get("inputCandidateSha256", "").lower() == current_hash,
            f"Repair targets a different candidate byte hash: {record_path}. Regenerate/rebase its input; do not relabel provenance.")
    box = validate_box(record["candidateBox"])
    require(record["coordinates"]["contextWorldBox"] == world_box(box),
            f"Repair contextWorldBox does not match candidateBox/artwork origin: {record_path}")
    if "candidateBox" in record["coordinates"]:
        require(record["coordinates"]["candidateBox"] == box, "Nested candidateBox differs from top-level candidateBox.")
    if "nativeCoreBox" in record["coordinates"]:
        require(record["coordinates"]["nativeCoreBox"] == [HALO, HALO, PATCH - HALO, PATCH - HALO],
                "Repair nativeCoreBox differs from the strict 1024-pixel core.")
    require([record["width"], record["height"]] == [PATCH, PATCH], "Repair record dimensions must be 1254 square.")
    require(record.get("resizedAfterGeneration") is not True, "A resized repair source is forbidden.")
    require(record.get("route", "builtin") in ("builtin", "builtin_image_gen"), "Repair must use the built-in route.")
    native = tile_path(record["file"])
    native_hash = check_file(native, checked, record["sha256"])
    pixels = load_png_bytes(native.read_bytes(), (PATCH, PATCH), "Native repair")
    if record.get("sourceOutputSha256") is not None:
        require(record["sourceOutputSha256"].lower() == native_hash, "Native repair differs from tool-return hash.")
    prompt = tile_path(record["prompt"])
    prompt_hash = check_file(prompt, checked, record.get("promptSha256"))
    require(bool(prompt.read_text(encoding="utf-8-sig").strip()), "Repair prompt is empty.")
    refs = record.get("refs", record.get("references"))
    require(isinstance(refs, list) and bool(refs), "Repair needs hashed refs/references.")
    for ref in refs:
        check_file(tile_path(ref["file"]), checked, ref["sha256"])
    evidence = record["evidence"]
    require(isinstance(evidence, dict) and bool(evidence), "Repair evidence is missing.")
    receipt = tile_path(evidence["toolReceipt"])
    receipt_hash = check_file(receipt, checked, evidence.get("toolReceiptSha256"))
    require(receipt.stat().st_size > 0, "Repair tool receipt is empty.")
    info = {"recordFile": str(record_path.resolve()), "recordSha256": record_hash,
            "nativeFile": str(native), "nativeSha256": native_hash, "actualNativePixels": [PATCH, PATCH],
            "inputCandidate": record.get("inputCandidate"), "inputCandidateSha256": current_hash, "candidateBox": box,
            "contextWorldBox": world_box(box), "prompt": str(prompt), "promptSha256": prompt_hash,
            "refs": refs, "evidence": evidence, "receiptSha256": receipt_hash,
            "configSnapshot": record.get("configSnapshot"), "submittedParameters": record.get("submittedParameters"),
            "actualModel": record.get("actualModel"), "actualQuality": record.get("actualQuality")}
    return pixels, info


def selected_records(single: str | None, selection: str | None, checked: dict[str, str]) -> tuple[list[Path], dict | None]:
    if single:
        return [Path(single).resolve()], None
    path = Path(selection).resolve() if selection else DEFAULT_SELECTION
    selection_hash = check_file(path, checked)
    values = read(path)
    require(isinstance(values, list) and bool(values), "repairs/selection.json must be a nonempty ordered list of record paths.")
    require(all(isinstance(value, str) and bool(value) for value in values), "Repair selections must be record path strings.")
    return [tile_path(value) for value in values], {"file": str(path), "sha256": selection_hash}


def validate_output(output: Path, source: Path, crop: bool, checked: dict[str, str]) -> None:
    output = output.resolve()
    require(output.is_relative_to(T.resolve()), "Output must stay inside this tile directory.")
    require(output.suffix.lower() == ".png", "Output must use a PNG filename.")
    require(output != source.resolve() and output != DEFAULT_INPUT.resolve(), "Never overwrite the input or original assembled candidate.")
    require(str(output) not in checked, "Output would overwrite a referenced source/provenance file.")
    if crop:
        require(output.is_relative_to((T / "repairs").resolve()), "Native input crops belong under r10_c05/repairs/.")
    else:
        require(output.is_relative_to((T / "output").resolve()) or output.is_relative_to((T / "repairs").resolve()),
                "Repaired candidates belong under this tile's output/ or repairs/ directory.")


def verify_unchanged(checked: dict[str, str]) -> None:
    for name, value in checked.items():
        require(Path(name).is_file() and sha(Path(name)) == value, f"Source changed during processing: {name}")


def write_output(output: Path, encoded: bytes, manifest: dict, manifest_suffix: str) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.stem + ".writing.png")
    temporary.write_bytes(encoded)
    require(sha(temporary) == digest(encoded), "Saved image bytes differ.")
    temporary.replace(output)
    manifest_path = output.with_suffix(manifest_suffix)
    manifest_temp = manifest_path.with_name(manifest_path.name + ".writing")
    manifest_temp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_temp.replace(manifest_path)
    return manifest_path


def execute(args: argparse.Namespace) -> dict:
    checked: dict[str, str] = {}
    script_hash = check_file(Path(__file__), checked)
    contract = validate_contract(checked)
    source = Path(args.input).resolve()
    source_hash = check_file(source, checked)
    original = source.read_bytes()
    require(digest(original) == source_hash, "Candidate changed while loading.")
    candidate = load_png_bytes(original, (FINAL, FINAL), "Input candidate")
    common = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
              "tile": "r10_c05", "script": {"file": str(Path(__file__)), "sha256": script_hash},
              "productionContract": contract, "inputCandidate": {"file": str(source), "sha256": source_hash},
              "coordinateConvention": "half-open 4096-tile pixel boxes; artwork origin [16384,36864]; not client world coordinates",
              "sourceResampling": False, "resize": False, "formalAccepted": False,
              "externalSeamsValidated": False, "clientMappingValidated": False}
    if args.candidate_box is not None:
        box = validate_box(args.candidate_box)
        left, top, right, bottom = box
        cropped = candidate[top:bottom, left:right].copy()
        encoded = encode_png(cropped)
        output = Path(args.output).resolve() if args.output else T / "repairs" / f"crop-{left}-{top}.png"
        validate_output(output, source, True, checked)
        manifest = {**common, "operation": "exact native crop; no generation", "candidateBox": box,
                    "coordinates": {"contextWorldBox": world_box(box)}, "width": PATCH, "height": PATCH,
                    "inputCandidateSha256": source_hash, "file": str(output), "sha256": digest(encoded),
                    "cropPixelSha256RGBRowMajor": digest(cropped.tobytes()), "isGeneratedRepair": False,
                    "nativePixelsPreserved": True}
        verify_unchanged(checked)
        manifest_path = None if args.preflight else write_output(output, encoded, manifest, ".crop.json")
        return {"status": "crop_preflight_passed" if args.preflight else "native_crop_saved",
                "writes": not args.preflight, "output": str(output), "outputSha256": digest(encoded),
                "inputCandidateSha256": source_hash, "candidateBox": box,
                "contextWorldBox": world_box(box), "coreBoxInCandidate": [left + HALO, top + HALO, right - HALO, bottom - HALO],
                "manifest": str(manifest_path) if manifest_path else None}

    records, selection = selected_records(args.record, args.selection, checked)
    current_hash, steps, encoded = source_hash, [], original
    for index, record_path in enumerate(records, 1):
        native, evidence = validate_repair(record_path, current_hash, checked)
        left, top, right, bottom = evidence["candidateBox"]
        before = candidate[top:bottom, left:right].copy()
        repaired, quilting = quilt(before, native, args.feather)
        updated = candidate.copy()
        updated[top:bottom, left:right] = repaired
        # Check every region outside the repair, without constructing an image-size mask.
        require(np.array_equal(updated[:top], candidate[:top])
                and np.array_equal(updated[bottom:], candidate[bottom:])
                and np.array_equal(updated[top:bottom, :left], candidate[top:bottom, :left])
                and np.array_equal(updated[top:bottom, right:], candidate[top:bottom, right:]),
                "Pixels outside the repair box changed.")
        encoded = encode_png(updated)
        next_hash = digest(encoded)
        steps.append({"index": index, **evidence, "beforeCropPixelSha256RGBRowMajor": digest(before.tobytes()),
                      "afterCropPixelSha256RGBRowMajor": digest(repaired.tobytes()),
                      "outputCandidateSha256": next_hash, "quilting": quilting,
                      "outsideCandidateBoxPixelsPreserved": True,
                      "visualQa": "pending: inspect four halo seams, all corners, geometry and material continuity"})
        candidate, current_hash = updated, next_hash
    output = Path(args.output).resolve() if args.output else DEFAULT_OUTPUT
    validate_output(output, source, False, checked)
    manifest = {**common, "operation": "ordered native local repairs with four-side minimum-error halo quilting",
                "selection": selection, "steps": steps,
                "output": {"file": str(output), "sha256": current_hash, "width": FINAL, "height": FINAL,
                           "mode": "RGB", "format": "PNG"},
                "blur": False, "colorAdjustment": False, "maximumFeatherRadiusPixels": args.feather,
                "mechanicalValidation": {"passed": True, "everyInputCandidateHashMatched": True,
                                         "everyNativeCorePreservedExactly": True, "noPixelResampling": True},
                "visualQa": "pending", "status": "repaired_candidate_pending_visual_QA"}
    verify_unchanged(checked)
    manifest_path = None if args.preflight else write_output(output, encoded, manifest, ".repair-assembly.json")
    return {"status": "repair_preflight_passed" if args.preflight else manifest["status"],
            "writes": not args.preflight, "repairCount": len(steps), "output": str(output),
            "outputSha256": current_hash, "manifest": str(manifest_path) if manifest_path else None,
            "stepOutputCandidateSha256": [step["outputCandidateSha256"] for step in steps],
            "formalAccepted": False, "visualQa": "pending"}


def self_test() -> dict:
    old = np.empty((PATCH, PATCH, 3), dtype=np.uint8)
    old[:, :, 0] = (np.arange(PATCH) % 251)[None, :]
    old[:, :, 1] = (np.arange(PATCH) % 253)[:, None]
    old[:, :, 2] = 97
    unchanged, _ = quilt(old, old, 2)
    require(np.array_equal(unchanged, old), "Identity quilting failed.")
    new = 255 - old
    result, details = quilt(old, new, 2)
    require(np.array_equal(result[HALO:-HALO, HALO:-HALO], new[HALO:-HALO, HALO:-HALO]), "Strict core test failed.")
    require(np.array_equal(result[0], old[0]) and np.array_equal(result[-1], old[-1])
            and np.array_equal(result[:, 0], old[:, 0]) and np.array_equal(result[:, -1], old[:, -1]),
            "Old outer-border preservation test failed.")
    for seam in details["seams"]:
        require(seam["seamMin"] >= 3 and seam["seamMax"] <= 111, "Bounded feather can escape the halo.")
    require(digest(encode_png(result)) == digest(encode_png(result)), "PNG bytes are not deterministic for hash chaining.")
    for box in ([2475, 480, 3729, 1734], [2560, 2490, 3814, 3744]):
        require(validate_box(box) == box, "Requested crop geometry failed.")
    return {"status": "self_test_passed", "writes": False,
            "checks": ["identical pixels", "exact new 1024 core", "unchanged old outer borders",
                       "bounded four-side masks and corners", "deterministic PNG hash chain", "requested crop boxes"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="4096-square input candidate PNG.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--record", help="One local-repair generation record.")
    mode.add_argument("--selection", help="Ordered JSON list of record paths, relative to the tile.")
    mode.add_argument("--candidate-box", type=int, nargs=4, metavar=("L", "T", "R", "B"), help="Crop mode: exact native input crop.")
    mode.add_argument("--self-test", action="store_true", help="Only in-memory invariant checks; no files written.")
    parser.add_argument("--output", help="Separate output PNG, never the original assembled candidate.")
    parser.add_argument("--preflight", action="store_true", help="Validate and compute in memory without writing.")
    parser.add_argument("--feather", type=int, choices=(0, 1, 2), default=2)
    args = parser.parse_args()
    try:
        result = self_test() if args.self_test else execute(args)
    except (ValueError, TypeError, KeyError, OSError, AttributeError) as error:
        parser.exit(1, f"Local repair stopped: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
