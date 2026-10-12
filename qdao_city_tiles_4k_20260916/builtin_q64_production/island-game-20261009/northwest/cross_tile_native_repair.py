"""Prepare/project ONE native1254 repair across an explicit 2x2 cluster.

Manifest schemaVersion1 tiles: [{tileId,image:{path,sha256},record:{path,sha256}}].
cropBox uses cluster-local8192 coordinates. No full8192 pixel array, resampling,
blending, automatic masking or visual acceptance. All output versions are new.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import numpy as np
from PIL import Image
import apply_native_tile_repair as r

SIZE, TILE, CLUSTER = r.SIZE, r.TILE, 2*r.TILE
PREPARE_OPERATION = "exact native-coordinate crop across verified tile cluster"
DERIVATION_OPERATION = "native-coordinate crop across verified 2x2 tiles"
OPERATION = "one native repair projected across verified tile cluster"
PROJECTION_OPERATION = "same-coordinate projection of one cross-tile native repair"
FALSE_FLAGS = ("registration","resizing","feathering","colorCorrection","pixelSynthesis")


def validate_box(box):
    r.require(isinstance(box,(list,tuple)) and len(box)==4 and all(type(v) is int for v in box), "Cluster cropBox requires four integer coordinates.")
    x0,y0,x1,y1=box
    r.require(0<=x0<x1<=CLUSTER and 0<=y0<y1<=CLUSTER and x1-x0==y1-y0==SIZE, "Cluster crop must be a 1254 square inside8192.")
    return list(box)


def validate_method(record):
    r.require(record.get("schemaVersion")==1 and record.get("isAiGeneration") is False, "Invalid mechanical cross-tile record.")
    for flag in FALSE_FLAGS:
        r.require(record.get("method",{}).get(flag) is False, f"Cross-tile operation must forbid {flag}.")


def zone_path(path,role):
    path=Path(path).resolve()
    r.require(path.is_relative_to(r.ZONE.resolve()), f"{role} must remain in the current zone.")
    return path


def load_manifest(path):
    path=zone_path(path,"Cluster manifest")
    data=r.read_json(path); tiles=data.get("tiles")
    r.require(data.get("schemaVersion")==1 and isinstance(tiles,list) and len(tiles)==4, "Explicit manifest must contain exactly four current tiles.")
    result=[]
    for item in tiles:
        tile_id=item.get("tileId"); origin=r.tile_origin(tile_id)
        image=r.pinned(item.get("image"),path.parent,"manifest current image")
        record=r.pinned(item.get("record"),path.parent,"manifest current provenance")
        zone_path(image["path"],"Base image"); zone_path(record["path"],"Base provenance")
        result.append({"tileId":tile_id,"tileOrigin":origin,"image":image,"record":record})
    origin=[min(t["tileOrigin"][axis] for t in result) for axis in (0,1)]
    expected={(origin[0]+x*TILE,origin[1]+y*TILE) for y in (0,1) for x in (0,1)}
    r.require({tuple(t["tileOrigin"]) for t in result}==expected and len({t["tileId"] for t in result})==4, "Manifest tiles must form one unique contiguous2x2 neighborhood.")
    r.require(len({t["image"]["path"] for t in result})==len({t["record"]["path"] for t in result})==4, "Each tile requires a distinct image and provenance record.")
    result.sort(key=lambda t:(t["tileOrigin"][1],t["tileOrigin"][0]))
    for tile in result:
        tile["clusterOffset"]=[tile["tileOrigin"][i]-origin[i] for i in (0,1)]
    return result,origin


def intersections(tiles,box):
    box=validate_box(box); parts=[]
    for tile in tiles:
        ox,oy=tile["clusterOffset"]
        x0,y0=max(box[0],ox),max(box[1],oy)
        x1,y1=min(box[2],ox+TILE),min(box[3],oy+TILE)
        if x1>x0 and y1>y0:
            parts.append({"tileId":tile["tileId"],"tileBox":[x0-ox,y0-oy,x1-ox,y1-oy],
                          "repairBox":[x0-box[0],y0-box[1],x1-box[0],y1-box[1]]})
    r.require(len(parts) in (2,4), "Crop must cross a tile boundary into two or four tiles.")
    return parts


def compose_crop(tiles,box,seen=None):
    """Validate each base; retain only its crop contribution in memory."""
    parts=intersections(tiles,box)
    crop=np.empty((SIZE,SIZE,3),dtype=np.uint8)
    coverage=np.zeros((SIZE,SIZE),dtype=np.uint8); proofs={}
    for tile in tiles:
        pixels,proof=r.validate_base(Path(tile["image"]["path"]),Path(tile["record"]["path"]),seen)
        r.require(proof["tileId"]==tile["tileId"] and proof["tileOrigin"]==tile["tileOrigin"], "Manifest identity differs from verified base provenance.")
        proofs[tile["tileId"]]=proof
        for part in parts:
            if part["tileId"]==tile["tileId"]:
                tx0,ty0,tx1,ty1=part["tileBox"]; sx0,sy0,sx1,sy1=part["repairBox"]
                crop[sy0:sy1,sx0:sx1]=pixels[ty0:ty1,tx0:tx1]
                coverage[sy0:sy1,sx0:sx1]+=1
        del pixels
    r.require(np.all(coverage==1), "Cross-tile crop must cover every native pixel exactly once.")
    return crop,parts,proofs


def canonical_context(manifest_path,box,seen=None):
    tiles,origin=load_manifest(manifest_path); box=validate_box(box)
    crop,parts,proofs=compose_crop(tiles,box,seen)
    return crop,{"manifest":r.file_info(manifest_path),"tiles":tiles,"clusterOrigin":origin,
                 "cropBox":box,"globalBox":[box[i]+origin[i%2] for i in range(4)],"parts":parts},proofs


def write_json(path,data):
    with path.open("x",encoding="utf-8") as handle:
        json.dump(data,handle,ensure_ascii=False,indent=2); handle.write("\n")


def prepare(manifest_path,box,stem,references_path,role):
    r.require(re.fullmatch(r"[A-Za-z0-9_-]+",stem or "") is not None, "Stem must be a plain filename token.")
    crop,context,_=canonical_context(manifest_path,box)
    refs=json.loads(references_path.read_text(encoding="utf-8-sig"))
    r.require(isinstance(refs,list) and len(refs)<=4, "Supply zero to four style/layout references; edit target is first.")
    refs=[{**item,**r.pinned(item,references_path.parent,"current generation reference")} for item in refs]
    guide_dir=r.ZONE/"guides"; guide_dir.mkdir(parents=True,exist_ok=True)
    target=guide_dir/f"{stem}.native-crop.png"; derivation_path=guide_dir/f"{stem}.native-crop.derivation.json"
    input_path=guide_dir/f"{stem}.input.json"; refs_path=guide_dir/f"{stem}.references.json"
    r.require(all(not p.exists() for p in (target,derivation_path,input_path,refs_path)), "Prepared version already exists; never overwrite.")
    with target.open("xb") as handle: Image.fromarray(crop).save(handle,format="PNG")
    derivation={"schemaVersion":1,"operation":DERIVATION_OPERATION,"isAiGeneration":False,
                "method":{flag:False for flag in FALSE_FLAGS},**context,
                "output":{**r.file_info(target),"dimensions":[SIZE,SIZE]}}
    write_json(derivation_path,derivation)
    inputs=[{**r.file_info(target),"nativeSize":[SIZE,SIZE],"role":role}]+refs
    data={"schemaVersion":1,"operation":PREPARE_OPERATION,"stem":stem,**context,
          "nativeSize":[SIZE,SIZE],"inputs":inputs,
          "editTarget":{**r.file_info(target),"derivationRecord":r.file_info(derivation_path)},
          "layoutPixelsForbiddenInFinal":True,"isFinalArt":False}
    write_json(input_path,data); write_json(refs_path,{"inputs":inputs})
    return {"input":r.file_info(input_path),"crop":r.file_info(target),"references":r.file_info(refs_path),"context":context}


def validate_input(manifest_path,input_path,seen=None):
    zone_path(input_path,"Cross-tile edit input")
    data=r.read_json(input_path)
    r.require(data.get("schemaVersion")==1 and data.get("operation")==PREPARE_OPERATION, "Unsupported cross-tile edit input.")
    r.require(data.get("nativeSize")==[SIZE,SIZE], "Cross-tile edit must remain native1254.")
    crop,context,proofs=canonical_context(manifest_path,data.get("cropBox"),seen)
    for key,value in context.items():
        r.require(data.get(key)==value, f"Cross-tile input {key} differs from the current pinned manifest.")
    target=r.pinned(data.get("editTarget"),input_path.parent,"cross-tile edit target")
    derivation_info=r.pinned(data["editTarget"].get("derivationRecord"),input_path.parent,"cross-tile crop derivation")
    derivation_path=Path(derivation_info["path"])
    zone_path(target["path"],"Crop target"); zone_path(derivation_path,"Crop derivation")
    derivation=r.read_json(derivation_path); validate_method(derivation)
    r.require(derivation.get("operation")==DERIVATION_OPERATION, "Unsupported cross-tile crop derivation.")
    for key,value in context.items():
        r.require(derivation.get(key)==value, f"Crop derivation {key} differs from verified current bases.")
    r.require(r.pinned(derivation.get("output"),derivation_path.parent,"derived crop output")==target and derivation["output"].get("dimensions")==[SIZE,SIZE], "Derivation identifies a different crop.")
    r.require(np.array_equal(crop,r.read_pixels(Path(target["path"]),SIZE)), "Edit target does not exactly equal the current verified cross-tile crop; ancestor reuse is not supported.")
    declared=data.get("inputs")
    r.require(isinstance(declared,list) and 1<=len(declared)<=5, "Input requires one to five actual references.")
    refs=[r.pinned(item,input_path.parent,"current cross-tile generation reference") for item in declared]
    r.require(refs[0]==target, "First actual reference must be the exact native cross-tile edit target.")
    evidence={"input":r.file_info(input_path),"editTarget":target,"cropDerivation":derivation_info,
              "references":refs,"globalBox":context["globalBox"],
              "currentCropExactlyMatchesEditTarget":True,"ancestorCropReuse":False}
    return crop,context,proofs,evidence


def validate_source(source_path,generation_path,input_evidence):
    pixels,source,generation=r.load_raw(source_path,generation_path)
    refs=generation.get("references")
    r.require(isinstance(refs,list), "Cross-tile generation must record actual references.")
    refs=[r.pinned(item,generation_path.parent,"cross-tile generation reference") for item in refs]
    r.require(refs==input_evidence["references"], "Generation reference order/list differs from cross-tile input.")
    receipt_path=Path(source["receipt"]["path"]); receipt=r.read_json(receipt_path)
    submitted=receipt.get("submitted",{}); actual=submitted.get("referenced_image_paths")
    r.require(isinstance(actual,list) and [str(r.resolve(p,receipt_path.parent)) for p in actual]==[ref["path"] for ref in refs], "Builtin receipt did not submit the exact ordered cross-tile references.")
    r.require(submitted.get("promptText")==Path(source["prompt"]["path"]).read_text(encoding="utf-8"), "Builtin receipt prompt text differs from saved prompt.")
    r.require(submitted.get("transparent_background") is False, "Cross-tile repair must be recorded as opaque.")
    source.update(input_evidence)
    return pixels,source


def selected_parts(context,mask):
    result=[]
    for part in context["parts"]:
        sx0,sy0,sx1,sy1=part["repairBox"]
        count=int(np.count_nonzero(mask[sy0:sy1,sx0:sx1]==255))
        if count: result.append({**part,"selectedPixelCount":count})
    r.require(sum(p["selectedPixelCount"] for p in result)==int(np.count_nonzero(mask==255)), "Selected mask escapes its declared crop intersections.")
    return result


def project_pixels(base,source,mask,part):
    r.require(base.shape==(TILE,TILE,3) and source.shape==(SIZE,SIZE,3) and mask.shape==(SIZE,SIZE), "Cross-tile source dimensions mismatch.")
    r.require(base.dtype==source.dtype==mask.dtype==np.uint8 and set(np.unique(mask).tolist()).issubset({0,255}), "Cross-tile projection requires uint8 pixels and a binary mask.")
    tx0,ty0,tx1,ty1=part["tileBox"]; sx0,sy0,sx1,sy1=part["repairBox"]
    r.require(all(type(v) is int for v in part["tileBox"]+part["repairBox"]) and 0<=tx0<tx1<=TILE and 0<=ty0<ty1<=TILE and 0<=sx0<sx1<=SIZE and 0<=sy0<sy1<=SIZE, "Projection boxes leave source or tile bounds.")
    r.require(tx1-tx0==sx1-sx0 and ty1-ty0==sy1-sy0, "Projection would resize its native source.")
    selection=mask[sy0:sy1,sx0:sx1]==255; result=base.copy()
    result[ty0:ty1,tx0:tx1][selection]=source[sy0:sy1,sx0:sx1][selection]
    return result


def validate_operation(operation_path,seen=None):
    operation_path=zone_path(operation_path,"Shared cross-tile operation")
    seen=set() if seen is None else set(seen)
    r.require(operation_path not in seen and len(seen)<32, "Cyclic or excessive cross-tile provenance chain.")
    seen.add(operation_path)
    operation=r.read_json(operation_path); validate_method(operation)
    r.require(operation.get("operation")==OPERATION, "Unsupported cross-tile operation record.")
    manifest=r.pinned(operation.get("manifest"),operation_path.parent,"operation manifest")
    input_info=r.pinned(operation.get("repairSource",{}).get("input"),operation_path.parent,"operation input")
    _,context,proofs,evidence=validate_input(Path(manifest["path"]),Path(input_info["path"]),seen)
    for key,value in context.items(): r.require(operation.get(key)==value, f"Cross-tile operation {key} changed.")
    declared=operation.get("repairSource",{})
    raw=r.pinned(declared,operation_path.parent,"operation raw repair")
    generation=r.pinned(declared.get("generationRecord"),operation_path.parent,"operation raw generation")
    source,source_info=validate_source(Path(raw["path"]),Path(generation["path"]),evidence)
    r.require(declared==source_info, "Cross-tile repair source evidence changed.")
    mask_info=r.pinned(operation.get("mask"),operation_path.parent,"operation binary mask")
    mask=r.read_mask(Path(mask_info["path"])); selected=selected_parts(context,mask)
    r.require(operation.get("selectedParts")==selected, "Cross-tile selected counts or source offsets changed.")
    outputs=operation.get("outputs")
    r.require(isinstance(outputs,list) and [o.get("tileId") for o in outputs]==[p["tileId"] for p in selected], "Operation must list exactly its affected tiles in canonical order.")
    for out in outputs:
        image=r.pinned(out.get("image"),operation_path.parent,"cross-tile output")
        zone_path(image["path"],"Projected output")
        r.require(out.get("projectionRecordPath")==str(Path(image["path"]).with_suffix(".cross-native-repair.json")), "Output projection record path differs.")
    return operation,context,proofs,source,mask,selected


def validate_projection(pixels,record,record_path,seen):
    validate_method(record)
    r.require(record.get("operation")==PROJECTION_OPERATION, "Unsupported cross-tile projection.")
    operation_info=r.pinned(record.get("operationRecord"),record_path.parent,"shared cross-tile operation")
    operation_path=zone_path(operation_info["path"],"Shared cross-tile operation")
    operation,context,proofs,source,mask,parts=validate_operation(operation_path,seen)
    matches=[t for t in context["tiles"] if t["tileId"]==record.get("tileId")]
    r.require(len(matches)==1, "Projection tile identity is absent from manifest.")
    tile=matches[0]; part_matches=[p for p in parts if p["tileId"]==tile["tileId"]]
    r.require(len(part_matches)==1, "Projection tile has no selected repair pixels.")
    part=part_matches[0]
    r.require(record.get("tileOrigin")==tile["tileOrigin"] and record.get("base")=={"image":tile["image"],"record":tile["record"]}, "Projection changed its parent base or tile origin.")
    r.require(record.get("selection")==part, "Projection changed the exact source/tile intersection.")
    output=next(o for o in operation["outputs"] if o["tileId"]==tile["tileId"])
    r.require(r.pinned(record.get("output"),record_path.parent,"projection output")==output["image"] and output["projectionRecordPath"]==str(record_path), "Projection output differs from shared operation.")
    parent_path=Path(tile["image"]["path"])
    r.require(r.file_info(parent_path)==tile["image"], "Parent changed after validation.")
    parent=r.read_pixels(parent_path,TILE)
    r.require(np.array_equal(pixels,project_pixels(parent,source,mask,part)), "Cross-tile output changed a mask-zero pixel or copied a wrong native coordinate.")
    r.require(record.get("coverageAssertions",{}).get("fullNativeCoverage") is True, "Cross-tile projection lacks native coverage assertion.")
    proof=proofs[tile["tileId"]]
    return {**proof,"priorRepairCount":proof["priorRepairCount"]+1,
            "crossTileRepairOperations":proof.get("crossTileRepairOperations",[])+[operation_info],
            "crossTileRepairReferenceAvailability":proof.get("crossTileRepairReferenceAvailability",[])+[
                {"fullReferenceAvailability":True,"references":operation["repairSource"]["references"]}],
            "lastCrossTileRepairSource":operation["repairSource"],"lastCrossTileRepairSelection":part}


def apply(manifest_path,input_path,source_path,generation_path,mask_path,output_dir,version,validate_only=False):
    _,context,proofs,evidence=validate_input(manifest_path,input_path)
    source,source_info=validate_source(source_path,generation_path,evidence)
    mask=r.read_mask(mask_path); selected=selected_parts(context,mask)
    if validate_only: return {"status":"cross_tile_inputs_verified_no_output","selectedParts":selected,"visualAcceptance":False}
    r.require(re.fullmatch(r"[A-Za-z0-9_-]+",version or "") is not None, "Version must be a plain filename token.")
    output_dir=zone_path(output_dir,"Output directory")
    r.require(not output_dir.is_relative_to(r.NATIVE.resolve()), "Mechanical projections must remain outside native/.")
    operation_path=output_dir/f"{version}.cross-native-operation.json"
    paths=[(part,output_dir/f"{part['tileId']}_{version}_4096.png") for part in selected]
    r.require(not operation_path.exists() and all(not p.exists() and not p.with_suffix(".cross-native-repair.json").exists() for _,p in paths), "Output version already exists; never overwrite.")
    output_dir.mkdir(parents=True,exist_ok=True); outputs=[]
    for part,path in paths:
        tile=next(t for t in context["tiles"] if t["tileId"]==part["tileId"])
        parent_path=Path(tile["image"]["path"])
        r.require(r.file_info(parent_path)==tile["image"], "Parent changed after preflight.")
        base=r.read_pixels(parent_path,TILE); result=project_pixels(base,source,mask,part)
        with path.open("xb") as handle: Image.fromarray(result).save(handle,format="PNG")
        outputs.append({"tileId":part["tileId"],"image":r.file_info(path),"projectionRecordPath":str(path.with_suffix(".cross-native-repair.json"))})
        del base,result
    operation={"schemaVersion":1,"operation":OPERATION,"isAiGeneration":False,
               "createdAtUtc":datetime.now(timezone.utc).isoformat(),"tool":r.file_info(Path(__file__).resolve()),
               **context,"repairSource":source_info,"mask":r.file_info(mask_path),
               "selectedParts":selected,"outputs":outputs,"method":{flag:False for flag in FALSE_FLAGS},
               "visualAcceptance":False,"formalAcceptedCount":0}
    write_json(operation_path,operation)
    for output,part in zip(outputs,selected):
        tile=next(t for t in context["tiles"] if t["tileId"]==part["tileId"])
        record={"schemaVersion":1,"operation":PROJECTION_OPERATION,"isAiGeneration":False,
                "tileId":tile["tileId"],"tileOrigin":tile["tileOrigin"],
                "base":{"image":tile["image"],"record":tile["record"]},"operationRecord":r.file_info(operation_path),
                "selection":part,"output":{**output["image"],"dimensions":[TILE,TILE]},
                "method":{flag:False for flag in FALSE_FLAGS},
                "coverageAssertions":{"fullNativeCoverage":True,"unassignedPixels":0,"sameCoordinateRawOrUnchangedBase":True},
                "formalAcceptedCount":0,"visualAcceptance":False}
        write_json(Path(output["projectionRecordPath"]),record)
    return {"status":"cross_tile_candidate_pending_native_visual_review","operationRecord":r.file_info(operation_path),"outputs":outputs,"selectedParts":selected,"visualAcceptance":False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest="command",required=True)
    prep=commands.add_parser("prepare")
    for name in ("manifest","stem","references","role"): prep.add_argument("--"+name,required=True)
    prep.add_argument("--crop-box",nargs=4,type=int,required=True)
    app=commands.add_parser("apply")
    for name in ("manifest","input","source","generation-record","mask"): app.add_argument("--"+name,required=True)
    app.add_argument("--output-dir"); app.add_argument("--version"); app.add_argument("--validate-only",action="store_true")
    args=parser.parse_args(); path=lambda value:r.resolve(value,Path.cwd())
    if args.command=="prepare":
        result=prepare(path(args.manifest),args.crop_box,args.stem,path(args.references),args.role)
    else:
        r.require(args.validate_only or (args.output_dir and args.version), "Apply requires --output-dir and --version.")
        result=apply(path(args.manifest),path(args.input),path(args.source),path(args.generation_record),path(args.mask),
                     path(args.output_dir) if args.output_dir else r.ZONE,args.version,args.validate_only)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    try: main()
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as error:
        print(json.dumps({"status":"failed","error":str(error),"candidateAccepted":False},ensure_ascii=False),file=sys.stderr)
        sys.exit(1)
