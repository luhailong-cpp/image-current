from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime,timezone
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/12-yuexianshi")
notes=[
"稳定持琴开场；针对首稿多余光效重画后无可见法术。",
"眼睑与下视聚神发生小变化，手与琴保持支持。",
"托琴左前臂抬高，右手随琴上提。",
"右腕靠近上弦，真实前臂角度变化可见。",
"右指蓄势、琴略内收，动作幅度较小。",
"琴弦局部开始浅金微光，双手可读。",
"右指近上弦聚光；首次网络失败后重试出图。",
"集中光弧蓄势峰值，角色胸肩变化较小。",
"右指向弦面中段下拨，光跟随琴弦。",
"右腕进入中下弦，浅蓝暖金光弧仍局限琴附近。",
"右指达到下弦/琴底附近，腕臂明显下移；身体前倾幅度小。",
"右腕回收向中弦；回收幅度较上一帧明显，连播需复核节奏。",
"右手回近中弦，余光尚存；光强与12接近，连播需复核衰减。",
"琴回正常高度，明显光弧消失只留微亮点。",
"无光效，手腕和肩膝恢复。",
"独立收势图，无光效，回到开场持琴姿态族。"
]
now=datetime.now(timezone.utc).isoformat()
for i,n in enumerate(notes,1):
 p=root/"records"/"cast-E"/f"{i:02}.generation.json"
 d=json.loads(p.read_text(encoding="utf-8"));d["visualStatus"]="static-reviewed; playback pending"
 d["visualReview"]={"reviewedAt":now,"method":"Each returned native image visually inspected, then all exported frames visually inspected in 4-column contact sheet.","observation":n,"identity":"栗发单侧粗辫、靛蓝象牙衣、月牙弦琴保持；两手两足可辨，无翼尾。","handedness":"anatomical left supports harp underneath; anatomical right plucks strings","direction":"E fixed front three-quarter facing lower-right","anatomy":"no observed hand swap, missing limb or gross outward-twisted foot","limitation":"Manual static observation only; no client or continuous-playback approval."}
 if i==1:
  source=Path(d["derivedFrom"]["path"]);d["generatedAt"]=datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat();d["generatedAtEvidence"]="Native PNG filesystem last-write timestamp observed after generation; exact service timestamp not disclosed."
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
reject=Path(r"C:/Users/luyua/.codex/generated_images/01a10bb8-6c88-7051-bbfb-ef639e3e935c/exec-ce7a46a9-1483-44e1-83c3-720faae143b9.png")
im=Image.open(reject)
rej={"file":str(reject),"sha256":hashlib.sha256(reject.read_bytes()).hexdigest(),"generatedAt":datetime.fromtimestamp(reject.stat().st_mtime,timezone.utc).isoformat(),"generatedAtEvidence":"Native PNG filesystem last-write timestamp; service timestamp not disclosed.","width":im.width,"height":im.height,"mode":im.mode,"format":im.format,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads((root.parents[3]/"config"/"image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":[r"D:/work/image/designs/pets-xianling-20260924/source/12-yuexianshi-E.png",r"D:/work/image/designs/pets-xianling-20260924/source/12-yuexianshi-W.png",r"D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露实际模型和质量。","prompt":"prompts/cast-E/01.txt","evidence":{"receipt":"records/cast-E/01-rejected-receipt.json"},"disposition":"rejected: unsolicited opening magic, replaced by 01-fix generation","replacement":"runtime/cast/E/01.png"}
(root/"records"/"cast-E"/"01-rejected.generation.json").write_text(json.dumps(rej,ensure_ascii=False,indent=2),encoding="utf-8")
review={"group":"cast-E","frames":16,"staticStatus":"reviewed","method":"native single-frame tool images plus exported contact sheet","handDirectionAnatomy":"No hand swap, missing limbs, rear/front flip or gross outward foot twist observed.","animationLimitations":["Chest/knee action is subtle; right-arm/harp articulation is the clearest motion.","12-to-13 light decay is modest and recovery timing needs playback review.","Independent AI frames have minor hair/fabric and contour variations."],"playbackStatus":"not-verified","playbackBlocker":{"tool":"mcp__cua_repl.js","requested":"file:///D:/work/image/designs/creature-combat-20261005/pets/12-yuexianshi/preview.html","result":"Browser URL policy blocks file protocol; only http/https allowed. Tool explicitly forbade workaround or alternate browser surface. Stopped browser action."},"clientStatus":"not-integrated","framesObserved":[{"frame":i+1,"note":n} for i,n in enumerate(notes)]}
(root/"records"/"cast-E"/"visual-review.json").write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding="utf-8")
out=[]
for i in range(1,6):
 p=root/"records"/"attack-W"/f"{i:02}.generation.json";d=json.loads(p.read_text(encoding="utf-8"));src=Path(d["derivedFrom"]["path"]);im=Image.open(src);a=im.getchannel("A")
 e={"frame":i,"source":str(src),"size":list(im.size),"sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"bbox":a.getbbox(),"edgeCounts":{}}
 for threshold in [0,16,64,128,240]:
  ys=[y for y in range(im.height) if a.getpixel((im.width-1,y))>threshold]
  e["edgeCounts"][str(threshold)]={"count":len(ys),"yRange":[min(ys),max(ys)] if ys else None}
 out.append(e)
(root/"records"/"attack-W"/"right-edge-inspection.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out,ensure_ascii=False))

