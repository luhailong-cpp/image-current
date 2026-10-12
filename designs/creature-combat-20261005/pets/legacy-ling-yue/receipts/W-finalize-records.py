from pathlib import Path
from PIL import Image
import json,hashlib,re,datetime
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/legacy-ling-yue")
cfg=json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig"))
rejected={"W-design-attempt01.json":"九尾和四足无法清楚核验；继续修正。","W-design-attempt02.json":"仅8个可辨尾尖；第3次补足9尾。","W-attack-03.json":"抬起了近側前爪，左右关系不符；attempt02已修正。","W-attack-09.json":"漏一条支撑前腿；attempt02已修正。","W-hit-04.json":"回弹过直；attempt02已改成半蹲回弹。","W-attack-06.json":"爪尖过长偏手指；attempt02已改为紧凑兽爪。"}
for p in root.joinpath("receipts").glob("W-*.json"):
    if not re.match(r"W-(design-attempt\d+|hit-\d+(-attempt\d+)?|attack-\d+(-attempt\d+)?)\.json$",p.name):continue
    j=json.loads(p.read_text(encoding="utf-8-sig"))
    if "raw" not in j:
        m=re.search(r"as (.+?\.png) by default",j.get("output_hint",""))
        if not m:continue
        j["raw"]=m.group(1)
    src=Path(j["raw"])
    if src.exists():
        im=Image.open(src)
        j["native"]={"file":str(src),"sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"width":im.width,"height":im.height,"format":im.format,"mode":im.mode}
        j["generatedAt"]=datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone.utc).isoformat()
    j["tool"]="image_gen.imagegen";j["route"]="builtin";j["configSnapshot"]=cfg
    j["submittedParameters"]={"model":None,"quality":None,"transparent_background":True}
    j["actualModel"]=None;j["actualQuality"]=None
    j["unverifiedReason"]="宿主管理；工具未提供型号/质量选择器及可核实返回字段。"
    if "prompt" not in j:j["prompt"]="prompts/W-design.txt" if "01" in p.name else "prompts/W-design-attempt02.txt"
    if "references" not in j:
        j["references"]=[{"path":"D:/work/image/qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png","role":"existing identity"},{"path":"D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png","role":"approved painting style"}]
        if "02" in p.name:j["references"].insert(0,{"path":"C:/Users/luyua/.codex/generated_images/01a10bd2-88ea-7771-96b8-772c92804c0b/exec-fcf3fba6-ad83-4fd4-84fd-655a0785e399.png","role":"edit target, rejected prior W candidate"})
    j["submittedParameters"]["referenced_image_paths"]=[v["path"] if isinstance(v,dict) else v for v in j["references"]]
    if p.name in rejected:j["visualReview"]={"status":"superseded-rejected","reason":rejected[p.name]}
    p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding="utf-8")
reviews={
"hit":[
"警觉，真背向，9尾4足，耳后转。与中段存在小幅脚位偏差，连播需复验。",
"压肩低头，9尾4足，四肢屈曲。接触点相对01略移，未判支撑稳定通过。",
"反冲极点，9尾4足，耳压后，身体压缩清楚；支撑点与01不完全重合。",
"attempt02已修为半蹲回弹，9尾4足；较03头颈回升，未直接站直。",
"接近站直回中，9尾4足；与04的上升幅度需在连播复验。",
"稳定警觉收势，9尾4足；尾型近起势，仍需循环衔接复验。"],
"attack":[
"四足警觉，9尾，真背向；主体体量与后段略有差异需连播复验。",
"四足屈曲蓄力，9尾；压低幅度明显，02到03存在身高跳变风险。",
"attempt02已改远侧右前爪抬起，近侧前足与两后足落地，共4肢9尾。",
"同一右前爪收紧，3足支撑+1抬爪，9尾；抬爪在胸前重叠需原尺寸跟踪。",
"右前爪前旋，3足支撑+1抬爪，9尾；无第五足。",
"attempt02已改紧凑兽爪，3足支撑+1伸爪，9尾。",
"命中极点，右前爪伸向左上，3足支撑，9尾。",
"挥击下弧减速，右前爪悬空，3足支撑，9尾。",
"attempt02已补回近侧支撑前腿，右前爪收肘，4肢9尾。",
"右前爪落地，共4足9尾；远前足落点比设计基准偏前，支撑连续性未通过。",
"四足收势，9尾；落点延续10，需与01比较闭环。",
"四足稳定收势，9尾；未与01像素对齐，动态闭环仍需复验。"]}
for action,notes in reviews.items():
    for n,note in enumerate(notes,1):
        p=root/f"runtime/{action}/W/{n:02}.png.generation.json"
        j=json.loads(p.read_text(encoding="utf-8"))
        j["visualStatus"]="frame-reviewed-dynamic-not-approved"
        j["visualReview"]={"method":"实际查看每次工具输出和整组接触表，未将文件齐全视为动态通过。","note":note,"clientIntegration":"not-performed"}
        p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding="utf-8")
(root/"receipts/W-frame-visual-review.json").write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding="utf-8")
print("candidate metadata and final per-frame visual notes updated")

