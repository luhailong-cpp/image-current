"""Tile-parameterized mechanical guides and native-image provenance.

No image generation is performed. Resampling is permitted only for explicitly
labelled layout guides. Native overlaps are copied at their original scale.
This script never updates the zone's progress, selection, or legacy r10_c09.
"""
from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import shutil

from PIL import Image

ZONE = Path(__file__).resolve().parent
CONTRACT_PATH = ZONE.parent / "production-contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
CONFIG_PATH = ZONE.parents[3] / "config" / "image-generation.json"
NATIVE = CONTRACT["nativePatchPlan"]["expectedNativePixels"]
CORE = CONTRACT["nativePatchPlan"]["corePixels"]
HALO = CONTRACT["nativePatchPlan"]["haloPixels"]
TILE_SIZE = CONTRACT["formalTilePixels"][0]
LAYOUT_CLASS = "layout-only input; never final artwork"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def tile_indices(tile):
    match = re.fullmatch(r"r(\d{2})_c(\d{2})", tile)
    if not match:
        raise ValueError("Tile must be rNN_cNN")
    row, col = map(int, match.groups())
    if not (1 <= row <= CONTRACT["rows"] and 1 <= col <= CONTRACT["columns"]):
        raise ValueError("Tile outside contract canvas")
    return row, col


def preserve_input_snapshot(path):
    """Keep a hash-addressed submitted input when refreshing a mutable guide."""
    path = Path(path)
    if not path.exists():
        return
    dest = path.parent.parent / 'input-snapshots' / (sha(path) + '.png')
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(path, dest)
    record = path.with_suffix('.png.derivation.json')
    if record.exists() and not dest.with_suffix('.png.derivation.json').exists():
        shutil.copy2(record, dest.with_suffix('.png.derivation.json'))


def writable_tile(tile):
    row, col = tile_indices(tile)
    split_path = ZONE.parents[3] / 'docs' / 'MAP_PARALLEL_SPLIT_20261013.json'
    if split_path.exists():
        for batch in read(split_path).get('batches', []):
            if (batch.get('owner') == '01a1216d-4a55-7063-ba13-5ddf6d9106f7'
                    and batch.get('status') == 'allocated_root_reserved'
                    and tile in batch.get('tiles', [])):
                raise ValueError(f'{tile} reserved for parallel worker {batch.get("worker")}')
    zone_contract = next(z for z in CONTRACT["zones"] if z["id"] == "southeast")
    if not (zone_contract["rows"][0] <= row <= zone_contract["rows"][1]
            and zone_contract["columns"][0] <= col <= zone_contract["columns"][1]):
        raise ValueError("This workflow writes southeast tiles only")
    if tile == "r10_c09":
        raise ValueError("Legacy r10_c09 is read-only in this workflow")
    return ZONE / tile


def plan_path(tile):
    local = ZONE / tile / "coordinate-plan.json"
    if local.exists():
        return local
    legacy = ZONE / "coordinate-plan.json"
    if legacy.exists() and read(legacy).get("tile") == tile:
        return legacy
    raise FileNotFoundError(f"No coordinate plan for {tile}")


def patch(plan, pid):
    return next(p for p in plan["patches"] if p["id"] == pid)


def approved_refs():
    refs = [
        {"path": CONTRACT["layoutReference"], "role": "authoritative full-map layout only"},
        {"path": CONTRACT["detailStyleReference"], "role": "material and daylight style; independent close-up, NOT coordinate crop"},
        {"path": CONTRACT["primaryStyleReference"], "role": "primary approved rounded painterly style only; do not copy UI or night lighting"},
    ]
    for ref in refs:
        ref["sha256"] = sha(ref["path"])
    assert refs[0]["sha256"] == CONTRACT["layoutSha256"]
    assert refs[1]["sha256"] == CONTRACT["detailSha256"]
    return refs


