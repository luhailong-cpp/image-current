from pathlib import Path
import json, hashlib, argparse
from PIL import Image
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument("direction")
parser.add_argument("frame",type=int)
parser.add_argument("source")
parser.add_argument("started")
parser.add_argument("finished")
a=parser.parse_args()
n=f"{a.frame:02}"
source=Path(a.source); im=Image.open(source)
rawsha=hashlib.sha256(source.read_bytes()).hexdigest()
out=root/"runtime"/"hit"/a.direction/(n+".png")
out.parent.mkdir(parents=True,exist_ok=True)
if im.size[0]!=im.size[1]: raise ValueError("Unexpected nonsquare native output; requires review")
native={"width":im.width,"height":im.height,"mode":im.mode,"format":im.format}
im.convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS).save(out)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
refs=[{"path":"D:/work/image/designs/pets-xianling-20260924/source/03-shuangtuan-E.png","purpose":"E existing identity front-right-down"},{"path":"D:/work/image/designs/pets-xianling-20260924/source/03-shuangtuan-W.png","purpose":"W existing identity rear-left-up"},{"path":"D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png","purpose":"Primary confirmed hand-painted material/style"}]
if a.frame>1:
 refs.append({"path":f"runtime/hit/{a.direction}/01.png","purpose":"Fixed direction pose proportions and scale"})
rec={"file":out.relative_to(root).as_posix(),"sha256":sha,"generatedAt":a.finished,"startedAt":a.started,"width":1024,"height":1024,"format":"PNG","tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具无model/quality选择器且未披露真实值","prompt":f"prompts/hit/{a.direction}/{n}.txt","references":refs,"evidence":{"receipt":f"records/hit/{a.direction}/{n}.receipt.json","returnedFields":["image_url","output_hint"],"modelQualityFieldsReturned":False},"native":native,"derivedFrom":{"path":str(source),"sha256":rawsha,"native":native,"retention":"tool-managed original outside task write scope"},"operation":{"type":"uniform-canvas-resize","from":[native["width"],native["height"]],"to":[1024,1024],"filter":"LANCZOS","perFrameAlignment":False},"visualStatus":"pending-sequence-review"}
rp=root/"records"/"hit"/a.direction/(n+".generation.json")
rp.parent.mkdir(parents=True,exist_ok=True)
rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(out),"native":native,"alphaExtrema":im.getchannel("A").getextrema() if "A" in im.getbands() else None,"sha256":sha}))

