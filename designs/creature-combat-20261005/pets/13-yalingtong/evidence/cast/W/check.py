from pathlib import Path
import hashlib,json
from PIL import Image
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/13-yalingtong")
items=[]
for i in range(1,17):
 n=f"{i:02d}"; f=root/f"runtime/cast/W/{n}.png"; im=Image.open(f); a=im.getchannel("A")
 e=json.loads((root/f"evidence/cast/W/{n}.generation.json").read_text(encoding="utf-8"))
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 edge=list(a.crop((0,0,1024,1)).getdata())+list(a.crop((0,1023,1024,1024)).getdata())+list(a.crop((0,0,1,1024)).getdata())+list(a.crop((1023,0,1024,1024)).getdata())
 items.append({"frame":n,"file":str(f),"size":list(im.size),"mode":im.mode,"alphaExtrema":list(a.getextrema()),"alphaBBox":list(a.getbbox()),"substantialAlphaBBox":list(a.point(lambda v:255 if v>=16 else 0).getbbox()),"edgeAlphaMax":max(edge),"sha256":sha,"recordShaMatches":sha==e["sha256"],"actualModel":e.get("actualModel"),"actualQuality":e.get("actualQuality"),"promptExists":(root/e["prompt"]).exists(),"nativeExists":Path(e["native"]["path"]).exists()})
out={"scope":"cast W post AI correction; before root final uniform export","count":len(items),"expected":16,"duplicateShaCount":len(items)-len(set(x["sha256"] for x in items)),"all1024RGBA":all(x["size"]==[1024,1024] and x["mode"]=="RGBA" for x in items),"allRecordShaMatches":all(x["recordShaMatches"] for x in items),"allTransparent":all(x["alphaExtrema"]==[0,255] for x in items),"allPromptExists":all(x["promptExists"] for x in items),"allNativeExists":all(x["nativeExists"] for x in items),"frames":items}
(root/"evidence/cast/W/technical-check.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in out.items() if k!="frames"},ensure_ascii=False))
print(json.dumps([{"frame":x["frame"],"edgeAlphaMax":x["edgeAlphaMax"],"bboxAlpha16":x["substantialAlphaBBox"]} for x in items],ensure_ascii=False))