def prepare(tile):
    dest = writable_tile(tile)
    row, col = tile_indices(tile)
    x0, y0 = (col - 1) * TILE_SIZE, (row - 1) * TILE_SIZE
    guides = dest / "layout-only"
    guides.mkdir(parents=True, exist_ok=True)
    refs = approved_refs()
    overview = Image.open(refs[0]["path"])
    overview.load()
    canvas = CONTRACT["artCanvasPixels"]
    assert overview.width == overview.height == 1254
    assert canvas[0] == canvas[1] == 57344
    scale = overview.width / canvas[0]
    records = []
    for sr in range(1, CONTRACT["nativePatchPlan"]["subrows"] + 1):
        for sc in range(1, CONTRACT["nativePatchPlan"]["subcolumns"] + 1):
            x, y = x0 + (sc - 1) * CORE, y0 + (sr - 1) * CORE
            box = [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO]
            refbox = [v * scale for v in box]
            pid = f"p{sr}{sc}"
            out = guides / f"{pid}-layout-only.png"
            overview.transform((NATIVE, NATIVE), Image.Transform.EXTENT,
                               refbox, Image.Resampling.BICUBIC).save(out)
            record = {
                "id": pid, "subrow": sr, "subcolumn": sc,
                "file": str(out), "sha256": sha(out), "classification": LAYOUT_CLASS,
                "operation": "uniform mechanical overview extent crop/resample",
                "derivedFrom": refs[0], "outputDimensions": [NATIVE, NATIVE],
                "globalBox": box, "overviewBox": refbox,
                "coreBox": [x, y, x + CORE, y + CORE],
                "coreCropNative": [HALO, HALO, HALO + CORE, HALO + CORE],
            }
            write(out.with_suffix(".png.derivation.json"), record)
            records.append(record)
    tilebox = [x0, y0, x0 + TILE_SIZE, y0 + TILE_SIZE]
    tileguide = guides / f"{tile}-layout-only.png"
    overview.transform((1024, 1024), Image.Transform.EXTENT,
                       [v * scale for v in tilebox], Image.Resampling.BICUBIC).save(tileguide)
    write(tileguide.with_suffix(".png.derivation.json"), {
        "file": str(tileguide), "sha256": sha(tileguide), "classification": LAYOUT_CLASS,
        "operation": "uniform mechanical overview extent crop/resample",
        "derivedFrom": refs[0], "globalBox": tilebox,
        "overviewBox": [v * scale for v in tilebox], "outputDimensions": [1024, 1024],
    })
    plan = {
        "createdAt": now(), "tile": tile, "tileRow": row, "tileColumn": col,
        "tileOrigin": [x0, y0], "tileCoreBox": tilebox,
        "contract": {"path": str(CONTRACT_PATH), "sha256": sha(CONTRACT_PATH)},
        "referenceSize": list(overview.size), "artCanvasPixels": canvas,
        "expectedNativeSize": [NATIVE, NATIVE], "corePixels": CORE,
        "haloPixels": HALO, "adjacentOverlapPixels": HALO * 2,
        "resizeFinalArtAllowed": False, "references": refs, "patches": records,
        "status": "mechanical_inputs_only_no_native_art_generated",
    }
    write(dest / "coordinate-plan.json", plan)
    return {"tile": tile, "tileCoreBox": tilebox, "layoutGuides": len(records),
            "plan": str(dest / "coordinate-plan.json")}


def selected_path(tile, explicit=None):
    if explicit:
        path = Path(explicit).resolve()
    elif (ZONE / tile / "selected-patches.json").exists():
        path = ZONE / tile / "selected-patches.json"
    else:
        path = ZONE / "selected-patches.json"
    selection_bytes = path.read_bytes()
    selected = json.loads(selection_bytes.decode("utf-8-sig"))
    if selected.get("tile") != tile:
        raise ValueError(f"Selection {path} does not identify {tile}")
    return path, selected, hashlib.sha256(selection_bytes).hexdigest()


def safe_native_path(tile, relative):
    base = (ZONE / tile).resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base) or path.relative_to(base).parts[0] not in ("native", "processed"):
        raise ValueError("Native source must be in the source tile's native or processed directory")
    return path


