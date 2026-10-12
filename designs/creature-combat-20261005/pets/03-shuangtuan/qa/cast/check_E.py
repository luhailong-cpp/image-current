from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
BASE=Path(__file__).resolve().parents[2]
out=BASE/"qa"/"cast"
sheet=Image.new("RGB",(2048,2176),(46,54,55))
draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",24)
checks=[]
for n in range(1,17):
 p=BASE/"runtime"/"cast"/"E"/f"{n:02d}.png"
 im=Image.open(p); a=im.getchannel("A")
 pix=a.load()
 edge=[(x,y,pix[x,y]) for x,y in ([(x,0) for x in range(im.width)]+[(x,im.height-1) for x in range(im.width)]+[(0,y) for y in range(im.height)]+[(im.width-1,y) for y in range(im.height)]) if pix[x,y]>8]
 x=((n-1)%4)*512;y=((n-1)//4)*544
 cell=Image.new("RGB",(512,512),(46,54,55))
 r=im.resize((512,512),Image.Resampling.LANCZOS)
 cell.paste(r,(0,0),r)
 sheet.paste(cell,(x,y+32));draw.text((x+12,y+4),f"CAST E {n:02d} | 45 ms",font=font,fill=(235,239,230))
 checks.append({"frame":n,"file":p.relative_to(BASE).as_posix(),"size":list(im.size),"mode":im.mode,"alpha":list(a.getextrema()),"alphaBBox":a.getbbox(),"edgeAlphaOver8Count":len(edge),"edgeAlphaOver8Max":max([v for _,_,v in edge],default=0),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
sheet.save(out/"E-contact-sheet.png")
report={"frames":checks,"count":len(checks),"uniqueShaCount":len(set(v["sha256"] for v in checks)),"all1024RGBA":all(v["size"]==[1024,1024] and v["mode"]=="RGBA" for v in checks),"allHaveTransparency":all(v["alpha"]==[0,255] for v in checks),"visualReview":"pending written notes","continuousPlayback":"not inspected, host file browser restriction; to be reviewed in preview externally"}
(out/"E-technical.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"count":report["count"],"unique":report["uniqueShaCount"],"edgeCounts":[[v["frame"],v["edgeAlphaOver8Count"],v["edgeAlphaOver8Max"]] for v in checks]},ensure_ascii=False))

