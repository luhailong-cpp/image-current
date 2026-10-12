import copy
import datetime
import hashlib
import json
import pathlib
import re

from PIL import Image, ImageChops


Q = pathlib.Path(__file__).resolve().parent
B = Q.parent.parent
CROP = [115, 115, 1139, 1139]
ORDER = ["NW", "NE", "SW", "SE"]
QUAD_CROPS = [[768, 768, 1024, 1024], [0, 768, 256, 1024],
              [768, 0, 1024, 256], [0, 0, 256, 256]]


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))


report_names = [f"r01_c14-row{r}-review.json" for r in range(1, 5)] + [
    "r01_c14_p01_01_v2-review.json", "r01_c14_p03_04_v2-review.json"]
reports = {n: read(Q / n) for n in report_names}
assembly_path = B / "candidates/r01_c14.4096-candidate.png.assembly.json"
assembly = read(assembly_path)
candidate = pathlib.Path(assembly["file"])
assert sha(candidate) == assembly["sha256"] == "505a8705793013fa077928c839fdf431444450a7c569c938c96e33e189f5b874"

selected = [[f"r01_c14_p{r:02d}_{c:02d}_v{2 if (r,c) in [(1,1),(3,4)] else 1}"
             for c in range(1, 5)] for r in range(1, 5)]
selected_ids = {i for row in selected for i in row}
assert len(selected_ids) == 16
sources = {}
cores = {}
generation_count = 0


def source(s):
    global generation_count
    sid = s["id"]
    if sid in sources:
        assert s["sha256"] == sources[sid]["sha256"], sid
        return copy.deepcopy(sources[sid])
    file = pathlib.Path(s["file"])
    actual = sha(file)
    assert actual == s["sha256"], sid
    image = Image.open(file).convert("RGB")
    assert list(image.size) == s.get("nativeSize", [1254, 1254]) == [1254, 1254], sid
    assert s.get("coreCrop", CROP) == CROP, sid
    generation_path = pathlib.Path(str(file) + ".generation.json")
    generation = read(generation_path)
    assert generation["sha256"] == actual, sid
    assert generation["id"] == sid, sid
    assert generation.get("size", [1254, 1254]) == [1254, 1254], sid
    assert generation["coreCrop"] == CROP, sid
    sources[sid] = {"id": sid, "file": file.as_posix(), "sha256": actual,
                    "nativeSize": [1254, 1254], "coreCrop": CROP,
                    "generationRecord": generation_path.as_posix(),
                    "generationRecordSha256": sha(generation_path)}
    cores[sid] = image.crop(CROP)
    if sid in selected_ids:
        generation_count += 1
    return copy.deepcopy(sources[sid])


for s in assembly["sources"]:
    item = dict(s, id=pathlib.Path(s["file"]).stem, coreCrop=s["sourceCrop"])
    src = source(item)
    assert src["id"] in selected_ids
    row = int(re.search(r"_p(\d+)_", src["id"])[1]) - 1
    col = int(re.search(r"_p\d+_(\d+)", src["id"])[1]) - 1
    assert selected[row][col] == src["id"]
    assert s["pasteAt"] == [col * 1024, row * 1024]

