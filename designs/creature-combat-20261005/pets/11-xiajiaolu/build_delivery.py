"""Export native AI frames using full-canvas resize; validate and build local previews.
No pose generation, interpolation, mirroring, cropping or per-frame alignment.
Run this after generation; it tolerates incomplete groups and reports them honestly.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SPECS = {"hit": (6,40), "attack": (12,30), "cast": (16,45)}
EXPECTED = sum(n*2 for n,d in SPECS.values())
SIZE = (1024,1024)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):
    return path.relative_to(ROOT).as_posix()
def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def write(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def alpha_info(im):
    a=im.getchannel("A")
    hist=a.histogram()
    box=a.getbbox()
    edge=max(a.crop((0,0,im.width,1)).getextrema()[1],
             a.crop((0,im.height-1,im.width,im.height)).getextrema()[1],
             a.crop((0,0,1,im.height)).getextrema()[1],
             a.crop((im.width-1,0,im.width,im.height)).getextrema()[1])
    return {"extrema":list(a.getextrema()),"transparentPixels":hist[0],
            "partialPixels":sum(hist[1:255]),"opaquePixels":hist[255],
            "bbox":list(box) if box else None,"edgeAlphaMax":edge}
def events(action,n):
    points={"hit":{1:"hit-start",3:"recoil-peak",6:"settled"},
            "attack":{1:"windup-start",4:"windup-peak",7:"contact",12:"settled"},
            "cast":{1:"gather-start",8:"charge-peak",10:"release",16:"settled"}}
    return points[action].get(n)
def resolve_ref(p):
    p=Path(p)
    return (p if p.is_absolute() else ROOT/p).resolve()
def removed_source_entry(cleanup,path,digest):
    """A flag or availability label alone cannot prove a source was retained correctly."""
    if cleanup.get("status")!="completed" or not digest:
        return None
    if resolve_ref(cleanup.get("root",""))!=ROOT:
        return None
    matches=[item for item in cleanup.get("deletedImages",[])
             if resolve_ref(item.get("path",""))==path.resolve()]
    if len(matches)!=1:
        return None
    item=matches[0]
    if (item.get("status")!="removed" or item.get("sha256")!=digest
            or resolve_ref(item.get("absolutePath",""))!=path.resolve()):
        return None
    return item
def checker(size):
    out=Image.new("RGBA",size,(224,226,229,255))
    draw=ImageDraw.Draw(out)
    for y in range(0,size[1],16):
        for x in range(0,size[0],16):
            if (x//16+y//16)%2:
                draw.rectangle((x,y,x+15,y+15),fill=(246,247,248,255))
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--allow-removed-sources",action="store_true",
                        help="Compatibility option: removed sources always require completed cleanup evidence and matching hashes.")
    args=parser.parse_args()
    errors=[]; warnings=[]; frames=[]; groups=[]; missing=[]; native_sizes=set()
    review_path=ROOT/"visual-review.json"
    review=read(review_path) if review_path.exists() else {}
    cleanup_path=ROOT/"cleanup.json"
    cleanup=read(cleanup_path) if cleanup_path.exists() else {}
    preview=ROOT/"preview"
    preview.mkdir(exist_ok=True)
    for action,(count,duration) in SPECS.items():
        for direction in ("E","W"):
            group_frames=[]
            for n in range(1,count+1):
                name=f"{n:02}"
                key=f"{action}/{direction}/{name}"
                source=ROOT/"work"/action/direction/(name+".png")
                runtime=ROOT/"runtime"/action/direction/(name+".png")
                generation=ROOT/"provenance"/action/direction/(name+".json")
                exported=ROOT/"provenance"/"export"/action/direction/(name+".json")
                if not source.exists() and not runtime.exists():
                    missing.append(key); continue
                if not generation.exists():
                    errors.append({"frame":key,"issue":"missing-generation-record"}); continue
                rec=read(generation)
                for field in ("sha256","generatedAt","configSnapshot","submittedParameters","actualModel","actualQuality","prompt","references","evidence"):
                    if field not in rec:
                        errors.append({"frame":key,"issue":"missing-provenance-field","field":field})
                prompt=ROOT/rec.get("prompt","missing")
                if not prompt.is_file():
                    errors.append({"frame":key,"issue":"missing-prompt","path":str(prompt)})
                native_size=[rec.get("width"),rec.get("height")]
                if source.exists():
                    with Image.open(source) as native:
                        if native.width!=native.height:
                            errors.append({"frame":key,"issue":"non-square-native","size":native.size}); continue
                        native_size=list(native.size)
                        native_sizes.add(tuple(native.size))
                        native_alpha=alpha_info(native.convert("RGBA"))
                        if native.mode!="RGBA":
                            errors.append({"frame":key,"issue":"native-not-RGBA","mode":native.mode})
                        digest=sha(source)
                        if digest!=rec.get("sha256"):
                            errors.append({"frame":key,"issue":"native-sha-mismatch"})
                        image=native.convert("RGBA").resize(SIZE,Image.Resampling.LANCZOS)
                    runtime.parent.mkdir(parents=True,exist_ok=True)
                    image.save(runtime,format="PNG",optimize=True)
                    export_record={
                        "file":rel(runtime),"sha256":sha(runtime),"width":1024,"height":1024,
                        "format":"PNG","mode":"RGBA","exportedAt":datetime.now(timezone.utc).isoformat(),
                        "derivedFrom":{"file":rel(source),"sha256":digest,
                                       "width":native_size[0],"height":native_size[1],
                                       "generationRecord":rel(generation)},
                        "operation":{"type":"full-canvas-resize","from":native_size,"to":[1024,1024],
                                     "resample":"LANCZOS","crop":None,"translation":None,"mirror":False,
                                     "perFrameFootAlignment":False},
                        "actualModel":rec.get("actualModel"),"actualQuality":rec.get("actualQuality"),
                        "nativeAlpha":native_alpha,"sourceAvailability":"present"
                    }
                else:
                    if not exported.exists():
                        errors.append({"frame":key,"issue":"missing-export-record-after-source-removal"}); continue
                    export_record=read(exported)
                    derived=export_record.get("derivedFrom",{})
                    retained=removed_source_entry(cleanup,source,rec.get("sha256"))
                    source_chain_ok=(retained is not None
                        and resolve_ref(rec.get("file",""))==source.resolve()
                        and resolve_ref(derived.get("file",""))==source.resolve()
                        and derived.get("sha256")==rec.get("sha256")
                        and derived.get("generationRecord")==rel(generation)
                        and rel(generation) in retained.get("generationRecords",[])
                        and rec.get("sourceAvailability")=="removed-after-final-export"
                        and export_record.get("sourceAvailability")=="removed-after-final-export"
                        and rec.get("retentionRecord")=="cleanup.json"
                        and export_record.get("retentionRecord")=="cleanup.json")
                    if not source_chain_ok:
                        errors.append({"frame":key,"issue":"removed-source-evidence-chain-mismatch",
                                       "path":rel(source),"cleanupStatus":cleanup.get("status")})
                        continue
                    if export_record.get("file")!=rel(runtime):
                        errors.append({"frame":key,"issue":"export-runtime-path-mismatch"})
                    if sha(runtime)!=export_record.get("sha256"):
                        errors.append({"frame":key,"issue":"runtime-sha-mismatch"})
                    with Image.open(runtime) as current:
                        image=current.convert("RGBA")
                for ref in rec.get("references",[]):
                    refpath=resolve_ref(ref["path"])
                    if refpath.exists():
                        if ref.get("sha256") and sha(refpath)!=ref["sha256"]:
                            errors.append({"frame":key,"issue":"reference-sha-mismatch","path":ref["path"]})
                    else:
                        is_internal_work=refpath.is_relative_to(ROOT/"work")
                        retained=removed_source_entry(cleanup,refpath,ref.get("sha256")) if is_internal_work else None
                        retained_evidence=(retained is not None
                            and ref.get("availability")=="removed-after-final-export"
                            and ref.get("retentionRecord")=="cleanup.json")
                        if not retained_evidence:
                            errors.append({"frame":key,"issue":"missing-reference-cleanup-evidence","path":ref["path"]})
                        elif ref.get("sourceGenerationRecord"):
                            source_record_path=resolve_ref(ref["sourceGenerationRecord"])
                            if (not source_record_path.is_relative_to(ROOT/"provenance")
                                    or not source_record_path.is_file()
                                    or ref["sourceGenerationRecord"] not in retained.get("generationRecords",[])):
                                errors.append({"frame":key,"issue":"reference-source-record-missing","path":ref["path"]})
                            else:
                                source_record=read(source_record_path)
                                if (source_record.get("sha256")!=ref.get("sha256")
                                        or resolve_ref(source_record.get("file",""))!=refpath
                                        or source_record.get("sourceAvailability")!="removed-after-final-export"):
                                    errors.append({"frame":key,"issue":"reference-source-record-mismatch","path":ref["path"]})
                    if ref.get("submittedPath"):
                        matching_remaps=[r for r in cleanup.get("referenceRemaps",[])
                            if r.get("record")==rel(generation)
                            and r.get("submittedPath")==ref["submittedPath"]
                            and resolve_ref(r.get("resolvedHistoricalPath",""))==refpath
                            and r.get("sha256")==ref.get("sha256")
                            and r.get("sourceGenerationRecord")==ref.get("sourceGenerationRecord")]
                        submitted=rec.get("submittedParameters",{}).get("referenced_image_paths",[])
                        if len(matching_remaps)!=1 or ref["submittedPath"] not in submitted:
                            errors.append({"frame":key,"issue":"reference-remap-evidence-mismatch","path":ref["path"]})
                # A recorded remap must still be represented in the generation metadata.
                for remap in cleanup.get("referenceRemaps",[]):
                    if remap.get("record")!=rel(generation):
                        continue
                    matching_refs=[ref for ref in rec.get("references",[])
                        if ref.get("submittedPath")==remap.get("submittedPath")
                        and resolve_ref(ref.get("path",""))==resolve_ref(remap.get("resolvedHistoricalPath",""))
                        and ref.get("sha256")==remap.get("sha256")
                        and ref.get("sourceGenerationRecord")==remap.get("sourceGenerationRecord")]
                    if len(matching_refs)!=1:
                        errors.append({"frame":key,"issue":"cleanup-reference-remap-missing-from-generation",
                                       "submittedPath":remap.get("submittedPath")})
                with Image.open(runtime) as check:
                    if check.mode!="RGBA" or check.size!=SIZE:
                        errors.append({"frame":key,"issue":"bad-runtime-dimensions-or-mode","size":check.size,"mode":check.mode})
                    alpha=alpha_info(check.convert("RGBA"))
                if alpha["extrema"]!=[0,255] or alpha["transparentPixels"]==0:
                    errors.append({"frame":key,"issue":"missing-useful-alpha"})
                if alpha["edgeAlphaMax"]>0:
                    warnings.append({"frame":key,"issue":"nonzero-alpha-at-canvas-edge","alpha":alpha["edgeAlphaMax"]})
                export_record["alpha"]=alpha
                pixel_sha=hashlib.sha256(image.tobytes()).hexdigest()
                export_record["pixelSha256"]=pixel_sha
                write(exported,export_record)
                visual=review.get("frames",{}).get(key,rec.get("visualReview",rec.get("visualStatus","pending-sequence-review")))
                item={"id":key,"action":action,"direction":direction,"frame":n,
                      "file":rel(runtime),"width":1024,"height":1024,"durationMs":duration,
                      "pivot":[0.5,0.08],"footPointTopLeft":[512,942],
                      "event":events(action,n),"sha256":sha(runtime),"pixelSha256":pixel_sha,
                      "nativeSize":native_size,"sourceSha256":rec.get("sha256"),
                      "generationRecord":rel(generation),"exportRecord":rel(exported),
                      "prompt":rel(prompt),"alpha":alpha,"visualStatus":visual,
                      "clientIntegration":"not-tested"}
                frames.append(item); group_frames.append(item)
            group={"id":f"{action}-{direction}","action":action,"direction":direction,
                   "expectedFrames":count,"presentFrames":len(group_frames),"durationMs":duration,
                   "sequenceDurationMs":count*duration,"complete":len(group_frames)==count,
                   "frames":group_frames,"contactSheet":f"preview/{action}-{direction}-contact.jpg",
                   "normalPreview":None,"slowPreview":None,
                   "previewDerivation":{"sources":[{"file":f["file"],"sha256":f["sha256"]} for f in group_frames],
                     "contactSheetOperation":"whole-frame thumbnails on checkerboard, four columns, labels; no generated poses",
                     "animationOperation":"lossless full-frame APNG packing; normal duration and slow duration multiplied by four; no interpolation"}}
            thumb=256; label=28; cols=4; rows=math.ceil(count/cols)
            sheet=Image.new("RGB",(cols*thumb,rows*(thumb+label)),(32,38,45))
            draw=ImageDraw.Draw(sheet)
            lookup={f["frame"]:f for f in group_frames}
            for n in range(1,count+1):
                x=((n-1)%cols)*thumb; y=((n-1)//cols)*(thumb+label)
                cell=checker((thumb,thumb))
                if n in lookup:
                    with Image.open(ROOT/lookup[n]["file"]) as im:
                        cell.alpha_composite(im.convert("RGBA").resize((thumb,thumb),Image.Resampling.LANCZOS))
                else:
                    ImageDraw.Draw(cell).text((64,124),"MISSING",fill=(190,40,40,255))
                sheet.paste(cell.convert("RGB"),(x,y))
                draw.text((x+8,y+thumb+7),f"{action} {direction} {n:02} / {count:02}",fill="white")
            sheet.save(ROOT/group["contactSheet"],quality=94)
            if group["complete"]:
                ims=[]
                for f in group_frames:
                    with Image.open(ROOT/f["file"]) as im:
                        ims.append(im.copy())
                for speed,multiplier in (("normal",1),("slow",4)):
                    out=preview/f"{action}-{direction}-{speed}.png"
                    ims[0].save(out,format="PNG",save_all=True,append_images=ims[1:],
                                duration=duration*multiplier,loop=0,disposal=0,blend=0)
                    group["normalPreview" if speed=="normal" else "slowPreview"]=rel(out)
            groups.append(group)
    hashes={}
    for f in frames:
        hashes.setdefault(f["sha256"],[]).append(f["id"])
    duplicates=[ids for ids in hashes.values() if len(ids)>1]
    if duplicates:
        errors.append({"issue":"duplicate-runtime-sha","groups":duplicates})
    source_hashes={}
    for f in frames:
        source_hashes.setdefault(f["sourceSha256"],[]).append(f["id"])
    duplicate_sources=[ids for ids in source_hashes.values() if len(ids)>1]
    if duplicate_sources:
        errors.append({"issue":"duplicate-native-sha","groups":duplicate_sources})
    pixel_hashes={}
    for f in frames:
        pixel_hashes.setdefault(f["pixelSha256"],[]).append(f["id"])
    duplicate_pixels=[ids for ids in pixel_hashes.values() if len(ids)>1]
    if duplicate_pixels:
        errors.append({"issue":"duplicate-decoded-pixels","groups":duplicate_pixels})
    if len(native_sizes)>1:
        warnings.append({"issue":"multiple-native-canvas-sizes","sizes":[list(s) for s in sorted(native_sizes)]})
    state="incomplete" if missing else ("failed" if errors else "passed")
    timestamp=datetime.now(timezone.utc).isoformat()
    validation={"checkedAt":timestamp,"technicalStatus":state,"expectedFrames":EXPECTED,
                "presentFrames":len(frames),"missingFrames":missing,"errors":errors,"warnings":warnings,
                "duplicateRuntimeHashes":duplicates,"duplicateNativeHashes":duplicate_sources,"duplicatePixelHashes":duplicate_pixels,
                "visualReview":review.get("summary","Pending final full-frame and normal/slow sequence review"),
                "clientIntegration":"not-tested",
                "scope":"Files, dimensions, RGBA alpha, SHA, source/record/prompt references only; this does not certify anatomy, motion or game integration."}
    manifest={"schemaVersion":1,"character":"霞角鹿","slug":"11-xiajiaolu","builtAt":timestamp,
              "expectedFrames":EXPECTED,"presentFrames":len(frames),"canvas":[1024,1024],
              "pivot":[0.5,0.08],"footPointTopLeft":[512,942],
              "directions":{"E":"true front three-quarter facing lower-right","W":"true rear three-quarter facing upper-left"},
              "exportPolicy":"whole square canvas resized to 1024; no per-frame crop, translation, mirror or foot alignment",
              "technicalStatus":state,"clientIntegration":"not-tested","groups":groups,"frames":frames}
    write(ROOT/"manifest.json",manifest);write(ROOT/"validation.json",validation)
    (preview/"data.js").write_text("window.DELIVERY="+json.dumps({"manifest":manifest,"validation":validation},ensure_ascii=False)+";\n",encoding="utf-8")
    (ROOT/"SHA256SUMS.txt").write_text("".join(f["sha256"]+"  "+f["file"]+"\n" for f in frames),encoding="utf-8")
    print(json.dumps({"status":state,"frames":len(frames),"expected":EXPECTED,"missing":len(missing),
                      "errors":len(errors),"warnings":len(warnings),"preview":str(preview/"index.html")},ensure_ascii=False))
if __name__=="__main__":
    main()
