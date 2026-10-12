from pathlib import Path
import json, hashlib
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw
ROOT=Path(r"D:/work/image/designs/creature-combat-20261005/pets/11-xiajiaolu")
PD=ROOT/"provenance"/"cast"/"W"
rows=[]
roles=["原有E身份与解剖","原有W身份与解剖","主要画法材质完成度","前帧连续性构图；01为16收势构图参考"]
for n in range(1,17):
    nn=f"{n:02}"
    p=PD/(nn+".json")
    data=json.loads(p.read_text(encoding="utf-8"))
    receipt=json.loads((ROOT/data["evidence"]["receipt"]).read_text(encoding="utf-8"))
    data["references"]=[{"path":ref,"role":roles[i] if i<len(roles) else "continuity","sha256":hashlib.sha256(Path(ref).read_bytes()).hexdigest()} for i,ref in enumerate(receipt["references"])]
    data["generatedAtLocal"]=datetime.fromisoformat(data["generatedAt"].replace("Z","+00:00")).astimezone(timezone(timedelta(hours=-4))).isoformat()
    data["timezone"]="America/New_York"
    data["visualStatus"]="individual-frames-inspected; sequence-playback-pending-root-review"
    data["visualReview"]={"method":"Every native generated image was displayed and visually inspected in generation tool outputs; final contact sheet inspected separately.","direction":"W rear three-quarter facing upper-left, back of head/back/rump visible","anatomy":"two antlers, two ears, four deer legs/cloven hooves, one short tail, no wings","accessories":"purple-blue nape knot/scarf and small flower; chest wooden pendant not relocated to back","clientValidated":False}
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    im=Image.open(ROOT/data["file"])
    alpha=im.getchannel("A")
    rows.append({"frame":n,"file":data["file"],"size":list(im.size),"mode":im.mode,"alphaExtrema":list(alpha.getextrema()),"alphaBBox":list(alpha.getbbox()),"sha256":data["sha256"]})
qa={"action":"cast","direction":"W","count":len(rows),"allNative1254Square":all(r["size"]==[1254,1254] for r in rows),"allRGBA":all(r["mode"]=="RGBA" for r in rows),"allHaveTransparency":all(r["alphaExtrema"]==[0,255] for r in rows),"uniqueSHA256":len({r["sha256"] for r in rows}),"nativeFinalFramesInspected":list(range(1,17)),"dynamicPlaybackReviewed":False,"clientValidated":False,"frames":rows,"targetedRepairs":[{"frame":6,"reason":"Glow touched top edge; redrawn with bounded glow","rejectedSHA256":"35da00e08c8a1b16194a988eeacb6c1e06fdfbcaf61fc56258c9c4e025b1a513","attemptPrompt":"prompts/cast/W/06.attempt1.txt","attemptReceipt":"provenance/cast/W/06.receipt.json"},{"frame":1,"reason":"Initial support positions differed from later sequence; independently redrawn with frame16 composition reference","attemptRecord":"provenance/cast/W/01.attempt1.json"}],"failures":[{"frame":9,"attempt":1,"elapsedSeconds":61.7,"error":"connection failed: error sending request"},{"frame":9,"attempt":2,"elapsedSeconds":58.7,"error":"connection failed: error sending request"}]}
(PD/"QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")
canvas=Image.new("RGB",(1280,1360),(225,226,230))
draw=ImageDraw.Draw(canvas)
for idx,row in enumerate(rows):
    x=(idx%4)*320;y=(idx//4)*340
    for yy in range(y+20,y+340,20):
        for xx in range(x,x+320,20):
            draw.rectangle((xx,yy,xx+19,yy+19),fill=(238,238,239) if ((xx-x)//20+(yy-y-20)//20)%2==0 else (205,207,211))
    im=Image.open(ROOT/row["file"]).resize((320,320),Image.Resampling.LANCZOS)
    canvas.paste(im,(x,y+20),im)
    draw.text((x+8,y+4),f"CAST W {idx+1:02}",fill=(20,20,24))
canvas.save(PD/"contact-sheet.jpg",quality=93)
print(json.dumps({k:v for k,v in qa.items() if k not in ["frames","targetedRepairs","failures"]},ensure_ascii=False))

