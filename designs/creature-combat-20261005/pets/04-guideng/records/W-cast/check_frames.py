import json,hashlib,datetime
from pathlib import Path
from PIL import Image
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/04-guideng")
rows=[]
for i in range(1,17):
    p=base/"runtime/cast/W"/f"{i:02d}.png"
    im=Image.open(p)
    a=im.getchannel("A")
    rec=json.loads((base/"records/W-cast"/f"{i:02d}.generation.json").read_text(encoding="utf-8-sig"))
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    rows.append({"frame":i,"path":str(p),"size":list(im.size),"mode":im.mode,"alphaExtrema":list(a.getextrema()),"alphaBBox":a.getbbox(),"opaqueBBox":a.point(lambda x:255 if x>=128 else 0).getbbox(),"sha256":sha,"shaMatchesRecord":sha==rec["sha256"],"receiptExists":(base/"records/W-cast"/f"{i:02d}.receipt.json").exists(),"promptExists":(base/"prompts/W-cast"/f"{i:02d}.txt").exists()})
report={"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"group":"W-cast","frames":16,"expected":16,"uniqueSha256":len(set(x["sha256"] for x in rows)),"technicalPassed":all(x["size"]==[1024,1024] and x["mode"]=="RGBA" and x["alphaExtrema"]==[0,255] and x["shaMatchesRecord"] and x["receiptExists"] and x["promptExists"] for x in rows),"framesNewThisContinuation":"08-16","visualReview":"Individually viewed native outputs and final exported PNGs for 08-16; true rear upper-left view, right lantern/left branch maintained; both soles and back sash consistent. Full continuous playback remains parent QA responsibility.","clientVerified":False,"rows":rows}
(base/"records/W-cast/technical-qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="rows"},ensure_ascii=False))
