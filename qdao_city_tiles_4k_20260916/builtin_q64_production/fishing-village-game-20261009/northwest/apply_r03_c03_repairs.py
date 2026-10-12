#!/usr/bin/env python3
"""Native overlay repair for r03_c03; separate outputs, never modifies base or plan.

Optional plan key (absent means []):
"overlays": [{
  "id": "sand-junction-v01",
  "nativeBox": [1421,397,2675,1651],
  "source": "native/repair-name.png",
  "sha256": "<native PNG SHA256>",
  "generationRecord": "native/repair-name.png.generation.json",
  "generationRecordSha256": "<record SHA256>",
  "bottomCutMinimumRanges": [
    {"xStart":644,"xEndExclusive":679,"minY":1221,
     "reason":"Keep the straight native rail bevel across the old join"}
  ]
}]
nativeBox is half-open, relative to the4096 candidate. Its inner1024 core
is forced to the repair. Each230px overlap supplies pixel-error costs;
eligible cut paths stay in the outer115px halo so no core pixel is lost.
Optional bottomCutMinimumRanges use repair-local coordinates and half-open
x ranges. They restrict the DP domain, never clamp a finished path; adjacent
path values therefore still differ by at most1. Omitted ranges mean[].
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SIZE, NATIVE, HALO, OVERLAP, CORE = 4096, 1254, 115, 230, 1024
DEFAULT_PLAN = ROOT / "assembly-plan.json"
DEFAULT_BASE = ROOT / "tiles" / "r03_c03.assembly.json"

def require(ok, message):
    if not ok:
        raise ValueError(message)

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for b in iter(lambda: stream.read(1048576), b""):
            h.update(b)
    return h.hexdigest()

def resolve(value):
    p = Path(value)
    return p.resolve() if p.is_absolute() else (ROOT / p).resolve()

def local(value):
    return resolve(value).relative_to(ROOT).as_posix()

def json_write(path, data):
    temp = path.with_name(path.name + ".writing")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)

def png_write(path, pixels):
    temp = path.with_name(path.stem + ".writing.png")
    Image.fromarray(pixels).save(temp, format="PNG", optimize=True)
    temp.replace(path)

def native_pixels(path):
    with Image.open(path) as image:
        image.load()
        require(image.format == "PNG" and image.size == (NATIVE,NATIVE), f"Native size/format mismatch: {path}")
        require(image.mode in ("RGB","RGBA"), f"Unsupported native mode: {path}")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255,255), f"Transparent map patch: {path}")
        return np.asarray(image)[...,:3].copy()

def validate_native(info, tile_origin):
    path = resolve(info["file"])
    record_path = resolve(info["generationRecord"])
    require(path.is_file() and record_path.is_file(), f"Missing source/record: {path}")
    require(sha(path) == info["sha256"], f"Source hash changed: {path}")
    require(sha(record_path) == info["generationRecordSha256"], f"Generation record hash changed: {record_path}")
    r = read(record_path)
    require(resolve(r["file"]) == path and r["sha256"] == info["sha256"], f"Generation identity mismatch: {path}")
    require(r.get("route") == "builtin" and r.get("tool") == "image_gen.imagegen", f"Non-builtin native: {path}")
    require(r.get("nativeScaleResampled") is False, f"Unverified native scaling: {path}")
    require([r.get("width"),r.get("height")] == [NATIVE,NATIVE], f"Recorded native size mismatch: {path}")
    require("submittedParameters" in r and "actualModel" in r and "actualQuality" in r, f"Missing model evidence: {path}")
    native_box = info["nativeBox"]
    expected_global = [native_box[0]+tile_origin[0],native_box[1]+tile_origin[1],
                       native_box[2]+tile_origin[0],native_box[3]+tile_origin[1]]
    require(r.get("globalNativeBox") == expected_global, f"Global native coordinates mismatch: {path}")
    prompt_path = resolve(r["prompt"])
    receipt_path = resolve(r["evidence"]["receipt"])
    request_path = resolve(r["evidence"].get("request", str(ROOT/"receipts"/(path.stem+".request.json"))))
    for p in (prompt_path,receipt_path,request_path):
        require(p.is_file(), f"Missing generation evidence: {p}")
    request, receipt = read(request_path), read(receipt_path)
    require(bool(receipt.get("output_hint")), f"Missing tool receipt: {receipt_path}")
    prompt = prompt_path.read_text(encoding="utf-8-sig").strip()
    require(bool(prompt), "Empty prompt")
    if "prompt" in request:
        require(request["prompt"].strip() == prompt, "Request/prompt differ")
    refs = r.get("references", [])
    require(refs and [resolve(a["file"]) for a in refs] ==
        [resolve(p) for p in request.get("referenced_image_paths",[])], "Request/reference list differs")
    for ref in refs:
        require(resolve(ref["file"]).is_file() and sha(resolve(ref["file"])) == ref["sha256"],
                f"Reference missing/hash changed: {ref['file']}")
        require(bool(ref.get("role")), "Reference role missing")
    return native_pixels(path), {
        **info, "file": str(path), "generationRecord": str(record_path),
        "prompt": {"file": str(prompt_path), "sha256": sha(prompt_path)},
        "receipt": {"file": str(receipt_path), "sha256": sha(receipt_path)},
        "request": {"file": str(request_path), "sha256": sha(request_path)},
        "references": refs, "configSnapshot": r.get("configSnapshot"),
        "submittedParameters": r["submittedParameters"], "actualModel": r["actualModel"],
        "actualQuality": r["actualQuality"], "unverifiedReason": r.get("unverifiedReason")
    }

def verify_pixels(pixels, ids, sources, source_arrays):
    require(pixels.shape == (SIZE,SIZE,3) and ids.shape == (SIZE,SIZE), "Final dimensions wrong")
    known = {int(s["sourceId"]) for s in sources}
    require(set(int(v) for v in np.unique(ids)) <= known and 0 not in np.unique(ids), "Unknown/uncovered pixel source")
    counts = []
    for source in sources:
        sid = int(source["sourceId"])
        yy,xx = np.nonzero(ids == sid)
        box = source["nativeBox"]
        sx,sy = xx-box[0],yy-box[1]
        require(np.all((sx>=0)&(sx<NATIVE)&(sy>=0)&(sy<NATIVE)), f"Source coordinates out of bounds: {sid}")
        require(np.array_equal(pixels[yy,xx],source_arrays[sid][sy,sx]), f"Native pixel provenance mismatch: {sid}")
        counts.append({"sourceId": sid, "pixelCount": int(len(xx)),
            "outputBoundingBox": [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None})
    require(sum(c["pixelCount"] for c in counts) == SIZE*SIZE, "Pixel coverage incomplete")
    return counts

def load_base(record_path):
    record = read(record_path)
    require(record.get("tile") == "r03_c03", "Wrong base tile")
    for artifact in record["artifacts"]:
        require(sha(resolve(artifact["file"])) == artifact["sha256"], f"Base artifact changed: {artifact['file']}")
    if "candidate" in record:
        candidate_path = resolve(record["candidate"]["file"])
    else:
        matches = [a for a in record["artifacts"] if "candidate" in Path(a["file"]).name and a["file"].endswith(".png")]
        require(len(matches) == 1, "Cannot identify unique base candidate")
        candidate_path = resolve(matches[0]["file"])
    ids_path = resolve(record["sourceIdMap"]["file"])
    with Image.open(candidate_path) as image:
        require(image.mode == "RGB" and image.size == (SIZE,SIZE), "Base candidate encoding wrong")
        pixels = np.asarray(image).copy()
    with Image.open(ids_path) as image:
        require(image.size == (SIZE,SIZE) and image.mode in ("L","I","I;16"), "Base ID map encoding wrong")
        ids = np.asarray(image).astype(np.uint16)
    origin = record["globalCoreBox"][:2]
    sources,arrays = [],{}
    seen = set()
    for old in record["sources"]:
        sid = int(old["sourceId"])
        require(1 <= sid <= 65535 and sid not in seen, "Invalid/duplicate sourceId")
        seen.add(sid)
        box = old.get("nativeBox")
        if box is None:
            g = old["globalNativeBox"]
            box = [g[0]-origin[0],g[1]-origin[1],g[2]-origin[0],g[3]-origin[1]]
        info = {"sourceId":sid,"file":old["file"],"sha256":old["sha256"],
                "generationRecord":old["generationRecord"],
                "generationRecordSha256":old["generationRecordSha256"],
                "nativeBox":box}
        array,info = validate_native(info,origin)
        sources.append(info)
        arrays[sid] = array
    verify_pixels(pixels,ids,sources,arrays)
    base = {"record":str(record_path),"recordSha256":sha(record_path),
            "candidate":str(candidate_path),"candidateSha256":sha(candidate_path),
            "sourceIdMap":str(ids_path),"sourceIdMapSha256":sha(ids_path),
            "globalCoreBox":record["globalCoreBox"]}
    return pixels,ids,sources,arrays,base

def minimum_path(cost, first, last, lower_bounds=None):
    """Inclusive path-domain limits, step -1/0/+1, exact integer DP."""
    require(cost.ndim == 2 and 0 <= first <= last < cost.shape[1], "Invalid seam domain")
    c = cost[:,first:last+1]
    height,width = c.shape
    bounds = np.full(height,first,dtype=np.int32) if lower_bounds is None else np.asarray(lower_bounds)
    require(bounds.shape == (height,) and np.issubdtype(bounds.dtype,np.integer), "Invalid seam lower bounds")
    require(np.all((bounds>=first)&(bounds<=last)), "Seam lower bound outside eligible halo")
    columns = np.arange(first,last+1)
    infinity = np.int64(1<<60)
    previous = c[0].copy()
    previous[columns<bounds[0]] = infinity
    back = np.zeros((height,width),dtype=np.int8)
    offsets = np.array([0,-1,1],dtype=np.int8)
    for y in range(1,height):
        a = np.concatenate((np.array([infinity]),previous[:-1]))
        b = np.concatenate((previous[1:],np.array([infinity])))
        options = np.stack((previous,a,b))
        choice = np.argmin(options,axis=0)
        back[y] = offsets[choice]
        previous = c[y] + options[choice,np.arange(width)]
        previous[columns<bounds[y]] = infinity
    seam = np.empty(height,dtype=np.int32)
    seam[-1] = np.argmin(previous)
    total = int(previous[seam[-1]])
    require(total < infinity, "No connected seam satisfies requested bounds")
    for y in range(height-1,0,-1):
        seam[y-1] = seam[y]+back[y,seam[y]]
    seam += first
    require(np.all(np.abs(np.diff(seam)) <= 1), "Disconnected path")
    require(np.all(seam>=bounds), "Seam violates a minimum constraint")
    return seam,total

def bottom_constraints(entry):
    ranges = entry.get("bottomCutMinimumRanges",[])
    require(isinstance(ranges,list), "bottomCutMinimumRanges must be a list")
    bounds = np.full(NATIVE,NATIVE-HALO,dtype=np.int32)
    for item in ranges:
        require(isinstance(item,dict), "Bottom constraint must be an object")
        values = [item.get(k) for k in ("xStart","xEndExclusive","minY")]
        require(all(type(v) is int for v in values), "Bottom constraint coordinates must be integers")
        x0,x1,min_y = values
        require(0<=x0<x1<=NATIVE, "Bottom constraint x range out of bounds")
        require(NATIVE-HALO<=min_y<NATIVE, "Bottom constraint leaves eligible115px halo")
        bounds[x0:x1] = np.maximum(bounds[x0:x1],min_y)
    return ranges,bounds

def remove_disconnected_corner_pixels(mask):
    """Keep core-connected ownership only; this changes selection, never RGB."""
    result = mask.copy()
    removed = 0
    for y0 in (0,NATIVE-HALO):
        for x0 in (0,NATIVE-HALO):
            corner = result[y0:y0+HALO,x0:x0+HALO]
            seen = np.zeros((HALO,HALO),dtype=bool)
            queue = deque()
            for y,x in zip(*np.nonzero(corner)):
                for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
                    ny,nx = int(y)+dy,int(x)+dx
                    gy,gx = y0+ny,x0+nx
                    if not (0<=ny<HALO and 0<=nx<HALO) and 0<=gy<NATIVE and 0<=gx<NATIVE and result[gy,gx]:
                        seen[y,x] = True
                        queue.append((int(y),int(x)))
                        break
            while queue:
                y,x = queue.popleft()
                for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
                    ny,nx = y+dy,x+dx
                    if 0<=ny<HALO and 0<=nx<HALO and corner[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx] = True
                        queue.append((ny,nx))
            removed += int(np.count_nonzero(corner & ~seen))
            corner &= seen
    return result,removed

def overlay_mask(base_crop,repair,constraints=None):
    require(base_crop.shape == (NATIVE,NATIVE,3) and repair.shape == base_crop.shape, "Overlay dimensions wrong")
    d = base_crop.astype(np.int32)-repair.astype(np.int32)
    cost = np.sum(d*d,axis=2,dtype=np.int64)
    # Native outermost pixels stay base; entire [115,1139) square is repair.
    left,lc = minimum_path(cost[:,:OVERLAP],1,HALO)
    right,rc = minimum_path(cost[:,-OVERLAP:],HALO,OVERLAP-1)
    right += NATIVE-OVERLAP
    top,tc = minimum_path(cost[:OVERLAP,:].T,1,HALO)
    ranges,bottom_bounds = bottom_constraints({"bottomCutMinimumRanges":constraints or []})
    bottom,bc = minimum_path(cost[-OVERLAP:,:].T,HALO,OVERLAP-1,
                             bottom_bounds-(NATIVE-OVERLAP))
    bottom += NATIVE-OVERLAP
    yy,xx = np.indices((NATIVE,NATIVE))
    mask = (xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:])
    mask,removed = remove_disconnected_corner_pixels(mask)
    require(mask[HALO:NATIVE-HALO,HALO:NATIVE-HALO].all(), "Repair core not fully owned")
    require(not mask[0].any() and not mask[-1].any() and not mask[:,0].any() and not mask[:,-1].any(), "Outer boundary changed")
    paths = {"leftXByY":left.tolist(),"rightXByY":right.tolist(),
             "topYByX":top.tolist(),"bottomYByX":bottom.tolist(),
             "bottomCutMinimumRanges":ranges,
             "bottomCutConstraintCoordinateSystem":"repair-local; xStart inclusive, xEndExclusive exclusive; cutY>=minY",
             "pathMaximumStep":1,
             "costSumSquaredRGB":{"left":lc,"right":rc,"top":tc,"bottom":bc},
             "coordinateSystem":"repair-local1254; add nativeBox origin for tile coordinates",
             "selectionRule":"repair iff x>=left[y] and x<right[y] and y>=top[x] and y<bottom[x]",
             "cornerRule":"intersection of4inside conditions; discard corner islands disconnected from mandatory core; final source-id map authoritative",
             "discardedDisconnectedCornerPixels":removed,
             "eligibleCuts":"outer115halo within each230px overlap; outermost1pixel preserved as base",
             "coreCrop":[HALO,HALO,NATIVE-HALO,NATIVE-HALO],
             "corePixelCountForcedToRepair":CORE*CORE}
    return mask,paths

def overlay_inputs(plan,origin,start_id):
    overlays = plan.get("overlays",[])
    require(isinstance(overlays,list), "overlays must be a list")
    selected = []
    names = set()
    for i,entry in enumerate(overlays):
        require(entry.get("id") and entry["id"] not in names, "Missing/duplicate overlay id")
        names.add(entry["id"])
        box = entry["nativeBox"]
        require(len(box)==4 and all(type(v) is int for v in box), "nativeBox must contain4 integers")
        x0,y0,x1,y1 = box
        require(x1-x0 == NATIVE and y1-y0 == NATIVE, "Overlay must be native1254square")
        require(0<=x0<x1<=SIZE and 0<=y0<y1<=SIZE, "Overlay extends beyond candidate")
        sid = start_id+i
        require(sid <= 65535, "PNG sourceId range exhausted")
        info = {"sourceId":sid,"overlayId":entry["id"],"file":entry["source"],
                "sha256":entry["sha256"],"generationRecord":entry["generationRecord"],
                "generationRecordSha256":entry["generationRecordSha256"],"nativeBox":box}
        pixels,info = validate_native(info,origin)
        ranges,_ = bottom_constraints(entry)
        info["bottomCutMinimumRanges"] = ranges
        selected.append((pixels,info))
    return selected

def compose_repairs(base_pixels,base_ids,sources,arrays,selected):
    pixels,ids = base_pixels.copy(),base_ids.copy()
    sources = list(sources)
    arrays = dict(arrays)
    protected = np.zeros((SIZE,SIZE),dtype=bool)
    seams = []
    for repair,info in selected:
        x0,y0,x1,y1 = info["nativeBox"]
        region = pixels[y0:y1,x0:x1]
        mask,path = overlay_mask(region,repair,info.get("bottomCutMinimumRanges",[]))
        require(not np.any(mask&protected[y0:y1,x0:x1]), "Overlay would overwrite another current-plan repair core")
        before = region.copy()
        region[mask] = repair[mask]
        ids[y0:y1,x0:x1][mask] = info["sourceId"]
        require(np.array_equal(region[~mask],before[~mask]), "Outside-mask pixels changed")
        protected[y0+HALO:y1-HALO,x0+HALO:x1-HALO] = True
        sources.append(info)
        arrays[info["sourceId"]] = repair
        seams.append({"id":info["overlayId"],"sourceId":info["sourceId"],
                      "nativeBox":info["nativeBox"],"selectedPixels":int(mask.sum()),**path})
    counts = verify_pixels(pixels,ids,sources,arrays)
    return pixels,ids,sources,counts,seams

def output_paths(tag):
    require(re.fullmatch(r"repair-v[1-9][0-9]*",tag) is not None, "Output tag must be repair-vN")
    out = ROOT/"tiles"
    return {
        "candidate":out/f"r03_c03.candidate-{tag}.png",
        "ids":out/f"r03_c03.source-id-{tag}.png",
        "seams":out/f"r03_c03.{tag}.seams.json",
        "record":out/f"r03_c03.{tag}.assembly.json"}

def prepare(plan_path,base_path):
    plan = read(plan_path)
    pixels,ids,sources,arrays,base = load_base(base_path)
    selected = overlay_inputs(plan,base["globalCoreBox"][:2],max(s["sourceId"] for s in sources)+1)
    return pixels,ids,sources,arrays,base,selected

def apply(plan_path,base_path,tag,replace):
    plan_hash = sha(plan_path)
    b,bi,sources,arrays,base,selected = prepare(plan_path,base_path)
    require(selected, "No overlays selected; base preserved and no duplicate output written")
    paths = output_paths(tag)
    require(all(p.resolve() not in {resolve(base["candidate"]),resolve(base["sourceIdMap"]),base_path} for p in paths.values()), "Output would replace base")
    if not replace:
        require(not any(p.exists() for p in paths.values()), "Repair output exists; choose new --tag or explicit --replace")
    pixels,ids,sources,counts,seams = compose_repairs(b,bi,sources,arrays,selected)
    # Freeze relevant input bytes again immediately before output.
    require(sha(plan_path)==plan_hash, "Plan changed during repair")
    require(sha(base_path)==base["recordSha256"] and sha(resolve(base["candidate"]))==base["candidateSha256"] and sha(resolve(base["sourceIdMap"]))==base["sourceIdMapSha256"], "Base changed during repair")
    for info in sources:
        require(sha(resolve(info["file"]))==info["sha256"] and sha(resolve(info["generationRecord"]))==info["generationRecordSha256"], "Source changed during repair")
    paths["candidate"].parent.mkdir(parents=True,exist_ok=True)
    png_write(paths["candidate"],pixels)
    mode = "L" if int(ids.max())<=255 else "I;16"
    png_write(paths["ids"],ids.astype(np.uint8 if mode=="L" else np.uint16))
    json_write(paths["seams"],{"overlap":OVERLAP,"halo":HALO,"core":CORE,
        "method":"independent4-side constrained minimum squared-error hard cuts; AND corner rule",
        "noFeather":True,"noScaling":True,"noColorRewrite":True,"overlays":seams})
    artifacts = [{"file":local(paths[k]),"sha256":sha(paths[k])} for k in ("candidate","ids","seams")]
    manifest = {
        "schemaVersion":1,"tile":"r03_c03","status":"candidate-repair-pending-100percent-visual-QA",
        "createdAt":datetime.now(timezone.utc).isoformat(),"formalAccepted":False,
        "candidate":{"file":local(paths["candidate"]),"sha256":sha(paths["candidate"])},
        "script":{"file":local(Path(__file__)),"sha256":sha(Path(__file__))},
        "plan":{"file":str(plan_path),"sha256":sha(plan_path)},"base":base,
        "globalCoreBox":base["globalCoreBox"],"outputSize":[SIZE,SIZE],
        "sourceIdMap":{"file":local(paths["ids"]),"mode":mode,"range":[int(ids.min()),int(ids.max())],
            "coordinateFormula":"sourceX=outputX-nativeBox[0]; sourceY=outputY-nativeBox[1]"},
        "composition":{"feather":False,"resample":False,"scale":False,"colorRewrite":False,
            "exactNativePixelOwnershipVerified":True,"repairCoreFullyForced":True},
        "sources":sources,"contributions":counts,"overlays":seams,"artifacts":artifacts,
        "visualQA":{"status":"pending","required":"Review all4repair boundaries, corners and the original sand defect at100%; provenance does not establish geometry/material acceptance."},
        "clientValidated":False,"navigationValidated":False,"capacity5000Validated":False}
    json_write(paths["record"],manifest)
    return {"candidate":str(paths["candidate"]),"record":str(paths["record"]),
            "pixelProvenanceVerified":SIZE*SIZE,"formalAccepted":False}

def check(plan_path,base_path,tag):
    paths = output_paths(tag)
    record = read(paths["record"])
    require(record["script"]["sha256"]==sha(Path(__file__)), "Repair script changed")
    require(record["plan"]["sha256"]==sha(plan_path), "Repair plan changed")
    for artifact in record["artifacts"]:
        require(sha(resolve(artifact["file"]))==artifact["sha256"], "Repair artifact changed")
    b,bi,sources,arrays,base,selected = prepare(plan_path,base_path)
    require(base==record["base"], "Base evidence changed")
    expected,expected_ids,sources,counts,seams = compose_repairs(b,bi,sources,arrays,selected)
    with Image.open(paths["candidate"]) as image:
        require(image.mode=="RGB" and image.size==(SIZE,SIZE), "Candidate dimensions/mode changed")
        require(np.array_equal(np.asarray(image),expected), "Repair pixels do not replay")
    with Image.open(paths["ids"]) as image:
        require(np.array_equal(np.asarray(image),expected_ids), "Source IDs do not replay")
    require(record["sources"]==sources and record["contributions"]==counts, "Source evidence/contributions differ")
    require(record["overlays"]==seams and read(paths["seams"])["overlays"]==seams, "Saved seam paths differ")
    return {"mechanicalValidation":"passed","pixelsVerified":SIZE*SIZE,"formalAccepted":False,"visualQA":"pending"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=DEFAULT_PLAN)
    parser.add_argument("--base-record",type=Path,default=DEFAULT_BASE)
    parser.add_argument("--tag",default="repair-v2")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--preflight",action="store_true",help="Read-only check; default. Missing overlays means[].")
    modes.add_argument("--apply",action="store_true",help="Write separate repair candidate, IDs and provenance.")
    modes.add_argument("--check",action="store_true",help="Read-only full replay/pixel check of repair outputs.")
    parser.add_argument("--replace",action="store_true",help="Allow replacing only outputs for this repair tag, never base.")
    args = parser.parse_args()
    plan_path,base_path = args.plan.resolve(),args.base_record.resolve()
    if args.apply:
        result = apply(plan_path,base_path,args.tag,args.replace)
    elif args.check:
        result = check(plan_path,base_path,args.tag)
    else:
        pixels,ids,sources,arrays,_,selected = prepare(plan_path,base_path)
        _,_,_,_,seams = compose_repairs(pixels,ids,sources,arrays,selected)
        result = {"preflight":"passed","baseSources":len(sources),"overlays":len(selected),
                  "pathConstraintsValidated":True,"pixelsVerified":SIZE*SIZE,
                  "bottomCutMinimumRanges":[s["bottomCutMinimumRanges"] for s in seams],
                  "outputsWritten":False}
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()

