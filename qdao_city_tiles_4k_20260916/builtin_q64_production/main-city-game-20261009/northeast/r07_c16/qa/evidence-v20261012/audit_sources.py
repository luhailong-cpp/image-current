"""Read-only r07_c16 source audit; writes JSON reports only beside this script.

Run with --require-complete when all 16 selected cores are expected. Otherwise
zero/partial production is an explicit waiting/partial state, never a pass.
Native artwork, selection, sidecars, prompts, progress and shared files are read
only. Mixed-guide replay is performed in memory without saving any image.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image

OUT = Path(__file__).resolve().parent
TILE = OUT.parent.parent
EXPECTED = [f"p{r}{c}" for r in range(1, 5) for c in range(1, 5)]
NATIVE_SIZE = [1254, 1254]
VERSION = "v20261012"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def norm(path):
    return str(Path(path).resolve()).casefold()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def image_rgb(path):
    with Image.open(path) as image:
        return image.convert("RGB")


def expected_neighbor(patch, direction):
    tr, tc = map(int, re.fullmatch(r"r(\d+)_c(\d+)", TILE.name).groups())
    r, c = int(patch[1]), int(patch[2])
    if direction == "west":
        c -= 1
        if c == 0:
            tc -= 1
            c = 4
    elif direction == "north":
        r -= 1
        if r == 0:
            tr -= 1
            r = 4
    elif direction == "east":
        c += 1
        if c == 5:
            tc += 1
            c = 1
    elif direction == "south":
        r += 1
        if r == 5:
            tr += 1
            r = 1
    return f"r{tr:02}_c{tc:02}", f"p{r}{c}"


def run(require_complete=False):
    require(TILE.name == "r07_c16", "This audit is restricted to r07_c16")
    errors, warnings, native_records, guide_records, selection_records = [], [], [], [], []
    refs_verified = derived_verified = layout_verified = 0
    selected_path = TILE / "selected-native.json"
    selection = {}
    try:
        if selected_path.exists():
            selection = read(selected_path)
            require(isinstance(selection, dict), "Selection must be an object")
        for patch, filename in selection.items():
            require(patch in EXPECTED, f"Unknown canonical selection key: {patch}")
            require(isinstance(filename, str), f"Selection {patch} filename is not a string")
            require(Path(filename).name == filename, f"Selection {patch} must contain a filename only")
            require(re.fullmatch(re.escape(patch) + r"-v20261012(?:-[A-Za-z0-9_-]+)?\.png", filename),
                    f"Selection {patch} is not a v20261012 filename: {filename}")
            source = TILE / "native" / filename
            require(source.is_file(), f"Selected native missing: {source}")
            selection_records.append({"patch": patch, "filename": filename, "sha256": sha(source)})
    except Exception as error:
        errors.append({"file": str(selected_path), "check": "selected-native", "error": str(error)})

    coordinates = {}
    try:
        data = read(TILE / "coordinates.json")
        require(data["tile"] == TILE.name, "Coordinate tile differs")
        require(sha(data["layoutSource"]) == data["layoutSha256"], "Layout source hash differs")
        coordinates = {item["id"]: item for item in data["patches"]}
        require(sorted(coordinates) == sorted(EXPECTED), "Coordinate patch IDs differ from 16 expected cores")
        for patch, coord in coordinates.items():
            require(coord["coreCrop"] == [115, 115, 1139, 1139], f"Unexpected core crop for {patch}")
            require(sha(coord["guide"]) == coord["guideSha256"], f"Layout guide hash differs for {patch}")
            require(list(image_rgb(coord["guide"]).size) == NATIVE_SIZE, f"Layout guide size differs for {patch}")
            layout_verified += 1
    except Exception as error:
        errors.append({"file": str(TILE / "coordinates.json"), "check": "coordinates-and-layout", "error": str(error)})

    native_files = sorted((TILE / "native").glob("*.png"))
    for native in native_files:
        try:
            record = read(str(native) + ".generation.json")
            digest = sha(native)
            require(norm(record["file"]) == norm(native), "Sidecar file does not identify this native")
            require(record["sha256"] == digest, "Native differs from sidecar SHA256")
            original = Path(record["sourceOutputPath"])
            require(original.is_file(), "Original sourceOutputPath is missing")
            require(sha(original) == digest, "Native is not byte-identical to original tool output")
            with Image.open(native) as image:
                size, fmt = list(image.size), image.format
                image.verify()
            require(size == NATIVE_SIZE, f"Native size is {size}, expected {NATIVE_SIZE}")
            require(fmt == "PNG", "Native format is not PNG")
            require(record["nativeSize"] == NATIVE_SIZE, "Recorded nativeSize differs")
            require(record.get("resized") is False, "Sidecar must explicitly record resized=false")
            require(record.get("route") == "builtin" and record.get("tool") == "image_gen", "Generation route is not built-in image_gen")
            require(record.get("actualModel", "missing") is None and record.get("actualQuality", "missing") is None,
                    "Undisclosed actual model/quality must remain null")
            patch = native.stem.split("-")[0]
            if patch in EXPECTED:
                require(native.stem.startswith(patch + "-" + VERSION), "Core native does not have the resumed version ID")
                require(record.get("coordinates") == coordinates.get(patch), "Native coordinate record differs from tile plan")
                require(record.get("dimensionsMatch1254Plan") is True, "Native does not confirm 1254 plan")
                require(record.get("width") == 1254 and record.get("height") == 1254, "Recorded width/height differs")

            expected_prompt = TILE / "prompts" / f"{native.stem}.prompt.txt"
            expected_request = TILE / "prompts" / f"{native.stem}.request.json"
            expected_receipt = TILE / "receipts" / f"{native.stem}.receipt.json"
            for key, expected_path in (("prompt", expected_prompt), ("request", expected_request), ("evidence", expected_receipt)):
                require(norm(record[key]) == norm(expected_path), f"{key} path does not share the native version ID")
                require(expected_path.is_file(), f"Missing {key}: {expected_path}")
            request, receipt = read(expected_request), read(expected_receipt)
            prompt = expected_prompt.read_text(encoding="utf-8-sig")
            require(prompt.strip() == request["prompt"].strip(), "Prompt text differs from saved request")
            require(norm(receipt["sourceOutputPath"]) == norm(original), "Receipt points to a different tool output")
            require(receipt.get("route") == "builtin" and receipt.get("tool") == "image_gen", "Receipt route is not built-in image_gen")
            require(receipt.get("actualModel", "missing") is None and receipt.get("actualQuality", "missing") is None,
                    "Receipt actual model/quality must remain null")
            require(request.get("transparent_background") is False, "Unexpected transparent-background request")
            references = record["references"]
            require(len(references) >= 4, "Fewer than 4 saved image references")
            require([norm(ref["file"]) for ref in references] == [norm(path) for path in request["referenced_image_paths"]],
                    "Request reference order differs from sidecar")
            require([ref["role"] for ref in references] == request["referenceRoles"], "Reference roles differ from request")
            for reference in references:
                require(sha(reference["file"]) == reference["sha256"], f"Reference SHA256 differs: {reference['file']}")
                refs_verified += 1
            if patch in EXPECTED:
                mixed_path = TILE / "layout-only" / f"{patch}-mixed-context.png"
                require(norm(mixed_path) in [norm(ref["file"]) for ref in references], "Core request lacks its mixed context guide")
                require(Path(str(mixed_path) + ".generation.json").is_file(), "Mixed context sidecar is missing")
            native_records.append({
                "native": str(native), "sha256": digest, "nativeSize": size,
                "selectedBy": [key for key, value in selection.items() if value == native.name],
                "sourceOutputPath": str(original), "sourceByteIdentity": True,
                "promptRequestReceiptCheck": True, "referenceHashCheck": True,
                "sourceArtResized": False,
            })
        except Exception as error:
            errors.append({"file": str(native), "check": "native-provenance", "error": str(error)})

    for sidecar in sorted((TILE / "native").glob("*.png.generation.json")):
        if not Path(str(sidecar).removesuffix(".generation.json")).is_file():
            errors.append({"file": str(sidecar), "check": "orphan-sidecar", "error": "Native PNG is missing"})

    for sidecar in sorted((TILE / "layout-only").glob("*-mixed-context.png.generation.json")):
        try:
            record = read(sidecar)
            output = Path(str(sidecar).removesuffix(".generation.json"))
            require(norm(record["file"]) == norm(output), "Mixed guide sidecar file differs")
            require(sha(output) == record["sha256"], "Mixed guide SHA256 differs")
            sources = record["derivedFrom"]
            require(bool(sources), "Mixed guide derivedFrom is empty")
            patch = output.name.split("-")[0]
            require(norm(sources[0]["file"]) == norm(coordinates[patch]["guide"]), "First mixed source is not the coordinate layout guide")
            replay = image_rgb(sources[0]["file"])
            for index, source in enumerate(sources):
                require(sha(source["file"]) == source["sha256"], f"Derived source SHA256 differs: {source['file']}")
                derived_verified += 1
                if index == 0:
                    require("crop" not in source and "paste" not in source, "Base layout source unexpectedly transformed")
                    continue
                crop, paste = source["crop"], source["paste"]
                require(len(crop) == 4 and len(paste) == 2 and all(type(x) is int for x in crop + paste), "Derived operation must use integer crop/paste coordinates")
                original = image_rgb(source["file"])
                require(0 <= crop[0] < crop[2] <= original.width and 0 <= crop[1] < crop[3] <= original.height, "Derived crop exceeds source bounds")
                require(0 <= paste[0] and 0 <= paste[1] and paste[0] + crop[2] - crop[0] <= replay.width and paste[1] + crop[3] - crop[1] <= replay.height, "Derived paste exceeds guide bounds")
                replay.paste(original.crop(tuple(crop)), tuple(paste))
            actual = image_rgb(output)
            require(list(actual.size) == NATIVE_SIZE and actual.size == replay.size, "Mixed guide dimensions differ")
            require(actual.tobytes() == replay.tobytes(), "Mixed guide differs from exact derived-source replay")
            declared = record.get("operation", {}).get("requiredDirections", [])
            require(isinstance(declared, list) and all(direction in ("north", "south", "east", "west") for direction in declared),
                    "Invalid declared requiredDirections")
            # Every core in this eastern tile has a produced west dependency.
            # Internal north dependencies are also mandatory. The top-row north
            # tile has not yet been produced; absence of that source is recorded
            # as an unaudited boundary, not misrepresented as a broken reference.
            required_directions = set(declared) | {"west"}
            if int(patch[1]) > 1:
                required_directions.add("north")
            actual_directions = []
            for direction in ("north", "south", "east", "west"):
                tile_id, neighbor = expected_neighbor(patch, direction)
                found = any(source.get("tile") == tile_id and source.get("patch") == neighbor for source in sources)
                if found:
                    actual_directions.append(direction)
                if direction in required_directions:
                    require(found, f"Missing required actual {direction} native dependency {tile_id}/{neighbor}")
            north_boundary_not_audited = int(patch[1]) == 1 and "north" not in actual_directions
            if north_boundary_not_audited:
                warnings.append({"check": "north-boundary-not-audited", "patch": patch,
                                 "note": "This historical context has no external north native source; source evidence passes without claiming north boundary continuity."})
            guide_records.append({"file": str(output), "sha256": record["sha256"], "sourceCount": len(sources),
                                  "pixelReplay": True, "declaredRequiredDirections": declared,
                                  "verifiedRequiredDirections": sorted(required_directions), "actualDirections": actual_directions,
                                  "northBoundaryNotAudited": north_boundary_not_audited, "resampling": False})
        except Exception as error:
            errors.append({"file": str(sidecar), "check": "mixed-guide-replay", "error": str(error)})

    missing = [patch for patch in EXPECTED if patch not in selection]
    if require_complete and missing:
        errors.append({"file": str(selected_path), "check": "completion", "error": f"Missing selected cores: {', '.join(missing)}"})
    pending = sorted(path.stem.removesuffix(".request") for path in (TILE / "prompts").glob("*.request.json")
                     if not (TILE / "native" / f"{path.stem.removesuffix('.request')}.png").exists())
    if pending:
        warnings.append({"check": "pending-requests", "ids": pending, "note": "Saved requests without native outputs are pending, not completion evidence."})
    count = len(selection_records)
    status = "fail" if errors else "pass" if count == 16 else "waiting" if count == 0 else "partial"
    result = {
        "tile": TILE.name, "auditedAt": datetime.now(timezone.utc).isoformat(), "status": status,
        "scope": "Source evidence only; does not approve artistic quality, seams or candidate composition.",
        "readOnlySourceAudit": True, "expectedSelectedCoreCount": 16, "selectedCoreCount": count,
        "nativeFilesFound": len(native_files), "nativeRecordsVerified": len(native_records),
        "layoutGuidesVerified": layout_verified, "directReferencesVerified": refs_verified,
        "derivedSourcesVerified": derived_verified, "mixedGuidesReplayed": len(guide_records),
        "missingSelectedPatches": missing, "selectionRecords": selection_records,
        "nativeRecords": native_records, "mixedGuideRecords": guide_records,
        "errors": errors, "warnings": warnings,
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report = OUT / f"source-audit-{stamp}.json"
    with report.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    summary = {key: result[key] for key in ("tile", "status", "selectedCoreCount", "expectedSelectedCoreCount", "nativeFilesFound", "nativeRecordsVerified", "mixedGuidesReplayed", "errors")}
    summary["report"] = str(report)
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true", help="Fail if any of the 16 selected core patches is missing")
    args = parser.parse_args()
    sys.exit(run(args.require_complete))
