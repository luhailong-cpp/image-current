from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/legacy-ling-yue")
data={}
for action,count,cols,duration in [("hit",6,3,40),("attack",12,4,30)]:
    rows=(count+cols-1)//cols
    contact=Image.new("RGB",(cols*384,rows*410),(52,59,68))
    draw=ImageDraw.Draw(contact)
    frames=[]
    vals=[]
    for n in range(1,count+1):
        p=root/f"runtime/{action}/W/{n:02}.png"
        im=Image.open(p)
        if im.mode!="RGBA" or im.size!=(1024,1024):raise ValueError(p)
        small=im.resize((368,368),Image.Resampling.LANCZOS)
        x=((n-1)%cols)*384+8;y=((n-1)//cols)*410+27
        contact.paste(small,(x,y),small)
        draw.text((x,y-20),f"W {action} {n:02} / {duration} ms",fill="white")
        matte=Image.new("RGBA",(512,512),(52,59,68,255))
        matte.alpha_composite(im.resize((512,512),Image.Resampling.LANCZOS))
        frames.append(matte.convert("RGB"))
        vals.append({"frame":n,"file":str(p.relative_to(root)).replace("\\","/"),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"mode":im.mode,"size":list(im.size),"alpha":im.getchannel("A").getextrema(),"bbox":im.getbbox()})
    contact.save(root/f"receipts/W-{action}-contact.png")
    for speed in [1,0.25]:
        frames[0].save(root/f"receipts/W-{action}-{'normal' if speed==1 else 'slow'}.webp",save_all=True,append_images=frames[1:],duration=int(duration/speed),loop=0,lossless=True)
    data[action]={"expected":count,"found":len(vals),"uniqueSHA":len(set(v["sha256"] for v in vals)),"frames":vals}
(root/"receipts/W-hit-attack-validation.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:{"found":v["found"],"uniqueSHA":v["uniqueSHA"]}for k,v in data.items()}))

