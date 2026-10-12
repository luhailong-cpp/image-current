"""从当前runtime生成八方向正常960ms与慢放预览；不编辑人物像素。"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
dirs=["N","NE","E","SE","S","SW","W","NW"]
font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",19)
frames=[];sources=[]
for i in range(1,17):
 out=Image.new("RGB",(1024,620),"#e7e4dc");draw=ImageDraw.Draw(out)
 for j,d in enumerate(dirs):
  p=ROOT/f"runtime/run/{d}/{i:02}.png";im=Image.open(p).convert("RGBA").resize((256,256),Image.Resampling.LANCZOS)
  x=(j%4)*256;y=(j//4)*300;out.paste(im,(x,y),im);draw.text((x+12,y+262),f"{d} · {i:02}/16",font=font,fill="#25423d")
  sources.append({"file":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
 draw.text((12,595),"星阵少女 · 正常 960ms / 圈 · 16 × 60ms",font=font,fill="#25423d")
 frames.append(out)
for label,duration in [("960ms",60),("slow",240)]:
 outputFrames=[]
 for frame in frames:
  rendered=frame.copy();draw=ImageDraw.Draw(rendered);draw.rectangle((0,591,1024,620),fill="#e7e4dc")
  draw.text((12,595),f"星阵少女 · {'正常' if duration==60 else '慢放'} {duration*16}ms / 圈 · 16 × {duration}ms",font=font,fill="#25423d")
  outputFrames.append(rendered)
 p=ROOT/f"preview/run-eight-directions-{label}.png"
 outputFrames[0].save(p,save_all=True,append_images=outputFrames[1:],duration=duration,loop=0,disposal=0,blend=0)
 r={"file":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"operation":"完整runtime画布等比显示、八方向拼排；非新AI生成","frameDurationsMs":[duration]*16,"loopMs":duration*16,"extraEndPauseMs":0,"sources":sources}
 Path(str(p)+".generation.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("八方向APNG已生成")
