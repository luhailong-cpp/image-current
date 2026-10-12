import json,sys,hashlib,shutil,datetime
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[2]
job=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
d=job["direction"];n=f'{job["frame"]:02d}'
dest=root/".work"/"cast"/d/(n+".png")
dest.parent.mkdir(parents=True,exist_ok=True)
folder=root/"records"/"cast"/d;folder.mkdir(parents=True,exist_ok=True)
old=folder/(n+".generation.json")
if old.exists():
    previous=json.loads(old.read_text(encoding="utf-8"));previous["disposition"]="superseded image; text provenance retained"
    k=1
    while (folder/(n+f".attempt-{k}.generation.json")).exists(): k+=1
    (folder/(n+f".attempt-{k}.generation.json")).write_text(json.dumps(previous,ensure_ascii=False,indent=2),encoding="utf-8")
    for suffix in ["receipt.json"]:
        src=folder/(n+"."+suffix)
        if src.exists(): shutil.copy2(src,folder/(n+f".attempt-{k}."+suffix))
    oldprompt=root/"prompts"/"cast"/d/(n+".txt")
    if oldprompt.exists(): shutil.copy2(oldprompt,oldprompt.with_name(n+f".attempt-{k}.txt"))
shutil.copy2(job["source"],dest)
im=Image.open(dest); sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
refRoles=[("native W identity" if p.endswith("-W.png") else "native E identity" if p.endswith("-E.png") else "primary style/material reference" if "attribute-panels" in p else "pose edit target") for p in job["references"]]
record={"file":f"runtime/cast/{d}/{n}.png","sourceFile":str(dest),"sourceSha256":sha(dest),"sha256":sha(dest),"generatedAt":job["generatedAt"],"startedAt":job["startedAt"],"width":im.width,"height":im.height,"format":"PNG","mode":im.mode,"action":"cast","direction":d,"frame":job["frame"],"durationMs":45,"pivot":[0.5,0.08],"event":"release" if job["frame"]==11 else None,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":job["references"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露型号/质量参数与返回值；提示词目标不等于锁定。","prompt":f"prompts/cast/{d}/{n}.txt","references":[{"path":p,"role":refRoles[k],"sha256":sha(p)} for k,p in enumerate(job["references"])],"evidence":{"receipt":f"records/cast/{d}/{n}.receipt.json","imagePayload":"Returned data:image/png;base64 payload preserved as exact PNG bytes in sourceFile; not duplicated in text receipt."},"technical":{"alphaExtrema":im.getchannel("A").getextrema() if im.mode=="RGBA" else None,"alphaBBox":im.getchannel("A").getbbox() if im.mode=="RGBA" else None},"visualReview":job.get("visualReview","pending"),"exportStatus":"pending root unified export"}
folder=root/"records"/"cast"/d;folder.mkdir(parents=True,exist_ok=True)
(folder/(n+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
(folder/(n+".receipt.json")).write_text(json.dumps({"output_hint":job["receipt"],"image_url":{"scheme":"data:image/png;base64","savedPayload":str(dest),"sha256":sha(dest)}},ensure_ascii=False,indent=2),encoding="utf-8")
p=root/"prompts"/"cast"/d;p.mkdir(parents=True,exist_ok=True)
(p/(n+".txt")).write_text(job["prompt"],encoding="utf-8")
print(json.dumps({"file":str(dest),"size":im.size,"sha256":sha(dest),"alpha":record["technical"]},ensure_ascii=False))
