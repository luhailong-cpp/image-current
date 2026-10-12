"""Build review artifacts only; never edits runtime PNGs or generation records."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from collections import defaultdict
import argparse, hashlib, json, re

BASE=Path(__file__).resolve().parents[1]
SPECS={"hit":(6,40,"受击"),"attack":(12,30,"普攻"),"cast":(16,45,"施法")}
QA=BASE/"qa"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):
    try: return Path(p).resolve().relative_to(BASE).as_posix()
    except ValueError: return str(p).replace("\\","/")
def resolve(raw,record_path=None):
    p=Path(str(raw).replace("\\","/"))
    if p.is_absolute(): return p
    options=[BASE/p, record_path.parent/p if record_path else BASE/p]
    return next((x for x in options if x.is_file()),options[0])
def read_json(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def native_removed(r):
    c=r.get("cleanup",{})
    return any(v is True and any(t in k.lower() for t in ("deleted","removed")) for k,v in c.items()) or r.get("derivedFrom",{}).get("sourceRetained") is False
def verify_historical_revision(path,expected,actual,revision,rp):
    """Verify both hashes against the exact fixed-direction export register."""
    if not isinstance(revision,dict):
        return {"verified":False,"reason":"missing_historical_revision"}
    if revision.get("sha256AtGeneration")!=expected or revision.get("currentSha256")!=actual:
        return {"verified":False,"reason":"historical_revision_hashes_do_not_match"}
    raw=revision.get("record")
    if not isinstance(raw,str) or not raw:
        return {"verified":False,"reason":"missing_export_registration_path"}
    register_path=resolve(raw,rp)
    required_path=(BASE/"export-registration.json").resolve()
    if register_path.resolve()!=required_path:
        return {"verified":False,"reason":"unexpected_export_registration_path"}
    if not register_path.is_file():
        return {"verified":False,"reason":"export_registration_missing"}
    try:
        registration=read_json(register_path)
        matches=[item for item in registration.get("frames",[])
                 if isinstance(item,dict) and isinstance(item.get("file"),str)
                 and str(resolve(item["file"],register_path).resolve()).lower()==str(path.resolve()).lower()]
    except (OSError,ValueError,TypeError,AttributeError) as ex:
        return {"verified":False,"reason":"invalid_export_registration","detail":str(ex)}
    if len(matches)!=1:
        return {"verified":False,"reason":"export_registration_file_not_unique"}
    item=matches[0]
    if item.get("beforeSha256")!=expected or item.get("afterSha256")!=actual:
        return {"verified":False,"reason":"export_registration_hashes_do_not_match"}
    return {"verified":True,"record":rel(register_path),"recordSha256":sha(register_path),
            "file":item["file"],"beforeSha256":expected,"afterSha256":actual}
def references(r,rp):
    found=[]
    declared_removed_inputs=set()
    def add(kind,raw,expected=None,removed=False,historical=None):
        if not isinstance(raw,str) or not raw or raw.startswith(("http:","https:","data:")): return
        p=resolve(raw,rp)
        entry={"kind":kind,"path":str(p),"expectedSha256":expected,"exists":p.is_file()}
        if entry["exists"]:
            actual=sha(p) if expected else None
            entry.update(actualSha256=actual,status="matched" if expected and actual==expected else "sha_mismatch" if expected else "exists_unhashed")
            if expected and actual!=expected and historical is not None:
                proof=verify_historical_revision(p,expected,actual,historical,rp)
                entry["historicalRevisionCheck"]=proof
                if proof["verified"]:entry["status"]="historical_revision_verified"
        else: entry["status"]="declared_removed" if removed else "missing"
        found.append(entry)
    add("prompt",r.get("prompt"))
    evidence=r.get("evidence",{})
    if isinstance(evidence,dict):
        for key in ("receipt","receiptPath"): add(key,evidence.get(key))
    for ref in r.get("references",[]):
        if isinstance(ref,dict):
            raw=ref.get("path",ref.get("file"))
            removed=ref.get("sourceRetained") is False or ref.get("retained") is False or ref.get("deleted") is True
            if removed and raw:declared_removed_inputs.add(str(resolve(raw,rp)).lower())
            add("input_reference",raw,ref.get("sha256"),removed,historical=ref.get("historicalRevision"))
        elif isinstance(ref,str): add("input_reference",ref)
    for value in r.get("submittedParameters",{}).get("referenced_image_paths",[]):
        add("submitted_reference",value,removed=str(resolve(value,rp)).lower() in declared_removed_inputs)
    deleted=native_removed(r)
    native_path=None; native_hash=None
    for key in ("native","nativeOutput","derivedFrom"):
        val=r.get(key,{})
        if isinstance(val,dict):
            path=val.get("path",val.get("file"))
            if path:
                add(key,path,val.get("sha256"),deleted or val.get("sourceRetained") is False)
                native_path=path
            native_hash=native_hash or val.get("sha256")
    if r.get("nativeSourcePath") and r["nativeSourcePath"]!=native_path: add("nativeSourcePath",r["nativeSourcePath"],native_hash,deleted)
    return found
def suggested_event(action,n,count):
    if n==count:return "recovery_end"
    return {("hit",3):"hit_peak",("attack",7):"attack_contact",("cast",9):"cast_release",("cast",10):"cast_peak"}.get((action,n))
def inspect_frame(action,direction,n,count,duration):
    name=f"{n:02d}.png"; path=BASE/"runtime"/action/direction/name
    entry={"id":f"{action}_{direction}_{n:02d}","frame":n,"action":action,"direction":direction,"file":rel(path),"exists":path.is_file(),"width":None,"height":None,"size":None,"durationMs":duration,"pivot":[0.5,0.08],"anchor":[512,942],"anchorOrigin":"top-left","event":suggested_event(action,n,count),"eventScope":"suggested_visual_marker_not_game_logic","sha256":None,"pixelSha256":None,"sourceRecord":None,"visualStatus":"not_reviewed_by_builder","errors":[]}
    if not entry["exists"]:
        entry["errors"].append("missing_frame")
        return entry
    try:
        with Image.open(path) as im:
            im.load()
            entry.update(width=im.width,height=im.height,size=[im.width,im.height],mode=im.mode,format=im.format,sha256=sha(path))
            rgba=im.convert("RGBA"); alpha=rgba.getchannel("A")
            entry["pixelSha256"]=hashlib.sha256(rgba.tobytes()).hexdigest()
            hist=alpha.histogram()
            entry.update(alphaExtrema=list(alpha.getextrema()),alphaBBox=alpha.getbbox(),visibleBBox=alpha.point(lambda x:255 if x>16 else 0).getbbox(),transparentPixels=hist[0],semiTransparentPixels=sum(hist[1:255]))
            entry["edgeAlphaMax"]=max(max(alpha.crop(box).get_flattened_data()) for box in [(0,0,1,im.height),(im.width-1,0,im.width,im.height),(0,0,im.width,1),(0,im.height-1,im.width,im.height)])
            if im.size!=(1024,1024):entry["errors"].append("incorrect_dimensions")
            if im.mode!="RGBA":entry["errors"].append("incorrect_mode")
            if hist[0]==0 or hist[255]==0:entry["errors"].append("missing_transparent_or_opaque_pixels")
    except Exception as ex:
        entry["errors"].append("unreadable_png: "+str(ex))
        return entry
    candidates=[path.with_suffix(".png.generation.json"),BASE/"provenance"/action/direction/f"{n:02d}.generation.json"]
    available=[x for x in candidates if x.is_file()]
    if not available:
        entry["errors"].append("missing_generation_record")
        return entry
    entry["generationRecordCandidates"]=[rel(x) for x in available]
    records=[]
    for rp in available:
        try:
            r=read_json(rp); expected=r.get("sha256",r.get("export",{}).get("sha256"))
            records.append((rp,r,expected))
        except Exception as ex:entry["errors"].append("invalid_generation_record: "+rel(rp)+": "+str(ex))
    if not records:return entry
    rp,r,expected=next((x for x in records if x[2]==entry["sha256"]),records[0])
    entry["sourceRecord"]=rel(rp)
    entry["recordSha256"]=sha(rp)
    entry["sourceRecordSha256Matches"]=expected==entry["sha256"]
    if expected!=entry["sha256"]:entry["errors"].append("output_sha_mismatch_or_missing")
    entry["referenceChecks"]=references(r,rp)
    for item in entry["referenceChecks"]:
        if item["status"] in ("missing","sha_mismatch"):entry["errors"].append(item["kind"]+"_"+item["status"]+": "+item["path"])
    if not r.get("prompt"):entry["errors"].append("missing_prompt_field")
    if not r.get("evidence",{}).get("receipt"):entry["errors"].append("missing_receipt_field")
    if not r.get("references"):entry["errors"].append("missing_input_references")
    entry["configTarget"]=r.get("configSnapshot")
    entry["actualModel"]=r.get("actualModel")
    entry["actualQuality"]=r.get("actualQuality")
    entry["visualStatus"]=r.get("visualReview",{})
    return entry
def font(size):
    for p in (Path("C:/Windows/Fonts/msyh.ttc"),Path("C:/Windows/Fonts/arial.ttf")):
        if p.is_file():return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()
def contact_sheet(group,background):
    tile=300; label=36; cols=4; rows=(len(group["frames"])+3)//4
    bg=(244,239,225,255) if background=="ivory" else (22,37,57,255)
    fg=(38,57,50) if background=="ivory" else (231,231,215)
    sheet=Image.new("RGBA",(cols*tile,rows*(tile+label)+56),bg); draw=ImageDraw.Draw(sheet)
    draw.text((14,12),group["id"]+"  "+str(group["durationMs"])+"ms/frame  "+background,font=font(22),fill=fg)
    for i,item in enumerate(group["frames"]):
        x=(i%cols)*tile;y=(i//cols)*(tile+label)+56
        if item["exists"]:
            with Image.open(BASE/item["file"]) as im:
                thumb=im.convert("RGBA").resize((tile,tile),Image.Resampling.LANCZOS)
                sheet.alpha_composite(thumb,(x,y))
        else: draw.text((x+80,y+130),"MISSING "+str(item["frame"]),font=font(18),fill=fg)
        draw.text((x+10,y+tile+6),f'{item["frame"]:02d}  {item["event"] or ""}',font=font(16),fill=fg)
    out=QA/(group["id"]+"-"+background+".png");sheet.convert("RGB").save(out)
    return rel(out)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--strict",action="store_true",help="Exit 1 when expected 68-frame package has missing frames or any technical errors.")
    parser.add_argument("--no-contact-sheets",action="store_true")
    args=parser.parse_args();QA.mkdir(exist_ok=True)
    groups=[];frames=[]
    for action,(count,ms,label) in SPECS.items():
        for direction in ("E","W"):
            rows=[inspect_frame(action,direction,n,count,ms) for n in range(1,count+1)]
            group={"id":action+"-"+direction,"action":action,"label":label,"direction":direction,"expectedFrames":count,"presentFrames":sum(x["exists"] for x in rows),"durationMs":ms,"totalDurationMs":count*ms,"frames":rows}
            if not args.no_contact_sheets:group["contactSheets"]=[contact_sheet(group,bg) for bg in ("ivory","navy")]
            groups.append(group);frames.extend(rows)
    hashes=defaultdict(list);pixels=defaultdict(list)
    for item in frames:
        if item["sha256"]:hashes[item["sha256"]].append(item["id"])
        if item["pixelSha256"]:pixels[item["pixelSha256"]].append(item["id"])
    duplicates=[ids for ids in hashes.values() if len(ids)>1];pixel_duplicates=[ids for ids in pixels.values() if len(ids)>1]
    expected={str((BASE/x["file"]).resolve()) for x in frames}
    extras=[rel(p) for p in (BASE/"runtime").rglob("*.png") if str(p.resolve()) not in expected]
    missing=[x["file"] for x in frames if not x["exists"]]
    errors=[{"frame":x["id"],"errors":x["errors"]} for x in frames if x["errors"]]
    summary={"expectedFrames":68,"presentFrames":sum(x["exists"] for x in frames),"missingFrames":missing,"errorFrames":errors,"duplicateFileHashes":duplicates,"duplicatePixelHashes":pixel_duplicates,"extraRuntimePngs":extras,"checksPassForPresentFrames":not [x for x in errors if x["errors"]!=["missing_frame"]] and not duplicates and not pixel_duplicates,"completeTechnicalPass":not missing and not errors and not duplicates and not pixel_duplicates and not extras}
    review_path=QA/'visual-review-final.json'
    playback_review={"status":"not_recorded","performedByBuildScript":False}
    if review_path.is_file():
        review=read_json(review_path)
        reviewed={x['file']:x['sha256'] for x in review.get('frames',[])}
        matches=all(reviewed.get(x['file'])==x['sha256'] for x in frames) and len(reviewed)==68
        playback_review={"status":review.get('status') if matches else 'stale_after_frame_change',"record":rel(review_path),"recordSha256":sha(review_path),"matchesCurrentFrames":matches,"performedByBuildScript":False}
    data={"schemaVersion":1,"pet":"砚羽灵","petId":"05-yanyuling","generatedAt":datetime.now(timezone.utc).isoformat(),"canvas":[1024,1024],"pivot":[0.5,0.08],"anchor":[512,942],"anchorStatus":"fixed_direction_export_reference_approximate","sourceImagesModified":False,"playbackReview":playback_review,"clientIntegration":"not_verified","summary":summary,"groups":groups,"frames":frames}
    (BASE/"manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    (QA/"technical-validation.json").write_text(json.dumps({"generatedAt":data["generatedAt"],**summary,"referenceChecks":[{"frame":x["id"],"checks":x.get("referenceChecks",[])} for x in frames if x["exists"]]},ensure_ascii=False,indent=2),encoding="utf-8")
    template=(BASE/"tools/preview.template.html").read_text(encoding="utf-8")
    embedded=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
    (BASE/"preview.html").write_text(template.replace("__MANIFEST_JSON__",embedded),encoding="utf-8")
    print(json.dumps({"manifest":str(BASE/"manifest.json"),"preview":str(BASE/"preview.html"),**summary},ensure_ascii=False,indent=2))
    if args.strict and not summary["completeTechnicalPass"]:raise SystemExit(1)
if __name__=="__main__":main()
