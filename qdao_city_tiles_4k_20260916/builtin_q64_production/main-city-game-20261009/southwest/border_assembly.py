"""Replay the native r10 south / r11 north border without changing either source.

--prepare-only writes only borders/r10-south-native-overlap.png and its record.
--input CONTEXT.png --output borders/NAME.png verifies a full-width native r11
context by exact replay, then writes a separate border-fixed context and record.
Contexts must include 115px outer halos: width 4326, height 1254/2278/3302/4326.
No cropped 4096px input, resize, color matching, blur, warp, art generation or
formal acceptance. Historical missing references are reported, never rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
T10, T11 = ROOT / "r10_c05", ROOT / "r11_c05"
BORDERS = T11 / "borders"
CONTRACT = ROOT.parent / "production-contract.json"
RESUME = ROOT.parent.parent / "resume-production-20261010" / "production-resume.json"
ASSEMBLER = ROOT / "assemble.py"
ASSEMBLY10 = T10 / "output" / "assembly.json"
FINAL_RECORD = T10 / "repairs" / "output" / "r10_c05.repaired.candidate.repair-assembly.json"
BORDER_PNG = BORDERS / "r10-south-native-overlap.png"
CORE, HALO, PATCH, OVERLAP, WIDTH = 1024, 115, 1254, 230, 4326
SEAM_MIN, SEAM_MAX = 117, 227


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixels_sha(array: np.ndarray) -> str:
    return hashlib.sha256(array.tobytes()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


class Snapshot:
    """Files whose bytes must not change between reading and writing output."""
    def __init__(self) -> None:
        self.files: dict[str, str] = {}
        self.absent: set[str] = set()

    def file(self, path: Path, expected: str | None = None) -> dict:
        path = path.resolve()
        require(path.is_file(), f"Required source is missing: {path}")
        actual = digest(path)
        require(expected is None or actual == expected.lower(), f"SHA-256 mismatch: {path}")
        key = str(path)
        require(key not in self.files or self.files[key] == actual, f"Source changed during reading: {path}")
        self.files[key] = actual
        return {"file": key, "sha256": actual}

    def check(self) -> None:
        for name, expected in self.files.items():
            path = Path(name)
            require(path.is_file() and digest(path) == expected, f"Source changed during replay: {path}")
        require(all(not Path(name).exists() for name in self.absent), "A selection appeared during replay; rerun.")


def read_png(path: Path, size: tuple[int, int] | None = None) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        require(image.format == "PNG" and image.mode in ("RGB", "RGBA"), f"Not an RGB/RGBA PNG: {path}")
        require(size is None or image.size == size, f"Incorrect native dimensions {image.size}: {path}")
        require(image.mode != "RGBA" or image.getextrema()[3] == (255, 255), f"Transparent pixels: {path}")
        return np.array(image.convert("RGB"), dtype=np.uint8)


def output_path(path: Path) -> Path:
    path = path.resolve()
    require(path.is_relative_to(BORDERS.resolve()), f"Output must be inside {BORDERS}: {path}")
    return path


def save_png(path: Path, array: np.ndarray) -> dict:
    path = output_path(path)
    require(path.suffix.lower() == ".png", "Output must be a PNG.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + ".writing.png")
    Image.fromarray(array).save(temporary, format="PNG", optimize=True)
    require(np.array_equal(read_png(temporary), array), f"PNG write changed pixels: {path}")
    temporary.replace(path)
    return {"file": str(path), "sha256": digest(path), "width": array.shape[1],
            "height": array.shape[0], "mode": "RGB", "format": "PNG",
            "rgbPixelSha256": pixels_sha(array), "resampled": False}


def save_json(path: Path, value: dict) -> None:
    path = output_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def persist_border(border: np.ndarray, record: dict) -> tuple[Path, dict]:
    """Keep previously referenced border records immutable across later runs."""
    if BORDER_PNG.exists():
        require(np.array_equal(read_png(BORDER_PNG), border),
                "Prepared border pixels differ; preserve its existing provenance and review the r10 source change.")
        output = {"file": str(BORDER_PNG.resolve()), "sha256": digest(BORDER_PNG),
                  "width": WIDTH, "height": OVERLAP, "mode": "RGB", "format": "PNG",
                  "rgbPixelSha256": pixels_sha(border), "resampled": False}
    else:
        output = save_png(BORDER_PNG, border)
    record = {**record, "output": output}
    canonical = {k: v for k, v in record.items() if k != "createdAtUtc"}
    identity = hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    path = BORDERS / f"r10-south-native-overlap.{identity[:20]}.source.json"
    if path.exists():
        previous = read(path)
        require({k: v for k, v in previous.items() if k != "createdAtUtc"} == canonical,
                "Immutable border record identity collision or modification.")
        return path, previous
    save_json(path, record)
    return path, record


def load_algorithm(snapshot: Snapshot) -> tuple[dict, dict]:
    assembly_file = snapshot.file(ASSEMBLY10)
    assembly = read(ASSEMBLY10)
    script = snapshot.file(ASSEMBLER, assembly["script"]["sha256"])
    require(assembly["composition"]["maximumFeatherRadiusPixels"] == 2,
            "r10 source assembly used a different feather radius; review before replay.")
    # Inspected module: definitions/constants only at top level; writes occur only
    # inside run/main. A non-main run_name avoids CLI execution and pycache files.
    api = runpy.run_path(str(ASSEMBLER), run_name="native_border_readonly_algorithm")
    return api, {"algorithm": script, "historicalAssembly": assembly_file,
                 "operation": "assemble_pixels: row strips, then row joins",
                 "sourceAssemblyFeatherRadiusPixels": 2}


def control(snapshot: Snapshot) -> dict:
    contract_file, resume_file = snapshot.file(CONTRACT), snapshot.file(RESUME)
    contract, resume = read(CONTRACT), read(RESUME)
    require(contract["artCanvasPixels"] == [65536, 65536]
            and contract["formalTilePixels"] == [4096, 4096], "Artwork grid changed.")
    plan = contract["nativePatchPlan"]
    require((plan["corePixels"], plan["haloPixels"], plan["expectedNativePixels"],
             plan["subrows"], plan["subcolumns"]) == (CORE, HALO, PATCH, 4, 4)
            and plan["resizeFinalArtAllowed"] is False, "Native patch contract changed.")
    require(resume["status"] == "released_for_art_production_with_local_entrance_review"
            and resume["preserveArtCoordinatesAndApprovedLayout"] is True,
            "Expected production resume authorization is unavailable.")
    return {"productionContract": contract_file, "productionResume": resume_file,
            "script": snapshot.file(Path(__file__))}


def reference_observations(record: dict) -> list[dict]:
    result = []
    for kind in ("references", "neighborSources"):
        for reference in record.get(kind, []):
            path = resolve(reference["file"])
            actual = digest(path) if path.is_file() else None
            status = ("historical_reference_unavailable" if actual is None else
                      "matches_record" if actual == reference["sha256"] else "historical_reference_hash_mismatch")
            result.append({"kind": kind, **reference, "currentSha256": actual, "status": status})
    return result


def native_sources(tile: Path, rows: range, snapshot: Snapshot) -> tuple[dict, dict]:
    selection_path = tile / "refinement" / "selection.json"
    selection = {}
    if selection_path.is_file():
        selection_evidence = snapshot.file(selection_path)
        selection = read(selection_path)
        require(isinstance(selection, dict), "Selection must map patch IDs to relative record paths.")
    else:
        snapshot.absent.add(str(selection_path.resolve()))
        selection_evidence = {"file": str(selection_path), "status": "absent; original native sources selected"}
    arrays, entries = {}, []
    origin_y = 36864 if tile == T10 else 40960
    for row in rows:
        for column in range(1, 5):
            name = f"p{row:02d}_{column:02d}"
            filename = f"{name}.png.generation.json"
            relative = Path(selection.get(name, "native/" + filename))
            require(not relative.is_absolute(), "Selection must be relative to its tile.")
            record_path = (tile / relative).resolve()
            allowed = {(tile / "native" / filename).resolve(),
                       (tile / "refinement" / "native" / filename).resolve()}
            require(record_path in allowed, f"Selected record path differs from patch identity: {name}")
            record_file = snapshot.file(record_path)
            record = read(record_path)
            native_path = resolve(record["file"])
            require(native_path == record_path.with_name(name + ".png"), f"Native and record identities differ: {name}")
            if tile == T10:
                require(name in selection and native_path.parent == (tile / "refinement" / "native").resolve(),
                        "r10 bottom row must use the confirmed selected refinement sources.")
            x, y = 16384 + (column - 1) * CORE, origin_y + (row - 1) * CORE
            expected = {"id": name, "row": row, "column": column,
                        "coreWorldBox": [x, y, x + CORE, y + CORE],
                        "contextWorldBox": [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO],
                        "nativeCoreBox": [HALO, HALO, HALO + CORE, HALO + CORE]}
            require(all(record["coordinates"].get(k) == v for k, v in expected.items()),
                    f"Incorrect native coordinates: {name}")
            require([record["width"], record["height"]] == [PATCH, PATCH]
                    and record["nativePixelsPreserved"] is True
                    and record["resizedAfterGeneration"] is False
                    and record["route"] == "builtin" and record["tool"] == "image_gen.imagegen",
                    f"Native production declaration differs: {name}")
            source = snapshot.file(native_path, record["sha256"])
            require(record.get("sourceOutputSha256") == source["sha256"], f"Tool output hash differs: {name}")
            arrays[(row, column)] = read_png(native_path, (PATCH, PATCH))
            entries.append({"id": name, "native": source, "generationRecord": record_file,
                            "recordSnapshot": record, "historicalReferenceObservations": reference_observations(record)})
    return arrays, {"selection": selection_evidence, "nativeSources": entries,
                    "validationScope": "strict native bytes, dimensions, coordinates, declarations and replay algorithm; historical reference observations are not generation revalidation"}


def build_border(api: dict, snapshot: Snapshot, provenance: dict) -> tuple[np.ndarray, dict]:
    sources, source_record = native_sources(T10, range(4, 5), snapshot)
    strip, metrics = api["assemble_pixels"](sources, (4, 1, 4, 4), 2)
    require(strip.shape == (PATCH, WIDTH, 3), "r10 row replay has unexpected dimensions.")
    final_record_file = snapshot.file(FINAL_RECORD)
    final_record = read(FINAL_RECORD)
    final_path = resolve(final_record["output"]["file"])
    require(final_path == (T10 / "repairs" / "output" / "r10_c05.repaired.candidate.png").resolve(),
            "Unexpected confirmed r10 final file.")
    final_evidence = snapshot.file(final_path, final_record["output"]["sha256"])
    final = read_png(final_path, (4096, 4096))
    border = strip[1024:1254, :].copy()
    require(np.array_equal(border[:115, 115:4211], final[3981:4096, :]),
            "r10 replay bottom115 differs from the confirmed final; do not invent a border.")
    record = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
              "kind": "native_r10_south_230_overlap", **provenance, **source_record,
              "r10Final": final_evidence, "r10FinalRecord": final_record_file,
              "coordinateConvention": "half-open x,y boxes; zero-based array slices use [y,x]",
              "rowStripPixels": [WIDTH, PATCH], "rowStripWorldBox": [16269, 39821, 20595, 41075],
              "cropBoxInRowStrip": [0, 1024, WIDTH, 1254],
              "contextWorldBox": [16269, 40845, 20595, 41075],
              "r10FinalComparison": {"borderBox": [115, 0, 4211, 115],
                  "finalBox": [0, 3981, 4096, 4096], "pixelExact": True, "differentChannels": 0},
              "nativeColumnHeaderBoxes": [[j * CORE, 0, j * CORE + PATCH, OVERLAP] for j in range(4)],
              "rowSeamMetrics": metrics, "sourceResampling": False, "colorAdjustment": False,
              "blur": False, "geometryWarping": False, "maximumFeatherRadiusPixels": 2,
              "formalAccepted": False, "visualQa": "pending; source identity is not geometric or material acceptance"}
    return border, record


def validate_context(array: np.ndarray) -> int:
    require(array.ndim == 3 and array.shape[1:] == (WIDTH, 3),
            "Input must be the full-width 4326px native context, not a 4096px cropped tile.")
    require(array.shape[0] in (1254, 2278, 3302, 4326),
            "Input height must be 1254, 2278, 3302 or 4326 (one to four native rows, both halos).")
    return (array.shape[0] - OVERLAP) // CORE


def quilt(api: dict, border: np.ndarray, context: np.ndarray, radius: int) -> tuple[np.ndarray, dict]:
    validate_context(context)
    require(border.shape == (OVERLAP, WIDTH, 3), "Incorrect border dimensions.")
    require(radius in (0, 1, 2), "Feather radius must be 0, 1 or 2.")
    # Transposition solves one continuous y(x) path across ALL 4326 columns.
    # Search starts at117, so radius2 still yields pure B at y115 (core row0).
    old = np.transpose(border[SEAM_MIN:SEAM_MAX + 1], (1, 0, 2))
    new = np.transpose(context[SEAM_MIN:SEAM_MAX + 1], (1, 0, 2))
    seam = api["minimum_seam"](old, new) + SEAM_MIN
    alpha = api["feather_mask"](seam, OVERLAP, radius).T
    output = context.copy()
    output[:OVERLAP] = api["blend_exact"](border, context[:OVERLAP], alpha)
    require(np.all(np.abs(np.diff(seam)) <= 1), "Border seam is not continuous.")
    require(np.array_equal(output[:116], border[:116]), "The halo or r11 core first row lost r10 ownership.")
    require(np.array_equal(output[229:], context[229:]), "Pixels past the allowed transition changed.")
    difference = border.astype(np.int16) - context[:OVERLAP].astype(np.int16)
    record = {"method": "one continuous constrained regularized minimum squared-error seam y(x), across full native width",
              "sourceOld": "recorded r10 south border", "sourceNew": "verified r11 assembled context",
              "seamSearchRangeInclusive": [SEAM_MIN, SEAM_MAX], "seamYByContextX": seam.tolist(),
              "seamSha256Int32LittleEndian": hashlib.sha256(seam.astype("<i4").tobytes()).hexdigest(),
              "seamMin": int(seam.min()), "seamMax": int(seam.max()),
              "maximumStepPerColumn": int(np.abs(np.diff(seam)).max()),
              "maximumFeatherRadiusPixels": radius, "feather": "bounded linear; no blend beyond radius",
              "blendArithmetic": "uint32; rounded (old*(255-alpha)+new*alpha+127)//255",
              "beforeBlendMeanAbsoluteDifference": float(np.abs(difference).mean()),
              "r10OwnedContextRowsInclusive": [0, 115], "r11CoreRowZeroContextY": 115,
              "unchangedNewRowsFromInclusive": 229, "sourceResampling": False,
              "colorAdjustment": False, "blur": False, "geometryWarping": False,
              "mechanicalValidation": {"first116RowsEqualB": True, "rowsFrom229Unchanged": True,
                                        "continuousSeam": True, "outputSizeUnchanged": True},
              "geometryValidated": False, "materialContinuityValidated": False}
    return output, record


def self_test(api: dict) -> dict:
    yy, xx = np.indices((OVERLAP, WIDTH), dtype=np.int32)
    border = np.stack((xx % 251, yy % 253, (xx + yy) % 255), axis=2).astype(np.uint8)
    context = np.full((PATCH, WIDTH, 3), 211, dtype=np.uint8)
    context[:OVERLAP] = 255 - border
    border_before, context_before = pixels_sha(border), pixels_sha(context)
    for radius in (0, 1, 2):
        result, record = quilt(api, border, context, radius)
        require(np.array_equal(result[:116], border[:116]) and np.array_equal(result[229:], context[229:]),
                "Adversarial all-different input violated the immutable source regions.")
        require(SEAM_MIN <= record["seamMin"] <= record["seamMax"] <= SEAM_MAX, "Seam escaped bounds.")
        identity, _ = quilt(api, context[:OVERLAP].copy(), context, radius)
        require(np.array_equal(identity, context), "Identical overlap changed pixels.")
    # Test masks directly at both legal extreme seam positions, not merely paths
    # preferred by the regularizer: core row0 must remain old at either extreme.
    for radius in (0, 1, 2):
        mask = api["feather_mask"](np.array([SEAM_MIN, SEAM_MAX]), OVERLAP, radius)
        require(np.all(mask[:, :116] == 0) and np.all(mask[:, 229:] == 255), "Extreme seam mask escaped ownership.")
    for rows in range(1, 5):
        shape = (rows * CORE + OVERLAP, WIDTH, 3)
        require(validate_context(np.broadcast_to(np.uint8(0), shape)) == rows, "Partial/full context rejected.")
        if rows > 1:
            tall = np.full(shape, 71 + rows, dtype=np.uint8)
            tall[:OVERLAP] = context[:OVERLAP]
            original_hash = pixels_sha(tall)
            for radius in (0, 1, 2):
                result, _ = quilt(api, border, tall, radius)
                require(np.array_equal(result[:116], border[:116])
                        and np.array_equal(result[229:], tall[229:]), "Full/partial ownership test failed.")
            require(pixels_sha(tall) == original_hash, "Quilt mutated the input context.")
    require(pixels_sha(border) == border_before and pixels_sha(context) == context_before,
            "Quilt mutated an input array.")
    for shape in ((1024, 4096, 3), (1254, 4325, 3), (2277, WIDTH, 3)):
        try:
            validate_context(np.broadcast_to(np.uint8(0), shape))
        except ValueError:
            pass
        else:
            raise ValueError("Cropped or mis-sized context incorrectly accepted.")
    return {"status": "self_test_passed", "writes": False,
            "checks": ["immutable halo and core row0", "unchanged lower input", "bounded continuous seam",
                       "0/1/2px feather including extreme seam positions", "identity replay",
                       "full and three partial heights", "reject cropped and mis-sized contexts"]}


def run(args: argparse.Namespace) -> dict:
    snapshot = Snapshot()
    controls = control(snapshot)
    api, algorithm = load_algorithm(snapshot)
    if args.self_test:
        return self_test(api)
    border, border_record = build_border(api, snapshot, {**controls, **algorithm})
    if args.prepare_only:
        snapshot.check()
        border_record_path, border_record = persist_border(border, border_record)
        return {"status": "native_border_prepared", "output": border_record["output"],
                "record": str(border_record_path), "r10Bottom115Exact": True, "formalAccepted": False}
    require(args.input and args.output, "Use --prepare-only, --self-test, or both --input and --output.")
    input_path, destination = Path(args.input).resolve(), output_path(Path(args.output))
    require(destination.suffix.lower() == ".png", "Output must be a PNG.")
    require(destination not in {input_path, BORDER_PNG.resolve()}, "Do not overwrite the input or prepared border.")
    record_path = destination.with_suffix(".border.json")
    require(not destination.exists() and not record_path.exists(), "Output already exists; choose a new output filename.")
    input_file = snapshot.file(input_path)
    context = read_png(input_path)
    rows = validate_context(context)
    sources, context_sources = native_sources(T11, range(1, rows + 1), snapshot)
    replay, metrics = api["assemble_pixels"](sources, (1, 1, rows, 4), args.context_feather)
    require(np.array_equal(context, replay),
            "Input does not exactly match selected r11 native replay; supply the correct halo-inclusive context and --context-feather.")
    result, composition = quilt(api, border, context, args.feather)
    snapshot.check()
    # Save a reproducible border alongside the result; never touch current assembly.
    border_record_path, border_record = persist_border(border, border_record)
    result_record = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
                     "status": "border_fixed_native_context_pending_visual_qa", **controls, **algorithm,
                     "input": input_file, "inputNativeReplayExact": True, **context_sources,
                     "inputReplayFeatherRadiusPixels": args.context_feather, "inputReplaySeamMetrics": metrics,
                     "borderSourceRecord": {"file": str(border_record_path), "sha256": digest(border_record_path)},
                     "borderSourceSnapshot": border_record, "composition": composition,
                     "contextWorldBox": [16269, 40845, 20595, 40845 + context.shape[0]],
                     "coveredCoreWorldBox": [16384, 40960, 20480, 40960 + rows * CORE],
                     "coreCropBox": [115, 115, 4211, 115 + rows * CORE],
                     "includesOuterHalo": True, "coveredRows": rows, "fullTileContext": rows == 4,
                     "output": save_png(destination, result), "r10FinalModified": False,
                     "sourceResampling": False, "formalAccepted": False, "visualQa": "pending",
                     "limitations": ["Native pixel ownership and coordinates are verified; geometry and materials require visual QA.",
                                     "Only the north boundary is composed; other external edges are not accepted.",
                                     "Historical reference availability is reported without rewriting generation evidence."]}
    snapshot.check()
    save_json(record_path, result_record)
    return {"status": result_record["status"], "output": result_record["output"],
            "record": str(record_path), "coveredRows": rows, "formalAccepted": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare-only", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    parser.add_argument("--input", help="Halo-inclusive full-width assembled r11 PNG; pixels must match selected native replay.")
    parser.add_argument("--output", help="New PNG path strictly inside r11_c05/borders/.")
    parser.add_argument("--feather", type=int, choices=(0, 1, 2), default=2)
    parser.add_argument("--context-feather", type=int, choices=(0, 1, 2), default=2,
                        help="Feather radius originally used to assemble the r11 input context.")
    args = parser.parse_args()
    try:
        require(not (args.prepare_only or args.self_test) or not (args.input or args.output),
                "--prepare-only/--self-test cannot be combined with --input/--output.")
        print(json.dumps(run(args), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, f"Border assembly stopped: {error}\n")


if __name__ == "__main__":
    main()