all_seams = {}
all_crossings = {}
for name in report_names:
    report = reports[name]
    for entry in report.get("seams", []):
        ids = [entry["a"]["id"], entry["b"]["id"]]
        if any(i.startswith("r01_c14_") and i not in selected_ids for i in ids):
            continue
        assert entry["status"].startswith("passed"), (name, entry["key"])
        x = copy.deepcopy(entry)
        x["a"] = source(x["a"])
        x["b"] = source(x["b"])
        evidence = Image.open(x["evidence"]).convert("RGB")
        crops = x["sourceCoreCrops"]
        a = cores[ids[0]].crop(crops[0])
        b = cores[ids[1]].crop(crops[1])
        is_vertical = x["side"] in ["east", "west"]
        expected = Image.new("RGB", (a.width + b.width, a.height) if is_vertical else (a.width, a.height + b.height))
        expected.paste(a, (0, 0))
        expected.paste(b, (a.width, 0) if is_vertical else (0, a.height))
        assert evidence.size == expected.size and ImageChops.difference(evidence, expected).getbbox() is None, x["key"]
        x.update(verificationReport=(Q / name).as_posix(), verificationReportSha256=sha(Q / name),
                 validation="both_current_native_hashes_match_passed_evidence",
                 evidenceSha256=sha(x["evidence"]), evidencePixelsMatchCurrentCoreCrops=True)
        x["basis"] = "carried_forward_hash_matched_passed_native_scale_visual_review"
        x["notes"] = "Exact selected-core boundary is continuous in water color and principal caustic contours; no blocking step or rectangular cut. Native interior density remnants are assessed separately using the selected current sources."
        all_seams[x["key"]] = x
    for entry in report.get("crossings", []):
        srcs = [entry["quadrants"][q] for q in ORDER] if "quadrants" in entry else entry["sources"]
        if any(s["id"] not in selected_ids for s in srcs):
            continue
        assert entry["status"].startswith("passed"), (name, entry["key"])
        srcs = [source(s) for s in srcs]
        first = srcs[0]["id"]
        match = re.search(r"_p(\d+)_(\d+)_", first)
        r, c = map(int, match.groups())
        key = f"row{r}-row{r+1}-col{c}"
        evidence = Image.open(entry["evidence"]).convert("RGB")
        expected = Image.new("RGB", (512, 512))
        for s, crop, point in zip(srcs, QUAD_CROPS, [(0, 0), (256, 0), (0, 256), (256, 256)]):
            expected.paste(cores[s["id"]].crop(crop), point)
        assert evidence.size == expected.size and ImageChops.difference(evidence, expected).getbbox() is None, key
        all_crossings[key] = {"key": key, "evidence": entry["evidence"],
                              "joinCoordinateInEvidence": [256, 256], "sources": srcs,
                              "sourceCoreCrops": QUAD_CROPS, "status": "passed_visible_core_crossing",
                              "basis": "carried_forward_hash_matched_passed_native_scale_visual_review",
                              "notes": "Exact four-way selected-core crossing is continuous without a blocking cross or rectangle; current-source native interior density remnants remain nonblocking.",
                              "verificationReport": (Q / name).as_posix(),
                              "verificationReportSha256": sha(Q / name),
                              "validation": "all_four_current_native_hashes_match_passed_evidence",
                              "evidenceSha256": sha(entry["evidence"]),
                              "evidencePixelsMatchCurrentCoreCrops": True}

internal = [s for s in all_seams.values() if s["scope"] == "internal"]
south = [s for s in all_seams.values() if s["scope"] == "external_south"]
west = [s for s in all_seams.values() if s["scope"] == "external_west"]
assert [len(internal), len(all_crossings), len(south), len(west)] == [24, 9, 4, 4]
expected_seams = set()
for r in range(4):
    for c in range(4):
        if c < 3:
            expected_seams.add(selected[r][c] + "__" + selected[r][c+1])
        if r < 3:
            expected_seams.add(selected[r][c] + "__" + selected[r+1][c])
assert {s["key"] for s in internal} == expected_seams
assert set(all_crossings) == {f"row{r}-row{r+1}-col{c}" for r in range(1, 4) for c in range(1, 4)}

center = copy.deepcopy(reports["r01_c14-row4-review.json"]["regionCenterCrossing"])
assert center["status"].startswith("passed") and center["worldCoordinate"] == [53248, 4096]
center["sources"] = [source(s) for s in center["sources"]]
center.update(verificationReport=(Q / "r01_c14-row4-review.json").as_posix(),
              verificationReportSha256=sha(Q / "r01_c14-row4-review.json"),
              evidenceSha256=sha(center["evidence"]),
              validation="all_four_current_native_hashes_match_passed_evidence")
center_expected = Image.new("RGB", (512, 512))
for s, crop, point in zip(center["sources"], QUAD_CROPS, [(0,0),(256,0),(0,256),(256,256)]):
    center_expected.paste(cores[s["id"]].crop(crop), point)
center_actual = Image.open(center["evidence"]).convert("RGB")
assert ImageChops.difference(center_actual, center_expected).getbbox() is None
center["evidencePixelsMatchCurrentCoreCrops"] = True

actual_candidate = Image.open(candidate).convert("RGB")
assert actual_candidate.size == (4096, 4096)
for r in range(4):
    for c in range(4):
        box = [c*1024, r*1024, (c+1)*1024, (r+1)*1024]
        assert ImageChops.difference(actual_candidate.crop(box), cores[selected[r][c]]).getbbox() is None

native_checks = []
for name in report_names:
    for check in reports[name].get("nativePatchChecks", []) + reports[name].get("interiorObservations", []):
        sid = check.get("patch", check.get("id"))
        if sid not in selected_ids:
            continue
        assert not check.get("status", "").startswith("blocking"), (sid, name)
        x = copy.deepcopy(check)
        x.update(verificationReport=(Q / name).as_posix(), verificationReportSha256=sha(Q / name))
        if "source" in x:
            x["source"] = source(x["source"])
        native_checks.append(x)

