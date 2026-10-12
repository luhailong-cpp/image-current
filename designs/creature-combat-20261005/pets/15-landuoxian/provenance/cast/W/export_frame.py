from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone,timedelta
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian")
dest=base/"provenance/cast/W"
num=int(sys.argv[1]); stem=f"{num:02d}"+(f".{sys.argv[2]}" if len(sys.argv)>2 else "")
receipt=json.loads((dest/f"{stem}.receipt.json").read_text(encoding="utf-8-sig"))
src=Path(receipt["sourcePath"])
native=dest/"_inprogress"/f"{stem}.png"
native.parent.mkdir(exist_ok=True)
shutil.copyfile(src,native)
im=Image.open(native)
assert im.width==im.height, f"non-square {im.size}"
assert im.mode=="RGBA" and im.getchannel("A").getextrema()==(0,255), f"not genuine alpha: {im.mode}"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native_meta={"file":str(native),"width":im.width,"height":im.height,"format":"PNG","mode":im.mode,"sha256":sha(native)}
out=Image.new("RGBA",(1024,1024))
out.alpha_composite(im.resize((920,920),Image.Resampling.LANCZOS),(52,37))
final=base/"runtime/cast/W"/f"{num:02d}.png"
out.save(final)
refs=[
{"path":"D:/work/image/designs/pets-xianling-20260924/source/15-landuoxian-E.png","role":"original E identity"},
{"path":"D:/work/image/designs/pets-xianling-20260924/source/15-landuoxian-W.png","role":"original W identity and rear anatomy orientation"},
{"path":"D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png","role":"primary hand-painted style and material reference"}
]
for r in refs:r["sha256"]=sha(Path(r["path"]))
for p in receipt.get("additionalReferences",[]):
    refs.append({"path":p,"role":"accepted action continuity reference","sha256":sha(Path(p))})
config=json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig"))
record={"file":str(final),"sha256":sha(final),"generatedAt":receipt["receivedAt"],"action":"cast","direction":"W","frame":num,"durationMs":45,"width":1024,"height":1024,"format":"PNG","mode":"RGBA","tool":"image_gen.imagegen","route":"builtin","configSnapshot":config,"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":[r["path"] for r in refs]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露／无可核实元数据；工具未开放 model/quality 选择器","prompt":str(dest/f"{stem}.prompt.txt"),"references":refs,"evidence":{"receipt":str(dest/f"{stem}.receipt.json"),"outputHint":receipt["output_hint"]},"native":native_meta,"derivedFrom":native_meta,"operation":{"type":"uniform-whole-canvas-resample-and-pad","resized":[920,920],"offset":[52,37],"canvas":[1024,1024],"filter":"Lanczos","noPerFrameBBoxAlignment":True},"alphaExtrema":list(out.getchannel("A").getextrema()),"alphaBBox":list(out.getchannel("A").getbbox()),"visualStatus":"static-inspected","dynamicStatus":"pending-root-preview","gameIntegration":"not-tested"}
(dest/f"{stem}.generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
(dest/f"{stem}.config-snapshot.json").write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frame":num,"nativeSize":im.size,"final":str(final),"sha256":sha(final),"alpha":out.getchannel("A").getextrema()}))
