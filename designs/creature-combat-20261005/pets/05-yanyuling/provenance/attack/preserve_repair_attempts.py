from pathlib import Path
import json,hashlib,shutil
B=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling")
for num,attempt,why in [("07","02","early wing closure and feet slipped left"),("11","01","second head dip and open beak in late recovery")]:
 d=B/"provenance"/"attack"/"E";p=B/"runtime"/"attack"/"E"/(num+".png")
 for suffix in ("prompt.txt","receipt.json"):
  src=d/(num+"."+suffix);dst=d/(num+".attempt"+attempt+"."+suffix)
  if dst.exists(): raise RuntimeError("Refusing to overwrite historical "+str(dst))
  shutil.copyfile(src,dst)
 r=json.loads(p.with_suffix(".png.generation.json").read_text(encoding="utf-8-sig"))
 r["formerOutputPath"]=r["file"];r["file"]=r["nativeSourcePath"]
 r["prompt"]=str(d/(num+".attempt"+attempt+".prompt.txt"));r["evidence"]["receipt"]=str(d/(num+".attempt"+attempt+".receipt.json"))
 r["disposition"]="rejected after static continuity review: "+why
 (d/(num+".attempt"+attempt+".generation.json")).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print("Historical prompt/receipt/generation text preserved; no PNG copied.")

