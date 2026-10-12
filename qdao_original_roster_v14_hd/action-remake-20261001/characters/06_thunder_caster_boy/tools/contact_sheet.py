from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,argparse,math
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument("action");ap.add_argument("direction");args=ap.parse_args()
counts={"run":16,"hit":6,"attack":12,"cast":16};labels={"run":"跑步","hit":"受击","attack":"普攻","cast":"施法"};count=counts[args.action]
font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",20)
w=320;h=350;cols=4;rows=math.ceil(count/cols);out=Image.new("RGB",(cols*w,rows*h),(224,227,225));draw=ImageDraw.Draw(out);sources=[]
for n in range(count):
 x=(n%cols)*w;y=(n//cols)*h;p=R/"runtime"/args.action/args.direction/f"{n:02d}.png"
 if p.exists():
  im=Image.open(p).convert("RGBA").resize((w,w),Image.Resampling.LANCZOS);out.paste(im,(x,y),im)
  sources.append({"file":p.relative_to(R).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"generationRecord":p.relative_to(R).as_posix()+".generation.json"})
  label=f"{labels[args.action]} {args.direction} {n:02d} · 当前帧"
 else:label=f"{n:02d} 未生成";draw.rectangle((x,y,x+w-1,y+h-1),fill=(200,202,200))
 draw.text((x+12,y+w+3),label,font=font,fill=(40,50,50))
p=R/"review"/f"{args.action}_{args.direction}_contact.png";out.save(p)
r={"file":p.relative_to(R).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"derivedFrom":sources,"operation":"完整画布等比缩小至320方图并排，仅用于当前帧逐帧检查；空槽明确显示未生成，不构成游戏帧","actualModel":None,"actualQuality":None}
p.with_name(p.name+".generation.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(str(p))

