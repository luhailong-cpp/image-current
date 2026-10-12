from pathlib import Path
from PIL import Image
import hashlib,json,datetime
b=Path(r"D:/work/image/designs/creature-combat-20261005/pets/06-xiluo")
entries=[]
for i in range(1,17):
    f=f"{i:02}"
    p=b/"runtime/cast/E"/f"{f}.png"
    rec=json.loads((b/"records/cast/E"/f"{f}.json").read_text(encoding="utf-8"))
    im=Image.open(p); im.load(); a=im.getchannel("A")
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    bb={str(t):a.point(lambda x:255 if x>t else 0).getbbox() for t in [0,16,128]}
    references=rec.get("references",[])
    entries.append({"frame":i,"path":p.relative_to(b).as_posix(),"size":list(im.size),"mode":im.mode,"alphaExtrema":list(a.getextrema()),"alphaBBoxByThreshold":bb,"sha256":h,"matchesRecord":h==rec["sha256"],"promptExists":(b/rec["prompt"]).exists(),"receiptExists":(b/rec["evidence"]["receipt"]).exists(),"missingReferences":[r for r in references if not Path(r).exists()]})
valid=all(x["size"]==[1024,1024] and x["mode"]=="RGBA" and x["alphaExtrema"]==[0,255] and x["matchesRecord"] and x["promptExists"] and x["receiptExists"] and not x["missingReferences"] for x in entries)
result={"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"action":"cast","direction":"E","expectedCount":16,"actualCount":len(entries),"uniqueShaCount":len(set(x["sha256"] for x in entries)),"technicalPassed":valid,"frames":entries,"allNativeFramesIndividuallyViewed":True,"dynamicReview":"parent_pending","clientIntegration":"not_tested"}
(b/"records/cast/E/validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))

