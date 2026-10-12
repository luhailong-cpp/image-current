from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
b=Path(r"D:/work/image/designs/creature-combat-20261005/pets/06-xiluo")
qa=b/"qa"; qa.mkdir(exist_ok=True)
font=ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf",28)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for start in [1,5,9,13]:
    canvas=Image.new("RGB",(1280,1360),(34,43,48))
    d=ImageDraw.Draw(canvas)
    for k,i in enumerate(range(start,start+4)):
        x=(k%2)*640;y=(k//2)*680
        im=Image.open(b/"runtime/cast/E"/f"{i:02}.png").convert("RGBA").resize((640,640),Image.Resampling.LANCZOS)
        canvas.paste(im,(x,y+40),im)
        d.text((x+16,y+5),f"cast E {i:02} | 45 ms",font=font,fill="white")
    canvas.save(qa/f"static-cast-E-{start:02}-{start+3:02}.jpg",quality=95)
records=[]
for p in sorted((b/"records/cast/E").glob("*.json")):
    if p.name=="validation.json":continue
    r=json.loads(p.read_text(encoding="utf-8-sig"))
    nat=r.get("native",{}); path=Path(nat.get("path",r.get("file","")))
    records.append({"record":str(p.relative_to(b)),"file":r.get("file"),"nativePath":str(path),"nativeExists":path.exists(),"nativeRecordedSHA":nat.get("sha256"),"nativeSHAConfirmed":path.exists() and sha(path)==nat.get("sha256"),"hasActualModelField":"actualModel" in r,"actualModel":r.get("actualModel"),"hasActualQualityField":"actualQuality" in r,"actualQuality":r.get("actualQuality"),"submittedParameters":r.get("submittedParameters"),"hasConfigSnapshot":bool(r.get("configSnapshot")),"hasUnverifiedReason":bool(r.get("unverifiedReason")),"references":r.get("references",[])})
pathIndex={str(Path(r["nativePath"])).casefold():r["record"] for r in records}
refs={}
for r in records:
    for path in r["references"]:
        key=str(Path(path)).casefold()
        if key in refs:continue
        p=Path(path)
        refs[key]={"path":str(p),"exists":p.exists(),"sha256":sha(p) if p.exists() else None,"matchedNativeRecord":pathIndex.get(key)}
result={"records":records,"uniqueReferences":list(refs.values())}
(qa/"cast-E-source-audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"records":len(records),"nativeSHAConfirmed":sum(x["nativeSHAConfirmed"] for x in records),"allNullActual":all(x["hasActualModelField"] and x["hasActualQualityField"] and x["actualModel"] is None and x["actualQuality"] is None for x in records),"unmappedReferences":[x for x in refs.values() if not x["matchedNativeRecord"]]},ensure_ascii=False))

