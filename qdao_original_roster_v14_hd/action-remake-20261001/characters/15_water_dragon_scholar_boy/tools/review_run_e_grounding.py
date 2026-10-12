from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone
import json,hashlib
b=Path(__file__).resolve().parents[1]
rows=json.loads((b/'audit/run-E-selection.json').read_text(encoding='utf-8'))['frames']
labels=['左足跟初触','左腿压缩承重','左支撑/右腿通过','左后掌推蹬（v3）','右领先早腾空','第一腾空峰值','第一下降','右足跟已到接触高度','右初触/压脚准备','右腿承重','右支撑/左腿通过','右后掌蹬离','左领先早腾空','第二腾空峰值','第二下降（v5）','左预触地']
dur=[50,70,60,40,30,30,35,45,50,70,60,40,30,25,35,50]
assert sum(dur)==720
data=[]
for r in rows:
 p=b/r['source']; im=Image.open(p).convert('RGBA'); a=im.getchannel('A'); box=a.point(lambda x:255 if x>128 else 0).getbbox(); y=box[3]-1
 xs=[x for yy in range(y-7,y+1) for x in range(im.width) if a.getpixel((x,yy))>128]
 data.append({'frame':r['frame'],'source':r['source'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generationRecord':r['generationRecord'],'soleNativeY':y,'soleNativeXRangeLast8Rows':[min(xs),max(xs)],'soleOutputY':round(49+y*940/1254,2),'planeDeltaSourceY':y-1191,'phaseObserved':labels[r['frame']-1],'customTrialMs':dur[r['frame']-1]})
attempts=[]
for n in [2,3]:
 key=f'run-E-{n:02d}-v3';p=b/'sources/new'/f'{key}.png';im=Image.open(p)
 attempts.append({'source':p.relative_to(b).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'soleNativeY':im.getchannel('A').point(lambda x:255 if x>128 else 0).getbbox()[3]-1,'generationRecord':f'provenance/generation/{key}.json','accepted':False,'reason':'请求局部收短支撑下肢但实际鞋底高度未改变，不能宣称修好；保留原选v2。'})
out={'snapshotAt':datetime.now(timezone.utc).isoformat(),'action':'run','direction':'E','staticFrameCount':16,'groundingAcceptance':'not_passed','clientAcceptance':'not_run_no_client','sourceSnapshot':'audit/run-E-selection.json read-only snapshot','measurementMethod':'逐张目视确认最低主体像素来自鞋底后，扫描alpha>128最低行；数值仅诊断，不用于逐帧平移。X范围为最低8行鞋底像素范围。','transform':{'wholeCanvasScale':[1254,940],'fixedInset':[42,49],'output':[1024,1024],'sourcePlaneY':1191,'outputPlaneY':942},'presetsMs':[480,640,720,800],'customDurationsMs':dur,'customCycleMs':sum(dur),'customBasis':'依据15角色E实图相位：02/03与10/11承重多停留，05/06和13/14飞行短停；08实际足跟已到接触高度，计早接触。没有沿用07权重。','frames':data,'rejectedLocalEdits':attempts,'browser':{'status':'pending'},'recommendation':'E04脚尖/摆臂、E10回摆和E15下降已针对性修正；更新快照后复核640/720/800与承重720，正式节奏未定。'}
(b/'audit/run-E-grounding-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
sheet=Image.new('RGB',(1536,1720),(227,232,236))
for i,r in enumerate(data):
 im=Image.open(b/r['source']).convert('RGBA');can=Image.new('RGBA',(1024,1024));can.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
 tile=Image.new('RGB',(384,430),(227,232,236));d=ImageDraw.Draw(tile);d.text((8,6),f'E{r["frame"]:02d} 鞋底y={r["soleNativeY"]} Δ{r["planeDeltaSourceY"]:+}',font=font,fill=(25,50,65));sm=can.resize((384,384),Image.Resampling.LANCZOS);tile.paste(sm,(0,35),sm)
 d.line((0,35+942*.375,384,35+942*.375),fill=(200,60,60),width=1);sheet.paste(tile,((i%4)*384,(i//4)*430))
sheet.save(b/'audit/run-E-grounding-contact.png')
print(json.dumps({'measured':len(data),'customMs':sum(dur),'sourceSoleYs':[r['soleNativeY']for r in data]},ensure_ascii=False))

