"""Extend the immutable eight-tile delivery with reviewed r05_c07.

All production and evidence files are stored byte-for-byte. Only the expressly
preview-only mosaic is resized. Writes are restricted to the NEW nine package.
Run with bundled Python -B. The previous package and production inputs are never
modified. No generation, network, backend assumptions or progress edits occur.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ZONE = Path(__file__).resolve().parent
OLD = ZONE / "verified-eight-tiles-20261012/34b29d9d5291760f"
TILE = ZONE / "r05_c07"
QA = TILE / "qa/r05_c07-candidate-localcut-e280bcf6d4f6"
OUTPUT = ZONE / "verified-nine-tiles-20261012"
checked = {}
additions = {}


def now():
    return datetime.now(timezone.utc).isoformat()


def require(test, message):
    if not test:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def ref(path):
    return {"file": str(Path(path).resolve()), "sha256": sha(path)}


def check(reference):
    path = Path(reference["file"]).resolve()
    actual = sha(path)
    require(actual == reference["sha256"], "Changed input: " + str(path))
    checked[str(path)] = actual
    return path


def keep(reference, entry=None):
    if isinstance(reference, (Path, str)):
        reference = ref(reference)
    path = check(reference)
    if entry is None:
        entry = "evidence/" + path.relative_to(ZONE).as_posix()
    require(entry not in additions or additions[entry][1] == reference["sha256"], "Conflicting addition: " + entry)
    additions[entry] = (path, reference["sha256"])
    return path


def record(reference):
    return read(keep(reference))


def write_new(path, value):
    require(not path.exists(), "Refusing to replace output: " + str(path))
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")


def linked_evidence(value):
    """Include hash-bound QA/candidate dependencies inside r05_c07 only.

    Historical image references may point to altered old guides or shared art;
    those are diagnosed by source validation, not silently required as current.
    """
    if isinstance(value, dict):
        if isinstance(value.get("file"), str) and value.get("sha256"):
            path = Path(value["file"]).resolve()
            if path.is_relative_to(TILE.resolve()) and any(part in ("qa", "candidate") for part in path.parts):
                keep(value)
        for child in value.values():
            linked_evidence(child)
    elif isinstance(value, list):
        for child in value:
            linked_evidence(child)


def validate_ninth(delivery, prior_tiles, destination):
    require(delivery["tile"] == "r05_c07" and delivery["selectedNativeCount"] == 16
            and delivery["internallyReviewed4kCandidateCount"] == 1
            and delivery["formalAcceptedCount"] == 0 and not delivery["formalAccepted"]
            and not delivery["zoneComplete"] and not delivery["unresolvedInternalBlockers"], "Invalid ninth delivery")
    review = record(delivery["qaEvidence"])
    acceptance = record(delivery["acceptance"])
    manifest = record(review["assemblyManifest"])
    require(manifest["output"] == delivery["candidate"], "Ninth candidate/assembly mismatch")
    require(acceptance["candidate"]["sha256"] == delivery["candidate"]["sha256"]
            and acceptance["internalQA"]["status"] == "passed" and not acceptance["formalAccepted"], "Wrong acceptance binding")
    require([manifest["nativePixels"], manifest["corePixels"], manifest["haloPixels"]]
            == [[1254, 1254], 1024, 115] and not manifest["sourceResampled"]
            and not manifest["sourceUpscaled"] and not manifest["colorMatching"]
            and not manifest["opticalFlow"] and not manifest["feathering"], "Invalid native assembly geometry")
    internal = review["internalQA"]
    require(internal["status"] == "passed" and internal["actuallyViewed"]
            and internal["allFinalCropsViewedAtOriginalDetail"]
            and [internal["seamSegments"], internal["junctions"]] == [24, 9]
            and len(internal["crops"]) == 33, "Incomplete ninth native review")
    require(not review["unresolvedInternalBlockers"], "Unresolved ninth internal blocker")
    candidate_path = keep(delivery["candidate"], "tiles/r05_c07-4096.png")
    with Image.open(candidate_path) as image:
        require(image.format == "PNG" and image.size == (4096, 4096) and image.mode == "RGB", "Wrong ninth PNG")
        candidate = np.asarray(image).copy()
        for crop in internal["crops"]:
            require(crop["actuallyViewed"] and crop["visualVerdict"] == "passed"
                    and crop["viewDetail"] == "original" and crop["nativePixelScale"] == 1
                    and not crop["sourceResampled"] and crop["derivedFrom"]["sha256"] == delivery["candidate"]["sha256"], "Nonpassed ninth crop")
            expected = image.crop(crop["cropLTRB"])
            if crop.get("rotationCCW90"):
                expected = expected.transpose(Image.Transpose.ROTATE_90)
            with Image.open(keep(crop)) as actual:
                require(np.array_equal(np.asarray(actual), np.asarray(expected)), "QA crop is not exact current candidate pixels")
    require({item["sha256"] for item in manifest["qa"]} == {item["sha256"] for item in internal["crops"]}, "Assembly QA coverage mismatch")
    selection = read(keep(TILE / "selection.json"))
    rows = []
    diagnostics = []
    source_arrays = []
    for index, source in enumerate(manifest["nativeSources"], 1):
        identifier = f"s{(index - 1) // 4 + 1:02d}_{(index - 1) % 4 + 1:02d}"
        require(source["id"] == identifier and source["sha256"] == delivery["selectedSources"][identifier]["sha256"], "Wrong native source order")
        selected = Path(selection.get(identifier, "native/" + identifier + ".png"))
        if not selected.is_absolute():
            selected = TILE / selected
        require(selected.resolve() == Path(source["file"]).resolve(), "Selection path mismatch")
        native = keep(source, "native/r05_c07/" + Path(source["file"]).name)
        with Image.open(native) as image:
            require(image.format == "PNG" and image.size == (1254, 1254), "Wrong native PNG")
            if "A" in image.getbands():
                require(image.getchannel("A").getextrema() == (255, 255), "Transparent native pixels")
            source_arrays.append(np.asarray(image.convert("RGB")).copy())
        generation = record(source["generationRecord"])
        require(generation["sha256"] == source["sha256"]
                and [generation["width"], generation["height"]] == [1254, 1254]
                and generation["route"] in ("builtin", "builtin_image_gen")
                and generation["actualModel"] is None and generation["actualQuality"] is None
                and not generation["resizedAfterGeneration"] and not generation["finalArtUpscaled"], "Invalid native generation record")
        host = generation.get("sourceHostFile", generation["evidence"].get("hostOutputPath"))
        check({"file": host, "sha256": source["sha256"]})
        for role in ("prompt", "request", "receipt"):
            keep(source[role])
            expected = generation["evidence"].get(role + "Sha256")
            if expected:
                require(expected == source[role]["sha256"], "Generation evidence hash mismatch")
        tool_path = TILE / "receipts" / (native.stem + ".tool.json")
        tool_record = ref(keep(tool_path)) if tool_path.is_file() else None
        for reference in generation.get("references", []):
            path = Path(reference["file"])
            available = path.is_file()
            matches = available and sha(path) == reference["sha256"]
            diagnostics.append({"id": identifier, "reference": reference,
                                "available": available, "currentHashMatches": matches})
            if matches and path.resolve().is_relative_to(TILE.resolve()):
                keep(reference)
        rows.append({"tile": "r05_c07", **source, "zipEntry": "native/r05_c07/" + native.name,
                     "currentSelectionMatches": True, "hostOutputMatchesExactly": True,
                     "toolRecord": tool_record})
    require(len(rows) == 16, "Not sixteen native sources")
    source_map_path = keep(manifest["sourceMap"])
    with Image.open(source_map_path) as image:
        require(image.mode == "L" and image.size == (4096, 4096), "Wrong source map")
        source_map = np.asarray(image).copy()
    require(set(np.unique(source_map)) == set(range(1, 17)), "Wrong source map IDs")
    counts = {}
    for index, (source, native) in enumerate(zip(manifest["nativeSources"], source_arrays), 1):
        yy, xx = np.nonzero(source_map == index)
        ox = (source["column"] - 1) * 1024 - 115
        oy = (source["row"] - 1) * 1024 - 115
        sx, sy = xx - ox, yy - oy
        require(sx.min() >= 0 and sy.min() >= 0 and sx.max() < 1254 and sy.max() < 1254, "Source sample leaves halo")
        require(np.array_equal(candidate[yy, xx], native[sy, sx]), "Changed nonnative output pixels")
        counts[source["id"]] = len(xx)
    require(sum(counts.values()) == 4096 * 4096, "Incomplete ninth pixel proof")
    external = review["externalQA"]
    require(external["status"] == "partial_passed" and external["actuallyViewed"]
            and external["reviewedSides"] == ["west"]
            and external["pendingSides"] == ["north", "east", "south"]
            and [external["nativeSegments"], external["boundaryJunctions"]] == [4, 3]
            and len(external["crops"]) == 7, "Wrong ninth boundary scope")
    west = next(item for item in prior_tiles if item["tile"] == "r05_c06")
    old_boundary_diagnostics = []
    with Image.open(check(west)) as left_image, Image.open(candidate_path) as right_image:
        join = Image.new("RGB", (320, 4096))
        join.paste(left_image.crop((3936, 0, 4096, 4096)), (0, 0))
        join.paste(right_image.crop((0, 0, 160, 4096)), (160, 0))
        for crop in external["crops"]:
            require(crop["actuallyViewed"] and crop["visualVerdict"] == "passed"
                    and crop["viewDetail"] == "original", "Unreviewed ninth west crop")
            path = keep(crop)
            if "segment" in path.stem:
                segment = int(path.stem[-2:])
                expected = join.crop((0, (segment - 1) * 1024, 320, segment * 1024))
            else:
                y = int(path.stem.split("-y")[-1])
                expected = join.crop((0, y - 160, 320, y + 160))
            with Image.open(path) as actual:
                a, e = np.asarray(actual), np.asarray(expected)
                require(np.array_equal(a[:, 160:], e[:, 160:]), "Historical west crop changed ninth half")
                changed = int(np.count_nonzero(np.any(a[:, :160] != e[:, :160], axis=2)))
                old_boundary_diagnostics.append({"historicalCrop": crop, "changedWestNeighborPixels": changed,
                    "ninthHalfUnchanged": True, "note": "Historical west neighbor half used native hard cores; actual minimum-error delivery boundary freshly reviewed below."})
        boundary_path = destination / "actual-west-boundary/visual-review.json"
        boundary = read(keep(boundary_path, "actual-west-boundary/visual-review.json"))
        require(boundary["status"] == "passed" and boundary["actuallyViewed"] and boundary["blockingCount"] == 0
                and boundary["candidate"]["sha256"] == delivery["candidate"]["sha256"]
                and boundary["neighbor"]["sha256"] == west["sha256"] and len(boundary["entries"]) == 7
                and [boundary["seamSegments"], boundary["junctions"]] == [4, 3]
                and not boundary["formalAccepted"], "Invalid actual packaged boundary review")
        keep(boundary["manifest"], "actual-west-boundary/manifest.json")
        for crop in boundary["entries"]:
            require(crop["actuallyViewed"] and crop["visualVerdict"] == "passed"
                    and crop["viewDetail"] == "original" and crop["nativePixelScale"] == 1
                    and not crop["sourceResampled"], "Unreviewed actual packaged boundary crop")
            path = keep(crop, "actual-west-boundary/" + Path(crop["file"]).name)
            with Image.open(path) as actual:
                require(np.array_equal(np.asarray(actual), np.asarray(join.crop(crop["joinCropLTRB"]))), "Actual boundary crop identity mismatch")
        independent_path = destination / "actual-west-boundary/independent-review.json"
        independent_reference = None
        independent_status = "pending_optional_review"
        if independent_path.exists():
            independent = read(keep(independent_path, "actual-west-boundary/independent-review.json"))
            require(independent["status"] == "passed" and independent["actuallyViewed"]
                    and independent["candidate"]["sha256"] == delivery["candidate"]["sha256"]
                    and independent["neighbor"]["sha256"] == west["sha256"]
                    and len(independent["entries"]) == 7 and not independent["formalAccepted"], "Independent actual boundary review failed")
            require({item["sha256"] for item in independent["entries"]}
                    == {item["sha256"] for item in boundary["entries"]}, "Independent actual boundary crop coverage mismatch")
            require(all(item["actuallyViewed"] and item["viewDetail"] == "original"
                        and item["visualVerdict"] == "passed" for item in independent["entries"]),
                    "Independent actual boundary report lacks full original-detail passed coverage")
            independent_reference = ref(independent_path)
            independent_status = "passed"
    for doc in (delivery, review, manifest):
        linked_evidence(doc)
    keep(QA / "current-evidence-validation.json")
    keep(candidate_path.with_suffix(".png.derivation.json"))
    keep(TILE / "qa/second-review-20261012/second-review-report.json")
    for directory in (TILE / "qa/second-review-20261012/final-e280bcf6d4f6",):
        for path in sorted(directory.iterdir()):
            if path.is_file():
                keep(path)
    # Prior review records/crops establish the 23 byte-identical inherited reviews.
    prior_review = read(TILE / "qa/second-review-20261012/second-review-report.json")
    linked_evidence(prior_review)
    child_dir = TILE / "qa/second-review-20261012/west-boundary"
    if child_dir.is_dir():
        for path in sorted(child_dir.rglob("*.json")):
            keep(path)
            linked_evidence(read(path))
    return rows, diagnostics, {"createdAtUtc": now(), "status": "passed",
        "candidate": delivery["candidate"], "sourceMap": manifest["sourceMap"],
        "checkedPixels": 4096 * 4096, "countsBySource": counts,
        "allPixelsUnmodifiedNativeSamplesAtExactWorldCoordinates": True,
        "nativePNGDimensions": [1254, 1254], "corePixels": 1024, "haloPixels": 115,
        "resampled": False, "blended": False, "warped": False, "recolored": False,
        "qaCurrentCandidateExactCropCount": 33,
        "actualPackagedWestNeighbor": west,
        "westNativeExactCropCount": 7, "actualPackagedWestBoundaryReview": ref(boundary_path),
        "independentActualPackagedWestBoundaryReview": independent_reference,
        "independentActualPackagedWestBoundaryStatus": independent_status,
        "historicalWestCropDifferenceDiagnostics": old_boundary_diagnostics, "formalAccepted": False}


def main():
    old_package = read(OLD / "package.json")
    old_archive = check(old_package)
    old_summary = read(check(old_package["summary"]))
    old_validation = read(check(old_package["sourceValidation"]))
    old_contents_path = check(old_package["packageContents"])
    old_contents = read(old_contents_path)
    require(old_summary["tileCount"] == 8 and old_summary["ownedZoneTileCount"] == 60
            and not old_summary["wholeZoneComplete"] and not old_summary["formalAccepted"]
            and old_summary["blockingCount"] == 0, "Invalid preserved eight package")
    require(old_validation["nativeSourceCount"] == 131 and old_validation["allHostOutputHashesMatch"], "Wrong preserved source audit")
    for source in old_validation["sources"]:
        native = check(source)
        with Image.open(native) as image:
            require(image.format == "PNG" and image.size == (1254, 1254), "Changed inherited native dimensions")
        generation = read(check(source["generationRecord"]))
        require(generation["sha256"] == source["sha256"] and not generation.get("resizedAfterGeneration", False)
                and not generation.get("finalArtUpscaled", False), "Changed inherited generation record")
        host = generation.get("sourceHostFile", generation.get("evidence", {}).get("hostOutputPath"))
        check({"file": host, "sha256": source["sha256"]})
        if source["kind"] == "fixed_grid":
            tile_path = ZONE / source["tile"]
            selection_path = tile_path / "selection.json"
            selection = read(check(ref(selection_path))) if selection_path.exists() else {}
            selected = Path(selection.get(source["id"], "native/" + source["id"] + ".png"))
            if not selected.is_absolute():
                selected = tile_path / selected
            require(selected.resolve() == native, "Changed inherited fixed selection")
    old_files = list(old_contents["files"]) + [{"originalFile": str(old_contents_path),
        "zipEntry": "package-contents.json", "sha256": old_package["packageContents"]["sha256"]}]
    require(len(old_files) == old_package["verifiedZipEntries"] == 1393, "Wrong eight archive inventory")
    with zipfile.ZipFile(old_archive) as archive:
        require(archive.testzip() is None, "Existing eight archive CRC failure")
        require(set(archive.namelist()) == {item["zipEntry"] for item in old_files}, "Eight archive inventory disagreement")
        for item in old_files:
            check({"file": item["originalFile"], "sha256": item["sha256"]})
            with archive.open(item["zipEntry"]) as stream:
                require(hashlib.file_digest(stream, "sha256").hexdigest() == item["sha256"], "Eight archive entry mismatch")
    delivery_path = keep(QA / "delivery-summary.json")
    delivery = read(delivery_path)
    tiles = [dict(item) for item in old_summary["tiles"]]
    tiles.append({"tile": "r05_c07", **delivery["candidate"], "tileWorldBox": [24576, 16384, 28672, 20480],
                  "zipEntry": "tiles/r05_c07-4096.png", "productionBytesUnmodified": True})
    tiles.sort(key=lambda item: item["tile"])
    identity = hashlib.sha256(json.dumps([(item["tile"], item["sha256"]) for item in tiles]).encode()).hexdigest()[:16]
    destination = OUTPUT / identity
    if destination.exists():
        require({path.name for path in destination.iterdir()} == {"actual-west-boundary"}, "Refusing to replace existing nine package outputs")
    else:
        destination.mkdir(parents=True)
    rows, diagnostics, proof = validate_ninth(delivery, old_summary["tiles"], destination)
    created = now()
    proof_path = destination / "r05_c07-native-pixel-proof.json"
    write_new(proof_path, proof)
    validation_path = destination / "source-validation.json"
    write_new(validation_path, {"createdAtUtc": created, "status": "passed", "nativeSourceCount": 147,
        "fixedGridSourceCount": 144, "additionalNativeBridgeCount": 3,
        "newNativeSourcesArchived": 16, "previousNativeSourcesReferenced": 131,
        "previousSources": old_validation["sources"], "newSources": rows,
        "allNewCurrentSelectionsMatch": True, "allNewHostOutputHashesMatch": True,
        "allPriorNativeHashesAndHostOutputsFreshlyRechecked": True,
        "allPriorFixedSelectionsFreshlyRechecked": True,
        "generationEvidenceHashesVerified": True, "nativePNGDimensions": [1254, 1254],
        "ninthHistoricalReferenceDiagnostics": diagnostics,
        "historicalReferenceMismatchCount": sum(not item["currentHashMatches"] for item in diagnostics),
        "preservedEightSourceValidation": old_package["sourceValidation"],
        "priorNativePixelProof": "Unmodified hash-validated evidence inherited from verified eight archive; new ninth proof rerun during this package creation."})
    preview = Image.new("RGB", (2560, 1624), "#20252b")
    draw = ImageDraw.Draw(preview)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
    draw.text((18, 8), "PREVIEW ONLY | 9 reviewed tiles | original tiles: 4096 x 4096", font=font, fill="white")
    available = {item["tile"] for item in tiles}
    for row in range(5, 8):
        for column in range(3, 8):
            name = f"r{row:02d}_c{column:02d}"
            xy = ((column - 3) * 512, 48 + (row - 5) * 512)
            if name not in available:
                draw.rectangle((xy[0], xy[1], xy[0] + 511, xy[1] + 511), fill="#30373f", outline="#59616b")
                draw.text((xy[0] + 24, xy[1] + 240), name + " | PENDING", font=font, fill="#a9b1ba")
    for tile in tiles:
        row, column = int(tile["tile"][1:3]), int(tile["tile"][5:7])
        xy = ((column - 3) * 512, 48 + (row - 5) * 512)
        with Image.open(check(tile)) as image:
            require(image.format == "PNG" and image.size == (4096, 4096), "Wrong production tile")
            preview.paste(image.resize((512, 512), Image.Resampling.LANCZOS), xy)
        draw.rectangle((xy[0], xy[1] + 476, xy[0] + 155, xy[1] + 511), fill="#20252b")
        draw.text((xy[0] + 10, xy[1] + 478), tile["tile"], font=font, fill="white")
    draw.text((18, 1586), "Reduced presentation mosaic. Northwest 60-tile zone remains incomplete; formal acceptance is pending.", font=font, fill="white")
    preview_path = destination / "preview-only-mosaic-2560.png"
    preview.save(preview_path)
    summary_path = destination / "delivery-summary.json"
    summary = {"schemaVersion": 1, "createdAtUtc": created,
        "status": "nine_tiles_internal_and_packaged_shared_boundaries_passed",
        "tileCount": 9, "tiles": tiles, "tilePixels": [4096, 4096],
        "boundingTileGrid": [5, 3], "boundingGridContainsMissingTiles": True,
        "artWorldBox": [8192, 16384, 28672, 28672], "ownedZoneTileCount": 60,
        "wholeZoneComplete": False, "formalAccepted": False, "formalAcceptedCount": 0,
        "blockingCount": 0, "nativeSourceCount": 147, "fixedGridSourceCount": 144,
        "additionalNativeBridgeCount": 3, "nativeOriginalsArchivedForNewTile": 16,
        "priorNativeOriginalsRemainAtRecordedLocalPaths": True,
        "verifiedNativeOutputPixels": 9 * 4096 * 4096,
        "freshlyRecheckedNinthNativePixels": 4096 * 4096,
        "inheritedEightPixelProofPixels": old_summary["verifiedNativeOutputPixels"],
        "productionResampled": False, "productionPNGBytesUnmodified": True,
        "actualModel": None, "actualQuality": None,
        "runtimeIntegration": False, "capacity5000Validated": False,
        "sourceValidation": ref(validation_path), "newNativePixelProof": ref(proof_path),
        "preservedEightPackage": ref(OLD / "package.json"),
        "preservedEightArchive": ref(old_archive), "ninthDelivery": ref(delivery_path),
        "ninthExternalReviewedSides": ["west"], "ninthExternalPendingSides": ["north", "east", "south"],
        "actualPackagedWestBoundaryReview": proof["actualPackagedWestBoundaryReview"],
        "independentActualPackagedWestBoundaryReview": proof["independentActualPackagedWestBoundaryReview"],
        "optionalIndependentActualPackagedWestBoundaryStatus": proof["independentActualPackagedWestBoundaryStatus"],
        "preview": {**ref(preview_path), "previewOnly": True, "productionArt": False,
                    "pixels": [2560, 1624], "tileDisplayPixels": [512, 512]},
        "outerPerimeterStatus": "Unfinished or unreviewed neighboring tiles remain; no whole-zone acceptance."}
    write_new(summary_path, summary)
    readme = destination / "README.txt"
    readme.write_text("Nine internally reviewed 4096 x 4096 production PNGs. Original PNG bytes are unchanged.\\n"
        "This extends the unchanged verified eight package with r05_c07. Its 16 original 1254 PNG sources, generation/request/receipt evidence, 33 native internal reviews, and 7 native actual-west-boundary reviews are included.\\n"
        "Every r05_c07 output pixel was reverified as an unmodified same-coordinate native sample. Earlier eight tile pixel proofs are inherited as unchanged validated evidence.\\n"
        "Previous eight native originals remain at their recorded local paths; their records and hashes are preserved.\\n"
        "The reduced mosaic is PREVIEW ONLY. Gray cells are pending. Northwest 60-tile zone remains incomplete. Formal acceptance, runtime integration and capacity validation remain false.\\n"
        "Prior eight root metadata is stored unchanged under historical-eight/. Production tiles and evidence retain their former archive names.\\n"
        "package-contents.json maps each archive entry to its original local file and SHA256. package.json and archive-verification.json alongside the archive verify CRC, entry hashes and original file identity.\\n", encoding="utf-8")
    keep(OLD / "package.json", "historical-eight/package.json")
    keep(__file__)
    old_entries = []
    for item in old_files:
        item = dict(item)
        item["inheritedFromArchiveEntry"] = item["zipEntry"]
        if "/" not in item["zipEntry"]:
            item["zipEntry"] = "historical-eight/" + item["zipEntry"]
        old_entries.append(item)
    files = old_entries + [{"originalFile": str(path), "zipEntry": entry, "sha256": digest}
                            for entry, (path, digest) in sorted(additions.items())]
    files += [{"originalFile": str(path), "zipEntry": path.name, "sha256": sha(path)}
              for path in (summary_path, validation_path, proof_path, preview_path, readme)]
    require(len({item["zipEntry"] for item in files}) == len(files), "Duplicate archive entry")
    contents_path = destination / "package-contents.json"
    write_new(contents_path, {"schemaVersion": 1, "files": files,
        "manifestSelfHashRecordedInPackageJson": True,
        "existingEightUncompressedEntriesPreservedByteForByte": True})
    files.append({"originalFile": str(contents_path), "zipEntry": contents_path.name, "sha256": sha(contents_path)})
    archive_path = destination / "northwest-nine-4k-tiles.zip"
    with zipfile.ZipFile(old_archive) as source_archive, zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for item in files:
            require(sha(item["originalFile"]) == item["sha256"], "Source changed during archive creation")
            if "inheritedFromArchiveEntry" in item:
                with source_archive.open(item["inheritedFromArchiveEntry"]) as source, archive.open(item["zipEntry"], "w", force_zip64=True) as target:
                    shutil.copyfileobj(source, target, 1024 * 1024)
            else:
                archive.write(item["originalFile"], item["zipEntry"])
    verified = []
    with zipfile.ZipFile(archive_path) as archive:
        require(archive.testzip() is None, "New archive CRC failure")
        require(set(archive.namelist()) == {item["zipEntry"] for item in files}, "New archive inventory mismatch")
        for item in files:
            with archive.open(item["zipEntry"]) as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            require(actual == item["sha256"] == sha(item["originalFile"]), "Archive/original byte mismatch")
            verified.append({**item, "archiveSha256": actual, "originalFileByteIdentity": True})
    require(all(sha(path) == digest for path, digest in checked.items()), "Protected production/evidence input changed")
    verification_path = destination / "archive-verification.json"
    write_new(verification_path, {"createdAtUtc": now(), "archive": ref(archive_path),
        "status": "passed", "zipCRCVerified": True, "allEntrySHA256Verified": True,
        "allOriginalFilesByteIdentityVerified": True, "verifiedEntries": len(files),
        "oldArchiveUnchanged": ref(old_archive), "allProtectedInputsUnchanged": True,
        "protectedInputCount": len(checked), "entries": verified})
    package = {"createdAtUtc": now(), **ref(archive_path), "sizeBytes": archive_path.stat().st_size,
        "verifiedZipEntries": len(files), "verifiedProductionTileEntries": 9,
        "verifiedNativeSources": 147, "newNativeOriginalsArchived": 16,
        "allZipEntryHashesVerified": True, "allOriginalFilesByteIdentityVerified": True,
        "zipCRCVerified": True, "existingEightDeliveryPreserved": True,
        "wholeZoneComplete": False, "formalAccepted": False,
        "summary": ref(summary_path), "preview": ref(preview_path),
        "sourceValidation": ref(validation_path), "nativePixelProof": ref(proof_path),
        "packageContents": ref(contents_path), "archiveVerification": ref(verification_path)}
    write_new(destination / "package.json", package)
    print(json.dumps(package, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

