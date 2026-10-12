from pathlib import Path
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
hand={
("hit","E"):[
"右肩前侧袖筒接右肘和水平右腕，手指扣住五符根部；左臂后伸，左拳完整握铃柄。",
"右肘屈收使符扇贴近胸前，腕与袖口连贯；左肩后侧袖筒接后伸左腕，铜铃随握拳倾斜。",
"受击后仰时右腕仍跟前臂托住符扇；左拳与铃柄连接清楚，没有多掌或腕部反折。",
"前俯压缩时右肘自然收向胸前、右手五符未换手；左臂在躯干后侧伸出袖口握铃。",
"恢复阶段右腕与黑袖自然相接，符扇根部由掌指夹持；左手后降握铃，肩肘腕轮廓连续。",
"右臂保持屈肘持扇，左臂下放、左手扣住铃环；腕部缩短是侧面透视，未见断接。"
],
("hit","W"):[
"远侧右臂屈肘，右掌从袖口伸出托住五符；近侧左臂下伸、左拳握铃，左右归属清楚。",
"右腕在胸前承托符扇，左肩带动屈肘提铃；拇指与拳形围住铃柄，没有悬空握持。",
"右手五符贴胸、右腕随前臂屈收；左拳顺左袖朝前，铃柄沿拳中穿过，连接完整。",
"身体前屈时双肘收拢；右掌仍持符扇、左拳仍握铃，手腕未因收臂而反折。",
"恢复时右肘屈曲持扇，左臂自然下伸，左手握铃环；袖口与手背方向连贯。",
"右手五符保持胸前，左手重新稍抬铜铃；两只手均与各自前臂相接，无换手。"
],
("run","S"):[
"右肩—屈肘—右腕前摆，右掌握五符；左臂后摆，左拳闭合握铃，左右持物连续。",
"与01同段，右前臂和右腕顺接，符根握在掌内；左袖后伸至握铃左手，没有反关节。",
"右臂经过身体侧前、肘略下降仍持五符；左臂随摆动后伸，左腕顺着袖口握铃。",
"左肩带动左肘前摆，左拳握铃柄且腕位处袖筒中心；右臂后摆持五符，未换手。",
"左前臂透视缩短但肩袖—肘—腕链相连；左手牢握铃、右手后摆握五符。",
"左拳前摆继续握铃，右腕后摆与黑袖连贯，肩部摆动与05连续。",
"左臂前摆屈肘、左拳握铃；右臂向后侧摆，右手五符根部仍被掌指包住。",
"左腕和拳从前向袖口伸出，铃柄在拳内；右臂后摆，右掌未反转或脱离袖口。",
"左拳稍回收仍握铃，右袖后伸连接右手五符；肩肘腕方向跟随摆臂。",
"左手在前继续握铃，右手后侧握五符，双腕弯曲幅度与09相接。",
"右肩带右肘前摆、右拳握住符根；左肩带左臂后伸，左拳扣住铃柄。",
"右臂前伸而肘保留弯曲，右腕由黑袖承接五符；左手后摆握铃，手臂没有横接。",
"右手五符进一步前摆，掌指与符根接触；左袖后伸接握铃左手，左右未交换。",
"右腕随前臂略转仍包住符根；左腕在后侧顺袖口握铃，无腕部外折。",
"右手前摆五符、左手后摆铜铃；双肩与两肘的前后关系可读，腕部连接完整。",
"右臂前摆略压缩、左臂后摆，符与铃归属延续15并顺接01；没有多手或断腕。"
],
("run","SW"):[
"右臂前摆，右掌从黑袖口伸出托住五符根；左肩后摆经袖筒接左拳握铃。",
"右前臂前摆并保持腕掌同向，左臂后伸握铃，持物归属与01一致。",
"右肘向下经过身体旁，右掌仍握五符；左腕由后摆黑袖相接，铜铃由左手扣柄。",
"右臂摆至身后仍持五符，左臂屈肘前摆握铃；两条袖筒分别接对应手腕。",
"前摆左拳包住铃柄，腕与前臂同向；后摆右手五符，肩袖连接与04连续。",
"前摆左臂屈肘、拳握铃，后摆右腕承接符扇；两手均有明确袖口和掌指接点。",
"左肩屈肘前摆，左拳握铃杆；右肩带袖筒后伸至五符右手，未出现反向腕。",
"左拳与前臂保持同一握柄轴，右手从后摆袖口握五符；本次手链复看通过，保留先前脚修正。",
"左臂前摆握铃、右臂后摆握五符，双腕与袖筒连续；保留先前后抬脚修正。",
"左拳继续前摆而铃柄牢靠，右腕后摆接五符；与09相比只有自然摆臂差异。",
"右肘前摆、右掌握五符，左肩带左袖后伸，左拳扣铜铃柄，前后链可辨。",
"右掌随屈肘前摆仍包住符根，左腕跟后摆袖口握铃；没有悬空手或多余指组。",
"右臂向前伸出，手腕跟随前臂转向符扇；左臂后摆握铃，肩肘腕没有断接。",
"右腕在前接五符、左腕在后接铃柄，掌指与持物根部接触清楚，姿态承接13。",
"右手前摆五符，左手后摆铜铃，肩袖和黑色腕袖连续，握持未因落地更换。",
"右腕略屈但与前臂同向持符，左拳继续后摆握铃；16至01没有左右手交换。"
]}
hitLeg={
"E":[
"双膝屈曲承受后仰，髋—膝—踝处于朝东的前后运动面；两鞋头朝右，鞋掌没有横撇。",
"重心后移时双膝继续弯曲，踝在对应裤脚下，两鞋向东且贴地。",
"后仰峰值保留自然膝弯，双踝与鞋帮相接，鞋头仍与东向躯干一致。",
"前俯压缩加深双膝屈曲，脚掌保持东向并承托两腿，没有横叉腿。",
"恢复时膝逐渐伸展，两踝未旋出，右向鞋头和支撑面保持连续。",
"双腿恢复较直站姿但未锁膝，两鞋仍朝东、没有鞋掌突然转横。"
],
"W":[
"双膝下沉、两踝在对应裤脚下，鞋头朝西，髋膝踝沿西向运动面而非横叉。",
"后仰承重保持双膝弯曲，两鞋头仍朝左，与腿的前后平面一致。",
"冲击峰值双腿继续支撑，踝鞋轴没有单独外旋，鞋掌保持西向。",
"前俯收身时膝弯加深，左右腿没有交叉，支撑鞋尖仍朝西。",
"重心恢复，膝踝连贯，脚掌与前一帧保持朝左的支撑方向。",
"恢复站稳时双膝仍有余量，两鞋向西、没有横撇或踝关节断接。"
]}
runLeg={
"S":[
"左髋—膝—踝承重链下接朝南鞋头；右腿在后侧收膝，双腿没有横叉。",
"左脚继续髋下承重且鞋头朝南，右膝开始前摆，右鞋中线跟随胫骨。",
"左脚后侧承重鞋头仍朝南；右膝前抬，右踝与鞋轴在纵深摆腿面内。",
"左腿后承重，髋膝踝没有外折；右脚前伸露底属前向透视，鞋底长轴未横转。",
"左腿后蹬、支撑鞋朝南；右脚前伸露底的倾斜跟随整条前腿。",
"左后脚持续支撑，膝踝鞋头方向仍朝南；右脚伸向落点，未单独旋踝。",
"右腿中央接地，膝踝下接朝南鞋头；左腿折膝后收，未张成横叉。",
"右膝压缩承重且踝鞋轴朝南，左脚后收，没有小腿向前而鞋掌横撇。",
"右脚髋下支撑且鞋头朝南；左后腿与鞋一起略偏移，未形成独立踝外旋。",
"右脚继续髋下承重，膝踝与鞋头同向；左腿近体后收，连到11前摆。",
"右腿后侧支撑、鞋头朝南，左膝前摆，两条腿仍各在自己的前后平面内。",
"右脚后承重、踝鞋轴保持正前；左前脚自然露底，鞋底中线随胫骨。",
"右腿后支撑、鞋头朝南，左腿继续前伸，微斜鞋底随整个前腿投影。",
"右后脚蹬地未横撇，左腿接近下次落点，膝踝鞋轴恢复更正面投影。",
"左前脚着地承重，膝踝朝南；右腿后折，双腿没有交叉。",
"左腿压缩承重、鞋头仍朝南，右脚后收，16至01保持左支撑。"
],
"SW":[
"左腿髋下支撑，膝踝下接朝左下的鞋头；右后腿折收，未横叉。",
"左脚同段承重、鞋头顺西南轴，右后鞋收在踝下；髋膝踝关系连贯。",
"左腿后承重且鞋头朝左下，右膝前摆；不是小腿朝前而鞋掌转横。",
"左腿继续后承重，踝鞋轴向左下；右前脚随膝摆动，双腿各在前后运动面。",
"左腿后蹬鞋尖顺左下；右前脚露底的宽头朝左，长轴与小腿前摆透视一致。",
"左后脚持续承重，鞋头仍顺西南轴；右前脚接近落点，膝踝连接稳定。",
"右腿中央支撑，膝踝接朝左下鞋头；左后腿自然折膝，不作机械直腿。",
"右支撑脚朝左下、膝踝相接；已修左后抬鞋收回踝下，保留该修正。",
"右腿髋下支撑，屈膝与朝左下鞋头属于同一前后运动面；左后鞋已向内收回，保留。",
"右脚髋下承重鞋头朝左下；左腿后折、小腿与鞋掌同向，承接09。",
"右后腿承重、鞋头朝左下，左膝前摆，两腿没有横叉或独立扭踝。",
"右后脚承重且鞋头顺西南轴；左脚前伸自然见底，鞋掌长轴随小腿投影。",
"右后腿保持屈膝支撑、鞋头向左下；左前脚鞋底宽头朝左、窄跟朝右下符合前伸透视。",
"右后脚蹬地仍向左下，左前脚降低，髋膝踝—鞋头连续，没有横踢。",
"左前脚着地并朝左下，髋膝踝承重链稳定；右腿后折收起。",
"左腿继续压缩承重、鞋头顺西南轴，右后腿收起，16至01支撑方向连续。"
]}
inv=read(R/"inventory-hit.json")
frames=[]
selected=sorted([f for f in inv["frames"] if (f["action"]=="hit" and f["direction"] in ["E","W"]) or (f["action"]=="run" and f["direction"] in ["S","SW"])],key=lambda f:(f["action"],f["direction"],f["frame"]))
assert len(selected)==44
for f in selected:
 a,d,n=f["action"],f["direction"],f["frame"];p=R/f["path"];h=sha(p)
 assert h==f["sha256"],f["path"]
 im=Image.open(p);assert im.size==(1024,1024) and im.mode=="RGBA"
 rec=read(R/f["source_record"]);assert rec["export"]["sha256"]==h
 ho=hand[(a,d)][n-1];lo=(hitLeg if a=="hit" else runLeg)[d][n-1]
 row={"action":a,"direction":d,"frame":n,"path":f["path"],"sha256":h,"decision":"retained","reason":"手链："+ho+" 脚链："+lo,"handObservation":ho,"legObservation":lo,"source_record":f["source_record"],"fullResolutionViewedThisReview":True,"durationMs":40 if a=="hit" else 75,"sourceHashVerified":True}
 if a=="run":row["supportFoot"]="RIGHT" if 7<=n<=14 else "LEFT"
 frames.append(row)
