"""Pure-data coordinate/provenance tests. Never edits production artwork.

Only the original assembly leaf validator is replaced by a deterministic
synthetic pixel oracle. Cross-tile prepare/apply, records, masks, source/ref
checks and validate_base dispatch/replay execute unchanged at native sizes.
"""
from contextlib import contextmanager, redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
import tempfile
import numpy as np
from PIL import Image
import apply_native_tile_repair as r
import cross_tile_native_repair as c

ZONE=r.ZONE
TEST_DIR=ZONE/"qa"/"cross_tile_native_validation"
TEST_DIR.mkdir(parents=True,exist_ok=True)
ROOT=Path(tempfile.mkdtemp(prefix="synthetic_",dir=TEST_DIR))
r.ZONE=ROOT; r.NATIVE=ROOT/"native"; r.NATIVE.mkdir()
checks={}
def dump(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def png(path,array): Image.fromarray(array).save(path)
def reject(name,call,contains=None):
    try: call()
    except (ValueError,OSError,KeyError,TypeError) as error:
        if contains: assert contains in str(error),(name,str(error))
        checks[name]={"pass":True,"rejection":str(error)}
    else: raise AssertionError(name+" was not rejected")
@contextmanager
def restore(*paths):
    saved={p:p.read_bytes() for p in paths}
    try: yield
    finally:
        for p,data in saved.items(): p.write_bytes(data)
def grid(index):
    y,x=np.indices((4096,4096),dtype=np.uint16)
    out=np.empty((4096,4096,3),np.uint8)
    out[:,:,0]=(x+17*index)%251
    out[:,:,1]=(y+31*index)%253
    out[:,:,2]=(x//19+y//23+43*index)%255
    return out
def synthetic_assembly(pixels,record,path):
    assert record.get("syntheticTestOnly") is True
    index=record["fixtureIndex"]
    r.require(np.array_equal(pixels,grid(index)),"Synthetic assembly pixel oracle mismatch.")
    return {"tileId":record["tileId"],"tileOrigin":r.tile_origin(record["tileId"]),
            "fullNativeCoverage":True,"verifiedPixelCount":4096**2,
            "originalRawSourceCount":0,"rootAssembly":r.file_info(path),
            "rootProvenance":{"syntheticTestOnly":True},"originalCellContributions":[],
            "priorRepairCount":0,"syntheticTestOnly":True}
r.validate_assembly=synthetic_assembly
manifest={"schemaVersion":1,"tiles":[]}
for index,tile_id in enumerate(("r03_c03","r03_c04","r04_c03","r04_c04")):
    path=ROOT/(tile_id+".png"); record_path=ROOT/(tile_id+".assembly.json")
    png(path,grid(index))
    dump(record_path,{"schemaVersion":1,"operation":r.ASSEMBLY_OPERATION,
                     "tileId":tile_id,"fixtureIndex":index,"syntheticTestOnly":True,
                     "output":{**r.file_info(path),"dimensions":[4096,4096]}})
    manifest["tiles"].append({"tileId":tile_id,"image":r.file_info(path),"record":r.file_info(record_path)})
mp=ROOT/"manifest.json"; dump(mp,manifest)
refs=ROOT/"references.json"; dump(refs,[])

def raw_fixture(stem,input_path):
    ip=r.read_json(input_path)
    source=r.NATIVE/(stem+".png")
    y,x=np.indices((1254,1254),dtype=np.uint16)
    array=np.stack(((x*3+y)%256,(x+y*5)%256,(x//3+y//7)%256),axis=2).astype(np.uint8)
    png(source,array)
    prompt=ROOT/(stem+".prompt.txt"); prompt.write_text("SYNTHETIC DATA ONLY; no AI generation.",encoding="utf-8")
    receipt=ROOT/(stem+".receipt.json")
    dump(receipt,{"syntheticTestOnly":True,"tool":"image_gen.imagegen","route":"builtin",
                  "submitted":{"transparent_background":False,"promptFile":str(prompt),
                    "promptText":prompt.read_text(),"referenced_image_paths":[i["path"] for i in ip["inputs"]]}})
    gp=source.with_suffix(".png.generation.json")
    dump(gp,{"syntheticTestOnly":True,"file":str(source),"sha256":r.file_info(source)["sha256"],
             "nativeWidth":1254,"nativeHeight":1254,"route":"builtin","tool":"image_gen.imagegen",
             "resizedAfterGeneration":False,"finalArtUpscaled":False,"prompt":str(prompt),
             "promptSha256":r.file_info(prompt)["sha256"],"references":ip["inputs"],
             "evidence":{"receipt":str(receipt)}})
    return source,gp,receipt

prepared=c.prepare(mp,[3500,3700,4754,4954],"four",refs,"SYNTHETIC QA")
ip=Path(prepared["input"]["path"]); target=Path(prepared["crop"]["path"])
source,gp,receipt=raw_fixture("four",ip)
mask=np.zeros((1254,1254),np.uint8)
mask[100:1100,100:1100]=255; mask[280:750,300:880]=0
mask_path=ROOT/"mask.png"; png(mask_path,mask)
result=c.apply(mp,ip,source,gp,mask_path,ROOT/"out","four")
assert len(result["outputs"])==4
raw=r.read_pixels(source,1254)
tiles,_=c.load_manifest(mp)
for output,part in zip(result["outputs"],result["selectedParts"]):
    image=Path(output["image"]["path"]); record=Path(output["projectionRecordPath"])
    actual,proof=r.validate_base(image,record)
    tile=next(t for t in tiles if t["tileId"]==part["tileId"])
    expected=r.read_pixels(Path(tile["image"]["path"]),4096)
    ox,oy=tile["clusterOffset"]
    ys,xs=np.nonzero(mask==255)
    valid=(xs+3500>=ox)&(xs+3500<ox+4096)&(ys+3700>=oy)&(ys+3700<oy+4096)
    expected[ys[valid]+3700-oy,xs[valid]+3500-ox]=raw[ys[valid],xs[valid]]
    assert np.array_equal(actual,expected)
    assert proof["rootAssembly"]==tile["record"] and proof["priorRepairCount"]==1
checks["four_way_exact_replay_and_root_provenance"]={"pass":True}

for name,box in [("vertical",[3500,1000,4754,2254]),("horizontal",[1000,3500,2254,4754])]:
    item=c.prepare(mp,box,name,refs,"SYNTHETIC QA")
    input_path=Path(item["input"]["path"]); raw_path,gen_path,_=raw_fixture(name,input_path)
    two=c.apply(mp,input_path,raw_path,gen_path,mask_path,ROOT/"out",name)
    assert len(two["outputs"])==2
    for output in two["outputs"]:
        r.validate_base(Path(output["image"]["path"]),Path(output["projectionRecordPath"]))
    checks[name+"_two_way_projection"]={"pass":True}
one_mask=np.zeros((1254,1254),np.uint8); one_mask[20:40,20:40]=255
one_mask_path=ROOT/"one_mask.png"; png(one_mask_path,one_mask)
one=c.apply(mp,ip,source,gp,one_mask_path,ROOT/"out","one")
assert len(one["outputs"])==1
checks["only_mask_affected_tiles_written"]={"pass":True}

reject("negative_crop",lambda:c.validate_box([-1,0,1253,1254]))
reject("outside_cluster_crop",lambda:c.validate_box([7000,0,8254,1254]))
reject("resized_crop",lambda:c.validate_box([0,0,1000,1000]))
reject("non_crossing_crop",lambda:c.canonical_context(mp,[0,0,1254,1254]))
with restore(mp):
    bad=deepcopy(manifest); bad["tiles"][1]["tileId"]="r03_c03"; dump(mp,bad)
    reject("duplicate_tile_identity",lambda:c.load_manifest(mp))
with restore(mp):
    bad=deepcopy(manifest); bad["tiles"][1]["image"]["sha256"]="0"*64; dump(mp,bad)
    reject("base_hash_tamper",lambda:c.load_manifest(mp),"Hash mismatch")
for field in ("globalBox","parts"):
    with restore(ip):
        bad=r.read_json(ip)
        if field=="globalBox": bad[field][0]+=1
        else: bad[field][0]["repairBox"][0]+=1
        dump(ip,bad); reject("wrong_"+field,lambda:c.validate_input(mp,ip),"differs")
deriv=Path(r.read_json(ip)["editTarget"]["derivationRecord"]["path"])
with restore(ip,deriv,target):
    changed=r.read_pixels(target,1254); changed[0,0]^=1; png(target,changed)
    d=r.read_json(deriv); d["output"]={**r.file_info(target),"dimensions":[1254,1254]}; dump(deriv,d)
    data=r.read_json(ip)
    data["editTarget"]={**r.file_info(target),"derivationRecord":r.file_info(deriv)}
    data["inputs"][0].update(r.file_info(target)); dump(ip,data)
    reject("retagged_target_pixel_tamper",lambda:c.validate_input(mp,ip),"does not exactly equal")
_,context,_,evidence=c.validate_input(mp,ip)
with restore(gp):
    data=r.read_json(gp); data["references"]=[]; dump(gp,data)
    reject("generation_reference_mismatch",lambda:c.validate_source(source,gp,evidence),"reference order/list")
with restore(receipt):
    data=r.read_json(receipt); data["submitted"]["referenced_image_paths"]=[]; dump(receipt,data)
    reject("receipt_reference_mismatch",lambda:c.validate_source(source,gp,evidence),"exact ordered")
with restore(receipt):
    data=r.read_json(receipt); data["submitted"]["promptText"]="different"; dump(receipt,data)
    reject("receipt_prompt_mismatch",lambda:c.validate_source(source,gp,evidence),"prompt text")
soft=ROOT/"soft_mask.png"; png(soft,np.full((1254,1254),127,np.uint8))
reject("nonbinary_mask",lambda:r.read_mask(soft),"only 0 and 255")
reject("crop_ancestry_cycle",lambda:c.validate_input(mp,ip,{Path(manifest["tiles"][0]["record"]["path"])}),"Cyclic")

output=result["outputs"][0]; image=Path(output["image"]["path"])
record_path=Path(output["projectionRecordPath"]); op=Path(result["operationRecord"]["path"])
with restore(record_path):
    record=r.read_json(record_path); record["selection"]["repairBox"][0]+=1; dump(record_path,record)
    reject("projection_offset_tamper",lambda:r.validate_base(image,record_path),"exact source/tile intersection")
with restore(op,record_path):
    operation=r.read_json(op); operation["selectedParts"][0]["repairBox"][0]+=1; dump(op,operation)
    record=r.read_json(record_path); record["operationRecord"]=r.file_info(op); dump(record_path,record)
    reject("retagged_operation_offset_tamper",lambda:r.validate_base(image,record_path),"source offsets changed")
with restore(op,record_path,image):
    array=r.read_pixels(image,4096); array[0,0]^=1; png(image,array)
    operation=r.read_json(op); operation["outputs"][0]["image"]=r.file_info(image); dump(op,operation)
    record=r.read_json(record_path); record["output"]={**r.file_info(image),"dimensions":[4096,4096]}
    record["operationRecord"]=r.file_info(op); dump(record_path,record)
    reject("retagged_unselected_output_pixel_change",lambda:r.validate_base(image,record_path),"mask-zero pixel")
reject("overwrite_existing_output_version",lambda:c.apply(mp,ip,source,gp,mask_path,ROOT/"out","four"),"already exists")
part=deepcopy(context["parts"][0]); part["tileBox"][2]=4097
reject("projection_out_of_bounds",lambda:c.project_pixels(grid(0),raw,mask,part),"bounds")

# Exercise ordinary single-tile repair on top of a new cross-tile projection.
base,proof=r.validate_base(image,record_path)
single_crop=ROOT/"single_crop.png"; png(single_crop,base[100:1354,100:1354])
single_deriv=ROOT/"single_derivation.json"
dump(single_deriv,{"operation":"native-coordinate crop","cropBox":[100,100,1354,1354],
                  "resizing":False,"registration":False,"feathering":False,"colorCorrection":False,
                  "output":r.file_info(single_crop),"derivedFrom":{**r.file_info(image),"assemblyRecord":r.file_info(record_path)}})
single_input=ROOT/"single_input.json"
dump(single_input,{"tileId":proof["tileId"],"tileCropBox":[100,100,1354,1354],"nativeSize":[1254,1254],
                   "globalBox":[8292,8292,9546,9546],"inputs":[r.file_info(single_crop)],
                   "editTarget":{**r.file_info(single_crop),"derivationRecord":r.file_info(single_deriv)}})
single_source,single_gen,_=raw_fixture("single",single_input)
single_output=ROOT/"out"/"single_followup.png"
sys.argv=["apply_native_tile_repair.py","--base",str(image),"--base-record",str(record_path),
          "--source",str(single_source),"--generation-record",str(single_gen),"--input",str(single_input),
          "--crop-box","100","100","1354","1354","--mask",str(one_mask_path),"--output",str(single_output)]
with redirect_stdout(io.StringIO()): r.main()
_,single_proof=r.validate_base(single_output,single_output.with_suffix(".native-repair.json"))
assert single_proof["priorRepairCount"]==2 and single_proof["rootAssembly"]==proof["rootAssembly"]
checks["single_tile_repair_after_cross_projection"]={"pass":True}
report={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"status":"passed","syntheticOnly":True,
        "productionArtworkMutated":False,"fullSize4096And1254":True,
        "fixtureAssemblyLeafUsesDeterministicPixelOracle":True,"fixtureDirectory":str(ROOT),
        "checks":checks,"checkCount":len(checks),"visualAcceptance":False}
dump(TEST_DIR/"validation.json",report)
print(json.dumps({"status":"passed","checkCount":len(checks),"report":str(TEST_DIR/"validation.json")}))
