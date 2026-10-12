"""Select current native patches, hard-seam assemble, and export 100% QA."""
import sys
sys.dont_write_bytecode = True

from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import re
import numpy as np
from PIL import Image

QA = Path(__file__).resolve().parent
ROOT = QA.parent
HELPER = ROOT / "tools" / "seam_helpers.py"
C, H, O, N = 1024, 115, 230, 1254


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def write(p, obj):
    assert p.parent == QA and p.name.startswith("full-tile-")
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def save(p, pixels):
    assert p.parent == QA and p.name.startswith("full-tile-")
    Image.fromarray(pixels).save(p)
    with Image.open(p) as im:
        assert np.array_equal(np.asarray(im), pixels)


def select(tile):
    candidates = {}
    pattern = re.compile(re.escape(tile)+r"_p(\d{2})_(\d{2})_v(\d+)\.png\.generation\.json$")
    for p in sorted((ROOT/"native").glob(tile+"_*.png.generation.json")):
        match = pattern.fullmatch(p.name)
        if not match:
            continue
        row, col, version = map(int, match.groups())
        if not (1 <= row <= 4 and 1 <= col <= 4):
            continue
        rec = read(p)
        status = rec.get("status", "").lower()
        if any(word in status for word in ("superseded", "rejected", "frozen")):
            continue
        key = (row, col)
        if key not in candidates or version > candidates[key][0]:
            candidates[key] = (version, p, rec)
    return candidates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tile", default="r09_c04")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    tile_match = re.fullmatch(r"r(\d{2})_c(\d{2})", args.tile)
    if not tile_match:
        raise ValueError("Invalid tile id")
    tr, tc = map(int, tile_match.groups())
    ox, oy = (tc-1)*4096-H, (tr-1)*4096-H
    chosen = select(args.tile)
    missing = [f"p{r:02d}_{c:02d}" for r in range(1,5) for c in range(1,5) if (r,c) not in chosen]
    if args.preflight:
        print(json.dumps({"tile": args.tile, "missing": missing,
                          "selected": [chosen[k][1].name for k in sorted(chosen)]}))
        return
    if missing:
        raise ValueError("Missing current native patches: "+", ".join(missing))
    spec = importlib.util.spec_from_file_location("full_tile_seam_helper", HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    sources, arrays = [], []
    for r in range(4):
        native_row = []
        for c in range(4):
            version, rp, rec = chosen[(r+1,c+1)]
            p = Path(rec["file"])
            expected = [ox+c*C, oy+r*C, ox+c*C+N, oy+r*C+N]
            assert rec["coordinates"]["globalContextBox"] == expected
            assert sha(p) == rec["sha256"]
            with Image.open(p) as im:
                im.load()
                assert im.size == (N,N) and im.mode in ("RGB","RGBA")
                if im.mode == "RGBA":
                    assert im.getextrema()[3] == (255,255)
                native_row.append(np.asarray(im.convert("RGB")).copy())
            sources.append({"patch": f"p{r+1:02d}_{c+1:02d}", "version": version,
                            "path": p.as_posix(), "sha256": rec["sha256"], "nativeSize": [N,N],
                            "record": rp.as_posix(), "recordSha256": sha(rp), "statusAtSelection": rec.get("status"),
                            "globalContextBox": expected, "contextDestinationBox": [c*C,r*C,c*C+N,r*C+N]})
        arrays.append(native_row)
    rows, seams = [], []
    for r, patches in enumerate(arrays):
        row = patches[0]
        for c, right in enumerate(patches[1:],1):
            seam = helper._minimum_vertical_seam(row[:,-O:],right[:,:O])
            overlap = np.where((np.arange(O)[None,:]>=seam[:,None])[:,:,None],right[:,:O],row[:,-O:])
            row = np.concatenate([row[:,:-O],overlap,right[:,O:]],axis=1)
            seams.append({"id":f"row{r+1}-c{c}-c{c+1}","axis":"vertical","stage":"row assembly",
                          "overlapBox":[c*C,r*C,c*C+O,r*C+N],"seamXByNativeRowInOverlap":seam.tolist(),
                          "seamXByNativeRowInContext":(seam+c*C).tolist(),"rightChosenAtOrRight":True})
        assert row.shape == (N,4326,3)
        rows.append(row)
    combined = rows[0]
    for r, lower in enumerate(rows[1:],1):
        seam = helper._minimum_vertical_seam(np.transpose(combined[-O:],(1,0,2)),np.transpose(lower[:O],(1,0,2)))
        overlap = np.where((np.arange(O)[:,None]>=seam[None,:])[:,:,None],lower[:O],combined[-O:])
        combined = np.concatenate([combined[:-O],overlap,lower[O:]],axis=0)
        seams.append({"id":f"row{r}-row{r+1}","axis":"horizontal","stage":"row-strip assembly",
                      "overlapBox":[0,r*C,4326,r*C+O],"seamYByColumnInOverlap":seam.tolist(),
                      "seamYByColumnInContext":(seam+r*C).tolist(),"lowerChosenAtOrBelow":True})
    assert combined.shape == (4326,4326,3)
    final = combined[H:H+4096,H:H+4096].copy()
    prefix = "full-tile-"+args.tile
    context_path, final_path = QA/(prefix+"-context-native.png"), QA/(prefix+"-candidate-4096.png")
    save(context_path,combined)
    save(final_path,final)
    sources_unchanged = all(sha(s["path"])==s["sha256"] for s in sources)
    assert sources_unchanged
    current = select(args.tile)
    assert {k:v[1] for k,v in current.items()} == {k:v[1] for k,v in chosen.items()}, "Selections changed during assembly"
    manifest = {"schemaVersion":1,"createdAtUtc":datetime.now(timezone.utc).isoformat(),"tile":args.tile,
      "status":"4096_candidate_pending_visual_and_external_joins","formalAcceptedCount":0,
      "selectionRule":"Highest numeric version per patch, excluding superseded/rejected/frozen statuses",
      "compositionOrder":"Build four horizontal strips in row-major order, then append strips top to bottom",
      "method":"Existing minimum-error seam with hard source-pixel choice; no feathering",
      "noResize":True,"noFeather":True,"noColourCorrection":True,"noDrawing":True,"sources":sources,"seams":seams,
      "script":{"path":Path(__file__).as_posix(),"sha256":sha(__file__)},
      "helper":{"path":HELPER.as_posix(),"sha256":sha(HELPER)},
      "context":{"path":context_path.as_posix(),"sha256":sha(context_path),"size":[4326,4326],"globalBox":[ox,oy,ox+4326,oy+4326]},
      "output":{"path":final_path.as_posix(),"sha256":sha(final_path),"size":[4096,4096],"cropFromContext":[115,115,4211,4211],"globalCoreBox":[ox+H,oy+H,ox+H+4096,oy+H+4096]},
      "mechanicalValidation":{"passed":True,"nativeSourceCount":16,"verticalSeams":12,"verticalPathLength":1254,"horizontalSeams":3,"horizontalPathLength":4326,"sourceHashesUnchanged":True,"allSavedPixelsVerified":True},"qa":[]}
    mp = QA/(prefix+"-assembly.json")
    write(mp,manifest)
    print(json.dumps({"stage":"candidate_and_trace_saved","candidate":final_path.as_posix(),"trace":mp.as_posix()}),flush=True)
    boxes=[]
    starts=[0,800,1600,2400,3196]
    for axis in ("v","h"):
        for boundary in (1024,2048,3072):
            for part,start in enumerate(starts,1):
                box = [boundary-345,start,boundary+345,start+900] if axis=="v" else [start,boundary-345,start+900,boundary+345]
                boxes.append((f"{prefix}-{axis}{boundary}-part{part:02d}-100pct.png",box,"full-seam native segment"))
    for y in (1024,2048,3072):
        for x in (1024,2048,3072):
            boxes.append((f"{prefix}-intersection-x{x}-y{y}-100pct.png",[x-450,y-450,x+450,y+450],"native seam intersection"))
    for name,box,role in boxes:
        p=QA/name
        save(p,final[box[1]:box[3],box[0]:box[2]])
        record={"file":p.as_posix(),"sha256":sha(p),"size":[box[2]-box[0],box[3]-box[1]],"role":role,
                "source":{"path":final_path.as_posix(),"sha256":manifest["output"]["sha256"]},"sourceBox":box,
                "operation":"integer crop only","noResize":True,"noFeather":True,"noDrawing":True}
        write(Path(str(p)+".derivation.json"),record)
        manifest["qa"].append(record)
    write(mp,manifest)
    for p,size in [(context_path,[4326,4326]),(final_path,[4096,4096])]:
        write(Path(str(p)+".derivation.json"),{"file":p.as_posix(),"sha256":sha(p),"size":size,
              "assemblyRecord":mp.as_posix(),"operation":manifest["method"],"sources":sources,
              "seamPathsRecord":mp.as_posix(),"noResize":True,"noFeather":True,"noDrawing":True,"formalAcceptance":False})
    print(json.dumps({"stage":"qa_saved","qaFiles":len(boxes),"candidate":final_path.as_posix()}))


if __name__ == "__main__":
    main()