out = {"tileId": "r01_c14", "status": "passed_current_selected_internal_south_west_and_region_center",
       "selectedCores": selected,
       "sources": [sources[s] for row in selected for s in row],
       "internalSeams": internal, "internalCrossings": list(all_crossings.values()),
       "southExternalSeams": south, "westExternalSeams": west,
       "regionCenterCrossing": center,
       "repairReviewReports": [(Q / n).as_posix() for n in report_names[-2:]],
       "nonblockingInteriorResidualReports": [(Q / n).as_posix() for n in report_names],
       "nativePatchChecks": native_checks,
       "sourceHashValidation": {"currentNativeGenerationRecordsMatched": generation_count,
                                "internalPairSourceHashesMatched": 24, "internalCrossingFourSourceHashesMatched": 9,
                                "southPairSourceHashesMatched": 4, "westPairSourceHashesMatched": 4,
                                "regionCenterFourSourceHashesMatched": 1,
                                "evidenceExactCurrentCorePixelsMatched": 42,
                                "candidateCoresExactCurrentSourcePixelsMatched": 16,
                                "unchangedPassedItemsReusedWithoutRepeatingVisualReview": True},
       "blockingIssues": [],
       "summary": {"selectedNativeCores": 16, "nativeDimensions": [1254, 1254], "exactCoreDimensions": [1024, 1024],
                   "internalSeamsPassed": 24, "internalSeamsTotal": 24,
                   "internalCrossingsPassed": 9, "internalCrossingsTotal": 9,
                   "southExternalSegmentsPassed": 4, "southExternalSegmentsTotal": 4,
                   "westExternalSegmentsPassed": 4, "westExternalSegmentsTotal": 4,
                   "regionCenterCrossingsPassed": 1, "blockingIssues": 0,
                   "candidateAssemblyReady": True, "mandatoryNewVersionRecommended": False,
                   "notEntireMapApproved": True, "formalAccepted": False},
       "externalEdges": {"north": {"status": "outer_map_boundary_no_external_tile", "tileRow": 1, "worldY": 0},
                         "east": {"status": "outer_map_boundary_no_external_tile", "tileColumn": 14, "worldX": 57344},
                         "south": {"status": "passed_current_hashes", "adjacentTile": "r02_c14", "segments": 4},
                         "west": {"status": "passed_current_hashes", "adjacentTile": "r01_c13", "segments": 4}},
       "regionExternalEdges": {"west": {"status": "pending_neighbor_unavailable", "adjacentTile": "r01_c12",
                                      "scope": "outside_this_2x2_local_region", "localRegionMissingArt": False,
                                      "searchReport": (Q / "r01_c13-row2-review.json").as_posix()}},
       "candidate": {"file": candidate.as_posix(), "sha256": sha(candidate), "dimensions": [4096, 4096],
                     "assemblyRecord": assembly_path.as_posix(), "assemblyRecordSha256": sha(assembly_path),
                     "exactCurrentCorePixelsMatched": 16, "sourceCrop": CROP, "resized": False,
                     "overallPreviewReview": {"status": "passed_overall_candidate_preview", "evidence": candidate.as_posix(),
                                              "evidenceSha256": sha(candidate), "displayedPreviewDimensions": [1600, 1600],
                                              "notes": "The 4096 candidate viewed as a fit preview has a coherent blue/cyan water field and caustic scale, without a blocking tile grid or large rectangular discontinuity. Local density variations are already assessed at native scale.",
                                              "scope": "overall appearance only; seam acceptance comes from unscaled native evidence"}},
       "formalAccepted": False, "finalMapComplete": False,
       "reviewer": "Codex incremental native-scale visual QA with current-hash pass reuse",
       "reviewedAtUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "method": "Incremental native-scale visual review plus exact current-hash pass reuse. Current 16 selected 1254 natives, cores [115,115,1139,1139); exact paste to 4096 without resize, blending or source/candidate edits. Prepared row2 and p03_04_v2 reports completed; prior passed reports retained intact. Source hashes, generation records and all 42 seam/crossing evidence images mechanically match current cores.",
       "resolvedNativeIssues": [{"oldSource": "r01_c14_p01_01_v1", "currentSource": "r01_c14_p01_01_v2", "status": "resolved_to_nonblocking_density_residual", "verificationReport": (Q / report_names[-2]).as_posix()},
                                {"oldSource": "r01_c14_p03_04_v1", "currentSource": "r01_c14_p03_04_v2", "status": "resolved_to_nonblocking_density_residual", "verificationReport": (Q / report_names[-1]).as_posix()}],
       "nonblockingInteriorResidualReportScope": "Only current selected hashes are accepted; old source entries are historical issue context and are excluded from all accepted seams, crossings and nativePatchChecks.",
       "generationMetadata": {"route": "builtin", "actualModel": "unknown", "actualQuality": "unknown", "unverifiedReason": "Built-in tool does not disclose model/quality metadata."}}

path = Q / "r01_c14-current-final-review.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(path)
print(json.dumps(out["summary"], ensure_ascii=False))
print("SHA256", sha(path))