sheets=[]
for a,d in [("hit","E"),("hit","W"),("run","S"),("run","SW")]:
 rp=R/f"records/{a}-{d}-contact-sheet.derived.json";rec=read(rp);ip=R/rec["file"]
 assert sha(ip)==rec["sha256"]
 for src in rec["derivedFrom"]:assert sha(R/src["file"])==src["sha256"]
 sheets.append({"action":a,"direction":d,"path":str(ip.relative_to(R)).replace("\\","/"),"sha256":sha(ip),"sourceRecord":str(rp.relative_to(R)).replace("\\","/"),"fullCanvasUniformScale":True,"viewedThisReview":True,"allSourceHashesCurrent":True})
refs=[
("D:/work/image/q_daoist_character_pack_4096/02_fire_talisman_boy_transparent_4096.png","committed_identity"),
("D:/work/image/designs/jubaozhai-ui/02-characters.png","confirmed_style"),
(str(R/"work/video-axis/reference-continuous-0.jpg"),"motion_only"),
(str(R/"work/video-axis/reference-continuous-3.jpg"),"motion_only")]
out={"schemaVersion":1,"reviewer":"finish_s_sw","reviewedAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"status":"full_limb_static_review_passed_dynamic_pending_root_review","frameCount":44,"decisionSummary":{"retained":44,"replaced":0},"frames":frames,"knownUnresolvedArtFailures":[],"contactSheets":sheets,"references":[{"path":p.replace("\\","/"),"sha256":sha(Path(p)),"role":role,"viewed":True} for p,role in refs],"reviewScope":["本轮实际重看44张1024正式图及四组完整画布联系表，专查肩—肘—腕、握持、解剖右手五符/左手铜铃。","逐图重查髋—膝—踝—鞋头，包含所有支撑脚；允许正常屈膝、前后蹬伸和透视，不把它们机械拉直。","对同组相邻画面核对持物归属、双手连接和鞋掌方向；跑步保留四个位置各两帧，不更改支撑节奏。"],"timing":{"hit":{"framesPerDirection":6,"frameMs":40,"totalMs":240},"run":{"framesPerDirection":16,"frameMs":75,"totalMs":1200,"supportPairs":{"RIGHT":[[7,8],[9,10],[11,12],[13,14]],"LEFT":[[15,16],[1,2],[3,4],[5,6]]}}},"newImageGeneration":{"performed":False,"reason":"本轮逐图复核未发现新的明确坏帧，全部保留当前正式图，包括前轮已修的SW08/09。","configuredTarget":"GPT Image 2.5 Sunburst / max","submittedModel":None,"submittedQuality":None,"actualModel":None,"actualQuality":None,"confirmation":"本轮无新增生图；现有图实际型号/质量证据保留各自原始生成记录，不将目标冒充实测。"},"limits":["本报告为本轮静态逐图及相邻姿态复核，主线程统一执行可见浏览器动态验收。","视频角色较小、有HUD遮挡，只据其核对动作平面和连续性；未声称精确测量关节角度。","客户端未接入。"]}
(R/"reviews/full-limb-hit-S-SW-20261004.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"report":"reviews/full-limb-hit-S-SW-20261004.json","reviewedAt":out["reviewedAt"],"frames":len(frames),"retained":44,"replaced":0,"contactSheets":len(sheets),"allCurrentHashesVerified":True}))

