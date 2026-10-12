"""Persist manually observed foot-axis and grounding review, never modifies sprites."""
from pathlib import Path
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(ZoneInfo("America/New_York")).isoformat()
w=[
"前伸鞋尖朝左，后抬鞋踝随屈膝折起，未见脚掌向镜头侧外撇。",
"前鞋脚尖朝左，屈膝鞋底接近平，保留鞋向。",
"一鞋支撑一鞋抬起，两个鞋头均朝W；腿交替与支撑可读性另验。",
"前鞋抬、后鞋前掌下压，鞋尖同朝左，非八字分叉。",
"大步腾空，前鞋顺左行进轴；后鞋折起露侧面不等于脚掌外转。",
"与05相近的大步腾空，鞋轴仍顺W，保留鞋向。",
"前腿下放、鞋尖朝左，后踝折起；未见外八。",
"前伸鞋跟向下、鞋尖朝W，保留鞋向。",
"前脚初接近地面，鞋头朝左；未见鞋掌外撇。",
"前鞋近平且脚尖朝左，鞋向可保留；和09的地面高度连续性待修。",
"支撑鞋头朝左、后脚折起，未见左右外撇。",
"后腿伸展，后鞋趾向下前掌蹬离候选；两鞋仍顺W。",
"前伸鞋左向、后足屈膝，方向可保留。",
"两鞋沿W运动，露出部分前鞋底是仰脚，不单独判作外八。",
"前鞋朝左并下放；未见明显外转。",
"前鞋仍朝左，首尾脚轴可保留，接触节奏需动态复核。"]
n=[
"支撑右鞋主要露后跟，左抬鞋底纵向；两鞋未向左右外撇。",
"右支撑鞋跟边平，长轴朝远处N；左鞋底纵向，保留。",
"右支撑、左抬，脚掌轴线近N，未见外八。",
"右后蹬鞋底长轴顺N投影。露底不独立证明离地或外撇。",
"右鞋后伸露底，左鞋高抬；脚底纵向，未横转。",
"交换阶段左鞋伸下、右腿折后，两鞋长轴近竖向。",
"左鞋下放、右鞋底朝镜头，鞋轴仍朝N。",
"左鞋预接触主要露后跟，右鞋抬；未见向侧外撇。",
"左脚初触候选、右脚抬，轴线均顺N。",
"左支撑鞋后跟可读，右鞋底纵向，无明确外八。",
"左平底支撑、右折膝，未见脚掌向外打开。",
"左鞋蹬离露底且长轴顺N；不能把露底本身判为错误。",
"左腿后伸、右腿前提，两鞋轴近N；左铃前摆已修。",
"新摆臂修订保留右腿下伸/左腿折后，两个鞋底纵向。",
"右脚下放、左脚抬，脚掌未横向外转。",
"右鞋预接触时仍露底，脚尖轴未外八；16→01俯仰变化另复核。"]
nw_keep={
4:"前提鞋与后蹬鞋都可读沿NW纵深，露出足底不独立判外八。前掌承重仍需动态复核。",
5:"大步腾空，前鞋脚尖左上、后鞋底顺前后轴，无明确侧向外撇。",
6:"换腿腾空，前鞋鞋底斜是脚踝俯仰，未见明确脚掌横向张开。",
7:"前鞋在左上纵深中下放，后鞋折起；保留鞋向候选。",
8:"前鞋露后跟和少量近侧面，纵深角度可读，未按疑似全错重画。",
9:"前鞋后跟朝镜头、鞋尖往左上，未见明显外转；初触承重另验。",
12:"后蹬鞋底顺NW投影，露底不能证明鞋尖外八；实际接地未确认。",
13:"一脚前提一脚后伸，鞋底沿纵深，不作整帧外转重画。"}
nw_repaired={1,2,3,10,11,14,15,16}
for direction,observations in (("W",w),("N",n),("NW",None)):
    rows=[]
    for frame in range(1,17):
        p=ROOT/f"frames/run/{direction}/{frame:02}.png"
        side=load(p.with_suffix(".png.generation.json"))
        rec=side["generationRecord"]
        repaired=direction=="NW" and frame in nw_repaired
        obs=(observations[frame-1] if observations else ("鞋尖从偏W正侧向调整到NW左上纵深，后跟转朝右下镜头；保留原腿距和相位。待整段动态连续性复核。" if repaired else nw_keep[frame]))
        rows.append({"frame":frame,"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"generationRecord":rec,"decision":"redrawn_direction_improved_pending_motion" if repaired else "keep_no_clear_outward_splay_observed","observation":obs,"criteria":{"shoeAxis":"single_frame_pass","wholeSequence":"pending_root_dynamic_review"},"visualScope":"静态全身联系表+固定下肢裁切复核；不等同游戏动态通过"})
    write(ROOT/f"work/run-{direction}/foot-direction-review-20261003.json",{"schema":1,"direction":direction,"reviewedAt":now,"criterion":"按当前帧膝踝与第二脚趾/脚掌长轴是否顺前进轴判断。不是腿距；不是露鞋底即错误；未使用月影为整套通过样板。","frames":rows,"limitations":["未运行客户端","根锚点与全run全局画布标定待主代理","未据此认定持物/手脚协调/步频全部通过"]})
# Update earlier notes to the selected, independently redrawn pixels.
for direction in ("W","N"):
    p=ROOT/f"work/run-{direction}/grounding-review-20261003.json";doc=load(p)
    doc["reviewedAt"]=now
    for row in doc["frames"]:
        row["sha256"]=sha(ROOT/row["path"])
        row["durationMs"]=75
        row["trialDurationMs"]=75
        if row.get("action")=="shorten_trial":
            row["action"]="review_flight_pose_at_uniform_75ms"
    doc["timing"]={"status":"user_requested_uniform_1200ms_client_unconfirmed","cycleMs":1200,"frameMs":75,"durationsMs":[75]*16,"phaseWeightsApplied":False,"reason":"用户最新明确统一正常1200ms，每帧75ms；不加权、不保留旧快档。时长不代替接地姿态验收。"}
    if direction=="W":
        row=doc["frames"][9]
        row.update(actualPhase="左脚缓冲候选",supportFoot="left",observation="attempt05从09初触独立重画：鞋位较旧10更低、底边更平、膝屈曲；与09地面更接近，仍待全周期注册判断。",action="new_review")
        row=doc["frames"][11]
        row.update(actualPhase="左前掌蹬离候选",supportFoot="left?",observation="新attempt03后腿伸展、后鞋趾下压且持物正确；比旧腾空改善，是否实际贴合共同地面仍待动态/标定。",action="new_review")
    else:
        updates={
          1:("右初触候选","right?","attempt02左铃前、右符后已修；支撑鞋后跟向下，压地连续性待验。","new_review"),
          3:("右支撑候选","right","attempt03左铃经过前中段、右符在后；平底支撑可读。","new_review"),
          4:("右后蹬/离地过渡","right?","鞋底纵向且前掌向下，可作为蹬离候选；仅露鞋底不足证明腾空或接地，须对共同地面复核。","check_toe_contact"),
          12:("左后蹬/离地过渡","left?","鞋底长轴顺N；是否前掌仍接地未确认。attempt02换手拒稿，保留原槽。","check_toe_contact"),
          13:("早腾空","none","attempt02已修左铃前摆、右符后摆；左脚后伸。","new_review"),
          14:("腾空换腿","none","attempt03已修左铃前摆、右符后摆，保留右腿伸下/左腿折后的腿相位。","new_review")}
        for f,(phase,support,obs,act) in updates.items(): doc["frames"][f-1].update(actualPhase=phase,supportFoot=support,observation=obs,action=act)
    write(p,doc)
nw_phases=[
("初触候选","right?","鞋跟朝镜头且底边近平；远近腿遮挡比旧稿改善，但左右归属仍需动态追踪。","review_leg_identity"),
("右缓冲支撑候选","right?","attempt04低位鞋平底、另一鞋高折，较旧02抬高前鞋改善；左右归属和01→02摆臂连续性需动态确认。","new_review"),
("支撑候选","right?","低位平底鞋、后折腿可读；新脚轴已朝NW，左右腿归属仍待联检。","review_leg_identity"),
("后蹬/离地过渡","right?","后腿伸展、前掌方向可读，真实toe接地仍需共同地面确认。","check_toe_contact"),
("早腾空","none","前后大分腿，脚底可见。","review_flight_pose"),
("腾空交换","none","前鞋抬起后鞋折膝，和05相位接近。","review_flight_pose"),
("下降","none","前脚稍下放；未见承重。","check"),
("预接触","left?","前鞋露后跟，但仍比03/11支撑鞋明显高。","check"),
("左初触候选","left","实际工具新稿用attempt05重新登记（attempt03导入撞名已纠正）；近左腿下伸、右腿折高，鞋跟较旧稿接近共同支撑地面；正确近左铃/远右符保持。","new_review"),
("缓冲候选","left?","左腿屈膝，鞋底近平但高度与11不同；脚向定点重画。","review_grounding"),
("支撑候选","left","可见近左鞋平底与胯上承重，新脚轴顺NW。","new_review"),
("蹬离过渡","left?","后腿伸展，鞋底朝镜头；是否前掌接地待复核。","check_toe_contact"),
("早腾空","none","前后分腿并露鞋底。","review_flight_pose"),
("换腿腾空","none","前鞋抬起、后鞋折膝；新鞋轴保持NW。","check_leg_identity"),
("下降","none","前腿下放，新鞋轴保留脚踝俯仰。","check"),
("预接触候选","right?","前鞋伸下仍未明确压地，首尾连续性待动态。","check")]
dur=[75]*16
rows=[]
for f,(phase,foot,obs,act) in enumerate(nw_phases,1):
    p=ROOT/f"frames/run/NW/{f:02}.png";rows.append({"frame":f,"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"actualPhase":phase,"supportFoot":foot,"observation":obs,"action":act,"trialDurationMs":dur[f-1]})
write(ROOT/"work/run-NW/grounding-review-20261003.json",{"schema":1,"direction":"NW","reviewedAt":now,"evidence":"16帧全身与固定下肢裁切逐图复核；静态证据不冒充动态通过。","ground":{"familyNormalizationPending":True,"rootTarget":[512,920],"definition":"全run统一虚拟地面/根锚点待主代理；不逐帧贴最低像素。"},"timing":{"status":"user_requested_uniform_1200ms_client_unconfirmed","cycleMs":1200,"frameMs":75,"durationsMs":dur,"phaseWeightsApplied":False,"reason":"用户最新明确统一正常1200ms，每帧75ms；时长不代替接地姿态验收。"},"frames":rows,"limitations":["NW02/09新接触候选已选，需实播看重心/地面连续性","左右腿归属有遮挡，需慢速联检","未运行客户端"]})
inventory=load(ROOT/"inventory-run-north.json")
inventory["expected_frames"]=55
inventory["ownershipNote"]="W/N/NW各16及NE01-06,09共55；NE07,08,10-16九张由cast代理独立inventory-run-ne-cast.json负责。"
inventory["reviewDocuments"]=[f"work/run-{d}/{name}-review-20261003.json" for d in ("W","N","NW") for name in ("foot-direction","grounding")]
write(ROOT/"inventory-run-north.json",inventory)
print(json.dumps({"reviewedDirections":["W","N","NW"],"inventoryOwnFrames":len(inventory["frames"]),"reviewedAt":now},ensure_ascii=False))

