"""Assemble recorded r11_c05 native art without resizing or filling missing art.

Run normally to write output/assembly.json and a candidate or partial plus QA.
--preflight validates current sources without writing. --self-test is in memory.
Both full and partial outputs contain only exact core-world coverage; outer halo
is cropped by 115 pixels on each side. A partial never fills a missing patch.
--through p01_02 limits a read-only preflight to the first two recorded patches.
Optional r11_c05/refinement/selection.json maps patch IDs to record paths relative
to r11_c05; only explicitly selected records replace the original native sources.
This script does not reconcile the upper cross-tile boundary or correct its tone.
No generation calls, progress changes, publication, or formal acceptance occur.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
TILE = "r11_c05"
T = ROOT / TILE
CONTRACT = ROOT.parent / "production-contract.json"
GRID, CORE, HALO = 4, 1024, 115
OVERLAP, PATCH, FINAL = 2 * HALO, CORE + 2 * HALO, GRID * CORE
ORIGIN = (16384, 40960)
EXPECTED = {(r, c) for r in range(1, GRID + 1) for c in range(1, GRID + 1)}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def pid(row: int, column: int) -> str:
    return f"p{row:02d}_{column:02d}"


def local(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def recorded_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def expected_coordinates(row: int, column: int) -> dict:
    x, y = ORIGIN[0] + (column - 1) * CORE, ORIGIN[1] + (row - 1) * CORE
    return {"id": pid(row, column), "row": row, "column": column,
            "coreWorldBox": [x, y, x + CORE, y + CORE],
            "contextWorldBox": [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO],
            "nativeCoreBox": [HALO, HALO, HALO + CORE, HALO + CORE]}


def validate_contract() -> str:
    contract = read(CONTRACT)
    plan = contract["nativePatchPlan"]
    require(contract["artCanvasPixels"] == [65536, 65536]
            and contract["formalTilePixels"] == [FINAL, FINAL]
            and contract["rows"] == 16 and contract["columns"] == 16,
            "Artwork coordinates changed; this assembler requires the current 64K contract.")
    require((plan["subrows"], plan["subcolumns"], plan["corePixels"],
             plan["haloPixels"], plan["expectedNativePixels"]) == (GRID, GRID, CORE, HALO, PATCH)
            and plan["resizeFinalArtAllowed"] is False,
            "Native patch geometry changed; re-plan the assembler before use.")
    require(contract["builtinOnly"] is True, "This assembler expects the built-in-only batch.")
    return sha(CONTRACT)


def selection_records(selection: dict) -> dict[str, Path]:
    require(isinstance(selection, dict), "Refinement selection must be an object mapping patch IDs to records.")
    known = {pid(r, c) for r, c in EXPECTED}
    records = {}
    for name, value in selection.items():
        require(name in known, f"Unknown refinement patch ID: {name}")
        require(isinstance(value, str) and bool(value), f"Invalid refinement record path: {name}")
        relative = Path(value)
        require(not relative.is_absolute() and not relative.drive and not relative.root,
                f"Refinement record path must be relative to {T}: {value}")
        path = (T / relative).resolve()
        filename = f"{name}.png.generation.json"
        require(path in {(T / "native" / filename).resolve(),
                         (T / "refinement" / "native" / filename).resolve()},
                f"Refinement record must use the matching filename inside native or refinement/native: {value}")
        records[filename] = path
    return records


def load_sources(through: str | None = None) -> tuple[dict, list[dict], dict[str, str]]:
    arrays, entries, checked_files = {}, [], {}

    def check_file(path: Path, expected_hash: str | None = None) -> str:
        require(path.is_file(), f"Missing provenance/source file: {path}")
        absolute = str(path.resolve())
        actual = checked_files.get(absolute)
        if actual is None:
            actual = sha(path)
            checked_files[absolute] = actual
        if expected_hash is not None:
            require(actual == expected_hash.lower(), f"SHA-256 mismatch: {path}")
        return actual

    selection_path = T / "refinement" / "selection.json"
    overrides, selection_evidence = {}, None
    if selection_path.is_file():
        selection_hash = check_file(selection_path)
        overrides = selection_records(read(selection_path))
        selection_evidence = {"file": local(selection_path), "sha256": selection_hash}
    source_records = {p.name: p for p in (T / "native").glob("*.generation.json")}
    source_records.update(overrides)
    for filename, record_path in sorted(source_records.items()):
        if through is not None and filename > f"{through}.png.generation.json":
            continue
        record_hash = check_file(record_path)
        record = read(record_path)
        coords = record["coordinates"]
        row, column = coords["row"], coords["column"]
        require((row, column) in EXPECTED, f"Out-of-grid record: {record_path}")
        name = pid(row, column)
        require((row, column) not in arrays, f"Duplicate native coordinates: {name}")
        require(filename == f"{name}.png.generation.json", f"Selected record identity differs: {filename}")
        overridden = filename in overrides
        native = recorded_path(record["file"])
        allowed_native = {(T / "native" / f"{name}.png").resolve()}
        if overridden:
            allowed_native.add((T / "refinement" / "native" / f"{name}.png").resolve())
        require(native in allowed_native, f"Native file identity differs: {name}")
        require(record_path.resolve() == native.with_name(native.name + ".generation.json"),
                f"Unexpected record filename: {record_path}")
        for field, value in expected_coordinates(row, column).items():
            require(coords.get(field) == value, f"Incorrect {field} for {name}")
        require(record.get("route") == "builtin" and record.get("tool") == "image_gen.imagegen",
                f"Unexpected generation route: {name}")
        require(record.get("nativePixelsPreserved") is True
                and record.get("resizedAfterGeneration") is False,
                f"Native preservation not established: {name}")
        require([record["width"], record["height"]] == [PATCH, PATCH],
                f"{name} is recorded as {record['width']}x{record['height']}, not {PATCH}x{PATCH}. "
                "Stop and re-plan native coverage; resizing or relabelling is forbidden.")
        native_hash = check_file(native, record["sha256"])
        require(record.get("sourceOutputSha256", "").lower() == native_hash,
                f"Tool-output byte hash differs from saved native file: {name}")
        original = recorded_path(record["sourceOutputPath"])
        original_available = original.is_file()
        if original_available:
            check_file(original, native_hash)
        # A temporary tool output may be cleaned after its identical native copy is saved.
        prompt = recorded_path(record["prompt"])
        prompt_hash = check_file(prompt, record["promptSha256"])
        require(bool(prompt.read_text(encoding="utf-8-sig").strip()), f"Empty prompt: {name}")
        receipt = recorded_path(record["evidence"]["toolReceipt"])
        receipt_hash = check_file(receipt, record["evidence"].get("toolReceiptSha256"))
        require(receipt.stat().st_size > 0, f"Empty tool receipt: {name}")
        receipt_data = read(receipt)
        require(receipt_data.get("status") == "returned_image"
                and receipt_data.get("tool") == "image_gen.imagegen",
                f"Missing successful built-in receipt: {name}")
        require("actualModel" in record and "actualQuality" in record,
                f"Missing actual model/quality disclosure fields: {name}")
        require(record["actualModel"] is None and record["actualQuality"] is None,
                f"This built-in batch has no confirmed model/quality return values: {name}")
        require(record.get("formalAccepted") is False,
                f"Unexpected acceptance status in native record: {name}")
        references = record.get("references", [])
        require(bool(references), f"Missing reference evidence: {name}")
        contract_data = read(CONTRACT)
        required_references = {recorded_path(contract_data[key])
                               for key in ("layoutReference", "detailStyleReference", "primaryStyleReference")}
        require(required_references <= {recorded_path(source["file"]) for source in references},
                f"A mandatory approved reference is absent: {name}")
        for source in references + record.get("neighborSources", []):
            check_file(recorded_path(source["file"]), source["sha256"])
        for source in record.get("neighborSources", []):
            if "generationRecord" in source:
                check_file(recorded_path(source["generationRecord"]), source["generationRecordSha256"])
            if "selectionFile" in source:
                selection_source = recorded_path(source["selectionFile"])
                check_file(selection_source)
                require(read(selection_source).get(source["sourcePatch"]) == source["selectedRecord"],
                        f"Recorded upper-neighbor selection changed: {name}")
        request_evidence = None
        if record.get("request"):
            request_path = recorded_path(record["request"])
            request_hash = check_file(request_path)
            request = read(request_path)
            require(request.get("prompt") == prompt.read_text(encoding="utf-8-sig")
                    and request.get("references") == references
                    and request.get("coordinates") == coords,
                    f"Saved request differs from generation record: {name}")
            request_evidence = {"file": str(request_path), "sha256": request_hash}
        with Image.open(native) as image:
            image.load()
            require(image.format == "PNG" and image.size == (PATCH, PATCH),
                    f"Actual file is not a native {PATCH}-square PNG: {name}")
            require(image.mode in ("RGB", "RGBA"), f"Unsupported native pixel mode: {name}")
            require(image.mode == record["mode"] and image.format == record["format"],
                    f"Native mode/format disagrees with generation record: {name}")
            require(image.mode != "RGBA" or image.getextrema()[3] == (255, 255),
                    f"Ground art contains transparent/unpainted pixels: {name}")
            arrays[(row, column)] = np.array(image.convert("RGB"), dtype=np.uint8)
        entries.append({"id": name, "row": row, "column": column,
                        "nativeFile": local(native), "nativeSha256": native_hash,
                        "actualNativePixels": [PATCH, PATCH],
                        "recordFile": local(record_path), "recordSha256": record_hash,
                        "selectionOverride": overridden,
                        "selectionEvidence": selection_evidence if overridden else None,
                        "promptFile": str(prompt), "promptSha256": prompt_hash,
                        "receiptFile": str(receipt), "receiptSha256": receipt_hash,
                        "requestEvidence": request_evidence,
                        "references": references, "neighborSources": record.get("neighborSources", []),
                        "cornerTreatment": record.get("cornerTreatment"),
                        "coordinates": coords, "sourceOutputPath": str(original),
                        "sourceOutputSha256": native_hash, "sourceOutputStillAvailable": original_available,
                        "route": record["route"], "tool": record["tool"],
                        "configSnapshot": record.get("configSnapshot"),
                        "submittedParameters": record.get("submittedParameters"),
                        "actualModel": record.get("actualModel"), "actualQuality": record.get("actualQuality"),
                        "unverifiedReason": record.get("unverifiedReason"),
                        "generatedAt": record.get("generatedAt"), "sourceResampling": False,
                        "formalAccepted": False})
    return arrays, entries, checked_files


def choose_rectangle(available: set[tuple[int, int]]) -> tuple[int, int, int, int] | None:
    """Largest completely populated rectangle; ties prefer width, then top/left."""
    options = []
    for top in range(1, GRID + 1):
        for left in range(1, GRID + 1):
            for bottom in range(top, GRID + 1):
                for right in range(left, GRID + 1):
                    cells = {(r, c) for r in range(top, bottom + 1) for c in range(left, right + 1)}
                    if cells <= available:
                        options.append(((len(cells), right - left + 1, -top, -left),
                                        (top, left, bottom, right)))
    return max(options)[1] if options else None


def minimum_seam(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Minimum squared-error seam, with weak center and edge regularization."""
    require(left.shape == right.shape and left.ndim == 3, "Invalid seam input geometry.")
    difference = left.astype(np.float32) - right.astype(np.float32)
    cost = np.mean(difference * difference, axis=2)
    height, width = cost.shape
    center = (width - 1) / 2.0
    normalized = np.abs((np.arange(width, dtype=np.float32) - center) / max(center, 1.0))
    typical = float(np.median(cost)) + 1.0
    cost += normalized[None, :] ** 4 * typical * 0.16
    margin = min(24, max(1, width // 12))
    cost[:, :margin] += typical * 8.0
    cost[:, -margin:] += typical * 8.0
    previous = cost[0].copy()
    backtrack = np.zeros((height, width), dtype=np.int8)
    for y in range(1, height):
        candidates = np.stack((np.r_[np.float32(np.inf), previous[:-1]], previous,
                               np.r_[previous[1:], np.float32(np.inf)]))
        choices = np.argmin(candidates, axis=0)
        backtrack[y] = choices.astype(np.int8) - 1
        previous = cost[y] + np.take_along_axis(candidates, choices[None, :], axis=0)[0]
    seam = np.empty(height, dtype=np.int32)
    seam[-1] = int(np.argmin(previous))
    for y in range(height - 1, 0, -1):
        seam[y - 1] = seam[y] + int(backtrack[y, seam[y]])
    return seam


def feather_mask(seam: np.ndarray, width: int, radius: int) -> np.ndarray:
    require(radius in (0, 1, 2), "Feather radius must be 0, 1, or 2 pixels.")
    distance = np.arange(width, dtype=np.int32)[None, :] - seam[:, None]
    if radius == 0:
        return np.uint8(distance >= 0) * 255
    # Bounded linear feather: exactly no blend beyond radius pixels of the seam.
    numerator = np.clip(distance + radius, 0, radius * 2) * 255
    return ((numerator + radius) // (radius * 2)).astype(np.uint8)


def blend_exact(left: np.ndarray, right: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    weight = alpha.astype(np.uint32)[..., None]
    return ((left.astype(np.uint32) * (255 - weight)
             + right.astype(np.uint32) * weight + 127) // 255).astype(np.uint8)


def append(base: np.ndarray, patch: np.ndarray, label: str, radius: int) -> tuple[np.ndarray, dict]:
    require(base.shape[0] == patch.shape[0] and min(base.shape[1], patch.shape[1]) >= OVERLAP,
            f"Invalid overlap geometry: {label}")
    left, right = base[:, -OVERLAP:], patch[:, :OVERLAP]
    seam = minimum_seam(left, right)
    alpha = feather_mask(seam, OVERLAP, radius)
    mixed = blend_exact(left, right, alpha)
    difference = np.abs(left.astype(np.int16) - right.astype(np.int16))
    metrics = {"label": label, "overlapPixels": OVERLAP, "seamLength": len(seam),
               "seamMin": int(seam.min()), "seamMax": int(seam.max()),
               "seamSha256Int32LittleEndian": hashlib.sha256(seam.astype("<i4").tobytes()).hexdigest(),
               "beforeBlendMeanAbsoluteDifference": float(difference.mean()),
               "beforeBlendP95AbsoluteDifference": float(np.percentile(difference, 95)),
               "featherRadiusPixels": radius, "geometryValidated": False}
    return np.concatenate((base[:, :-OVERLAP], mixed, patch[:, OVERLAP:]), axis=1), metrics


def assemble_pixels(arrays: dict, rectangle: tuple[int, int, int, int], radius: int) -> tuple[np.ndarray, list]:
    top, left, bottom, right = rectangle
    strips, metrics = [], []
    for row in range(top, bottom + 1):
        strip = arrays[(row, left)]
        for column in range(left + 1, right + 1):
            strip, metric = append(strip, arrays[(row, column)],
                                   f"row{row:02d}_c{column - 1:02d}_c{column:02d}", radius)
            metrics.append(metric)
        strips.append(strip)
    combined = np.transpose(strips[0], (1, 0, 2))
    for row, strip in enumerate(strips[1:], top + 1):
        combined, metric = append(combined, np.transpose(strip, (1, 0, 2)),
                                  f"rows{row - 1:02d}_{row:02d}", radius)
        metrics.append(metric)
    combined = np.transpose(combined, (1, 0, 2))
    require(combined.shape == ((bottom - top + 1) * CORE + OVERLAP,
                               (right - left + 1) * CORE + OVERLAP, 3),
            "Assembled native coverage does not match recorded coordinates.")
    return combined, metrics


def qa_regions(width: int, height: int, rows: int, columns: int, offset: int) -> list[dict]:
    regions = []
    # Cover the entire potential 230-pixel seam corridor plus four pixels.
    margin = HALO + 4
    xs, ys = [offset + c * CORE for c in range(1, columns)], [offset + r * CORE for r in range(1, rows)]
    for x in xs:
        regions.append({"name": f"vertical_x{x}_full", "kind": "full-length-internal-seam",
                        "box": [max(0, x - margin), 0, min(width, x + margin), height]})
    for y in ys:
        regions.append({"name": f"horizontal_y{y}_full", "kind": "full-length-internal-seam",
                        "box": [0, max(0, y - margin), width, min(height, y + margin)]})
    for y in ys:
        for x in xs:
            regions.append({"name": f"intersection_x{x}_y{y}", "kind": "internal-seam-intersection",
                            "box": [x - 256, y - 256, x + 256, y + 256]})
    return regions


def save_png(image: Image.Image, path: Path) -> dict:
    require(path.resolve().is_relative_to((T / "output").resolve())
            or path.resolve().is_relative_to((T / "qa").resolve()),
            f"Output path is outside r11_c05 output/qa: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + ".writing.png")
    image.save(temporary, format="PNG", optimize=True)
    with Image.open(temporary) as saved:
        saved.load()
        require(saved.mode == image.mode and saved.size == image.size
                and np.array_equal(np.asarray(saved), np.asarray(image)), f"Saved PNG differs: {path}")
    temporary.replace(path)
    return {"file": local(path), "sha256": sha(path), "width": image.width,
            "height": image.height, "mode": image.mode, "format": "PNG"}


def save_json(path: Path, value: dict) -> None:
    require(path.resolve().is_relative_to((T / "output").resolve())
            or path.resolve().is_relative_to((T / "qa").resolve()),
            f"Manifest path is outside r11_c05 output/qa: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run(radius: int, preflight: bool, through: str | None = None) -> dict:
    require(through is None or preflight, "--through is only allowed with --preflight; normal assembly uses all recorded sources.")
    contract_hash = validate_contract()
    script_hash = sha(Path(__file__))
    arrays, entries, checked_files = load_sources(through)
    available = set(arrays)
    rectangle = choose_rectangle(available)
    missing = [pid(r, c) for r, c in sorted(EXPECTED - available)]
    orphan_pngs = [local(p) for p in sorted((T / "native").glob("*.png"))
                   if not p.with_name(p.name + ".generation.json").is_file()]
    summary = {"tile": TILE, "verifiedNativeCount": len(arrays), "missingPatchIds": missing,
               "selectedRectangleInclusive": list(rectangle) if rectangle else None,
               "refinementOverridePatchIds": [entry["id"] for entry in entries if entry["selectionOverride"]],
               "unrecordedPngsExcluded": orphan_pngs, "formalAccepted": False,
               "preflightThroughPatch": through,
               "plannedCoreOutputPixels": ([CORE * (rectangle[3] - rectangle[1] + 1),
                                             CORE * (rectangle[2] - rectangle[0] + 1)] if rectangle else None),
               "upperCrossTileBoundary": "pending_separate_QA; existing leaf-tone difference is not corrected here"}
    if preflight:
        return {**summary, "status": "preflight_passed", "writes": False}
    require(rectangle is not None, "No recorded native artwork exists; no image/output was created.")
    top, left, bottom, right = rectangle
    selected = {(r, c) for r in range(top, bottom + 1) for c in range(left, right + 1)}
    complete = available == EXPECTED
    combined, seam_metrics = assemble_pixels(arrays, rectangle, radius)
    core_width, core_height = (right - left + 1) * CORE, (bottom - top + 1) * CORE
    rendered = combined[HALO:HALO + core_height, HALO:HALO + core_width].copy()
    image = Image.fromarray(rendered)
    require(image.size == (core_width, core_height), "Partial core crop dimensions differ from covered native cells.")
    require(not complete or image.size == (FINAL, FINAL), "Complete candidate must be exactly 4096 square.")
    # Fail if parent generation/provenance changed while this assembly was running.
    for path, digest in checked_files.items():
        require(Path(path).is_file() and sha(Path(path)) == digest, f"Source changed during assembly: {path}")
    selection_path = T / "refinement" / "selection.json"
    require(selection_path.is_file() == (str(selection_path.resolve()) in checked_files),
            "Refinement selection appeared or disappeared during assembly; rerun.")
    require(sha(CONTRACT) == contract_hash and sha(Path(__file__)) == script_hash,
            "Contract or assembler changed during assembly; rerun.")
    x, y = ORIGIN[0] + (left - 1) * CORE, ORIGIN[1] + (top - 1) * CORE
    core_box = [x, y, x + (right - left + 1) * CORE, y + (bottom - top + 1) * CORE]
    context_box = [core_box[0] - HALO, core_box[1] - HALO, core_box[2] + HALO, core_box[3] + HALO]
    tag = "candidate" if complete else f"partial-p{top:02d}_{left:02d}-p{bottom:02d}_{right:02d}"
    output = save_png(image, T / "output" / f"{TILE}.{tag}.png")
    qa_dir = T / "qa" / tag
    preview = image.copy()
    preview.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    preview_record = save_png(preview, qa_dir / "preview.png")
    preview_record.update({"kind": "downsampled-preview-only", "gameArt": False,
                           "resampled": preview.size != image.size, "resampling": "LANCZOS downsampling only"})
    qa = [preview_record]
    for region in qa_regions(image.width, image.height, bottom - top + 1, right - left + 1,
                             0):
        crop = image.crop(region["box"])
        qa_record = save_png(crop, qa_dir / f"{region['name']}.png")
        qa_record.update({"kind": region["kind"], "cropBoxInOutput": region["box"],
                          "resampled": False, "visualQa": "pending"})
        qa.append(qa_record)
    manifest = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
                **summary, "status": "candidate_pending_visual_and_external_seam_review" if complete else "partial_native_coverage",
                "complete4kCandidate": complete, "formalAcceptedCount": 0, "published": False,
                "clientMappingValidated": False, "capacity5000Validated": False,
                "script": {"file": local(Path(__file__)), "sha256": script_hash},
                "productionContract": {"file": str(CONTRACT), "sha256": contract_hash},
                "coordinateConvention": "half-open boxes; top-left origin; x right, y down",
                "selectedCoreWorldBox": core_box, "assembledContextWorldBox": context_box,
                "outputWorldBox": core_box,
                "outputIncludesOuterHalo": False,
                "grid": {"rows": bottom - top + 1, "columns": right - left + 1,
                         "corePixels": CORE, "nativePatchPixels": PATCH, "haloPixels": HALO,
                         "adjacentOverlapPixels": OVERLAP},
                "assembledBeforeOuterCrop": [combined.shape[1], combined.shape[0]],
                "outerCropPixelsPerSide": HALO,
                "assembledNativeCount": len(selected),
                "usedPatchIds": [pid(r, c) for r, c in sorted(selected)],
                "verifiedPatchIdsNotInThisOutput": [pid(r, c) for r, c in sorted(available - selected)],
                "nativeSources": entries, "seamMetrics": seam_metrics,
                "composition": {"method": "regularized minimum squared-error seam; row strips, then row joins",
                                "feather": "bounded linear", "maximumFeatherRadiusPixels": radius,
                                "sourceResampling": False, "finalArtUpscaled": False,
                                "colorMatching": False, "geometryWarping": False,
                                "globalBlur": False, "sharpening": False,
                                "missingPixelsFilled": False, "guidePixelsCompositedIntoFinal": False,
                                "upperCrossTileBoundaryComposited": False,
                                "blendArithmetic": "uint32; rounded /255; identical inputs remain identical",
                                "modeNormalization": "opaque RGBA sources, if any, converted to RGB without resampling"},
                "output": output, "qa": qa,
                "mechanicalValidation": {"passed": True, "opaqueRgbOutput": True,
                                         "savedPngPixelsVerified": True, "nativeCoverageWithoutGaps": True,
                                         "fullLengthInternalSeamCrops": sum(q["kind"] == "full-length-internal-seam" for q in qa),
                                         "internalIntersectionCrops": sum(q["kind"] == "internal-seam-intersection" for q in qa)},
                "visualQa": {"status": "pending", "internalGeometryReviewed": False,
                             "externalTileSeamsReviewed": False,
                             "upperBoundaryKnownIssue": "p01_01 leaves have a visible tone change at a straight hard core boundary; this assembler does not hide or repair it",
                             "note": "Inspect all full-length seam crops and intersections at 100%. "
                                     "Numeric seam costs and feathering do not establish geometric continuity. "
                                     "External edges and neighboring tile intersections require separate review."}}
    save_json(T / "output" / "assembly.json", manifest)
    return {**summary, "status": manifest["status"], "assembledNativeCount": len(selected),
            "output": str(T / "output" / f"{TILE}.{tag}.png"), "outputPixels": list(image.size),
            "assembly": str(T / "output" / "assembly.json"), "qaDirectory": str(qa_dir)}


def self_test() -> dict:
    # Different adjacent native windows from one coordinate field must reconstruct it exactly.
    y, x = np.indices((PATCH, PATCH + CORE), dtype=np.int32)
    plane = np.stack((x % 251, y % 253, (x + y) % 255), axis=2).astype(np.uint8)
    joined, _ = append(plane[:, :PATCH], plane[:, CORE:], "self-test", 2)
    require(np.array_equal(joined, plane), "Exact shared-overlap reconstruction failed.")
    values = np.broadcast_to(np.arange(256, dtype=np.uint8)[:, None, None], (256, 256, 3))
    alpha = np.broadcast_to(np.arange(256, dtype=np.uint8)[None, :], (256, 256))
    require(np.array_equal(blend_exact(values, values, alpha), values), "Blend changed identical pixels.")
    seam = np.array([6, 7], dtype=np.int32)
    for radius in (0, 1, 2):
        mask = feather_mask(seam, 16, radius)
        distance = np.arange(16)[None, :] - seam[:, None]
        require(np.all(mask[distance < -radius] == 0) and np.all(mask[distance > radius] == 255),
                "Feather exceeded its maximum radius.")
    available = {(1, 1), (1, 2), (1, 3), (1, 4), (2, 1)}
    require(choose_rectangle(available) == (1, 1, 1, 4), "Partial rectangle crosses a missing cell.")
    require(choose_rectangle(EXPECTED) == (1, 1, 4, 4), "Full rectangle selection failed.")
    side = FINAL + OVERLAP
    field = np.empty((side, side, 3), dtype=np.uint8)
    field[:, :, 0] = (np.arange(side) % 251)[None, :]
    field[:, :, 1] = (np.arange(side) % 253)[:, None]
    field[:, :, 2] = 173
    sources = {(r, c): field[(r - 1) * CORE:(r - 1) * CORE + PATCH,
                             (c - 1) * CORE:(c - 1) * CORE + PATCH]
               for r, c in EXPECTED}
    assembled, _ = assemble_pixels(sources, (1, 1, 4, 4), 2)
    require(np.array_equal(assembled, field)
            and assembled[HALO:HALO + FINAL, HALO:HALO + FINAL].shape == (FINAL, FINAL, 3),
            "Full 16-patch assembly/cropping changed coordinates or native pixels.")
    # Actual partial logic always crops the halo, retaining only known native core coverage.
    for columns in (2, 4):
        partial, _ = assemble_pixels(sources, (1, 1, 1, columns), 2)
        cropped = partial[HALO:HALO + CORE, HALO:HALO + columns * CORE]
        require(cropped.shape == (CORE, columns * CORE, 3)
                and np.array_equal(cropped, field[HALO:HALO + CORE, HALO:HALO + columns * CORE]),
                "Partial core output was padded, resampled, or incorrectly cropped.")
    regions = qa_regions(FINAL, FINAL, 4, 4, 0)
    require(sum(q["kind"] == "full-length-internal-seam" for q in regions) == 6
            and sum(q["kind"] == "internal-seam-intersection" for q in regions) == 9,
            "Full-tile QA coverage is incomplete.")
    require(all((q["box"][3] - q["box"][1] == FINAL
                 or q["box"][2] - q["box"][0] == FINAL)
                for q in regions if q["kind"] == "full-length-internal-seam"),
            "A seam crop does not cover its full length.")
    return {"status": "self_test_passed", "writes": False,
            "checks": ["native overlap reconstruction", "all-value blend identity", "bounded feather",
                       "missing-cell exclusion", "16-patch native reconstruction and 4096 crop",
                       "2048x1024 and 4096x1024 exact partial core crop",
                       "six full seam strips and nine intersections"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="Validate records and report coverage without writes.")
    mode.add_argument("--self-test", action="store_true", help="Run meaningful in-memory checks without writes.")
    parser.add_argument("--feather", type=int, choices=(0, 1, 2), default=2, help="Maximum feather radius in pixels.")
    parser.add_argument("--through", choices=sorted(pid(r, c) for r, c in EXPECTED),
                        help="Read-only preflight snapshot ending at this patch ID in row-major order.")
    args = parser.parse_args()
    try:
        require(not args.through or args.preflight, "--through requires --preflight.")
        result = self_test() if args.self_test else run(args.feather, args.preflight, args.through)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, f"Assembly stopped: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