def paste_overlap(image, target, source, source_path, source_tile, source_pid):
    sb, tb = source["globalBox"], target["globalBox"]
    overlap = [max(sb[0], tb[0]), max(sb[1], tb[1]), min(sb[2], tb[2]), min(sb[3], tb[3])]
    if overlap[0] >= overlap[2] or overlap[1] >= overlap[3]:
        raise ValueError(f"No native overlap with {source_tile}:{source_pid}")
    crop = [overlap[0] - sb[0], overlap[1] - sb[1], overlap[2] - sb[0], overlap[3] - sb[1]]
    at = [overlap[0] - tb[0], overlap[1] - tb[1]]
    native = Image.open(source_path)
    native.load()
    if native.size != (NATIVE, NATIVE) or native.mode != "RGB":
        raise ValueError("Native overlap must be exactly 1254x1254 RGB; never resize it")
    image.paste(native.crop(crop), tuple(at))
    evidence = source_path.with_suffix(".png.generation.json")
    if not evidence.exists():
        evidence = source_path.with_suffix(".png.derivation.json")
    record = {
        "sourceTile": source_tile, "sourcePatch": source_pid,
        "source": str(source_path), "sha256": sha(source_path),
        "nativeDimensions": list(native.size), "sourceGlobalBox": sb,
        "globalOverlapBox": overlap, "sourceCrop": crop, "pasteAt": at,
        "pastedDimensions": [crop[2] - crop[0], crop[3] - crop[1]],
        "operation": "unscaled pixel copy", "role": "exact native overlap constraint",
    }
    if evidence.exists():
        record["sourceProvenance"] = {"path": str(evidence), "sha256": sha(evidence)}
    return record


def refresh_left(tile, from_tile=None, selection=None):
    dest = writable_tile(tile)
    row, col = tile_indices(tile)
    from_tile = from_tile or f"r{row:02d}_c{col - 1:02d}"
    if tile_indices(from_tile) != (row, col - 1):
        raise ValueError("Left source must be the immediate tile to the west")
    target_plan = read(plan_path(tile))
    source_plan = read(plan_path(from_tile))
    selection_path, selected, selection_sha = selected_path(from_tile, selection)
    records = []
    for sr in range(1, 5):
        pid, sid = f"p{sr}1", f"p{sr}4"
        target, source = patch(target_plan, pid), patch(source_plan, sid)
        source_path = safe_native_path(from_tile, selected["patches"][sid])
        image = Image.open(target["file"]).convert("RGB")
        source_record = paste_overlap(image, target, source, source_path, from_tile, sid)
        assert source_record["sourceCrop"] == [CORE, 0, NATIVE, NATIVE]
        assert source_record["pasteAt"] == [0, 0]
        out = dest / "layout-only" / f"{pid}-left-boundary-conditioned.png"
        preserve_input_snapshot(out)
        image.save(out)
        record = {
            "file": str(out), "sha256": sha(out), "tile": tile, "patch": pid,
            "classification": "input guide only; enlarged layout pixels are forbidden in final art",
            "operation": "exact unscaled west native overlap over layout-only guide",
            "outputDimensions": [NATIVE, NATIVE], "targetGlobalBox": target["globalBox"],
            "layoutSource": {"path": target["file"], "sha256": target["sha256"]},
            "nativeSources": [source_record],
            "selectionSnapshot": {"path": str(selection_path), "sha256": selection_sha,
                                  "status": selected.get("status"), "tile": from_tile},
            "refreshedAt": now(), "crossTileSeamAccepted": False,
        }
        write(out.with_suffix(".png.derivation.json"), record)
        records.append(record)
    if sha(selection_path) != selection_sha:
        raise RuntimeError("Source selection changed during refresh; rerun refresh-left")
    result = {
        "tile": tile, "fromTile": from_tile, "refreshedAt": now(),
        "selectionPath": str(selection_path), "selectionSha256": selection_sha,
        "selectedSourcePatches": {f"p{sr}4": selected["patches"][f"p{sr}4"] for sr in range(1, 5)},
        "leftOverlapWidth": HALO * 2, "sourceRightStripX": [CORE, NATIVE],
        "targetLeftStripX": [0, HALO * 2], "guides": records,
        "status": "candidate_constraints_refresh_again_after_source_selection_changes",
        "refreshCommand": f"tile_native_workflow.py --tile {tile} refresh-left --from-tile {from_tile}",
        "crossTileSeamAccepted": False,
    }
    write(dest / "left-boundary-sources.json", result)
    return {"tile": tile, "conditionedGuides": len(records), "selectionSha256": result["selectionSha256"]}


