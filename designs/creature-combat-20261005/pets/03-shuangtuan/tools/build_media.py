from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
root=Path(__file__).resolve().parents[1]
out=root/"preview"/"media";out.mkdir(parents=True,exist_ok=True)
qa=root/"qa"/"contact";qa.mkdir(parents=True,exist_ok=True)
media=[]
for action,count,ms in [("hit",6,40),("attack",12,30),("cast",16,45)]:
 for d in ("E","W"):
  files=[root/"runtime"/action/d/f"{i:02}.png" for i in range(1,count+1)]
  if not all(p.exists() for p in files):continue
  frames=[];sources=[];tiles=[]
  for i,p in enumerate(files,1):
   im=Image.open(p).convert("RGBA")
   bg=Image.new("RGBA",(512,512),(232,237,232,255))
   bg.alpha_composite(im.resize((512,512),Image.Resampling.LANCZOS))
   frames.append(bg.convert("RGB"))
   tile=Image.new("RGB",(512,544),(232,237,232));tile.paste(bg.convert("RGB"))
   dr=ImageDraw.Draw(tile);dr.text((14,519),f"{action} {d}  {i:02}/{count}  {ms} ms",fill=(22,58,46))
   tiles.append(tile);sources.append({"file":p.relative_to(root).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
  cols=3 if count==6 else 4;rows=math.ceil(count/cols)
  sheet=Image.new("RGB",(cols*512,rows*544),(232,237,232))
  for k,tile in enumerate(tiles):sheet.paste(tile,((k%cols)*512,(k//cols)*544))
  sheet_path=qa/f"{action}-{d}.png";sheet.save(sheet_path)
  for tag,factor in [("normal",1),("slow",4)]:
   target=out/f"{action}-{d}-{tag}.webp"
   frames[0].save(target,save_all=True,append_images=frames[1:],duration=ms*factor,loop=0,lossless=True,method=4)
   with Image.open(target) as test:
    frame_count=test.n_frames
    if frame_count!=count:raise ValueError(f"Animation lost frame: {target}")
   media.append({"file":target.relative_to(root).as_posix(),"width":512,"height":512,"frameCount":count,"durationMs":ms*factor,"speed":1/factor,"operation":"preview-only lossless webp from exact ordered runtime frames; neutral background; no generated or interpolated frames","sources":sources})
  media.append({"file":sheet_path.relative_to(root).as_posix(),"operation":"preview-only labeled contact sheet from runtime frames","sources":sources})
(root/"preview"/"media-manifest.json").write_text(json.dumps(media,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"completeGroups":len(media)//3,"previews":len(media)}))

