"""Build requested review contact sheets and animated previews from full canvases."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
import argparse, hashlib, json, math
from timing_profile import RUN_NORMAL_DURATIONS, RUN_FRAME_MS
ROOT = Path(__file__).resolve().parents[1]
SPECS = {"run":(16,RUN_FRAME_MS),"hit":(6,40),"attack":(12,30),"cast":(16,45)}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write_record(out, sources, operation):
    data={"file":out.relative_to(ROOT).as_posix(),"sha256":sha(out),"createdAt":datetime.now(timezone.utc).isoformat(),"route":"deterministic_preview","modelGenerated":False,"actualModel":None,"actualQuality":None,"operation":operation,"derivedFrom":sources,"note":"预览只按统一整画布显示原PNG，不计新增动作帧；实际版本/质量追溯各帧来源"}
    out.with_name(out.name+".generation.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def build(action,direction):
    count,ms=SPECS[action]
    sources=[]; frames=[]
    for i in range(1,count+1):
        p=ROOT/"frames"/action/direction/f"frame_{i:02d}.png"
        if p.exists():
            sources.append({"frame":i,"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"generation":p.with_suffix(".generation.json").relative_to(ROOT).as_posix()})
            with Image.open(p) as im: frames.append(im.convert("RGBA").copy())
        else: frames.append(None)
    font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",18)
    cell=280; cols=4; rows=math.ceil(count/cols)
    grid=Image.new("RGB",(cols*cell,rows*(cell+28)),(245,240,226))
    draw=ImageDraw.Draw(grid)
    for i,im in enumerate(frames):
        x=(i%cols)*cell; y=(i//cols)*(cell+28)
        draw.rectangle((x,y,x+cell-1,y+cell+27),outline=(140,150,140))
        draw.text((x+8,y+5),f"{action} {direction}  {i+1:02d}"+(" / 缺帧" if im is None else ""),fill=(34,60,48),font=font)
        if im is not None:
            thumb=im.resize((cell,cell),Image.Resampling.LANCZOS)
            grid.paste(thumb,(x,y+28),thumb)
    out=ROOT/"preview"/f"{action}_{direction}_contact.png"
    grid.save(out);write_record(out,sources,{"type":"whole_canvas_contact_sheet","cellCanvas":cell,"missingSlots":"label_only_no_placeholder_frame"})
    if any(im is None for im in frames):
        print(json.dumps({"action":action,"direction":direction,"present":len(sources),"target":count,"animated":False})); return
    variants = (("normal",ms,1),("slow",ms*4,4))
    for speed,period,mult in variants:
        rendered=[]
        for im in frames:
            stage=Image.new("RGBA",(512,512),(245,240,226,255))
            stage.alpha_composite(im.resize((512,512),Image.Resampling.LANCZOS))
            rendered.append(stage.convert("RGB"))
        durations=list(period) if isinstance(period,list) else [period]*count
        if action != "run" and not isinstance(period,list) and period%10:
            durations=[math.floor(period/10)*10 if i%2==0 else math.ceil(period/10)*10 for i in range(count)]
        out=ROOT/"preview"/f"{action}_{direction}_{speed}{'.apng' if action=='run' else '.gif'}"
        if action=="run":
            rendered[0].save(out,format="PNG",save_all=True,append_images=rendered[1:],duration=durations,loop=0,disposal=0,blend=0)
        else:
            rendered[0].save(out,save_all=True,append_images=rendered[1:],duration=durations,loop=0,disposal=2,optimize=False)
        write_record(out,sources,{"type":"animated_whole_canvas_preview","encoding":"APNG" if action=='run' else "GIF","scale":0.5,"background":[245,240,226],"durationsMs":durations,"logicalFrameMs":ms*mult,"sequenceDurationMs":sum(durations),"speedMultiplier":1/mult,"timingStatus":"user_selected_offline_960_client_unconfirmed" if action=="run" else "specified","encodingTimingNote":"跑步APNG与HTML精确60ms/帧，总960ms，无额外首尾帧。战斗GIF只支持10ms单位，施法45ms用40/50ms交替，总720ms。"})
    print(json.dumps({"action":action,"direction":direction,"present":len(sources),"target":count,"animated":True}))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("action",choices=SPECS);p.add_argument("direction");a=p.parse_args();build(a.action,a.direction)