def condition(tile, pid, source_specs):
    """Specs: source-tile:patch:relative-native-path, applied in listed order."""
    dest = writable_tile(tile)
    target = patch(read(plan_path(tile)), pid)
    boundary_manifest = dest / "left-boundary-sources.json"
    base_path = Path(target["file"])
    base_sources = []
    if target["subcolumn"] == 1 and boundary_manifest.exists():
        manifest = read(boundary_manifest)
        refresh_left(tile, manifest["fromTile"], manifest["selectionPath"])
        base_path = dest / "layout-only" / f"{pid}-left-boundary-conditioned.png"
        base_sources = read(base_path.with_suffix(".png.derivation.json"))["nativeSources"]
    image = Image.open(base_path).convert("RGB")
    sources = list(base_sources)
    for spec in source_specs:
        source_tile, sid, relative = spec.split(":", 2)
        source = patch(read(plan_path(source_tile)), sid)
        source_path = safe_native_path(source_tile, relative)
        sources.append(paste_overlap(image, target, source, source_path, source_tile, sid))
    out = dest / "layout-only" / f"{pid}-native-conditioned.png"
    preserve_input_snapshot(out)
    image.save(out)
    record = {
        "file": str(out), "sha256": sha(out), "tile": tile, "patch": pid,
        "classification": "input guide only; layout region cannot count as final native detail",
        "operation": "unscaled exact neighbor overlaps pasted in order; later sources own shared corners",
        "outputDimensions": [NATIVE, NATIVE], "targetGlobalBox": target["globalBox"],
        "layoutSource": {"path": target["file"], "sha256": target["sha256"]},
        "baseInput": {"path": str(base_path), "sha256": sha(base_path)},
        "nativeSources": sources, "createdAt": now(),
    }
    write(out.with_suffix(".png.derivation.json"), record)
    return {"file": str(out), "nativeSourceCount": len(sources), "sha256": record["sha256"]}


def ingest(tile, pid, version, src):
    """Archive a future builtin result without updating selections or progress."""
    dest_tile = writable_tile(tile)
    coordinate = patch(read(plan_path(tile)), pid)
    if not re.fullmatch(r"v\d+", version):
        raise ValueError("Version must be vN")
    stem = f"{pid}-{version}"
    request_path = dest_tile / f"{stem}.request.json"
    prompt_path = dest_tile / f"{stem}.prompt.txt"
    receipt_path = dest_tile / f"{stem}.receipt.json"
    request = read(request_path)
    receipt = read(receipt_path)
    prompt_path.read_text(encoding="utf-8-sig")
    refs = []
    for i, ref in enumerate(request["referenced_image_paths"], 1):
        refs.append({"path": ref, "sha256": sha(ref),
                     "role": request.get("referenceRoles", {}).get(str(i), "See exact role in prompt")})
    dest = dest_tile / "native" / f"{stem}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and sha(dest) != sha(src):
        raise FileExistsError("Refusing to overwrite a different native result; use a new version")
    if Path(src).resolve() != dest.resolve():
        shutil.copy2(src, dest)
    image = Image.open(dest)
    image.load()
    record = {
        "file": str(dest), "sha256": sha(dest), "ingestedAt": now(),
        "generatedAt": receipt.get("receivedAt", now()), "generatedAtBasis": "tool response received time",
        "nativeDimensions": list(image.size), "width": image.width, "height": image.height, "format": image.format,
        "tool": "image_gen__imagegen", "route": "builtin", "configSnapshot": read(CONFIG_PATH) if CONFIG_PATH.exists() else {
            "model": None, "quality": None, "preferred_route": "builtin",
            "status": "shared_config_unavailable_at_ingest",
            "missingPath": str(CONFIG_PATH),
            "note": "Builtin selector and returned model/quality remain undisclosed; no shared config recreated or inferred",
        },
        "submittedParameters": {"model": None, "quality": None}, "actualModel": None, "actualQuality": None,
        "unverifiedReason": "Host-managed builtin; no model/quality selector or returned model/quality metadata",
        "prompt": str(prompt_path), "promptSha256": sha(prompt_path), "references": refs,
        "evidence": {"request": str(request_path), "requestSha256": sha(request_path),
                     "receipt": str(receipt_path), "receiptSha256": sha(receipt_path), "sourcePath": str(src)},
        "coordinate": coordinate, "upsamplingApplied": False,
        "status": "candidate_pending_geometry_and_seam_review" if image.size == (NATIVE, NATIVE)
                  else "dimension_replanning_required_do_not_resize",
    }
    write(dest.with_suffix(".png.generation.json"), record)
    return {"file": str(dest), "sha256": record["sha256"], "nativeDimensions": list(image.size), "status": record["status"]}


