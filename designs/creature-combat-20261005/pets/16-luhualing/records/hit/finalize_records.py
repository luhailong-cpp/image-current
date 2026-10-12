from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
b=Path(r"D:/work/image/designs/creature-combat-20261005/pets/16-luhualing")
now=datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
notes={
"E01":"Eyes open with pained brow; branch arm flexed near chest, upright pitcher secured abdomen; two natural forward shoes.",
"E02":"Stronger hunched shoulders/narrowed eyes; knees closer; branch hand guards near shoulder; pitcher remains same arm and upright.",
"E03":"Closed-eye maximum flinch, branch elbow tucked, local head/shoulder recoil; same upright pitcher and two close feet.",
"E04":"Eyes half-reopened with strained expression; branch elbow still tucked, body returning; cloth settling behind.",
"E05":"Eyes open and torso nearly upright; branch arm reopens farther as a slight overshoot before E06 settles, both shoes natural.",
"E06":"Recovered near-idle pose with branch arm open, pitcher upright, relaxed face; selected from original E04 request because returned pose matched recovery endpoint.",
"W01":"True rear view, back braid/waist and two rear shoe soles clear; branch screen-left tucked near upper chest, pitcher securely screen-right.",
"W02":"Back shoulders hunched, branch hand closer toward head, knees mildly gathered; pitcher screen-right, two rear feet no outward twist.",
"W03":"Maximum recoil shown by bowed head and locally contracted shoulders, branch hand near forehead, knees gathered; stable back camera and prop sides.",
"W04":"Recoil reduced, hand descends beside ear/shoulder with bent elbow, torso recovering; attached W03 to preserve anatomy and stage continuity.",
"W05":"Nearly recovered with branch elbow halfway open and shoulders relaxed, pitcher screen-right, exactly two rear feet; attached W02 for continuity.",
"W06":"Recovered rear ready pose, branch arm open screen-left, pitcher screen-right, back braid/waist and two heels/soles; originally requested W04 but visually selected as recovery endpoint."
}
rows=[]
for d in ("E","W"):
 for n in range(1,7):
  num=f"{n:02}";key=d+num;p=b/".work"/"hit"/d/(num+".png")
  im=Image.open(p);alpha=im.getchannel("A")
  row={"frame":key,"nativeFile":p.relative_to(b).as_posix(),"nativeSHA256":sha(p),"size":list(im.size),"mode":im.mode,"alphaExtrema":list(alpha.getextrema()),"alphaBBox":list(alpha.getbbox()),"transparentPixelCount":alpha.histogram()[0],"singleFrameReview":notes[key]}
  rows.append(row)
  rp=b/"records"/"hit"/d/(num+".generation.json")
  rec=json.loads(rp.read_text(encoding="utf-8-sig"))
  rec["visualReview"]={"status":"reviewed-single-frame","viewImagePerformed":True,"reviewedAt":now,"result":notes[key],"anatomy":"one head, two arms/hands, two legs/feet, no wing/horn/tail; one pitcher/one branch","direction":"E front lower-right" if d=="E" else "W genuine rear upper-left","dynamicReview":"pending root playback","clientIntegration":"not tested"}
  if key in ("E06","W06"):rec["stageReassignment"]=notes[key]
  rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
for tag,reason,prompt in [("first","Rejected: ambiguous extra-looking shoe overlap and too much face turn.","prompts/hit/W01.txt"),("second","Rejected: pitcher drifted to screen-left, breaking original prop-side continuity.","prompts/hit/W01-retry.txt")]:
 rp=b/"records"/"hit"/"rejected"/("W01-"+tag+".generation.json")
 rec=json.loads(rp.read_text(encoding="utf-8-sig"))
 rec.update({"file":".work/hit/rejected/W01-"+tag+".png","nativeFile":".work/hit/rejected/W01-"+tag+".png","prompt":prompt,"selection":"rejected","rejectionReason":reason})
 rec["evidence"]["receipt"]="records/hit/rejected/W01-"+tag+".receipt.json"
 rec["visualReview"]={"status":"rejected","reason":reason}
 rec["exportStatus"]="not a runtime deliverable; exclude from manifest; remove rejected PNG after selected outputs verified"
 rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 rp=b/"records"/"hit"/"rejected"/("W01-"+tag+".receipt.json")
 rec=json.loads(rp.read_text(encoding="utf-8-sig"))
 rec["image_url"]["payloadSavedAs"]=".work/hit/rejected/W01-"+tag+".png"
 rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
report={"checkedAt":now,"selectedFrameCount":len(rows),"expected":12,"uniqueNativeHashes":len(set(x["nativeSHA256"] for x in rows)),"allRGBA":all(x["mode"]=="RGBA" for x in rows),"allNative1254":all(x["size"]==[1254,1254] for x in rows),"allRealAlpha":all(x["alphaExtrema"]==[0,255] for x in rows),"frames":rows}
(b/"records"/"hit"/"native-validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
status={"updatedAt":now,"action":"hit","phase":"12 selected native frames complete; awaiting root final export and dynamic review","selectedNativeFrames":12,"expectedRuntimeFrames":12,"nativeSize":[1254,1254],"runtimeTargetSize":[1024,1024],"durationMs":40,"actualModel":None,"actualQuality":None,"targetModel":"gpt-image-2.5-sunburst","targetQuality":"max","singleFrameVisualReview":"all 12 inspected with view_image and generatedImage; notes in records/hit/native-validation.json","technicalNativeReview":{k:v for k,v in report.items() if k!="frames"},"dynamicReview":"pending root normal/0.25 playback and final exported frames","clientIntegration":"not tested","rejectedAttempts":2,"networkErrors":1,"stageReassignments":["original E04 request selected as E06; separate corrected E04 generated","original W04 request selected as W06; separate corrected W04 generated"],"exportNotes":"Use root common 1254->896 pasted at [64,69]; no per-frame alignment. Exclude .work/hit/rejected and runtime/hit/rejected from final output. Preserve historical source SHA after native cleanup. W04/W05 have native W03/W02 fourth reference, respectively."}
(b/"hit-status.json").write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="frames"},ensure_ascii=False))

