"""Create a NEW local eight-tile milestone package; never rewrite production inputs.

The 4096 PNG entries are copied byte-for-byte. Pillow only creates the explicitly
preview-only reduced mosaic. Existing review/provenance records remain unchanged.
Run with the bundled Python using -B to avoid writing import caches.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont

ZONE = Path(__file__).resolve().parent
SIX = ZONE / "joint-six-tile-review/ac2031be4f9bb37b/delivery-summary.json"
SEVENTH = ZONE / "r07_c04/delivery-summary.json"
EIGHTH = ZONE / "r05_c03/delivery-summary-20261012.json"
OUTPUT_ROOT = ZONE / "verified-eight-tiles-20261012"
documents = {}
checked_hashes = {}
source_rows = []
reference_diagnostics = []
review_checks = set()
legacy_review_links = []


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(reference, include=True):
    path = Path(reference["file"]).resolve()
    expected = reference["sha256"]
    key = str(path)
    if key not in checked_hashes:
        checked_hashes[key] = sha(path)
    require(checked_hashes[key] == expected, "Changed input: " + key)
    if include:
        relative = path.relative_to(ZONE).as_posix()
        documents[key] = {"path": path, "zipEntry": "evidence/" + relative,
                          "sha256": expected}
    return path


def ref(path):
    return {"file": str(Path(path).resolve()), "sha256": sha(path)}


def keep(path):
    return check(ref(path))


def record(reference):
    return read(check(reference))


def selected(tile, identifier):
    directory = ZONE / tile
    selection_path = directory / "selection.json"
    selection = read(keep(selection_path)) if selection_path.is_file() else {}
    value = Path(selection.get(identifier, str(directory / "native" / (identifier + ".png"))))
    path = value if value.is_absolute() else directory / value
    path.resolve().relative_to(directory.resolve())
    return path.resolve()


def source_check(source, tile, is_bridge=False):
    native = check(source, include=False)
    require(source.get("sourceResampled", False) is False, "Resampled native source")
    with Image.open(native) as image:
        require(image.size == (1254, 1254) and image.format == "PNG", "Wrong native PNG dimensions")
    generation_ref = source.get("generationRecord")
    if generation_ref is None:
        generation_ref = ref(native.with_suffix(".png.generation.json"))
    generation = record(generation_ref)
    require(generation["sha256"] == source["sha256"], "Generation record disagrees with native source")
    require([generation["width"], generation["height"]] == [1254, 1254], "Generation dimensions mismatch")
    require(generation["route"] in ("builtin", "builtin_image_gen"), "Unexpected generation route")
    require(not generation.get("resizedAfterGeneration", False) and not generation.get("finalArtUpscaled", False), "Changed generation pixels")
    host = generation.get("sourceHostFile", generation.get("evidence", {}).get("hostOutputPath"))
    check({"file": host, "sha256": source["sha256"]}, include=False)
    if is_bridge:
        for role in ("request", "receipt"):
            check(source[role])
        require(generation["sourceHostSha256"] == source["sha256"], "Bridge host record mismatch")
        require(generation["request"] == source["request"] and generation["toolReceipt"] == source["receipt"], "Bridge receipt mismatch")
        request = record(source["request"])
        for name in ("placement.json", "prompt.txt"):
            keep(native.parent / name)
    else:
        require(sha(selected(tile, source["id"])) == source["sha256"], "Current fixed selection changed")
        for role in ("request", "receipt", "prompt"):
            check(source[role])
        evidence = generation["evidence"]
        for role in ("request", "receipt", "prompt"):
            hash_field = role + "Sha256"
            if hash_field in evidence:
                require(evidence[hash_field] == source[role]["sha256"], "Generation evidence hash mismatch")
            path_value = generation.get("prompt") if role == "prompt" else evidence.get(role)
            if path_value:
                check({"file": path_value, "sha256": source[role]["sha256"]})
        request = record(source["request"])
    references = generation.get("references", request.get("references", []))
    for reference in references:
        path = Path(reference["file"])
        available = path.is_file()
        matches = available and sha(path) == reference["sha256"]
        reference_diagnostics.append({"tile": tile, "id": source["id"], "reference": reference,
                                      "available": available, "currentHashMatches": matches})
    source_rows.append({"tile": tile, "id": source["id"], "file": str(native),
                        "sha256": source["sha256"], "kind": "native_bridge" if is_bridge else "fixed_grid",
                        "currentSelectionMatches": True, "hostOutputMatchesExactly": True,
                        "generationRecord": generation_ref,
                        "request": source["request"], "receipt": source["receipt"],
                        **({"prompt": source["prompt"]} if "prompt" in source else {})})


def crop_ref(entry):
    return entry.get("reference", entry)


def review_entry(entry, stack=()):
    reference = crop_ref(entry)
    check(reference)
    verdict = entry.get("verdict", entry.get("status", entry.get("visualVerdict", "")))
    require(verdict.startswith("passed") or verdict in ("pass_no_blocking_geometry", "pass_at_requested_threshold", "nonblocking"), "Nonpassed reviewed crop")
    inherited = entry.get("inheritedFrom")
    if inherited:
        report_reference = "report" not in inherited and Path(inherited.get("file", "")).suffix.lower() == ".json"
        report_path = inherited["file"] if report_reference else inherited["report"]
        report_hash = inherited["sha256"] if report_reference else inherited.get("reportSha256", inherited.get("reportSHA256"))
        if report_hash is None:
            report_hash = sha(report_path)
            legacy_review_links.append({"report": report_path, "currentReportSha256": report_hash,
                                        "note": "Historical link records crop hash and report path but no report hash. Existing report and matching crop are validated and packaged unchanged."})
        old_report = record({"file": report_path, "sha256": report_hash})
        crop_hash = reference["sha256"] if report_reference else inherited.get("cropSha256", inherited.get("cropSHA256", inherited.get("sha256")))
        require(crop_hash == reference["sha256"], "Inherited crop is not identical")
        if "file" in inherited and not report_reference:
            check(inherited)
        key = (report_path, crop_hash)
        require(key not in stack, "Review inheritance cycle")
        old_entries = old_report.get("entries", old_report.get("items"))
        require(old_entries is not None, "Legacy review schema needs entry mapping: " + report_path)
        matches = [old for old in old_entries if crop_ref(old)["sha256"] == crop_hash]
        require(matches, "Inherited crop absent from earlier review")
        same_name = [old for old in matches if old.get("name", old.get("id")) == entry.get("name", entry.get("id"))]
        review_entry((same_name or matches)[0], stack + (key,))
    else:
        require(entry.get("actuallyViewed") is True, "Crop lacks actual or inherited visual review")
    review_checks.add((reference["file"], reference["sha256"]))


def review_report(reference, candidate_hash=None, expected_entries=None):
    report = record(reference)
    require(report.get("blockingCount", 0) == 0, "Blocking current QA report")
    if candidate_hash is not None:
        require(report["candidate"]["sha256"] == candidate_hash, "Review binds another candidate")
    if expected_entries is not None:
        require(len(report["entries"]) == expected_entries, "Incomplete review entry count")
    for entry in report["entries"]:
        review_entry(entry)
    return report


def qa_covered(manifest, report_entries):
    covered = {crop_ref(entry)["sha256"] for entry in report_entries}
    for item in manifest.get("qa", []) + manifest.get("bridgeBoundaryQa", []):
        check(item)
        require(item["sha256"] in covered, "Assembly QA crop has no passed review")


def write_new(path, value):
    require(not path.exists(), "Refusing to replace package output: " + str(path))
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    protected_paths = [SIX, SIX.parent / "source-audit.json", SIX.parent / "northwest-six-4k-tiles.zip"]
    protected_before = {str(path): sha(path) for path in protected_paths}
    six = read(keep(SIX)); seventh = read(keep(SEVENTH)); eighth = read(keep(EIGHTH))
    require(six["tileCount"] == 6 and six["blockingCount"] == 0 and not six["formalAccepted"] and not six["wholeZoneComplete"], "Invalid six milestone")
    audit = record(six["sourceAudit"])
    require(audit["nativeSourceCount"] == 96 and audit["allHostOutputsExact"] and not audit["nativePixelIssues"], "Invalid six source audit")
    first_four = record(six["firstFourReview"])
    require(first_four["blockingCount"] == 0 and first_four["currentJointTileCount"] == 4, "Invalid first four review")
    require(first_four["nativePixelProvenance"]["status"] == "passed"
            and first_four["nativePixelProvenance"]["pixelsVerified"] == 4 * 4096 * 4096
            and first_four["tileCropsVerified"] == 4, "Incomplete first four pixel proof")
    first_manifest = record(first_four["assemblyManifest"])
    check(first_four["jointImage"], include=False)
    for report in first_four["reviewReports"]:
        review_report(report)
    for entry in first_four["entries"]:
        review_entry(entry)
    qa_covered(first_manifest, first_four["entries"])
    for source in first_manifest["nativeSources"]:
        source_check(source, source["tile"])
    manifests = []
    for tile, manifest_path in [("r05_c06", ZONE / "r05_c06/candidate/r05_c06-candidate-minimum-error-03d4dd9f7332.assembly.json"),
                                ("r06_c06", ZONE / "r06_c06/candidate/r06_c06-candidate-hard-077556c4fb59.assembly.json")]:
        manifest = read(keep(manifest_path)); manifests.append(manifest)
        for source in manifest["nativeSources"]:
            source_check(source, tile)
        reports = [reference for reference in six["newInternalReviews"] if tile in reference["file"]]
        entries = []
        for report in reports:
            entries += review_report(report, manifest["output"]["sha256"])["entries"]
        require(len({crop_ref(entry)["sha256"] for entry in entries}) == 33, "Incomplete tile internal QA")
        qa_covered(manifest, entries)
    require({(source["tile"], source["id"], source["sha256"]) for source in audit["sources"]}
            == {(source["tile"], source["id"], source["sha256"]) for source in source_rows}, "Six source audit mismatch")
    for source in audit["sources"]:
        check(source, include=False); check(source["generationRecord"])
    boundary = review_report(six["newBoundaryReview"], expected_entries=22)
    require({(item["tile"], item["sha256"]) for item in boundary["sources"]}
            == {(item["tile"], item["sha256"]) for item in six["tiles"]}, "Six boundary binds changed tiles")
    for reference in six["pixelEvidence"]:
        proof = record(reference)
        if "r05_c06" in reference["file"]:
            require(proof["passed"] and proof["verifiedPixels"] == 4096 * 4096
                    and proof["unmatchedPixels"] == 0 and proof["sameWorldCoordinate"], "Invalid r05_c06 pixel proof")
            require(proof["candidate"]["sha256"] == manifests[0]["output"]["sha256"], "Proof candidate mismatch")
        elif "r06_c06" in reference["file"]:
            require(proof["allOutputPixelsVerified"] and proof["verifiedExactNativePixels"] == 4096 * 4096, "Invalid r06_c06 pixel proof")
            require(proof["candidate"]["sha256"] == manifests[1]["output"]["sha256"], "Proof candidate mismatch")
    tiles = [dict(item) for item in six["tiles"]]
    for delivery, tile in [(seventh, "r07_c04"), (eighth, "r05_c03")]:
        require(delivery["tile"] == tile and delivery["internalQA"]["status"] == "passed"
                and delivery["internalQA"]["actuallyViewed"] and not delivery["formalAccepted"], "New tile is not verified")
        require([delivery["internalQA"]["seamSegments"], delivery["internalQA"]["junctions"]] == [24, 9], "Incomplete internal QA")
        manifest = record(delivery["assemblyManifest"])
        require(manifest["output"]["sha256"] == delivery["candidate"]["sha256"], "Candidate/manifest mismatch")
        expected = 19 if tile == "r07_c04" else 16
        require(len(manifest["nativeSources"]) == expected, "Wrong source count")
        for index, source in enumerate(manifest["nativeSources"]):
            source_check(source, tile, is_bridge=index >= 16)
        if tile == "r07_c04":
            config = record(delivery["config"])
            require([item["id"] for item in config["bridges"]] == [item["id"] for item in manifest["nativeSources"][16:]], "Current bridge selection mismatch")
            require(delivery["bridgeSources"] == manifest["nativeSources"][16:], "Bridge delivery records mismatch")
            for reference in (manifest["baseManifest"], manifest["script"], manifest["dependency"], manifest["sourceIndex"], delivery["evidence"]["eastUnchanged"]):
                check(reference)
            proof = manifest["pixelProof"]
            require(proof == delivery["pixelProof"] and proof["status"] == "passed"
                    and proof["checkedPixels"] == 4096 * 4096
                    and proof["allPixelsUnmodifiedNativeSamplesAtExactWorldCoordinates"]
                    and sum(proof["countsBySource"].values()) == 4096 * 4096, "Invalid bridge pixel proof")
        else:
            proof = record(delivery["pixelProof"])
            require(proof["allOutputPixelsVerified"] and proof["verifiedExactNativePixels"] == 4096 * 4096
                    and not proof["resampled"] and not proof["blended"] and not proof["recolored"], "Invalid eighth pixel proof")
            require(proof["candidate"]["sha256"] == delivery["candidate"]["sha256"], "Eighth pixel proof candidate mismatch")
        internal = review_report(delivery["evidence"]["internal"], delivery["candidate"]["sha256"], 47 if tile == "r07_c04" else 33)
        qa_covered(manifest, internal["entries"])
        external = review_report(delivery["evidence"]["external"], delivery["candidate"]["sha256"], 4 if tile == "r07_c04" else 7)
        if tile == "r07_c04":
            require(external["north"]["status"] == "passed", "North boundary not passed")
            north_hash = next(item["sha256"] for item in six["tiles"] if item["tile"] == "r06_c04")
            require(all(entry["north"]["sha256"] == north_hash for entry in external["entries"]), "North neighbor changed")
        else:
            require(external["status"] == "passed" and external["neighbor"]["sha256"]
                    == next(item["sha256"] for item in six["tiles"] if item["tile"] == "r05_c04"), "Eighth east neighbor changed")
        tiles.append({"tile": tile, **delivery["candidate"]})
    require(len(source_rows) == 131 and len({(item["tile"], item["id"]) for item in source_rows}) == 131, "Expected 131 unique native sources")
    tiles.sort(key=lambda item: item["tile"])
    for tile in tiles:
        check(tile, include=False)
        with Image.open(tile["file"]) as image:
            require(image.format == "PNG" and image.size == (4096, 4096), "Invalid 4096 delivery")
        row, column = int(tile["tile"][1:3]), int(tile["tile"][5:7])
        tile.update({"tileWorldBox": [(column - 1) * 4096, (row - 1) * 4096, column * 4096, row * 4096],
                     "zipEntry": "tiles/" + tile["tile"] + "-4096.png", "productionBytesUnmodified": True})
    identity = hashlib.sha256(json.dumps([(item["tile"], item["sha256"]) for item in tiles]).encode()).hexdigest()[:16]
    destination = OUTPUT_ROOT / identity
    require(not destination.exists(), "Package directory already exists; refusing to replace it: " + str(destination))
    destination.mkdir(parents=True)
    created = now()
    source_validation = {"createdAtUtc": created, "status": "passed", "nativeSourceCount": 131,
                         "fixedGridSourceCount": 128, "additionalNativeBridgeCount": 3,
                         "allCurrentSelectionsMatch": True, "allHostOutputHashesMatch": True,
                         "generationEvidenceHashesVerified": True, "nativePNGDimensions": [1254, 1254],
                         "reviewCropRecordsVerified": len(review_checks), "sources": source_rows,
                         "legacyReviewLinksWithoutRecordedReportHash": legacy_review_links,
                         "historicalReferenceDiagnostics": reference_diagnostics,
                         "historicalReferenceMismatchCount": sum(not item["currentHashMatches"] for item in reference_diagnostics)}
    validation_path = destination / "source-validation.json"; write_new(validation_path, source_validation)
    preview = Image.new("RGB", (2048, 1624), "#20252b")
    draw = ImageDraw.Draw(preview)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
    draw.text((18, 8), "PREVIEW ONLY | 8 verified tiles | original tiles: 4096 x 4096", font=font, fill="white")
    available = {item["tile"] for item in tiles}
    for row in range(5, 8):
        for column in range(3, 7):
            name = f"r{row:02d}_c{column:02d}"
            xy = ((column - 3) * 512, 48 + (row - 5) * 512)
            if name not in available:
                draw.rectangle((xy[0], xy[1], xy[0] + 511, xy[1] + 511), fill="#30373f", outline="#59616b")
                draw.text((xy[0] + 24, xy[1] + 240), name + " | PENDING", font=font, fill="#a9b1ba")
    for tile in tiles:
        row, column = int(tile["tile"][1:3]), int(tile["tile"][5:7])
        xy = ((column - 3) * 512, 48 + (row - 5) * 512)
        with Image.open(tile["file"]) as image:
            preview.paste(image.resize((512, 512), Image.Resampling.LANCZOS), xy)
        draw.rectangle((xy[0], xy[1] + 476, xy[0] + 155, xy[1] + 511), fill="#20252b")
        draw.text((xy[0] + 10, xy[1] + 478), tile["tile"], font=font, fill="white")
    draw.text((18, 1586), "Reduced presentation mosaic. Whole northwest zone remains incomplete; formal acceptance is pending.", font=font, fill="white")
    preview_path = destination / "preview-only-mosaic-2048.png"; preview.save(preview_path)
    summary = {"schemaVersion": 1, "createdAtUtc": created,
               "status": "eight_contiguous_tiles_internal_and_shared_boundaries_passed",
               "tileCount": 8, "tiles": tiles, "tilePixels": [4096, 4096],
               "boundingTileGrid": [4, 3], "boundingGridContainsMissingTiles": True,
               "artWorldBox": [8192, 16384, 24576, 28672], "ownedZoneTileCount": 60,
               "wholeZoneComplete": False, "formalAccepted": False, "blockingCount": 0,
               "nativeSourceCount": 131, "fixedGridSourceCount": 128, "additionalNativeBridgeCount": 3,
               "verifiedNativeOutputPixels": 8 * 4096 * 4096, "productionResampled": False,
               "productionPNGBytesUnmodified": True, "actualModel": None, "actualQuality": None,
               "runtimeIntegration": False, "capacity5000Validated": False,
               "sourceValidation": ref(validation_path), "existingSixDelivery": ref(SIX),
               "seventhDelivery": ref(SEVENTH), "eighthDelivery": ref(EIGHTH),
               "preview": {**ref(preview_path), "previewOnly": True, "productionArt": False,
                           "pixels": [2048, 1624], "tileDisplayPixels": [512, 512]},
               "outerPerimeterStatus": "Unfinished or unreviewed neighboring tiles remain; no whole-zone acceptance.",
               "archiveIncludesNativeOriginalPNGs": False,
               "nativeOriginalsPolicy": "Original 1254 PNGs stay at recorded local paths; their validated hashes and generation/request/receipt records are included.",
               "preservedExistingSixPackage": {"file": str(protected_paths[2]), "sha256": protected_before[str(protected_paths[2])]}}
    summary_path = destination / "delivery-summary.json"; write_new(summary_path, summary)
    readme = destination / "DELIVERY.txt"
    readme.write_text("LOCAL EIGHT-TILE MILESTONE\n8 exact 4096x4096 PNG files; 131 validated native sources (128 fixed + 3 bridges).\n"
                      "Internal and shared available boundary QA passed. Original delivery PNG bytes are unchanged.\n"
                      "The mosaic is a reduced PREVIEW ONLY; gray cells are missing from this milestone.\n"
                      "Whole northwest zone is incomplete. Formal acceptance, runtime integration and capacity validation remain false.\n"
                      "Original 1254 PNGs remain at the recorded local paths. Their provenance records and existing QA evidence are included.\n"
                      "Use package-contents.json to map original evidence paths to archive entries and verify every file hash.\n", encoding="utf-8")
    keep(__file__)
    files = [(Path(item["file"]), item["zipEntry"], item["sha256"]) for item in tiles]
    files += [(item["path"], item["zipEntry"], item["sha256"]) for item in documents.values()]
    files += [(path, path.name, sha(path)) for path in (summary_path, validation_path, preview_path, readme)]
    require(len({name for _, name, _ in files}) == len(files), "Duplicate ZIP entry")
    contents_path = destination / "package-contents.json"
    write_new(contents_path, {"schemaVersion": 1, "files": [{"originalFile": str(path), "zipEntry": name, "sha256": digest} for path, name, digest in files]})
    files.append((contents_path, contents_path.name, sha(contents_path)))
    archive_path = destination / "northwest-eight-4k-tiles.zip"
    with zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for path, name, digest in files:
            require(sha(path) == digest, "Input changed while packaging: " + str(path))
            archive.write(path, name)
    with zipfile.ZipFile(archive_path) as archive:
        require(archive.testzip() is None, "ZIP CRC failure")
        require(len(archive.infolist()) == len(files), "ZIP count mismatch")
        for _, name, digest in files:
            with archive.open(name) as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            require(actual == digest, "ZIP entry changed: " + name)
    protected_after = {str(path): sha(path) for path in protected_paths}
    require(protected_before == protected_after, "Existing six package was changed")
    package = {"createdAtUtc": now(), **ref(archive_path), "sizeBytes": archive_path.stat().st_size,
               "verifiedZipEntries": len(files), "verifiedProductionTileEntries": 8, "verifiedNativeSources": 131,
               "allZipEntryHashesVerified": True, "existingSixDeliveryPreserved": True,
               "wholeZoneComplete": False, "formalAccepted": False, "summary": ref(summary_path),
               "preview": ref(preview_path), "sourceValidation": ref(validation_path), "packageContents": ref(contents_path)}
    write_new(destination / "package.json", package)
    print(json.dumps(package, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
