from pathlib import Path
from PIL import Image
import json,hashlib
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/10-xuanchaogui")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):
 try:return Path(p).relative_to(base).as_posix()
 except ValueError:return str(p)
def refs(paths):
 roles=["identity E front-three-quarter","identity W rear-three-quarter","primary painting/material style"]
 return [{"path":p,"sha256":sha(p) if Path(p).exists() else None,"role":roles[i] if i<3 else "animation continuity / fixed composition; exact role in submitted prompt"} for i,p in enumerate(paths)]
report=[]
for direction,total in [("E",12),("W",6)]:
 for n in range(1,total+1):
  stem=f"{n:02}"
  g=base/"provenance"/"attack"/direction/(stem+".generation.json")
  out=base/"runtime"/"attack"/direction/(stem+".png")
  if not g.exists() or not out.exists(): raise SystemExit(f"missing {direction}/{stem}")
  rec=json.loads(g.read_text(encoding="utf-8"))
  job=json.loads((g.parent/(stem+".job.json")).read_text(encoding="utf-8"))
  rpaths=job["references"]
  rec["references"]=refs(rpaths)
  rec["submittedParameters"]["prompt"]=rel(rec["prompt"])
  rec["prompt"]=rel(rec["prompt"])
  receipt_path=g.parent/(stem+".receipt.json")
  receipt={"tool":"image_gen.imagegen","returnedFields":["image_url","output_hint"],"output_hint":rec["receipt"],"image_urlOmitted":"base64 returned/displayed by host; native PNG path and hashes retained","actualModel":None,"actualQuality":None}
  receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding="utf-8")
  rec["evidence"]={"receipt":rel(receipt_path),"returnedFields":["image_url","output_hint"],"output_hint":rec["receipt"]}
  g.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
  im=Image.open(out);a=im.getchannel("A")
  side={key:rec[key] for key in ["generatedAt","configSnapshot","actualModel","actualQuality","submittedParameters","unverifiedReason","prompt","references","evidence","durationMs","pivot"]}
  side.update({"file":rel(out),"sha256":sha(out),"width":im.width,"height":im.height,"format":"PNG","mode":im.mode,"derivedFrom":{**rec["derivedFrom"],"generationRecord":rel(g)},"operation":{"type":"whole-canvas-uniform-resize","sourceSize":[rec["native"]["width"],rec["native"]["height"]],"targetSize":[1024,1024],"resampling":"Lanczos","translation":[0,0],"contentAwareAlignment":False},"alphaBBox":a.getbbox(),"alphaExtrema":a.getextrema(),"visualStatus":"individual-frame-reviewed; sequence review pending","visualNotes":rec["visualReview"]["notes"],"anchorTopLeft":[512,942],"event":"impact" if n==7 else None})
  Path(str(out)+".generation.json").write_text(json.dumps(side,ensure_ascii=False,indent=2),encoding="utf-8")
  report.append({"file":rel(out),"sha256":side["sha256"],"mode":im.mode,"size":list(im.size),"alphaExtrema":list(a.getextrema()),"sidecar":rel(str(out)+".generation.json"),"promptExists":(base/rec["prompt"]).exists(),"referenceCount":len(rpaths)})
config=json.loads((base/"provenance/attack/E/01.generation.json").read_text(encoding="utf-8"))["configSnapshot"]
for p in (base/"provenance/attack").rglob("*.rejected.json"):
 r=json.loads(p.read_text(encoding="utf-8"))
 r["configSnapshot"]=config
 r["tool"]="image_gen.imagegen";r["route"]="builtin"
 r["unverifiedReason"]="宿主管理，工具未披露实际model/quality。"
 if r.get("references") and isinstance(r["references"][0],str):
  paths=r["references"];r["submittedParameters"]["referenced_image_paths"]=paths;r["references"]=refs(paths)
 r["submittedParameters"]["prompt"]=rel(r["prompt"])
 r["prompt"]=rel(r["prompt"])
 r["evidence"]={"returnedFields":["image_url","output_hint"],"output_hint":r["receipt"]}
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
check={"ownedCount":len(report),"expectedCount":18,"all1024RGBA":all(r["mode"]=="RGBA" and r["size"]==[1024,1024] for r in report),"allHaveTransparency":all(r["alphaExtrema"]==[0,255] for r in report),"allPromptPathsExist":all(r["promptExists"] for r in report),"uniqueSha256":len(set(r["sha256"] for r in report)),"frames":report,"sequenceReview":"pending root browser playback"}
(base/"provenance/attack/owned-validation.json").write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in check.items() if k!="frames"},ensure_ascii=False))

