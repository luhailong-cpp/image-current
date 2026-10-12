"""Assemble an explicitly selected native 4x4 grid into a CANDIDATE only.

Usage (run from this zone; the script itself is not a generation tool):
    <bundled-python> assemble_candidate.py records/r06_c12.selection.json
    <bundled-python> assemble_candidate.py records/r06_c12.selection.json --replace-candidate

Selection format: exactly the sixteen patch IDs, no discovery/latest/globs.
Paths are absolute or relative to this script's zone. Every value is either a
path string or {"path": "...", "sha256": "<optional pinned image SHA256>"}.
Example structure (replace the ellipsis with ALL sixteen explicit entries):
    {
      "schemaVersion": 1,
      "tile": "r06_c12",
      "patches": {
        "r06_c12_p11": "native/r06_c12_p11-bridge-candidate.png",
        "r06_c12_p12": "native/r06_c12_p12-bridge-candidate.png",
        "...": "...",
        "r06_c12_p44": {"path": "native/r06_c12_p44-v1.png"}
      }
    }

Only outputs:
    tiles/r06_c12.candidate.png
    tiles/r06_c12.candidate.png.derived.json
    qa/r06_c12/selection.snapshot.json
    qa/r06_c12/manifest.json
    qa/r06_c12/v_p11_p12.native-1to1.png ... 12 vertical boundaries
    qa/r06_c12/h_p11_p21.native-1to1.png ... 12 horizontal boundaries
    qa/r06_c12/junction_r1_c1.native-1to1.png ... 9 intersections
    qa/r06_c12/r06_c12.preview-only-1024.png

The candidate is only crop[115,115,1139,1139] plus opaque integer paste.
All 24 QA strips cover the full 1024-pixel shared edge, 128 pixels each side.
All 9 junction crops are 512 square. Only the preview is resized.
No progress, source, selection, coordinate, contract or acceptance file changes.
No automatic visual approval. complete/formal flags stay false even when every
mechanical check passes. Cross-tile borders and game integration stay unverified.
Existing outputs require the explicit --replace-candidate option.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import re
import sys
import uuid
from pathlib import Path

from PIL import Image
from PIL.PngImagePlugin import PngInfo

ZONE = Path(__file__).resolve().parent
TILE = "r06_c12"
SIDE = 4096
CORE = 1024
NATIVE = 1254
CORE_BOX = (115, 115, 1139, 1139)
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    return sha_bytes(Path(path).read_bytes())


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def resolve(value, relative_to=ZONE):
    path = Path(value)
    return (path if path.is_absolute() else relative_to / path).resolve()


def inside(path, root, label):
    path, root = Path(path).resolve(), Path(root).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"{label} must stay inside {root}: {path}")
    return path


def evidence_path(value, record_path):
    """Historical records use zone-relative or sidecar-relative paths."""
    if isinstance(value, dict):
        value = value.get("path")
    if not isinstance(value, str) or not value:
        raise ValueError(f"Invalid evidence path in {record_path}")
    p = Path(value)
    if p.is_absolute():
        return p.resolve()
    zone_path = (ZONE / p).resolve()
    local_path = (record_path.parent / p).resolve()
    if zone_path.is_file() or not local_path.is_file():
        return zone_path
    return local_path


def ref(path, **extra):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": sha_file(path), **extra}


def expected_coordinates(row, column, origin):
    x, y = origin[0] + (column - 1) * CORE, origin[1] + (row - 1) * CORE
    return {
        "id": f"{TILE}_p{row}{column}",
        "coreGlobalBox": [x, y, x + CORE, y + CORE],
        "nativeGlobalBox": [x - 115, y - 115, x + CORE + 115, y + CORE + 115],
        "nativeCoreBox": list(CORE_BOX),
        "expectedSize": [NATIVE, NATIVE],
    }


class Provenance:
    """A deduplicated graph of retained source-image/record evidence."""

    def __init__(self):
        self.nodes = {}
        self.active = set()
        self.missing_historical_images = []

    def inspect(self, image_path, required=False, record_hint=None):
        image_path = inside(image_path, ZONE / "native", "Native source")
        key = str(image_path)
        if key in self.active:
            raise ValueError(f"Cyclic derivation: {image_path}")
        if key in self.nodes:
            if required and not self.nodes[key]["imageAvailable"]:
                raise ValueError(f"Selected source is missing: {image_path}")
            return key

        derived = image_path.with_name(image_path.name + ".derived.json")
        generated = image_path.with_name(image_path.name + ".generation.json")
        if derived.is_file():
            record_path, kind = derived, "mechanical_derived"
        elif generated.is_file():
            record_path, kind = generated, "image_gen_native"
        else:
            raise ValueError(f"No generation/derivation record for {image_path}")
        if record_hint is not None and record_hint != record_path:
            # Some historical sources name generationRecord while a later derived
            # record exists. That is ambiguous, so do not silently use either.
            raise ValueError(f"Parent record pointer differs from selected provenance: {image_path}")

        raw = record_path.read_bytes()
        record = json.loads(raw.decode("utf-8-sig"))
        expected_hash = record.get("sha256")
        if not isinstance(expected_hash, str) or not HASH_RE.fullmatch(expected_hash):
            raise ValueError(f"Invalid recorded image SHA256: {record_path}")
        recorded_name = record.get("file")
        if recorded_name and evidence_path(recorded_name, record_path) != image_path:
            raise ValueError(f"Record names a different image: {record_path}")

        present = image_path.is_file()
        if required and not present:
            raise ValueError(f"Selected source is missing: {image_path}")
        actual_hash = sha_file(image_path) if present else None
        if present and actual_hash.lower() != expected_hash.lower():
            raise ValueError(f"Image no longer matches provenance SHA256: {image_path}")

        node = {
            "image": key,
            "sha256": expected_hash.lower(),
            "imageAvailable": present,
            "imageHashVerified": present,
            "sourceType": kind,
            "provenanceRecord": {"path": str(record_path), "sha256": sha_bytes(raw)},
            "parents": [],
        }
        self.active.add(key)
        if kind == "mechanical_derived":
            parents = record.get("derivedFrom")
            if isinstance(parents, dict):
                parents = [parents]
            if not isinstance(parents, list) or not parents:
                raise ValueError(f"Derived source lacks parents: {record_path}")
            operation = record.get("operation")
            if not isinstance(operation, str) or not operation.strip():
                raise ValueError(f"Derived source lacks operation: {record_path}")
            node["operation"] = operation
            # Preserve all crop/replacement/global geometry, not just filenames.
            node["derivationRecordFields"] = {
                k: v for k, v in record.items()
                if k not in ("file", "sha256", "derivedFrom")
            }
            for parent in parents:
                if not isinstance(parent, dict):
                    raise ValueError(f"Invalid derived parent: {record_path}")
                parent_path = evidence_path(parent.get("path", parent.get("file")), record_path)
                parent_hash = parent.get("sha256")
                if not isinstance(parent_hash, str) or not HASH_RE.fullmatch(parent_hash):
                    raise ValueError(f"Derived parent lacks SHA256: {record_path}")
                hint = parent.get("derivedRecord") or parent.get("generationRecord")
                hint_path = evidence_path(hint, record_path) if hint else None
                parent_key = self.inspect(parent_path, record_hint=hint_path)
                if self.nodes[parent_key]["sha256"] != parent_hash.lower():
                    raise ValueError(f"Derived parent hash disagrees with its record: {parent_path}")
                node["parents"].append({
                    "node": parent_key,
                    "sha256": parent_hash.lower(),
                    "originalParentEntry": parent,
                })
        else:
            if record.get("tool") not in ("image_gen.imagegen", "image_gen__imagegen"):
                raise ValueError(f"Generation source is not builtin image_gen: {record_path}")
            if record.get("route") != "builtin":
                raise ValueError(f"Generation source route is not builtin: {record_path}")
            node["generationEvidence"] = {
                k: record.get(k) for k in (
                    "tool", "route", "generatedAt", "observedAtUtc", "width", "height",
                    "nativeSize", "format", "coordinates", "nativeGlobalBox",
                    "configSnapshot", "submittedParameters", "actualModel",
                    "actualQuality", "unverifiedReason", "prompt", "receipt", "evidence"
                )
            }
            # Metadata is evidence of native generation; references are creative
            # inputs, not pixel parents and are not counted as pasted coverage.
            node["creativeReferences"] = record.get("references", [])
            receipt = record.get("receipt") or record.get("evidence", {}).get("receipt")
            if not receipt:
                raise ValueError(f"Generation record lacks a tool receipt: {record_path}")
            receipt_path = evidence_path(receipt, record_path)
            if not receipt_path.is_file():
                raise ValueError(f"Missing tool receipt: {receipt_path}")
            if isinstance(receipt, dict) and receipt.get("sha256"):
                if sha_file(receipt_path) != receipt["sha256"].lower():
                    raise ValueError(f"Tool receipt hash mismatch: {receipt_path}")
            node["verifiedReceiptFile"] = ref(receipt_path)

        if not present:
            self.missing_historical_images.append(key)
            node["historicalPixelVerification"] = (
                "Image absent; retained hashed provenance only. No claim of present-pixel revalidation."
            )
        self.active.remove(key)
        self.nodes[key] = node
        return key


def decode_native(path):
    """Full decode; preserve original RGB sample values, allowing opaque RGBA."""
    raw = path.read_bytes()
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        if image.format != "PNG" or image.size != (NATIVE, NATIVE):
            raise ValueError(f"Selected native must decode as 1254x1254 PNG: {path}")
        if image.mode not in ("RGB", "RGBA"):
            raise ValueError(f"Unsupported native mode {image.mode}: {path}")
        mode = image.mode
        if mode == "RGBA" and image.getchannel("A").getextrema() != (255, 255):
            raise ValueError(f"Nonopaque native cannot supply complete coverage: {path}")
        result = image.convert("RGB")
    return result, sha_bytes(raw), mode


def encode_png(image, purpose):
    buffer = io.BytesIO()
    info = PngInfo()
    info.add_text("purpose", purpose)
    info.add_text("acceptance", "candidate; visual review pending; formalAccepted=false")
    image.save(buffer, format="PNG", pnginfo=info)
    encoded = buffer.getvalue()
    # Verify the saved representation, not only the in-memory canvas.
    with Image.open(io.BytesIO(encoded)) as decoded:
        decoded.load()
        if decoded.size != image.size or decoded.convert("RGB").tobytes() != image.tobytes():
            raise ValueError("PNG round-trip changed dimensions or pixels")
    return encoded


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("selection", help="Explicit sixteen-patch selection JSON")
    parser.add_argument("--replace-candidate", action="store_true",
                        help="Explicitly replace this candidate and its QA outputs only")
    args = parser.parse_args()

    selection_path = resolve(args.selection)
    selection_raw = selection_path.read_bytes()
    selection = json.loads(selection_raw.decode("utf-8-sig"))
    if selection.get("tile") != TILE:
        raise ValueError(f"This script only assembles {TILE}")
    chosen = selection.get("patches")
    keys = [f"{TILE}_p{r}{c}" for r in range(1, 5) for c in range(1, 5)]
    if not isinstance(chosen, dict) or set(chosen) != set(keys):
        raise ValueError("Selection must contain exactly p11..p44; no missing or extra entries")

    coordinate_path = ZONE / "records" / f"{TILE}.coordinates.json"
    coordinate_raw = coordinate_path.read_bytes()
    document = json.loads(coordinate_raw.decode("utf-8-sig"))
    if document.get("tile") != TILE:
        raise ValueError("Coordinate record tile mismatch")
    tile_row, tile_column = 6, 12
    origin = [(tile_column - 1) * SIDE, (tile_row - 1) * SIDE]
    if document.get("tileOrigin") != origin:
        raise ValueError("Tile origin disagrees with global 4096 grid")
    expected_tile_box = [origin[0], origin[1], origin[0] + SIDE, origin[1] + SIDE]
    if document.get("tileCoreBox") != expected_tile_box:
        raise ValueError("Coordinate record has incorrect tile core")
    recorded_patches = document.get("patches", [])
    coordinates = {p["id"]: p for p in recorded_patches}
    if len(coordinates) != 16 or len(recorded_patches) != 16 or set(coordinates) != set(keys):
        raise ValueError("Coordinate file must describe exactly sixteen unique patches")

    provenance = Provenance()
    canvas = Image.new("RGB", (SIDE, SIDE))
    coverage = Image.new("L", (SIDE, SIDE), 0)  # Coverage audit, never rendered art.
    inputs, seen_paths, core_hashes = [], set(), {}
    for row in range(1, 5):
        for column in range(1, 5):
            patch_id = f"{TILE}_p{row}{column}"
            expected = expected_coordinates(row, column, origin)
            coordinate = coordinates[patch_id]
            for field, value in expected.items():
                if coordinate.get(field) != value:
                    raise ValueError(f"Unexpected coordinate field {field}: {patch_id}")

            entry = chosen[patch_id]
            if isinstance(entry, str):
                entry = {"path": entry}
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise ValueError(f"Selection entry needs an explicit path: {patch_id}")
            path = inside(resolve(entry["path"]), ZONE / "native", "Selected image")
            if path in seen_paths:
                raise ValueError(f"A selected native image is reused: {path}")
            if not re.match(r"^" + re.escape(patch_id) + r"(?:[-.]|$)", path.name):
                raise ValueError(f"Filename patch ID does not match selection key: {path}")
            seen_paths.add(path)
            node_key = provenance.inspect(path, required=True)
            node = provenance.nodes[node_key]
            if entry.get("sha256") is not None:
                pinned = entry["sha256"]
                if not isinstance(pinned, str) or not HASH_RE.fullmatch(pinned):
                    raise ValueError(f"Invalid pinned SHA256 for {patch_id}")
                if pinned.lower() != node["sha256"]:
                    raise ValueError(f"Pinned selection SHA256 mismatch: {patch_id}")

            source_record = read_json(node["provenanceRecord"]["path"])
            source_coordinates = source_record.get("coordinates") or {}
            source_box = source_coordinates.get("nativeGlobalBox", source_record.get("nativeGlobalBox"))
            if source_box != expected["nativeGlobalBox"]:
                raise ValueError(f"Source record does not establish expected native box: {patch_id}")
            if source_record.get("patchId") not in (None, patch_id):
                raise ValueError(f"Source generation record names another patch: {patch_id}")

            native, image_hash, original_mode = decode_native(path)
            if image_hash != node["sha256"]:
                raise ValueError(f"Source changed while being decoded: {path}")
            core = native.crop(CORE_BOX)
            x, y = (column - 1) * CORE, (row - 1) * CORE
            destination = [x, y, x + CORE, y + CORE]
            if coverage.crop(destination).getextrema() != (0, 0):
                raise ValueError(f"Overlapping destination coverage: {patch_id}")
            canvas.paste(core, (x, y))
            coverage.paste(255, destination)
            pixel_hash = sha_bytes(core.tobytes())
            core_hashes[patch_id] = pixel_hash
            inputs.append({
                "patchId": patch_id, "row": row, "column": column,
                "path": str(path), "sha256": image_hash, "nativePixels": [NATIVE, NATIVE],
                "originalMode": original_mode, "opaque": True,
                "operation": "integer crop and opaque paste; RGB values preserved",
                "nativeCropBox": list(CORE_BOX), "destinationBox": destination,
                "coreRgbPixelSha256": pixel_hash, "coordinates": coordinate,
                "provenanceNode": node_key,
            })

    histogram = coverage.histogram()
    if histogram[255] != SIDE * SIDE or sum(histogram[:255]) != 0:
        raise ValueError("Candidate coverage contains missing or partial pixels")
    for item in inputs:
        if sha_bytes(canvas.crop(item["destinationBox"]).tobytes()) != item["coreRgbPixelSha256"]:
            raise ValueError(f"Placed core differs from source: {item['patchId']}")

    candidate_path = inside(ZONE / "tiles" / f"{TILE}.candidate.png", ZONE, "Candidate output")
    qa_dir = inside(ZONE / "qa" / TILE, ZONE, "QA output")
    candidate_data = encode_png(canvas, "4096 candidate from sixteen native cores; no resize or visual approval")
    candidate_hash = sha_bytes(candidate_data)
    outputs = [(candidate_path, candidate_data)]
    qa = []

    def add_qa(filename, box, kind, neighbors, seam_axis=None):
        image = canvas.crop(box)
        data = encode_png(image, "native 1:1 seam QA; no scaling; pending human/agent visual review")
        path = qa_dir / filename
        outputs.append((path, data))
        item = {
            "file": str(path), "sha256": sha_bytes(data), "kind": kind,
            "pixels": list(image.size), "candidateCropBox": list(box),
            "sourceCandidateSha256": candidate_hash,
            "neighborPatchIds": neighbors, "pixelScale": 1,
            "operation": "1:1 integer crop from unscaled candidate; no blend",
            "visualReview": "pending", "visualPassed": False, "formalAccepted": False,
        }
        if seam_axis is not None:
            item["seamAxis"] = seam_axis
            item["seamLocalCoordinate"] = 128
            item["completeSharedEdgePixels"] = CORE
        qa.append(item)

    # Full length of every core-to-core boundary: 12 vertical + 12 horizontal.
    for row in range(1, 5):
        for column in range(1, 4):
            x, y = column * CORE, (row - 1) * CORE
            add_qa(f"v_p{row}{column}_p{row}{column + 1}.native-1to1.png",
                   (x - 128, y, x + 128, y + CORE), "vertical_boundary",
                   [f"{TILE}_p{row}{column}", f"{TILE}_p{row}{column + 1}"], "x")
    for row in range(1, 4):
        for column in range(1, 5):
            x, y = (column - 1) * CORE, row * CORE
            add_qa(f"h_p{row}{column}_p{row + 1}{column}.native-1to1.png",
                   (x, y - 128, x + CORE, y + 128), "horizontal_boundary",
                   [f"{TILE}_p{row}{column}", f"{TILE}_p{row + 1}{column}"], "y")
    for row in range(1, 4):
        for column in range(1, 4):
            x, y = column * CORE, row * CORE
            add_qa(f"junction_r{row}_c{column}.native-1to1.png",
                   (x - 256, y - 256, x + 256, y + 256), "four_patch_junction",
                   [f"{TILE}_p{r}{c}" for r in (row, row + 1) for c in (column, column + 1)])
            qa[-1]["intersectionLocalCoordinate"] = [256, 256]
    if len(qa) != 33:
        raise ValueError("Expected exactly 24 boundary strips and 9 junction crops")

    preview = canvas.resize((1024, 1024), Image.Resampling.LANCZOS)
    preview_path = qa_dir / f"{TILE}.preview-only-1024.png"
    preview_data = encode_png(preview, "PREVIEW ONLY: 4096 candidate downsampled to 1024; not native game art")
    outputs.append((preview_path, preview_data))
    preview_entry = {
        "file": str(preview_path), "sha256": sha_bytes(preview_data),
        "pixels": [1024, 1024], "sourceCandidateSha256": candidate_hash,
        "previewOnly": True, "notGameArt": True,
        "operation": "LANCZOS downsample 4096 to 1024 for overview only", "pixelScale": 0.25,
    }
    outputs.append((qa_dir / "selection.snapshot.json", selection_raw))

    checks = {
        "selectedSourceCount": 16, "allSelectedPngsDecode": True,
        "allSelectedNativePixels": [1254, 1254], "allSelectedHashesMatchProvenance": True,
        "allSelectedNativeCoordinateBoxesValidated": True,
        "duplicateSelectedImagePaths": 0, "corePastePixelEquality": True,
        "filledPixels": histogram[255], "expectedPixels": SIDE * SIDE,
        "missingPixels": 0, "overlapPixels": 0,
        "candidatePngRoundTripDecodeAndPixelEquality": True,
        "allQaPngRoundTripDecodeAndPixelEquality": True,
        "verticalBoundaryStripCount": 12, "horizontalBoundaryStripCount": 12,
        "fourPatchJunctionCount": 9, "nativeUpscalePerformed": False,
        "finalResamplingPerformed": False, "blendingPerformed": False,
        "meaning": "Mechanical integrity only. Does not certify layout, seam geometry or visual quality.",
    }
    acceptance = {
        "status": "candidate_pending_visual_and_external_seam_review",
        "complete": False, "complete4k": False, "strictComplete": False,
        "formalAccepted": False, "visualPassed": False,
        "internalVisualReview": "pending; inspect all 24 strips and 9 junctions at 100%",
        "externalTileEdgesVerified": False, "crossZoneEdgesVerified": False,
        "navigationValidated": False, "clientMappingValidated": False,
        "capacity5000Validated": False,
    }
    manifest = {
        "schemaVersion": 1, "createdAtUtc": utc_now(), "tile": TILE,
        "tileOrigin": origin, "tileGlobalCoreBox": expected_tile_box,
        "candidate": {"file": str(candidate_path), "sha256": candidate_hash, "pixels": [SIDE, SIDE],
                      "format": "PNG", "mode": "RGB", "nativeCoreCoveragePixels": SIDE * SIDE},
        "selection": {"path": str(selection_path), "sha256": sha_bytes(selection_raw),
                      "snapshotPath": str(qa_dir / "selection.snapshot.json")},
        "coordinateRecord": {"path": str(coordinate_path), "sha256": sha_bytes(coordinate_raw)},
        "script": ref(Path(__file__)),
        "operation": "Sixteen 1:1 crop[115,115,1139,1139] and opaque paste operations only",
        "inputs": inputs, "provenanceGraph": provenance.nodes,
        "missingHistoricalImages": provenance.missing_historical_images,
        "qa": qa, "preview": preview_entry, "mechanicalChecks": checks, **acceptance,
    }
    manifest_path = qa_dir / "manifest.json"
    derived = {
        "schemaVersion": 1, "file": str(candidate_path), "sha256": candidate_hash,
        "pixels": [SIDE, SIDE], "createdAtUtc": manifest["createdAtUtc"],
        "derivedFrom": inputs, "operation": manifest["operation"],
        "nativeGlobalBox": expected_tile_box, "manifest": str(manifest_path),
        "mechanicalChecks": checks, **acceptance,
    }

    def json_bytes(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    outputs.append((candidate_path.with_name(candidate_path.name + ".derived.json"), json_bytes(derived)))
    # Written last, so its hashes expose incomplete/failed publication or mixed runs.
    outputs.append((manifest_path, json_bytes(manifest)))
    for path, _ in outputs:
        inside(path, ZONE, "Output")
        if path.exists() and not args.replace_candidate:
            raise ValueError(f"Output already exists; use --replace-candidate explicitly: {path}")
    if selection_path in {p for p, _ in outputs}:
        raise ValueError("Selection cannot be one of the script's output files")
    # Fail before publishing if inputs changed during processing.
    if selection_path.read_bytes() != selection_raw or coordinate_path.read_bytes() != coordinate_raw:
        raise ValueError("Selection or coordinates changed during assembly")
    for node in provenance.nodes.values():
        if node["imageAvailable"] and sha_file(node["image"]) != node["sha256"]:
            raise ValueError(f"Source changed during assembly: {node['image']}")
        evidence = node["provenanceRecord"]
        if sha_file(evidence["path"]) != evidence["sha256"]:
            raise ValueError(f"Source provenance changed during assembly: {evidence['path']}")

    # Individual files are atomic. The complete output set is NOT a transaction.
    # A disk error stops the command; never mark the candidate complete from it.
    for path, data in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
        try:
            temporary.write_bytes(data)
            if sha_file(temporary) != sha_bytes(data):
                raise OSError(f"Written bytes failed hash verification: {temporary}")
            temporary.replace(path)
            if sha_file(path) != sha_bytes(data):
                raise OSError(f"Published bytes failed hash verification: {path}")
        finally:
            if temporary.exists():
                temporary.unlink()

    print(json.dumps({
        "candidate": str(candidate_path), "sha256": candidate_hash,
        "manifest": str(manifest_path), "boundaryStrips": 24, "junctions": 9,
        "previewOnly": str(preview_path), "mechanicalChecksPassed": True,
        "complete": False, "complete4k": False, "formalAccepted": False,
        "visualReview": "pending", "progressModified": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc), "type": type(exc).__name__,
                          "complete": False, "formalAccepted": False}, ensure_ascii=False),
              file=sys.stderr)
        raise SystemExit(2)

