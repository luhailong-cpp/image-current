"""Record reviewed two-pose spatial stages, retaining prior review as history."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,argparse
R=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
ap=argparse.ArgumentParser();ap.add_argument("--browser-reviewed",action="store_true");a=ap.parse_args()
applied=rd(R/"provenance/grounding-pairs-applied.json")["applied"]
review=rd(R/"provenance/offline-visual-review.json")
notes={"N":"背面纵向跟轴朝N，接地点随身体经过向画面下方推进；露底只属于折起的摆腿。","NE":"后斜视NE，接地点向屏幕左后方逐段推进，非横向外八。","E":"侧视E，支撑从屏幕右前方经过髋下移向屏幕左后方，鞋尖均朝右。","SE":"前斜视SE，支撑从前伸经过身下再落到后侧；鞋掌顺SE不横撇。","S":"正面S，左腿屏右、右腿屏左；前落在近处，后侧在较高纵深，同脚不提前换支撑。","SW":"前斜视SW，支撑前落→身下→右后方推进，缩短外伸前掌，鞋尖顺SW。","W":"侧视W，支撑由屏左前方经过髋下向屏右后方推进，脚尖朝左。","NW":"后斜视NW，支撑由较前方经过髋下向屏右后方推进，后跟与抬起的鞋底区分。"}
labels={"front_landing":"前方直脚落地","under_hip":"身体经过支撑脚上方","behind_hip":"支撑脚相对身体进入后侧","rear_push":"后方前掌承重准备换脚"}
for g in review["groups"]:
 if g["action"]!="run":continue
 d=g["direction"];rows=rd(R/f"grounding4/{d}/selected.json");fs=[x for x in applied if x["direction"]==d]
 assert len(rows)==16 and all(r["visualStaticReviewed"] for r in rows)
 pairs=[{"frames":[n,n+1],"supportFoot":rows[n-1]["supportFoot"],"position":rows[n-1]["position"],"description":labels[rows[n-1]["position"]],"durationMs":150} for n in range(1,17,2)]
 segs=[{"supportFoot":rows[n-1]["supportFoot"],"frames":list(range(n,n+8)),"durationMs":600} for n in [1,9]]
 changed=[f["frame"] for f in fs if f["mode"]=="local_AI_edit"];retained=[f["frame"] for f in fs if f["mode"]=="retained"];rephased=[f["frame"] for f in fs if f["mode"]=="rephased_existing"]
 g.update(staticReviewed=True,retained=f"原槽保留{retained}；既有独立帧改相位{rephased}",repaired=f"局部AI修正{changed}",footDirection=notes[d],pose="同一支撑脚连续8帧，四个空间位置各2张独立姿态；另一脚抬起前摆，09换脚，16→01衔接。",browserNormalSlowObserved=a.browser_reviewed,offlineVisualAccepted=True,frameMs=75,loopMs=1200)
 g["grounding4"]={"latestRequirement":"同一脚连续8张独立接地姿态，前落/身下/后侧/后蹬各2帧，再换脚。","staticReviewed":True,"offlineReviewed":a.browser_reviewed,"contactSegments":segs,"positionPairs":pairs,"replacementFrames":changed,"retainedFrames":retained,"rephasedFrames":rephased,"spatialInterpretation":notes[d],"sourcePlan":f"grounding4/{d}/selected.json","appliedRecord":"provenance/grounding-pairs-applied.json","normalLoopMs":1200,"frameMs":75,"mirrored":False,"interpolated":False,"repeatedImages":False}
 if a.browser_reviewed:g.update(displaySizesPx=[128,256],loopBoundaryStepsObserved=[15,16,1,2])
review.update(updatedAt=datetime.now(timezone.utc).isoformat(),reviewMethod="当前128跑步逐图/联系表检查腿髋连接、同脚接地与四空间位置；正常与慢放浏览器抽看和逐帧检查以browserEvidence为准。旧68战斗保留已完成的审核。帧数/SHA只作技术校验。")
review["browserEvidence"]={"page":"preview/run-E-grounding.html","currentRevision":"2026-10-04_position_pairs","observed":a.browser_reviewed,"allImagesLoaded":"128/128" if a.browser_reviewed else "pending","controlsObserved":["normal1200","slow4800","pause","step","size128","size256"] if a.browser_reviewed else [],"timingBoundaryTechnicalCheck":"provenance/run-playback-uniform-check.json","observationScope":"正常/慢放抽样与逐帧图像观察；不是游戏内移动速度或滑步验收。"}
wr(R/"provenance/offline-visual-review.json",review)
if a.browser_reviewed:
 sel=rd(R/"selection.json")
 for f in sel["frames"]:
  if f["action"]!="run":continue
  f["dynamicReview"]="browser_normal_slow_and_pair_steps_observed";p=R/f["generationRecord"];rec=rd(p);rec["dynamicReview"]=f["dynamicReview"];rec["visualReview"]="grounding_pairs_offline_reviewed";wr(p,rec)
 wr(R/"selection.json",sel)
print(json.dumps({"static":128,"browserReviewed":a.browser_reviewed,"frameMs":75,"loopMs":1200}))

