"""QA only: native hard-seam assembly with explicit missing coverage and pixel replay."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import numpy as np
from PIL import Image

QA = Path(__file__).resolve().parent
ZONE = QA.parent
PREFIX = "capacity-gate-r09c06-v1"
C, N, O, H = 1024, 1254, 230, 115
ORIGIN = [20480, 32768]

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))

def write(p, data):
    assert p.parent == QA and p.name.startswith(PREFIX) and not p.exists(), str(p)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def save(p, array):
    assert p.parent == QA and p.name.startswith(PREFIX) and not p.exists(), str(p)
    Image.fromarray(array).save(p)
    assert np.array_equal(np.asarray(Image.open(p)), array)

def artifact(p, array):
    save(p, array)
    return {"path":p.as_posix(), "sha256":sha(p), "size":[array.shape[1],array.shape[0]]}

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def main():
    original = load_module("existing_native_selector", QA/"full-tile-assemble.py")
    helper_path = original.HELPER
    if not helper_path.exists():
        helper_path = ZONE.parents[1]/"parallel_20261005/donghai_lantern/r09_c15/assembly-contract-v1/snapshots/3c9fb69c334985b7-seam_helpers.py"
    assert sha(helper_path) == "3c9fb69c334985b77a51b254b59b5945bec893e746bda0ff71b0d41dca167a48"
    helper = load_module("existing_seam_helper", helper_path)
    chosen = original.select("r09_c06")
    assert set(chosen) == {(r,c) for r in range(1,5) for c in range(1,5)}-{(4,4)}
    arrays, ids, sources, seams = {}, {}, [], []
    for sid, (key, (version, rp, rec)) in enumerate(sorted(chosen.items()), 1):
        row,col = key
        x,y = (col-1)*C,(row-1)*C
        path = Path(rec["file"])
        assert sha(path) == rec["sha256"]
        expected = [ORIGIN[0]-H+x,ORIGIN[1]-H+y,ORIGIN[0]-H+x+N,ORIGIN[1]-H+y+N]
        assert rec["coordinates"]["globalContextBox"] == expected
        im = Image.open(path)
        assert im.size == (N,N) and im.mode in ("RGB","RGBA")
        if im.mode == "RGBA": assert im.getextrema()[3] == (255,255)
        arrays[key] = np.asarray(im.convert("RGB")).copy()
        ids[key] = np.full((N,N),sid,dtype=np.uint8)
        sources.append({"sourceId":sid,"patch":f"p{row:02d}_{col:02d}","version":version,
            "path":path.as_posix(),"sha256":rec["sha256"],"record":rp.as_posix(),"recordSha256":sha(rp),
            "statusAtSelection":rec.get("status"),"contextDestinationBox":[x,y,x+N,y+N],
            "globalContextBox":expected,"nativeSize":[N,N]})
    rows, row_ids = [], []
    for r in range(1,5):
        row, rid = arrays[(r,1)], ids[(r,1)]
        for c in range(2,5 if r<4 else 4):
            right, rightid = arrays[(r,c)], ids[(r,c)]
            seam = helper._minimum_vertical_seam(row[:,-O:],right[:,:O])
            choose = np.arange(O)[None,:] >= seam[:,None]
            row = np.concatenate([row[:,:-O],np.where(choose[:,:,None],right[:,:O],row[:,-O:]),right[:,O:]],axis=1)
            rid = np.concatenate([rid[:,:-O],np.where(choose,rightid[:,:O],rid[:,-O:]),rightid[:,O:]],axis=1)
            seams.append({"id":f"row{r}-c{c-1}-c{c}","axis":"vertical","stage":"row assembly",
                "overlapBox":[(c-1)*C,(r-1)*C,(c-1)*C+O,(r-1)*C+N],
                "seamXByNativeRowInOverlap":seam.tolist(),"seamXByNativeRowInContext":(seam+(c-1)*C).tolist(),
                "rightChosenAtOrRight":True})
        rows.append(row); row_ids.append(rid)
    combined = np.zeros((4326,4326,3),dtype=np.uint8)
    source_map = np.zeros((4326,4326),dtype=np.uint8)
    combined[:N] = rows[0]; source_map[:N] = row_ids[0]
    for r in range(1,4):
        y, lower, lid = r*C, rows[r], row_ids[r]
        width = lower.shape[1]
        old, new = combined[y:y+O,:width],lower[:O]
        seam = helper._minimum_vertical_seam(old.transpose(1,0,2),new.transpose(1,0,2))
        choose = np.arange(O)[:,None] >= seam[None,:]
        combined[y:y+O,:width] = np.where(choose[:,:,None],new,old)
        source_map[y:y+O,:width] = np.where(choose,lid[:O],source_map[y:y+O,:width])
        combined[y+O:y+N,:width] = lower[O:]
        source_map[y+O:y+N,:width] = lid[O:]
        seams.append({"id":f"row{r}-row{r+1}","axis":"horizontal","stage":"row-strip assembly",
            "overlapBox":[0,y,width,y+O],"seamYByColumnInOverlap":seam.tolist(),
            "seamYByColumnInContext":(seam+y).tolist(),"lowerChosenAtOrBelow":True,
            "missingLowerCoverageRule":"No seam or choice outside common source coverage; retain covered upper pixels."})
    coverage = source_map > 0
    expected_coverage = np.zeros_like(coverage)
    replay = np.zeros_like(combined)
    replay_counts = []
    for s in sources:
        x0,y0,x1,y1 = s["contextDestinationBox"]
        expected_coverage[y0:y1,x0:x1] = True
        mask = source_map[y0:y1,x0:x1] == s["sourceId"]
        key = tuple(map(int,(s["patch"][1:3],s["patch"][4:6])))
        replay[y0:y1,x0:x1][mask] = arrays[key][mask]
        replay_counts.append({"sourceId":s["sourceId"],"pixels":int(mask.sum())})
    assert np.array_equal(coverage,expected_coverage)
    assert np.array_equal(replay,combined)
    assert not coverage[3302:,3302:].any() and (~coverage).sum() == 1024**2
    rgba = np.dstack((combined,coverage.astype(np.uint8)*255))
    core = rgba[H:H+4096,H:H+4096].copy()
    context_record = artifact(QA/(PREFIX+"-partial-context-native.png"),rgba)
    core_record = artifact(QA/(PREFIX+"-partial-core-qa-4096.png"),core)
    coverage_record = artifact(QA/(PREFIX+"-coverage-mask.png"),coverage.astype(np.uint8)*255)
    source_map_record = artifact(QA/(PREFIX+"-source-id-map.png"),source_map)
    prior_report_path = QA/"preflight-r09_c06-rows12-v1-visual-audit.json"
    prior = read(prior_report_path)
    oldcore_path = Path(prior["partialCore"]["path"])
    assert sha(oldcore_path) == prior["partialCore"]["sha256"]
    oldcore = np.asarray(Image.open(oldcore_path).convert("RGB"))
    old_reviewed = np.zeros((2048,4096),dtype=bool)
    for item in prior["qaReviews"]:
        p = Path(item["path"])
        assert item["actuallyViewed"] and sha(p) == item["sha256"]
        x0,y0,x1,y1 = item["sourceBox"]
        assert np.array_equal(np.asarray(Image.open(p).convert("RGB")),oldcore[y0:y1,x0:x1])
        old_reviewed[y0:y1,x0:x1] = True
    prior_exact = np.zeros((4096,4096),dtype=bool)
    prior_exact[:2048] = np.all(core[:2048,:,:3]==oldcore,axis=2) & (core[:2048,:,3]==255) & old_reviewed
    inherited_region = core[:1933,:,:3].copy()
    assert np.array_equal(inherited_region,oldcore[:1933])
    boxes = []
    starts=[0,800,1600,2400,3196]
    for axis in ("v","h"):
        for boundary in (1024,2048,3072):
            for part,start in enumerate(starts,1):
                box = [boundary-345,start,boundary+345,start+900] if axis=="v" else [start,boundary-345,start+900,boundary+345]
                boxes.append((f"{axis}{boundary}-part{part:02d}",box))
    for y in (1024,2048,3072):
        for x in (1024,2048,3072):
            boxes.append((f"intersection-x{x}-y{y}",[x-450,y-450,x+450,y+450]))
    qa=[]
    for key,box in boxes:
        x0,y0,x1,y1 = box
        pixels = core[y0:y1,x0:x1]
        record = artifact(QA/(PREFIX+"-"+key+"-100pct.png"),pixels)
        inherited = bool(prior_exact[y0:y1,x0:x1].all())
        record.update({"id":key,"sourceBox":box,"globalBox":[x0+ORIGIN[0],y0+ORIGIN[1],x1+ORIGIN[0],y1+ORIGIN[1]],
            "source":core_record,"coveredPixels":int((pixels[:,:,3]==255).sum()),"missingPixels":int((pixels[:,:,3]==0).sum()),
            "nativeRGBPixelSha256":hashlib.sha256(pixels[:,:,:3].tobytes()).hexdigest(),
            "operation":"integer crop only; transparent area has no artwork source", "noResize":True,"noDrawing":True,
            "visualReviewInherited":inherited,"actuallyViewedThisRun":False})
        if inherited:
            oldregion = oldcore[y0:y1,x0:x1]
            record["inheritanceEvidence"]={"reportPath":prior_report_path.as_posix(),"reportSha256":sha(prior_report_path),
                "priorCore":prior["partialCore"],"everyPixelExactlyEqual":True,"entireRegionCoveredByPreviouslyViewedQa":True,
                "priorRGBPixelSha256":hashlib.sha256(oldregion.tobytes()).hexdigest()}
            assert record["nativeRGBPixelSha256"] == record["inheritanceEvidence"]["priorRGBPixelSha256"]
        write(Path(record["path"]+".derivation.json"),record)
        qa.append(record)
    assert all(sha(s["path"]) == s["sha256"] for s in sources)
    current=original.select("r09_c06")
    assert {k:v[1] for k,v in current.items()} == {k:v[1] for k,v in chosen.items()}
    report={"schemaVersion":1,"createdAtUtc":datetime.now(timezone.utc).isoformat(),"tile":"r09_c06",
        "status":"partial_15_slot_mechanical_QA_only","notFullTile":True,"internalComplete4k":0,"formalAcceptedCount":0,
        "gate":"capacity_layout_validation_before_new_area_expansion","imageGenerationCalls":0,"missingSlots":["p04_04"],
        "missingContextBox":[3302,3302,4326,4326],"missingCoreBox":[3187,3187,4096,4096],
        "missingCoreWorldBox":[23667,35955,24576,36864],"missingNominalSlotCoreBox":[3072,3072,4096,4096],
        "missingCoverageNote":"Adjacent native halos cover part of nominal absent slot; this does not make it generated or accepted.",
        "compositionOrder":"Row strips left to right, then common-width overlaps top to bottom; no choice against missing pixels",
        "method":"Existing helper minimum-error seam; hard source-pixel choice","noResize":True,"noFeather":True,"noColourCorrection":True,"noDrawing":True,
        "sources":sources,"seams":seams,"context":context_record,"partialCore":core_record,"coverageMask":coverage_record,"sourceIdMap":source_map_record,
        "sourceIdMapMeaning":"0 missing; other values refer to sources.sourceId, local coordinate equals context coordinate minus contextDestinationBox origin",
        "globalContextBox":[20365,32653,24691,36979],"globalCoreBox":[20480,32768,24576,36864],
        "script":{"path":Path(__file__).as_posix(),"sha256":sha(__file__)},"helper":{"path":helper_path.as_posix(),"sha256":sha(helper_path),"originalPath":original.HELPER.as_posix(),"restoredReadOnlyFromIdenticalHashSnapshot":helper_path!=original.HELPER},
        "mechanicalValidation":{"sourceHashesUnchanged":True,"savedPixelsVerified":True,"coverageEqualsUnionOfSources":True,
            "fullCoveredPixelReplayPass":True,"allUncoveredRGBZeroAndAlphaZero":bool((rgba[~coverage]==0).all()),
            "coveredContextPixels":int(coverage.sum()),"missingContextPixels":int((~coverage).sum()),
            "coveredCorePixels":int((core[:,:,3]==255).sum()),"missingCorePixels":int((core[:,:,3]==0).sum()),
            "sourcePixelCounts":replay_counts,"verticalSeams":11,"horizontalSeamLengths":[4326,4326,3302]},
        "priorAudit":{"path":prior_report_path.as_posix(),"sha256":sha(prior_report_path),
            "first1933CoreRowsExactlyEqual":True,"identicalRGBPixelSha256":hashlib.sha256(inherited_region.tobytes()).hexdigest()},
        "qa":qa}
    write(QA/(PREFIX+"-trace.json"),report)
    print(json.dumps({"context":context_record,"trace":str(QA/(PREFIX+"-trace.json")),"qa":len(qa),"inherited":sum(q["visualReviewInherited"] for q in qa),"missingSlots":["p04_04"],"pixelReplay":True}))

if __name__ == "__main__":
    main()
