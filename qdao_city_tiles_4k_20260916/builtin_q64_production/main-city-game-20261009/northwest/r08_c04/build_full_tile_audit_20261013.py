"""Build one immutable r08_c04 native candidate and its 33 + 7 audit crops.
Includes only the two explicitly root-approved row2 x2048 native masks.
No ImageGen calls, selection edits, acceptance changes or packages.
Run with --check-ready first; no argument builds only when all 16 selections exist.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, sys
import numpy as np
from PIL import Image

T = Path(__file__).resolve().parent
Z = T.parent
TILE = "r08_c04"
NORTH = Z / "r07_c04/candidate/r07_c04-candidate-native-bridges-2268d482e68c2928/candidate.png"
NORTH_SHA = "12a5ba0622b6ba365a7e89971a7d7682065f1194bdefe6c2d6141c28cece9a20"
IDS = [f"s{r:02d}_{c:02d}" for r in range(1, 5) for c in range(1, 5)]
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("native_production", Z / "production_v2.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

def ref(path):
    return {"file": str(path), "sha256": p.sha(path)}

def pixel_key(im):
    rgb = im.convert("RGB")
    return f"{rgb.width}x{rgb.height}:" + hashlib.sha256(rgb.tobytes()).hexdigest()

def ready():
    selection = p.read(T / "selection.json")
    missing = [pid for pid in IDS if pid not in selection or not Path(selection[pid]).is_file()]
    extra = sorted(set(selection) - set(IDS))
    return selection, missing, extra

def review_catalog():
    """Reuse exact crop pixels, with explicit per-crop verdicts preferred.
    A mixed source-level finding never grants a pass to unnamed individual crops.
    """
    catalog, issues = {}, []
    for review_file in sorted((T / "qa/source-review").glob("*/*review*.json")):
        review = p.read(review_file)
        if review.get("actuallyViewed") is not True:
            continue
        manifest_path = review_file.parent / "manifest.json"
        manifest = p.read(manifest_path) if manifest_path.exists() else {}
        names = {x.get("name", Path(x.get("file", "")).stem): x
                 for x in manifest.get("crops", [])}
        entries = review.get("cropReviews") or review.get("crops") or review.get("viewedCrops") or []
        if not str(review.get("status", "")).startswith("passed"):
            issues.append({"review": ref(review_file), "status": review.get("status"),
                           "finding": review.get("finding", review.get("sourceInterior")),
                           "source": review.get("source", review.get("sourceId")),
                           "fullTileInternalQAPassed": False})
        for item in entries:
            if item.get("actuallyViewed") is False:
                continue
            entry = dict(names.get(item.get("name"), {}))
            entry.update(item)
            if not entry.get("file") or not entry.get("sha256"):
                continue
            source = Path(entry["file"])
            if not source.is_file() or p.sha(source) != entry["sha256"]:
                continue
            explicit = item.get("status", item.get("verdict"))
            if explicit in {"passed", "pass"}:
                status = "passed"
            elif explicit in {"needs_repair", "failed", "unpassed"}:
                status = "needs_repair"
            elif explicit is not None:
                status = "pending"
            elif str(review.get("status", "")).startswith("passed"):
                status = "passed"
            else:
                status = "unpassed_source_issue_without_crop_verdict"
            evidence = {"review": ref(review_file), "reviewedCrop": ref(source),
                        "status": status, "explicitPerCropVerdict": explicit is not None,
                        "finding": item.get("finding", review.get("finding")),
                        "sourceLevelStatus": review.get("status")}
            key = pixel_key(Image.open(source))
            catalog.setdefault(key, []).append(evidence)
    return catalog, issues

def additional_neighbors():
    report = {}
    for side, tile in [("west", "r08_c03"), ("east", "r08_c05")]:
        directory = Z / tile
        report[side] = {"tile": tile, "checkedDirectory": str(directory),
                        "directoryExists": directory.is_dir(),
                        "verifiedFinal": None, "extraNeighborQACreated": False,
                        "status": "missing_verified_final_in_checked_owner_path"}
        if directory.is_dir():
            manifests = list(directory.glob("qa/acceptance.json"))
            report[side]["acceptanceEvidenceFiles"] = [ref(x) for x in manifests]
            report[side]["status"] = "requires_current_final_confirmation"
    directory = Z.parent / "southwest/r09_c04"
    manifest = directory / "pipeline/qa/recover20261013-v01/manifest.json"
    south = {"tile": "r09_c04", "checkedDirectory": str(directory),
             "directoryExists": directory.is_dir(), "verifiedFinal": None,
             "extraNeighborQACreated": False, "status": "missing_verified_final"}
    if manifest.exists():
        data = p.read(manifest)
        core = data.get("core", {})
        candidate = Path(core.get("file", ""))
        valid = candidate.is_file() and p.sha(candidate) == core.get("sha256")
        south.update({"observedManifest": ref(manifest), "observedCandidate": core,
                      "candidateHashVerified": valid,
                      "manifestFormalAccepted": data.get("formalAccepted"),
                      "manifestInternalAccepted": data.get("internalAccepted"),
                      "status": "candidate_exists_but_observed_manifest_not_accepted"
                      if valid and not data.get("formalAccepted")
                      else "requires_current_final_confirmation"})
    report["south"] = south
    return report

def apply_approved_repairs(image, owner, registry):
    directory = T / "repair-batches/row2-west-joints-20261013"
    approval_file = directory / "root-independent-local-review.json"
    approval = p.read(approval_file)
    assert approval.get("actuallyViewed") is True
    assert approval.get("status") == "approved_local_native_roi_adoption"
    handoff_file = directory / "handoff.json"
    handoff = p.read(handoff_file)
    proposals = handoff["acceptedROIProposals"]
    assert len(proposals) == 2
    assert {x["sha256"] for x in proposals} == set(approval["sourceHashes"])
    baseline = image.copy()
    original_context = Image.open(directory / "joint-x2048-01/edit-target.png").convert("RGB")
    selected_total = 0
    for index, proposal in enumerate(proposals, 17):
        source, mask_file = Path(proposal["source"]), Path(proposal["mask"])
        assert p.sha(source) == proposal["sha256"]
        assert p.sha(mask_file) == proposal["maskSha256"]
        assert proposal["worldBox"] == [13709, 29581, 14963, 30835]
        assert proposal["originInTile"] == [1421, 909]
        raw = Image.open(source).convert("RGB")
        mask_image = Image.open(mask_file)
        assert raw.size == mask_image.size == (1254, 1254)
        mask = np.asarray(mask_image)
        assert set(np.unique(mask)).issubset({0, 255})
        selected = mask == 255
        count = int(selected.sum())
        assert count == proposal["pixelCount"]
        x, y = proposal["originInTile"]
        baseline_pixels = np.asarray(baseline.crop((x, y, x+1254, y+1254)))
        assert np.array_equal(baseline_pixels[selected], np.asarray(original_context)[selected])
        region = owner[y:y+1254, x:x+1254]
        assert not np.any(region[selected] >= 17), "Repair masks overlap"
        image.paste(raw, (x, y), mask_image)
        region[selected] = index
        generation_file = source.parent / "generation.json"
        generation = p.read(generation_file)
        assert generation["sha256"] == proposal["sha256"]
        host = Path(generation["hostPath"])
        host_exists = host.is_file()
        if host_exists:
            assert p.sha(host) == proposal["sha256"]
        registry.append({"id": "approved-row2-x2048-" + source.parent.name,
                         "ownerIndex": index, "file": str(source),
                         "sha256": proposal["sha256"],
                         "generationRecord": ref(generation_file),
                         "request": ref(source.parent / "request.json"),
                         "prompt": ref(source.parent / "prompt.txt"),
                         "receipt": ref(source.parent / "tool-receipt.json"),
                         "worldBoxWithHalo": proposal["worldBox"],
                         "nativeOriginInTile": [x, y],
                         "nativeMask": ref(mask_file), "sourcePixelCount": count,
                         "sourceROI": proposal["roi"], "targetTileROI": proposal["tileROI"],
                         "localApproval": ref(approval_file),
                         "hostOutputPath": str(host), "hostAvailable": host_exists,
                         "hostBytesIdentical": True if host_exists else None,
                         "actualModel": None, "actualQuality": None})
        selected_total += count
    assert selected_total == 120413
    return {"approval": ref(approval_file), "handoff": ref(handoff_file),
            "approvedSourceCount": 2, "selectedPixelCount": selected_total,
            "sameWorldBaselineUnderMasksVerified": True,
            "sourceResampled": False, "sourceBlended": False}

def build():
    selection, missing, extra = ready()
    if missing or extra:
        return {"status": "not_ready_no_artifacts_written", "selected": len(selection),
                "missing": missing, "unexpectedKeys": extra}
    selection_sha = p.sha(T / "selection.json")
    coords = p.read(T / "coordinates.json")
    assert coords["tileWorldBox"] == [12288, 28672, 16384, 32768]
    expected = {x["id"]: x for x in coords["patches"]}
    image = Image.new("RGB", (4096, 4096))
    owner = np.zeros((4096, 4096), dtype=np.uint8)
    registry, cores = [], {}
    for index, pid in enumerate(IDS, 1):
        source = Path(selection[pid]).resolve()
        source.relative_to(T / "native")
        valid = p.validate_native(source, T, pid)
        generation_path = Path(valid["generationRecord"])
        generation = p.read(generation_path)
        for key in ["worldBoxWithHalo", "coreWorldBox", "coreCrop"]:
            assert generation[key] == expected[pid][key], (pid, key)
        row, col = int(pid[1:3]) - 1, int(pid[4:6]) - 1
        x, y = col * 1024, row * 1024
        with Image.open(source) as raw:
            core = raw.convert("RGB").crop((115, 115, 1139, 1139))
        image.paste(core, (x, y))
        owner[y:y+1024, x:x+1024] = index
        cores[index] = np.asarray(core)
        host = Path(generation.get("evidence", {}).get("hostOutputPath", ""))
        host_exists = host.is_file()
        if host_exists:
            assert p.sha(host) == valid["sha256"], (pid, "host byte mismatch")
        registry.append({"id": pid, "ownerIndex": index, "file": str(source),
                         "sha256": valid["sha256"], "generationRecord": ref(generation_path),
                         "prompt": ref(Path(valid["prompt"])),
                         "request": ref(Path(valid["request"])),
                         "receipt": ref(Path(valid["receipt"])),
                         "worldBoxWithHalo": generation["worldBoxWithHalo"],
                         "coreWorldBox": generation["coreWorldBox"],
                         "sourceCoreCrop": [115, 115, 1139, 1139],
                         "tileCorePasteXY": [x, y], "nativeOriginInTile": [x-115, y-115],
                         "sourcePixelCount": 1048576, "corePixelKey": pixel_key(core),
                         "hostOutputPath": str(host), "hostAvailable": host_exists,
                         "hostBytesIdentical": True if host_exists else None,
                         "actualModel": generation.get("actualModel"),
                         "actualQuality": generation.get("actualQuality")})
    assert p.sha(NORTH) == NORTH_SHA
    north = Image.open(NORTH).convert("RGB")
    assert north.size == (4096, 4096)
    arr = np.asarray(image)
    for item in registry:
        x, y = item["tileCorePasteXY"]
        index = item["ownerIndex"]
        assert np.all(owner[y:y+1024, x:x+1024] == index)
        assert np.array_equal(arr[y:y+1024, x:x+1024], cores[index])
    assert set(np.unique(owner)) == set(range(1, 17))
    repair_info = apply_approved_repairs(image, owner, registry)
    arr = np.asarray(image)
    proved = 0
    for item in registry:
        ox, oy = item["nativeOriginInTile"]
        x0, y0 = max(0, ox), max(0, oy)
        x1, y1 = min(4096, ox+1254), min(4096, oy+1254)
        mask = owner[y0:y1, x0:x1] == item["ownerIndex"]
        raw = np.asarray(Image.open(item["file"]).convert("RGB"))
        source_pixels = raw[y0-oy:y1-oy, x0-ox:x1-ox]
        assert np.array_equal(arr[y0:y1, x0:x1][mask], source_pixels[mask])
        item["sourcePixelCount"] = int(mask.sum())
        proved += item["sourcePixelCount"]
    assert proved == 16777216 and set(np.unique(owner)) == set(range(1, 19))
    assert p.sha(T / "selection.json") == selection_sha, "Selection changed; build stopped"
    catalog, source_issues = review_catalog()
    repair_dir = T / "repair-batches/row2-west-joints-20261013"
    repaired_seam = repair_dir / "x2048-combined-west-seam.png"
    catalog.setdefault(pixel_key(Image.open(repaired_seam)), []).append({
        "review": repair_info["approval"], "reviewedCrop": ref(repaired_seam),
        "status": "passed", "explicitPerCropVerdict": True,
        "finding": "Root approved both exact native masks after viewing combined seam and all perimeters",
        "sourceLevelStatus": "approved_local_native_roi_adoption"})
    neighbors = additional_neighbors()
    fingerprint = hashlib.sha256(json.dumps(
        [(x["id"], x["sha256"]) for x in registry]).encode()).hexdigest()[:16]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    version = f"native-18-source-audit-{stamp}-{fingerprint}"
    candidate_dir, qa_dir = T / "candidate" / version, T / "qa" / version
    candidate_dir.mkdir(parents=True, exist_ok=False)
    qa_dir.mkdir(parents=True, exist_ok=False)
    output = candidate_dir / "candidate.png"
    p.save_png(output, image)
    owner_file = candidate_dir / "owner-index.png"
    p.save_png(owner_file, Image.fromarray(owner))
    assert np.array_equal(np.asarray(Image.open(output).convert("RGB")), arr)
    assert np.array_equal(np.asarray(Image.open(owner_file)), owner)
    p.write_json(candidate_dir / "source-registry.json",
                 {"tile": TILE, "sourceCount": 18, "baseSelectedCoreCount": 16, "sources": registry,
                  "ownerIndex": ref(owner_file), "sourceResampled": False,
                  "sourceRecolored": False, "repairOverlaysIncluded": True,
                  "approvedRepairs": repair_info})
    proof = {"candidate": ref(output), "ownerIndex": ref(owner_file),
             "sourceRegistry": ref(candidate_dir / "source-registry.json"),
             "status": "passed_exact_same_world_native_pixels",
             "provedPixels": proved, "nativeSources": 18,
             "approvedRepairPixels": 120413,
             "unownedPixels": 0, "nativePixelScale": 1,
             "savedCandidateAndOwnerIndexDecodedPixelsVerified": True,
             "sourceResampled": False, "sourceRecolored": False, "sourceBlended": False,
             "formalAccepted": False}
    p.write_json(candidate_dir / "native-pixel-proof.json", proof)
    crops = []
    def emit(name, pic, group, location):
        file = qa_dir / (name + ".png")
        p.save_png(file, pic)
        key = pixel_key(pic)
        old = catalog.get(key, [])
        statuses = {x["status"] for x in old}
        if not old:
            status = "pending"
        elif "needs_repair" in statuses:
            status = "needs_repair"
        elif "unpassed_source_issue_without_crop_verdict" in statuses:
            status = "unpassed_source_issue_without_crop_verdict"
        elif statuses == {"passed"}:
            status = "passed"
        else:
            status = "pending"
        crops.append(dict(ref(file), name=name, group=group, location=location,
                          pixelKey=key, nativePixelScale=1, sourceResampled=False,
                          actuallyViewed=False, reviewReusedByExactPixelIdentity=bool(old),
                          status=status, priorReviews=old))
    for seam in [1024, 2048, 3072]:
        for segment in range(4):
            x_box = [seam-160, segment*1024, seam+160, (segment+1)*1024]
            y_box = [segment*1024, seam-160, (segment+1)*1024, seam+160]
            emit(f"internal-x{seam}-segment{segment+1:02d}", image.crop(x_box),
                 "internal_segment", {"candidateLTRB": x_box})
            emit(f"internal-y{seam}-segment{segment+1:02d}", image.crop(y_box),
                 "internal_segment", {"candidateLTRB": y_box})
    for y in [1024, 2048, 3072]:
        for x in [1024, 2048, 3072]:
            box = [x-160, y-160, x+160, y+160]
            emit(f"internal-junction-x{x}-y{y}", image.crop(box),
                 "internal_junction", {"candidateLTRB": box})
    strip = Image.new("RGB", (4096, 320))
    strip.paste(north.crop((0, 3936, 4096, 4096)), (0, 0))
    strip.paste(image.crop((0, 0, 4096, 160)), (0, 160))
    for segment in range(4):
        box = [segment*1024, 0, (segment+1)*1024, 320]
        emit(f"north-segment{segment+1:02d}", strip.crop(box),
             "north_segment", {"combinedStripLTRB": box})
    for x in [1024, 2048, 3072]:
        box = [x-160, 0, x+160, 320]
        emit(f"north-junction{x}", strip.crop(box),
             "north_junction", {"combinedStripLTRB": box})
    assert len(crops) == 40
    counts = {status: sum(c["status"] == status for c in crops)
              for status in sorted({c["status"] for c in crops})}
    manifest = {"tile": TILE, "candidate": ref(output),
                "selectionSnapshotSha256": selection_sha, "selectionSnapshot": selection,
                "sourceRegistry": ref(candidate_dir / "source-registry.json"),
                "pixelProof": ref(candidate_dir / "native-pixel-proof.json"),
                "actualNorthNeighbor": ref(NORTH), "northNeighborTile": "r07_c04",
                "internalSeamSegments": 24, "internalJunctions": 9,
                "northSegments": 4, "northJunctions": 3, "cropCount": 40,
                "crops": crops, "reviewStatusCounts": counts,
                "sourceLevelIssues": source_issues, "additionalNeighbors": neighbors,
                "reusedReviews": sum(c["reviewReusedByExactPixelIdentity"] for c in crops),
                "actuallyViewedThisBuild": False, "fullTileInternalQAPassed": False,
                "formalAccepted": False, "repairOverlaysIncluded": True,
                "approvedRepairs": repair_info,
                "createdAtUtc": datetime.now(timezone.utc).isoformat()}
    p.write_json(qa_dir / "manifest.json", manifest)
    p.write_json(candidate_dir / "assembly.json",
                 {"tile": TILE, "output": ref(output), "nativeSources": registry,
                  "missingNativePatches": [], "qa": crops[:33],
                  "qaManifest": ref(qa_dir / "manifest.json"),
                  "ownerIndex": ref(owner_file), "pixelProof": proof,
                  "sourceResampled": False, "sourceUpscaled": False,
                  "sourceRecolored": False, "sourceBlended": False,
                  "baseSelectedCoreCount": 16, "nativeSourceCount": 18,
                  "repairOverlaysIncluded": True, "approvedRepairs": repair_info,
                  "formalAccepted": False})
    summary = {"status": "candidate_and_audit_ready_not_accepted",
               "candidate": ref(output), "candidateDirectory": str(candidate_dir),
               "qaManifest": str(qa_dir / "manifest.json"), "cropCount": 40,
               "provedPixels": proved, "statusCounts": counts,
               "reused": manifest["reusedReviews"], "formalAccepted": False}
    p.write_json(qa_dir / "build-summary.json", summary)
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-ready", action="store_true")
    args = parser.parse_args()
    if args.check_ready:
        selection, missing, extra = ready()
        result = {"ready": not missing and not extra, "selected": len(selection),
                  "missing": missing, "unexpectedKeys": extra}
    else:
        result = build()
    print(json.dumps(result, ensure_ascii=False))

