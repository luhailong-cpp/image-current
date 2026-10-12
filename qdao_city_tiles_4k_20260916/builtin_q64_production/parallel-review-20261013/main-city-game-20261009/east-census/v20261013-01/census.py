"""Independent read-only east-zone metadata census; no image edits or production writes."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib, json, sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
SOURCE = Path(r"D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\main-city-game-20261009")
OUT = Path(__file__).resolve().parent
snapshot = {}
issues = []

def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()

def within(p):
    return p.resolve().is_relative_to(SOURCE.resolve())

def evidence(p, expected=None, image=False):
    p = Path(p)
    out = {"path": str(p), "exists": p.is_file()}
    if not within(p):
        out.update(readAllowed=False, status="external_reference_declared_only")
        return out
    if not p.is_file():
        return out
    st = p.stat()
    out.update(sha256=sha(p), bytes=st.st_size)
    snapshot[str(p)] = {"sha256":out["sha256"], "bytes":st.st_size, "mtimeNs":st.st_mtime_ns}
    if expected:
        out.update(recordedSha256=expected, hashMatchesRecord=(expected==out["sha256"]))
    if image:
        with Image.open(p) as im:
            out.update(pixels=list(im.size), mode=im.mode, format=im.format)
            if im.mode=="RGBA":
                out["alphaExtrema"] = list(im.getchannel("A").getextrema())
                out["allPixelsOpaque"] = out["alphaExtrema"]==[255,255]
            else:
                out["allPixelsOpaque"] = "transparency" not in im.info
            im.verify()
        out["pngIntegrityVerified"] = True
    return out

def read(p):
    p=Path(p)
    if not within(p): raise ValueError("Source is outside authorized directory")
    evidence(p)
    return json.loads(p.read_text(encoding="utf-8-sig"))

def pathof(v):
    if isinstance(v,str): return v
    if isinstance(v,dict): return v.get("path") or v.get("file")

def descriptor(v):
    p=pathof(v)
    if p:
        return evidence(p, v.get("sha256") if isinstance(v,dict) else None)

def gather_refs(d):
    refs=[]
    if isinstance(d,dict):
        for k,v in d.items():
            if k=="references" and isinstance(v,list):
                refs.extend(x for x in v if isinstance(x,dict))
            elif isinstance(v,(dict,list)):
                refs.extend(gather_refs(v))
    elif isinstance(d,list):
        for v in d: refs.extend(gather_refs(v))
    return refs

def selected_native(zone,tile_dir):
    if zone=="northeast":
        selection_path=tile_dir/"selected-native.json"
        selection=read(selection_path) if selection_path.is_file() else {f"p{r}{c}":f"p{r}{c}.png" for r in range(1,5) for c in range(1,5)}
    else:
        selection_path=tile_dir/"active-native-map.json"
        selection=read(selection_path) if selection_path.is_file() else {}
    natives=[]; refs=[]
    for pid, v in selection.items():
        name=v if str(v).endswith(".png") else str(v)+".png"
        p=tile_dir/"native"/name
        item={"id":pid, **evidence(p,image=True)}
        gp=Path(str(p)+".generation.json")
        if gp.is_file():
            gd=read(gp)
            item["generationRecord"]=evidence(gp)
            item["recordedNativeSha256"]=gd.get("sha256")
            item["nativeHashMatchesRecord"]=(item.get("sha256")==gd.get("sha256")) if item["exists"] else False
            item["actualModel"]=gd.get("actualModel")
            refs.extend(gather_refs(gd))
        natives.append(item)
    byref={}
    for r in refs:
        p=pathof(r)
        if p:
            key=(p.replace("\\","/").lower(),r.get("sha256"),r.get("role"))
            byref[key]={"path":p,"recordedSha256":r.get("sha256"),"role":r.get("role"),"status":"declared_in_selected_native_generation_record; external_pixels_not_reopened"}
    return {"selectionManifest":evidence(selection_path) if selection_path.is_file() else None,
            "selectionRule":"explicit selected-native overrides canonical p11..p44" if zone=="northeast" else "explicit active-native-map versions",
            "selectedNativeEntries":natives,"existingSelectedCoreCount":sum(x["exists"] for x in natives),
            "missingSelectedIds":[x["id"] for x in natives if not x["exists"]],
            "dimensions":dict(Counter("x".join(map(str,x.get("pixels",[]))) for x in natives if x["exists"])),
            "references":list(byref.values())}

def review_evidence(pdoc, tile_dir):
    result=[]
    for k,v in pdoc.items():
        if any(t in k.lower() for t in ("review","visualqa","nativeqa","repairqa","sourcereplay","sourceaudit","pixelreplay","verification")):
            p=pathof(v)
            if p:
                if not Path(p).is_absolute(): p=str(tile_dir/p)
                if Path(p).suffix.lower()==".json":
                    item={"role":k,**evidence(p,v.get("sha256") if isinstance(v,dict) else None)}
                    if item.get("exists") and within(Path(p)):
                        d=read(p)
                        item["recordedStatus"]={kk:vv for kk,vv in d.items() if any(q in kk.lower() for q in ("status","conclusion","observation","passed","externalneighbor","internalartqa","localrepairqa"))}
                    result.append(item)
    return result

records=[]
zone_docs={z:read(SOURCE/z/"progress.json") for z in ("northeast","southeast")}
adopted=read(SOURCE/"northeast/current-adopted-index-20261012.json")
adopted_by={x["tile"]:x for x in adopted["candidates"]}
groups=read(SOURCE/"northeast/connected-groups.json")["groups"]
for zone in ("northeast","southeast"):
    top={x["tile"]:x for x in zone_docs[zone]["tiles"]}
    for tile_dir in sorted((SOURCE/zone).glob("r??_c??")):
        tile=tile_dir.name; t=top.get(tile,{})
        pp=tile_dir/("tile-progress.json" if zone=="northeast" else "progress.json")
        pd=read(pp) if pp.is_file() else t
        exists_complete=(pd.get("completeCandidateCount",pd.get("complete4kCandidateCount",0))==1 or (zone=="southeast" and bool(t.get("candidate"))))
        selected=selected_native(zone,tile_dir)
        cp=(pd.get("candidate") or pathof(t.get("candidate"))) if exists_complete else None
        if isinstance(cp,dict):cp=pathof(cp)
        expected=(pd.get("candidateSha256") or (t.get("candidate",{}).get("sha256") if isinstance(t.get("candidate"),dict) else t.get("candidateSha256")))
        if zone=="northeast" and tile in adopted_by:
            cp=adopted_by[tile]["file"]; expected=adopted_by[tile]["sha256"]
        if zone=="southeast" and cp:
            for candidate_mp in (pd.get("assemblyManifest"), pd.get("repairManifest")):
                if candidate_mp and Path(candidate_mp).is_file():
                    md=read(candidate_mp); cd=md.get("candidate")
                    if isinstance(cd,dict) and pathof(cd)==cp and cd.get("sha256"):
                        expected=cd["sha256"]
        current=evidence(cp,expected,image=True) if cp else None
        candidate_declared=pd.get("candidate")
        if zone=="southeast":
            # Repaired current candidate selection outranks an old base assembly pointer.
            mp=pd.get("repairManifest") or pd.get("assemblyManifest") or pathof(t.get("manifest"))
        else:
            mp=str(cp)+".generation.json" if cp else (pd.get("partialAssemblyManifest") or pd.get("partialAssembly"))
        native_manifest=evidence(mp) if mp else None
        base_manifest=pd.get("assembly") if zone=="northeast" else pd.get("assemblyManifest")
        rec={"tile":tile,"zone":zone,"coordinate":[int(tile[1:3]),int(tile[5:7])],
             "worldCoreBox":[(int(tile[5:7])-1)*4096,(int(tile[1:3])-1)*4096,int(tile[5:7])*4096,int(tile[1:3])*4096],
             "currentCandidate":current,"complete4kCandidate":bool(current and current.get("exists") and current.get("pixels")==[4096,4096] and current.get("allPixelsOpaque")),
             "candidateDeclaredInTileProgress":candidate_declared,
             "nativeManifest":native_manifest,"baseAssemblyManifest":evidence(base_manifest) if base_manifest and base_manifest!=mp else None,
             "internalStatus":{"workerStatus":pd.get("status"),"internalArtQA":pd.get("internalArtQA"),"internalSeamQA":pd.get("internalSeamQA"),"internalPassed4kCount":pd.get("internalPassed4kCount",0)},
             "formalStatus":{"formalAccepted":False,"externalNeighborSeamQA":pd.get("externalNeighborSeamQA",t.get("externalNeighborSeamQA")),"externalPassed4kCount":pd.get("externalPassed4kCount",0)},
             "progressEvidence":evidence(pp) if pp.is_file() else evidence(SOURCE/zone/"progress.json"),"progressUpdatedAt":pd.get("updatedAt"),
             "existingSelectedCoreCount":selected["existingSelectedCoreCount"],"missingSelectedIds":selected["missingSelectedIds"],
             "selectionManifest":selected["selectionManifest"],"selectionRule":selected["selectionRule"],"selectedNativeDimensions":selected["dimensions"],
             "selectedNativeEntries":selected["selectedNativeEntries"],"references":selected["references"],
             "reviewEvidence":review_evidence(pd,tile_dir),"crossZoneFormalEvidence":[],"nextStepRecorded":pd.get("nextStep")}
        if zone=="northeast":
            rec["connectedGroupEvidence"]=[]
            for g in groups:
                if tile in g["sources"]:
                    sources={tid:dict(v) for tid,v in g["sources"].items()}
                    matches=all(Path(v["file"]).is_file() and sha(Path(v["file"]))==v["sha256"] for v in sources.values())
                    rec["connectedGroupEvidence"].append({"group":g["group"],"review":evidence(g["review"],g.get("reviewSha256")),"sourceManifest":evidence(g["sourceManifest"]),"sourceHashesMatchCurrent":matches,"sources":sources,"scope":"within northeast group only; not all exterior edges or cross-zone acceptance"})
        if zone=="southeast" and current:
            tc=t.get("candidate",{})
            if tc.get("path")!=current["path"]:
                rec["staleZoneDelivery"]={"zoneProgressCandidate":tc,"status":"superseded_by_newer_tile_progress"}
            latest=tile_dir/"candidate/latest-assembly.json"
            if latest.is_file():
                ld=read(latest)
                if pathof(ld.get("candidate"))!=current["path"]:
                    rec["staleLatestAssemblyPointer"]={"path":str(latest),"candidate":ld.get("candidate"),"status":"base_assembly_pointer_older_than_explicit_repair_selection"}
        if exists_complete and not rec["complete4kCandidate"]:issues.append({"tile":tile,"issue":"recorded complete candidate failed file/size/opacity verification"})
        if current and current.get("hashMatchesRecord") is False:issues.append({"tile":tile,"issue":"current candidate hash differs from selected record"})
        records.append(rec)

rules={"formalTilePixels":[4096,4096],"fullCanvasPixels":[65536,65536],"tileOriginFormula":"((column-1)*4096,(row-1)*4096)",
       "nativePatchPlan":{"nativePixels":[1254,1254],"coreCropHalfOpen":[115,115,1139,1139],"corePixels":[1024,1024],"grid":[4,4]},
       "safeIndependentAssembly":"Only paste already selected 4096-square candidates at integer tile offsets. Preserve all existing candidate pixels and defects. Do not rerun production compositors, apply new feathering, rescale, draw missing areas, or claim formal acceptance.",
       "historicalAssemblyNote":"NE records generally use exact core crops plus recorded native repair overlays; SE records also preserve per-source overlap/masks/repair recipes. Census verifies selected files and metadata, not a new pixel replay of every historic recipe.",
       "referenceValidation":"Recorded reference paths/hashes collected from selected core generation records. External reference pixels were not opened in this source-restricted census. Actual model stays null/unconfirmed.",
       "formalAcceptance":"No east-zone tile has all exterior edges formally accepted. Local/group passes do not constitute whole-map completion."}

coords={r["tile"]:r for r in records}
coverage={}
for zone,rows in (("northeast",range(1,9)),("southeast",range(9,17))):
    targets=[f"r{r:02d}_c{c:02d}" for r in rows for c in range(9,17)]
    full=[t for t in targets if t in coords and coords[t]["complete4kCandidate"]]
    partial=[t for t in targets if t in coords and not coords[t]["complete4kCandidate"] and coords[t]["existingSelectedCoreCount"]]
    coverage[zone]={"targetTileCount":64,"completeCandidateCount":len(full),"completeCandidates":full,
       "partialCoordinates":partial,"missingCompleteCandidates":[t for t in targets if t not in full],
       "coordinatesWithNoExistingSelectedCore":[t for t in targets if t not in coords or not coords[t]["existingSelectedCoreCount"]],
       "formalAcceptedCount":0,"topProgressCountsSnapshot":{k:v for k,v in zone_docs[zone].items() if k.endswith("Count") and not isinstance(v,(list,dict))}}

review_queue=[
 {"pair":["r06_c13","r07_c13"],"status":"old north-final report hashes old r07_c13 f615...; current r07_c13 179d... differs; verify top-edge pixel identity or re-review seam","evidence":str(SOURCE/"northeast/r07_c13/qa/north-final-20261011/report.json")},
 {"pair":["r06_c14","r07_c14"],"status":"current source hashes match r07_c14 internal-seam-review; north 4 segments already reviewed; old delivery open-side list is stale","evidence":str(SOURCE/"northeast/r07_c14/qa/internal-seam-review.json")},
 {"pair":["r13_c13","r13_c14"],"status":"west parasol geometry still failed; frozen four-tile corner pending"},
 {"pair":["r13_c14","r14_c14"],"status":"far-east local repair passed; old north x2842/2874 transition unresolved; no whole-edge pass"},
 {"pair":["r13_c15","r14_c15"],"status":"north N01 x230 board joint locally repaired; full north edge pending"},
 {"pair":["r14_c14","r14_c15"],"status":"west W01/W02/W03 and material pending/failed; r14c14 far-east review used older r14c15 source so treat shared-edge evidence conservatively"},
 {"pair":["r14_c14","r15_c14"],"status":"north N01/N02 remain failed in r15c14 current QA; neighbor r14c14 changed; re-review current true cores"},
 {"pair":["r15_c13","r15_c14"],"status":"west W01/W02 remain failed in r15c14 current QA"},
 {"pair":["r13_c15","r13_c16"],"status":"geometry local connection with stone material watch; no formal whole-edge acceptance"},
 {"pair":["r14_c13","r15_c13"],"status":"north local pass with texture watch; full external acceptance pending"},
 {"pair":["r15_c13","r16_c13"],"status":"r16c13 full candidate exists but internal and external visual QA pending"},
 {"boundary":"NE/SE row8-row9 columns9..16","status":"neighbor row9 source absent in southeast current inventory; no complete cross-zone pair"},
 {"boundary":"NW/NE col8-col9 rows1..8","status":"no c09 candidate in northeast current inventory; no complete cross-zone pair"},
 {"boundary":"SW/SE col8-col9 rows9..16","status":"no c09 candidate in southeast current inventory; no complete cross-zone pair"}
]

ref_summary={}
for r in records:
 for ref in r["references"]:
  p=ref["path"].replace("\\","/").lower()
  if any(k in p for k in ("tianyong-spring-natural-stone-v9","tianyong-natural-stone-detail-v1","mail-ui-v1","mail-daoist-style","team-ui-v2")):
   k=(p,ref.get("recordedSha256")); ref_summary.setdefault(k,{"path":ref["path"],"recordedSha256":ref.get("recordedSha256"),"tiles":[]})["tiles"].append(r["tile"])

for fn,data in (("current-tiles.json",records),("coverage.json",coverage),("assembly-rules.json",rules),("review-queue.json",review_queue),("reference-summary.json",list(ref_summary.values())),("issues.json",issues)):
    with (OUT/fn).open("x",encoding="utf-8") as f:json.dump(data,f,ensure_ascii=False,indent=2)

changed=[]
for p,initial in snapshot.items():
    q=Path(p)
    if not q.is_file():changed.append({"path":p,"change":"source_removed"});continue
    st=q.stat()
    if st.st_size!=initial["bytes"] or st.st_mtime_ns!=initial["mtimeNs"]:
        changed.append({"path":p,"change":"source_stat_changed","initial":initial,"currentSha256":sha(q)})
with (OUT/"input-snapshot.json").open("x",encoding="utf-8") as f:json.dump(snapshot,f,ensure_ascii=False,indent=2)
validation={"finishedAtUtc":datetime.now(timezone.utc).isoformat(),"sourceFileCount":len(snapshot),"sourceChangesDuringCensus":changed,"status":"current_at_capture" if not changed else "stale_recheck_required","actualModel":None,"generationCalls":0,"productionWrites":0,"imageWrites":0,"scope":"metadata/file-integrity census; existing visual evidence reused; no new visual verdict"}
with (OUT/"snapshot-validation.json").open("x",encoding="utf-8") as f:json.dump(validation,f,ensure_ascii=False,indent=2)
print(json.dumps({"out":str(OUT),"records":len(records),"coverage":{z:{k:v for k,v in c.items() if k in ("completeCandidateCount","partialCoordinates","formalAcceptedCount")} for z,c in coverage.items()},"issues":issues,"snapshot":validation},ensure_ascii=False,indent=2))