def audit(tile):
    dest = writable_tile(tile)
    plan = read(plan_path(tile))
    row, col = tile_indices(tile)
    count = 0
    for target in plan["patches"]:
        x = (col - 1) * TILE_SIZE + (target["subcolumn"] - 1) * CORE
        y = (row - 1) * TILE_SIZE + (target["subrow"] - 1) * CORE
        assert target["coreBox"] == [x, y, x + CORE, y + CORE]
        assert target["globalBox"] == [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO]
        assert sha(target["file"]) == target["sha256"]
        assert Image.open(target["file"]).size == (NATIVE, NATIVE)
        count += 1
    checks = []
    manifest_path = dest / "left-boundary-sources.json"
    if manifest_path.exists():
        manifest = read(manifest_path)
        assert sha(manifest["selectionPath"]) == manifest["selectionSha256"], "Selection changed: run refresh-left"
        for guide in manifest["guides"]:
            assert sha(guide["file"]) == guide["sha256"]
            source = guide["nativeSources"][0]
            assert sha(source["source"]) == source["sha256"]
            native = Image.open(source["source"])
            image = Image.open(guide["file"])
            base = Image.open(guide["layoutSource"]["path"])
            assert image.crop((0, 0, HALO * 2, NATIVE)).tobytes() == native.crop((CORE, 0, NATIVE, NATIVE)).tobytes()
            assert image.crop((HALO * 2, 0, NATIVE, NATIVE)).tobytes() == base.crop((HALO * 2, 0, NATIVE, NATIVE)).tobytes()
            checks.append({"patch": guide["patch"], "unscaledLeftOverlapByteIdentical": True,
                           "remainingLayoutPixelsByteIdentical": True, "sourceSha256": source["sha256"]})
    result = {"tile": tile, "auditedAt": now(), "coordinateGuidesVerified": count,
              "expectedGuideCount": 16, "leftBoundaryChecks": checks,
              "nativeArtGeneratedByThisWorkflow": False, "finalArtOrAcceptanceClaimed": False,
              "status": "mechanical_preparation_verified"}
    assert count == 16
    write(dest / "preparation-audit.json", result)
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--tile", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("prepare")
    left = commands.add_parser("refresh-left")
    left.add_argument("--from-tile")
    left.add_argument("--selected")
    cond = commands.add_parser("condition")
    cond.add_argument("patch")
    cond.add_argument("sources", nargs="*")
    ingest_cmd = commands.add_parser("ingest")
    ingest_cmd.add_argument("patch")
    ingest_cmd.add_argument("version")
    ingest_cmd.add_argument("source")
    commands.add_parser("audit")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.tile)
    elif args.command == "refresh-left":
        result = refresh_left(args.tile, args.from_tile, args.selected)
    elif args.command == "condition":
        result = condition(args.tile, args.patch, args.sources)
    elif args.command == "ingest":
        result = ingest(args.tile, args.patch, args.version, args.source)
    else:
        result = audit(args.tile)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
