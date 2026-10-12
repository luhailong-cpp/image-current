"""Export exact current southern-neighbor references; never generate or edit art."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from PIL import Image

ANCHORS_ROOT = Path(__file__).resolve().parent
BATCH_ROOT = ANCHORS_ROOT.parent
BASE = BATCH_ROOT.parent.parent
LEGACY_ZONE = BASE / "island-game-20261009" / "northwest"
TILES = ("r03_c02", "r03_c03", "r03_c04")
SIZE, CORE, HALO, PADDED = 1254, 4096, 115, 4326


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path):
    path = Path(path).resolve()
    return {"path": path.as_posix(), "sha256": sha(path), "bytes": path.stat().st_size}


def writable(path):
    path = Path(path).resolve()
    require(path.is_relative_to(ANCHORS_ROOT), f"Output outside anchors forbidden: {path}")
    return path


def save_json(path, data):
    path = writable(path)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return record(path)


def save_png(path, pixels):
    path = writable(path)
    image = Image.fromarray(pixels)
    with path.open("xb") as handle:
        image.save(handle, format="PNG")
    with Image.open(path) as saved:
        require(np.array_equal(np.asarray(saved), pixels), f"PNG roundtrip changed pixels: {path}")
        size, mode = list(saved.size), saved.mode
    return {**record(path), "dimensions": size, "mode": mode}


def intersection(a, b):
    box = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    return box if box[0] < box[2] and box[1] < box[3] else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Explicit new vNN output directory.")
    args = parser.parse_args()
    require(re.fullmatch(r"v\d{2,}", args.version), "Version must be explicit vNN.")
    require(BATCH_ROOT.name == "island-west-residences" and ANCHORS_ROOT.name == "anchors", "Unexpected builder location.")
    output = writable(ANCHORS_ROOT / args.version)
    require(not output.exists(), "Version exists; choose a new version. Never overwrite or delete it.")
    started = datetime.now(timezone.utc).isoformat()
    plan_path = BATCH_ROOT / "anchor-plan-v01.json"
    plan = read(plan_path)
    require(tuple(a["tile"] for a in plan["anchors"]) == TILES, "Plan must name exactly the three southern anchors.")
    input_snapshots = []
    for item in plan["fileInventory"]:
        require(item.get("exists") and Path(item["path"]).is_file(), f"Plan input missing: {item['path']}")
        actual = record(item["path"])
        require(actual["sha256"] == item["sha256"], f"Plan input changed; obtain a new plan: {item['path']}")
        input_snapshots.append(actual)
    authority = read(plan["authority"]["path"])
    authority_now = record(plan["authority"]["path"])
    current = {t["tileId"]: t for t in authority["tiles"]}
    for anchor in plan["anchors"]:
        adopted = current[anchor["tile"]]
        for kind, field in (("image", "currentCandidate"), ("record", "currentRecord")):
            require(Path(adopted[kind]["path"]).resolve() == Path(anchor[field]["path"]).resolve()
                    and adopted[kind]["sha256"] == anchor[field]["sha256"], "Current southern-anchor selection changed.")

    # These imported functions only read/verify. main/save/compose/join are never called.
    # The bytecode flag is set before importing any legacy module.
    sys.path.insert(0, str(LEGACY_ZONE))
    import assemble_connected_tiles as connected

    # Cache verified immutable provenance, not pixels or changed source files.
    # Every first visit performs the original complete source replay. Cache hits
    # rehash the exact candidate and record, then read its pixels afresh. All
    # observed dependency hashes are rechecked at completion. This avoids the
    # repeated recursive replay of the same connected/cross-repair subgraphs.
    dependency_snapshots = {}
    original_file_info = connected.repair.file_info
    original_validate_base = connected.repair.validate_base
    validated = {}
    cache_statistics = {"firstValidations": 0, "reusedValidations": 0}

    def tracked_file_info(path):
        value = original_file_info(path)
        key = Path(value["path"]).resolve().as_posix()
        previous = dependency_snapshots.get(key)
        require(previous is None or previous["sha256"] == value["sha256"], f"Dependency changed during verification: {key}")
        dependency_snapshots[key] = {"path": key, "sha256": value["sha256"]}
        return value

    def memo_validate_base(image_path, record_path, seen=None):
        image_path, record_path = Path(image_path).resolve(), Path(record_path).resolve()
        active = set() if seen is None else set(seen)
        require(record_path not in active and len(active) < 32, "Cyclic or excessive cached provenance chain.")
        key = (image_path.as_posix(), record_path.as_posix())
        if key in validated:
            saved = validated[key]
            require(tracked_file_info(image_path)["sha256"] == saved["imageHash"]
                    and tracked_file_info(record_path)["sha256"] == saved["recordHash"], "Cached candidate or record changed.")
            cache_statistics["reusedValidations"] += 1
            return connected.repair.read_pixels(image_path, CORE), copy.deepcopy(saved["proof"])
        result, proof = original_validate_base(image_path, record_path, seen)
        validated[key] = {"imageHash": tracked_file_info(image_path)["sha256"],
                          "recordHash": tracked_file_info(record_path)["sha256"], "proof": copy.deepcopy(proof)}
        cache_statistics["firstValidations"] += 1
        return result, proof

    connected.repair.file_info = tracked_file_info
    connected.repair.validate_base = memo_validate_base

    padded, proofs, roots, planes, cores = {}, {}, {}, {}, {}
    for anchor in plan["anchors"]:
        tile = anchor["tile"]
        pixels, proof = connected.reconstruct_padded(Path(anchor["currentCandidate"]["path"]),
                                                    Path(anchor["currentRecord"]["path"]))
        require(pixels.shape == (PADDED, PADDED, 3), "Incorrect reconstructed padded dimensions.")
        require(proof["image"]["sha256"] == anchor["currentCandidate"]["sha256"], "Current core identity differs.")
        root_path = Path(proof["rootAssembly"]["path"])
        root = read(root_path)
        with np.load(proof["rootPaddedProvenance"]["path"], allow_pickle=False) as archive:
            ids = archive["padded_source_id"].copy()
        require(ids.shape == (PADDED, PADDED) and ids.dtype == np.uint8 and np.all(ids < 16), "Invalid original source mask.")
        padded[tile], proofs[tile], roots[tile], planes[tile] = pixels, proof, root, ids
        cores[tile] = pixels[HALO:HALO + CORE, HALO:HALO + CORE].copy()
        print(f"Verified current core and original native halo: {tile}", flush=True)

    output.mkdir(parents=True, exist_ok=False)
    proof_files = {}
    for tile in TILES:
        proof_files[tile] = save_json(output / f"{tile}-verified-current-core-proof.json", {
            "schemaVersion": 1, "isAiGeneration": False, "rawNative": False,
            "operation": "read-only replay of current candidate and original halo ownership",
            "sourceProof": proofs[tile], "builder": record(__file__),
            "legacyPureReadFunction": {**record(LEGACY_ZONE / "assemble_connected_tiles.py"), "name": "reconstruct_padded"},
            "resampling": False, "formalAccepted": False,
        })
    exports = []
    for anchor in plan["anchors"]:
        tile = anchor["tile"]
        origin = proofs[tile]["tileOrigin"]
        padded_box = [origin[0] - HALO, origin[1] - HALO, origin[0] + CORE + HALO, origin[1] + CORE + HALO]
        # Each source gets a distinct owner ID. Current core IDs are 16..18;
        # original raw/composite cell IDs 0..15 retain the archived root scope.
        pixels = padded[tile].copy()
        owners = planes[tile].copy()
        current_registry = []
        for index, neighbor_tile in enumerate(TILES):
            neighbor_origin = proofs[neighbor_tile]["tileOrigin"]
            neighbor_box = [neighbor_origin[0], neighbor_origin[1], neighbor_origin[0] + CORE, neighbor_origin[1] + CORE]
            box = intersection(padded_box, neighbor_box)
            current_registry.append({"ownerId": 16 + index, "tileId": neighbor_tile,
                "image": proofs[neighbor_tile]["image"], "record": proofs[neighbor_tile]["record"],
                "globalBox": neighbor_box, "proof": proof_files[neighbor_tile]})
            if box is None:
                continue
            dx, dy = box[0] - padded_box[0], box[1] - padded_box[1]
            sx, sy = box[0] - neighbor_box[0], box[1] - neighbor_box[1]
            width, height = box[2] - box[0], box[3] - box[1]
            pixels[dy:dy + height, dx:dx + width] = cores[neighbor_tile][sy:sy + height, sx:sx + width]
            owners[dy:dy + height, dx:dx + width] = 16 + index
        require(np.array_equal(pixels[HALO:HALO + CORE, HALO:HALO + CORE], cores[tile]), "Own current core was changed by lateral halo overlay.")
        for entry in anchor["derivedReferencePlans"]:
            x0, y0, x1, y1 = entry["rootPaddedCrop"]
            patch = pixels[y0:y1, x0:x1].copy()
            owner_patch = owners[y0:y1, x0:x1].copy()
            root_ids = planes[tile][y0:y1, x0:x1].copy()
            fallback = owner_patch < 16
            require(patch.shape == (SIZE, SIZE, 3) and owner_patch.shape == (SIZE, SIZE), "Bad reference shape.")
            # Recheck every exported current-core pixel at identical global coordinates.
            for source in current_registry:
                ys, xs = np.nonzero(owner_patch == source["ownerId"])
                if not xs.size:
                    continue
                sx = xs + entry["globalBox"][0] - source["globalBox"][0]
                sy = ys + entry["globalBox"][1] - source["globalBox"][1]
                require(np.array_equal(patch[ys, xs], cores[source["tileId"]][sy, sx]), "Current core pixels changed or moved.")
            require(np.array_equal(patch[fallback], padded[tile][y0:y1, x0:x1][fallback]), "Native fallback halo changed.")
            stem = entry["anchorSlot"] + f"_current-derived-{args.version}"
            reference = save_png(output / f"{stem}.png", patch)
            overlap = save_png(output / f"{stem}.north-overlap-1254x230.png", patch[:230])
            owner_file = save_png(output / f"{stem}.owner-id-mask.png", owner_patch)
            root_mask_file = save_png(output / f"{stem}.original-root-source-id-mask.png", root_ids)
            fallback_file = save_png(output / f"{stem}.original-halo-selection-mask.png", fallback.astype(np.uint8) * 255)
            provenance_path = writable(output / f"{stem}.provenance.npz")
            with provenance_path.open("xb") as handle:
                np.savez_compressed(handle, owner_id=owner_patch, original_root_source_id=root_ids,
                    original_halo_selected=fallback, global_origin=np.array(entry["globalBox"][:2], np.int32))
            original_sources = []
            for source_id in np.unique(owner_patch[fallback]).tolist():
                source = roots[tile]["sources"][source_id]
                original_sources.append({"ownerId": source_id, "rootTileId": tile, "source": source,
                    "pixelCount": int(np.count_nonzero(owner_patch == source_id)),
                    "coordinateRule": "sourceLocal=referenceLocal+reference.globalOrigin-source.globalNativeBox.origin"})
            counts = {str(int(owner)): int(np.count_nonzero(owner_patch == owner)) for owner in np.unique(owner_patch)}
            require(sum(counts.values()) == SIZE * SIZE, "Reference provenance does not cover every pixel.")
            derivation = {
                "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
                "file": reference["path"], "sha256": reference["sha256"], "outputs": {"reference": reference, "northOverlap": overlap},
                "isAiGeneration": False, "rawNative": False, "mechanicalReference": True,
                "route": "mechanical_reference", "actualModel": None, "newModelOrQualityClaim": None,
                "tileId": tile, "anchorSlot": entry["anchorSlot"], "versionStem": stem,
                "nativeSize": [SIZE, SIZE], "dimensions": [SIZE, SIZE],
                "globalBox": entry["globalBox"], "coreBox": entry["coreBox"],
                "rootPaddedCrop": entry["rootPaddedCrop"], "currentCandidate": anchor["currentCandidate"],
                "currentCandidateRecord": anchor["currentRecord"], "verifiedCurrentCoreProof": proof_files[tile],
                "rootAssembly": proofs[tile]["rootAssembly"], "rootPaddedProvenance": proofs[tile]["rootPaddedProvenance"],
                "originalHaloSources": original_sources, "currentCoreSourceRegistry": current_registry,
                "sourceOwnership": {"ownerIdMask": owner_file, "originalRootSourceIdMask": root_mask_file,
                    "originalHaloSelectionMask": fallback_file, "provenancePlanes": record(provenance_path),
                    "ownerIdMeaning": "0..15=original root native/composite cell;16..18=current r03_c02,c03,c04 core",
                    "originalMaskMeaning": "Recorded root assembly ownership before current-core overlay; only fallback mask255 is used as halo",
                    "ownerPixelCounts": counts},
                "futureTarget": {"slot": entry["futureTarget"], "globalBox": entry["targetGlobalBox"],
                    "globalOverlapBox": entry["globalOverlapBox"], "sourceCrop": [0, 0, SIZE, 230],
                    "targetPasteTopLeft": [0, 1024], "overlapDimensions": [SIZE, 230]},
                "operation": "same-global-coordinate current core overlay on verified original native halo; exact integer crop",
                "resampling": False, "registration": False, "feathering": False,
                "colorCorrection": False, "pixelSynthesis": False, "formalAccepted": False,
                "assertions": {"fullSameCoordinateCoverage": True, "currentCorePixelsExact": True,
                    "adjacentCurrentCorePixelsExact": True, "originalHaloPixelsExact": True,
                    "diskPngPixelsExact": True, "overlapExactlyReferenceTop230": True},
                "limits": ["Reference only; not new generated art or formal map acceptance.",
                    "Current-core/original-halo boundary and paired new output still require visual review.",
                    "This mechanical record must not be relabeled as a builtin generation receipt."],
            }
            sidecar = save_json(output / f"{stem}.derivation.json", derivation)
            overlap_record = save_json(output / f"{stem}.north-overlap-1254x230.png.derivation.json", {
                "schemaVersion": 1, "isAiGeneration": False, "rawNative": False, "mechanicalReference": True,
                "file": overlap, "source": reference, "sourceDerivation": sidecar,
                "cropBox": [0, 0, SIZE, 230], "globalBox": entry["globalOverlapBox"],
                "dimensions": [SIZE, 230], "resampling": False, "pixelCopyExact": True,
                "targetSlot": entry["futureTarget"], "targetPasteTopLeft": [0, 1024], "formalAccepted": False,
            })
            exports.append({"anchorSlot": entry["anchorSlot"], "reference": reference, "derivation": sidecar,
                "northOverlap": overlap, "northOverlapDerivation": overlap_record, "futureTarget": entry["futureTarget"],
                "globalBox": entry["globalBox"], "coreBox": entry["coreBox"], "sourceOwnership": derivation["sourceOwnership"]})
            print(f"Exported reference and 100% overlap: {entry['anchorSlot']}", flush=True)
    complete_snapshots = {item["path"]: item for item in input_snapshots}
    complete_snapshots.update(dependency_snapshots)
    drift = []
    for item in complete_snapshots.values():
        final_hash = sha(item["path"])
        if final_hash != item["sha256"]:
            drift.append({"path": item["path"], "initialSha256": item["sha256"], "endSha256": final_hash})
    authority_end = record(plan["authority"]["path"])
    manifest = {
        "schemaVersion": 1, "status": "ready_mechanical_references_only" if not drift else "input_drift_do_not_use",
        "startedAtUtc": started, "endedAtUtc": datetime.now(timezone.utc).isoformat(),
        "isAiGeneration": False, "rawNative": False, "mechanicalReference": True,
        "builder": record(__file__), "plan": record(plan_path),
        "authorityAtStart": authority_now, "authorityAtEnd": authority_end,
        "authorityUnchanged": authority_now["sha256"] == authority_end["sha256"],
        "inputSnapshots": input_snapshots, "inputDrift": drift,
        "replayedDependencySnapshots": list(dependency_snapshots.values()),
        "verificationCache": cache_statistics,
        "currentCoreProofs": proof_files, "exports": exports,
        "statistics": {"currentCandidatesVerified": 3, "references1254Square": len(exports),
            "overlaps1254x230": len(exports), "fullResolutionReferencePixels": len(exports) * SIZE * SIZE,
            "overlapPixels": len(exports) * SIZE * 230, "unassignedPixels": 0,
            "inputDriftCount": len(drift), "newAiOutputs": 0, "sharedWrites": 0},
        "noSharedBytecodeWrites": sys.dont_write_bytecode,
        "resampling": False, "formalAcceptedCount": 0,
    }
    manifest_file = save_json(output / "current-south-anchors.manifest.json", manifest)
    print(json.dumps({"manifest": manifest_file, "statistics": manifest["statistics"],
                      "authorityUnchanged": manifest["authorityUnchanged"], "status": manifest["status"]}, ensure_ascii=False, indent=2))
    require(not drift, "Inputs changed during export; preserve this version and obtain a revised plan.")


if __name__ == "__main__":
    main()
