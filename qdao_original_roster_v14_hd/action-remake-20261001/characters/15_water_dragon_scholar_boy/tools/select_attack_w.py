from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy");out=B/"review/diagonals";out.mkdir(parents=True,exist_ok=True)
keys=["attack-W-01-foot-v2","attack-W-02-foot-v2","attack-W-03-foot-v1","attack-W-04-foot-v1","attack-W-05-foot-v1","attack-W-06-foot-v1","attack-W-07-foot-v1","attack-W-08-foot-v1","attack-W-09-foot-v1","attack-W-10-foot-v1","attack-W-11-foot-v1","attack-W-12-foot-v2"]
notes=["低架起势，右手持扇、近左空手护腰，双靴承重。","起势调整，保持双脚位置；右手持扇、左空手后展。","右臂抬到头后蓄力极点，左空手前伸平衡；双靴与W06固定。","以原W05-v2重选W04，右肘尚屈，扇轴较靠胸，启动前挥。","以原W04-v3重选W05，局部屈肘已修复扇尖出画；幅度介于W04和W06。","W06-v2为前挥伸展极点，握轴连贯，扇已全部入画。","右腕下压随动，左空手后展，靴位稳定。","扇回到胸腹，右肘回收，近左空手靠前，重心略后。","扇回到直立守势，双臂收势，脚位延续。","低架恢复，身体和头尺寸回稳，右手握轴。","W11-v2从W10局部修正，头脚尺寸保持，右腕微上提、左手放松。","结束守势，右手扇回收胸前，左空手下放，保留短身比例。"]
q=json.loads((B/"audit/attack-selection.json").read_text(encoding="utf-8-sig"));q["frames"]=[x for x in q["frames"] if x["direction"]!="W"]
now=datetime.now(timezone.utc).isoformat();frames=[];review=[]
font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",18)
contact=Image.new("RGB",(1536,1290),(226,231,236));draw=ImageDraw.Draw(contact)
for i,key in enumerate(keys):
 p=B/"sources/new"/(key+".png");im=Image.open(p).convert("RGBA");a=im.getchannel("A");box=a.point(lambda x:255 if x>8 else 0).getbbox()
 row={"action":"attack","direction":"W","frame":i+1,"source":p.relative_to(B).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"accepted":True,"nativeSingleFrame":True,"generationRecord":"provenance/generation/"+key+".json","review":{"reviewer":"/root/finish_attack_diagonals","reviewedAt":now,"notes":notes[i]+" 本轮保留原动作，只改后侧膝踝和靴，双靴鞋尖与脚掌轴均朝W，前掌/后跟落在地面；已排除放大重试稿。逐图已看；静态候选，完整动态观感仍待主审。"},"event":{2:"windup_peak",4:"contact",5:"strike_peak",11:"recovery_end"}.get(i)}
 q["frames"].append(row);review.append({"key":key,"slot":i+1,"observations":notes[i],"alphaBBoxGreater8":box,"nativeSize":im.size,"sha256":row["sha256"]})
 frame=Image.new("RGB",(512,560),(226,231,236));spr=im.resize((512,512),Image.Resampling.LANCZOS);frame.paste(spr,(0,0),spr)
 ImageDraw.Draw(frame).text((12,524),f"普攻 W {i+1:02} / 12",font=font,fill=(20,30,40));frames.append(frame)
 thumb=frame.resize((384,420));contact.paste(thumb,(i%4*384,i//4*430))
q.update(staticCandidateCount=len(q["frames"]),dynamicAccepted=False,exported=False,updatedAt=now)
(B/"audit/attack-selection.json").write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding="utf8")
contact.save(out/"attack-W-contact.png")
for label,duration in [("normal",30),("slow",120)]:
 frames[0].save(out/("attack-W-"+label+".gif"),save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=False,disposal=2)
(out/"attack-W-review.json").write_text(json.dumps({"reviewedAt":now,"status":"static_selected_dynamic_review_pending","frameDurationMs":30,"durationMs":360,"frames":review,"clientIntegrated":False,"operation":"review contact/GIF wholecanvas downsample; no altered sprite geometry","remaining":["主审正常倍速、慢速完整实播，重点W03到W04弧线与W07到W08回收跨度","当前为离线候选，非客户端验收"]},ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"selected":len(q["frames"]),"W":len(keys),"bboxes":[[r["key"],r["alphaBBoxGreater8"]] for r in review]}))


