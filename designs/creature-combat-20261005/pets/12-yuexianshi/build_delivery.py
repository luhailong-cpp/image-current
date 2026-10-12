"""Build metadata/contact previews from existing real runtime frames only."""
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import hashlib, json, math
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
SPECS={"hit":(6,40),"attack":(12,30),"cast":(16,45)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def save(p,data):Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
def resolve(p):
    path=Path(p)
    return path if path.is_absolute() else ROOT/path
def contact(action,direction,count):
    tile=256;label=24
    sheet=Image.new("RGB",(tile*4,(tile+label)*math.ceil(count/4)),(38,46,51));draw=ImageDraw.Draw(sheet)
    for index in range(1,count+1):
        x=((index-1)%4)*tile;y=((index-1)//4)*(tile+label)
        for yy in range(0,tile,16):
            for xx in range(0,tile,16):
                c=(58,68,72) if (xx//16+yy//16)%2 else (48,58,62)
                draw.rectangle((x+xx,y+yy,x+xx+15,y+yy+15),fill=c)
        source=ROOT/"runtime"/action/direction/f"{index:02}.png"
        if source.exists():
            with Image.open(source) as im:thumb=im.convert("RGBA").resize((tile,tile),Image.Resampling.LANCZOS)
            sheet.paste(thumb,(x,y),thumb);text=f"{action} {direction} {index:02}"
        else:text=f"{action} {direction} {index:02} MISSING"
        draw.text((x+8,y+tile+5),text,fill=(240,235,220))
    dest=ROOT/"preview"/f"{action}-{direction}-contact.png"
    dest.parent.mkdir(parents=True,exist_ok=True)
    pending=dest.with_suffix(".pending.png")
    sheet.save(pending,format="PNG")
    pending.replace(dest)
    return dest.relative_to(ROOT).as_posix()
def main():
    review_path=ROOT/"records"/"sequence-continuity-review.json"
    sequence_review=read(review_path) if review_path.exists() else {}
    static_failed=sequence_review.get("status")=="requires-repair"
    errors=[];warnings=[];missing=[];frames=[];groups=[];hashes=[];pixel_groups=defaultdict(list);file_groups=defaultdict(list)
    for action,(count,duration) in SPECS.items():
        for direction in ("E","W"):
            group=[];available=0
            for index in range(1,count+1):
                relative=f"runtime/{action}/{direction}/{index:02}.png";record_relative=f"records/{action}-{direction}/{index:02}.generation.json";path=ROOT/relative;rp=ROOT/record_relative
                event="impact" if action=="hit" and index==3 else "release" if (action=="attack" and index==7) or (action=="cast" and index==11) else None
                frame={"file":relative,"action":action,"direction":direction,"frame":index,"durationMs":duration,"pivot":[0.5,0.08],"anchorTopLeft":[512,942],"event":event,"record":record_relative}
                if not path.exists():
                    missing.append(relative);frame.update({"available":False,"visualStatus":"missing"});group.append(frame);frames.append(frame);continue
                available+=1;digest=sha(path);hashes.append(f"{digest}  {relative}");file_groups[digest].append(relative)
                with Image.open(path) as im:
                    actual_size=list(im.size);mode=im.mode;format_=im.format;rgba=im.convert("RGBA");alpha=rgba.getchannel("A");extrema=list(alpha.getextrema());hist=alpha.histogram()
                    pixelhash=hashlib.sha256(rgba.tobytes()).hexdigest();bbox=alpha.getbbox()
                    transparency={"range":extrema,"fullyTransparentPixels":hist[0],"partialAlphaPixels":sum(hist[1:255]),"fullyOpaquePixels":hist[255],"bbox":bbox}
                if actual_size!=[1024,1024] or mode!="RGBA" or format_!="PNG":errors.append({"file":relative,"error":"format_contract","actual":[actual_size,mode,format_]})
                if not hist[0] or not sum(hist[1:]):errors.append({"file":relative,"error":"missing_alpha_or_empty_subject"})
                pixel_groups[pixelhash].append(relative)
                frame.update({"available":True,"width":actual_size[0],"height":actual_size[1],"format":format_,"mode":mode,"sha256":digest,"pixelSha256":pixelhash,"alpha":transparency,"visualStatus":"unreviewed"})
                if not rp.exists():errors.append({"file":relative,"error":"generation_record_missing"})
                else:
                    try:rec=read(rp)
                    except Exception as ex:errors.append({"file":relative,"error":"record_unreadable","details":str(ex)});rec={}
                    for field in ("configSnapshot","submittedParameters","actualModel","actualQuality","prompt","references","native","derivedFrom","evidence"):
                        if field not in rec:errors.append({"file":relative,"error":"record_field_missing","field":field})
                    if rec.get("sha256")!=digest:errors.append({"file":relative,"error":"record_sha_mismatch"})
                    if rec.get("file")!=relative:errors.append({"file":relative,"error":"record_file_mismatch"})
                    if (rec.get("action"),rec.get("direction"),rec.get("frame"),rec.get("durationMs"))!=(action,direction,index,duration):errors.append({"file":relative,"error":"record_identity_or_duration_mismatch"})
                    op=rec.get("operation",{})
                    if op.get("resize")!=[960,960] or op.get("offset")!=[32,16] or op.get("perFrameAlignment") is not False:errors.append({"file":relative,"error":"nonuniform_export_transform"})
                    core={Path(ref["path"]).name for ref in rec.get("references",[])}
                    if not {"12-yuexianshi-E.png","12-yuexianshi-W.png","01-character-ui-no-affinity.png"}.issubset(core):errors.append({"file":relative,"error":"missing_required_identity_or_style_input"})
                    for kind,value in (("prompt",rec.get("prompt")),("receipt",rec.get("evidence",{}).get("receipt"))):
                        if not value or not resolve(value).exists():errors.append({"file":relative,"error":kind+"_missing","path":value})
                    ref_checks=[]
                    for ref in rec.get("references",[]):
                        ref_path=resolve(ref["path"]);exists=ref_path.exists();historical=ref.get("historicalGenerationInput") is True or "generated_images" in str(ref_path);entry={"path":ref["path"],"role":ref.get("role"),"exists":exists,"historicalGenerationInput":historical}
                        if exists:
                            entry["shaMatches"]=not ref.get("sha256") or sha(ref_path)==ref["sha256"]
                            if not entry["shaMatches"]:errors.append({"file":relative,"error":"reference_sha_mismatch","path":ref["path"]})
                        elif historical:warnings.append({"file":relative,"warning":"historical_generation_input_not_retained","path":ref["path"]})
                        else:errors.append({"file":relative,"error":"current_identity_or_style_reference_missing","path":ref["path"]})
                        ref_checks.append(entry)
                    source=rec.get("derivedFrom",{});source_path=resolve(source["path"]) if source.get("path") else None
                    if source_path and source_path.exists() and sha(source_path)!=source.get("sha256"):errors.append({"file":relative,"error":"native_source_sha_mismatch"})
                    frame.update({"source":source,"native":rec.get("native"),"prompt":rec.get("prompt"),"references":ref_checks,"actualModel":rec.get("actualModel"),"actualQuality":rec.get("actualQuality"),"visualStatus":rec.get("visualStatus","unreviewed"),"visualReview":rec.get("visualReview")})
                group.append(frame);frames.append(frame)
            expected={f"{i:02}.png" for i in range(1,count+1)}
            for e in (ROOT/"runtime"/action/direction).glob("*.png"):
                if e.name not in expected:errors.append({"file":e.relative_to(ROOT).as_posix(),"error":"unexpected_runtime_png"})
            groups.append({"id":f"{action}-{direction}","action":action,"direction":direction,"expectedFrames":count,"availableFrames":available,"durationMs":duration,"totalDurationMs":count*duration,"contact":contact(action,direction,count),"frames":group,"visualStatus":"read individual records; no automatic visual approval","playbackStatus":"pending manual review"})
    duplicates=[v for v in pixel_groups.values() if len(v)>1]
    if duplicates:errors.append({"error":"duplicate_runtime_pixels","groups":duplicates})
    complete=len(missing)==0 and not errors
    technical={"status":"passed" if complete else "partial" if missing and not errors else "failed","expectedFrames":68,"presentFrames":sum(x["available"] for x in frames),"missing":missing,"errors":errors,"warnings":warnings,"duplicatePixels":duplicates,"duplicateFiles":[v for v in file_groups.values() if len(v)>1],"checkedAt":datetime.now(timezone.utc).isoformat(),"limits":"Format/hash/completeness checks do not establish animation, art or client approval."}
    manifest={"schemaVersion":1,"character":"12-yuexianshi","name":"月弦师","status":"assets-complete-playback-pending" if complete else "partial","expectedFrames":68,"presentFrames":technical["presentFrames"],"technicalStatus":technical["status"],"visualStatus":"per-frame records and manual group review; not inferred from technical checks","playbackStatus":"not-verified-browser-policy-blocked","playbackEvidence":"records/cast-E/browser-policy-rejection.json","clientStatus":"not-integrated","generatedAt":technical["checkedAt"],"groups":groups,"frames":frames}
    if static_failed:
        manifest.update({"status":"assets-present-static-review-failed" if complete else "partial","visualStatus":"static-review-failed","acceptanceStatus":"requires-repair","staticReviewRecord":"records/sequence-continuity-review.json"})
        affected_groups={group for finding in sequence_review.get("confirmedFindings",[]) for group in finding.get("affectedGroups",[])}
        affected_files={file for finding in sequence_review.get("confirmedFindings",[]) for file in finding.get("affectedFiles",[])}
        for group in groups:
            group["currentStaticReview"]={"status":"requires-repair" if group["id"] in affected_groups else "reviewed-static-only","record":"records/sequence-continuity-review.json"}
        for frame in frames:
            frame["currentStaticReview"]={"status":"requires-repair" if frame["file"] in affected_files else "see-group-review","record":"records/sequence-continuity-review.json"}
    elif sequence_review.get("status")=="static-repairs-complete-playback-pending":
        manifest.update({"status":"assets-complete-playback-pending" if complete else "partial","visualStatus":"static-reviewed-after-guard-repair","acceptanceStatus":"static-reviewed-playback-pending","staticReviewRecord":"records/sequence-continuity-review.json"})
        for group in groups:
            group["currentStaticReview"]={"status":"reviewed-static-after-repair","record":"records/sequence-continuity-review.json"}
    save(ROOT/"manifest.json",manifest);save(ROOT/"technical-validation.json",technical)
    save(ROOT/"preview"/"contact-records.json",[{"file":g["contact"],"sha256":sha(ROOT/g["contact"]),"derivedFrom":[{"path":f["file"],"sha256":f.get("sha256"),"generationRecord":f["record"]} for f in g["frames"] if f["available"]],"operation":"uniform resize each final frame to256 square; composite with checkerboard and frame labels, four columns; review-only contact sheet"} for g in groups])
    (ROOT/"SHA256SUMS").write_text("\n".join(hashes)+"\n",encoding="utf-8")
    (ROOT/"preview"/"manifest.js").write_text("window.SPRITE_MANIFEST = "+json.dumps(manifest,ensure_ascii=False)+";\n",encoding="utf-8")
    print(json.dumps({k:technical[k] for k in ("status","expectedFrames","presentFrames","missing","errors")},ensure_ascii=False))
if __name__=="__main__":main()
