from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy");R=B.parent/"09_bamboo_archer_girl"
m9=json.loads((R/"manifest.json").read_text(encoding="utf-8-sig"));m17=json.loads((B/"preview/manifest-preview.json").read_text(encoding="utf-8-sig"))
e={"referenceRoot":R.as_posix(),"manifest09Sha256":hashlib.sha256((R/"manifest.json").read_bytes()).hexdigest(),"timing09":json.loads((R/"animation-timing.json").read_text(encoding="utf-8-sig")),"manifest17BuiltAt":m17["built_at"],"reference09":[],"selected17":[]}
for s in m9["sequences"]:
 if s["action"] not in ["hit","attack","cast"] or s["direction"] not in ["E","W"]:continue
 for f in s["frames"]:
  p=R/f["file"];sha=hashlib.sha256(p.read_bytes()).hexdigest()
  e["reference09"].append(dict(slot=f["slot"].replace("/","-"),file=p.as_posix(),sha256=sha,manifestMatches=sha==f["sha256"],key="09-"+f["slot"].replace("/","-")))
for s in m17["slots"]:
 if s["action"] in ["hit","attack","cast"] and s["direction"] in ["E","W"]:
  f=s["selected"];p=(B/"preview"/f["path"]).resolve();e["selected17"].append(dict(slot=s["slot"],key="17-"+f["key"],file=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
def sheet(rows,cols,name):
 size=240;c=Image.new("RGB",(cols*size,((len(rows)+cols-1)//cols)*(size+24)),(220,220,220));d=ImageDraw.Draw(c)
 for j,r in enumerate(rows):
  x=(j%cols)*size;y=(j//cols)*(size+24);d.text((x+4,y+4),r["key"],fill=(0,0,0))
  if r.get("file"):
   im=Image.open(r["file"]).convert("RGBA").resize((size,size),Image.Resampling.LANCZOS);c.paste(im,(x,y+24),im)
 c.save(B/"review"/name)
for a,cols in [("hit",6),("attack",6),("cast",8)]:
 rows=[]
 for group in ["reference09","selected17"]:
  for dr in ["E","W"]:rows += [r for r in e[group] if r["slot"].startswith(a+"-"+dr+"-")]
 sheet(rows,cols,"reference09-combat-"+a+".png")
(B/"review"/"reference09-combat-input-evidence.json").write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding="utf-8")
ne9=next(s for s in m9["sequences"] if s["action"]=="run" and s["direction"]=="NE")
nr9=[dict(key="09-NE-"+str(f["frame"]).zfill(2),file=(R/f["file"]).as_posix(),sha256=f["sha256"]) for f in ne9["frames"]]
nr17=[]
for s in m17["slots"]:
 if s["action"]=="run" and s["direction"]=="NE":
  f=s["selected"];p=(B/"preview"/f["path"]).resolve() if f else None
  nr17.append(dict(key=f["key"] if f else "17-NE-"+str(s["frame"]).zfill(2)+"-MISSING",file=p.as_posix() if p else None,slot=s["slot"]))
sheet(nr9,4,"reference09-NE-contact.png");sheet(nr17,4,"reference17-NE-current-contact.png")
(B/"review"/"reference09-NE-input-evidence.json").write_text(json.dumps(dict(reference=nr9,selected=nr17),ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(dict(count09=len(e["reference09"]),count17=len(e["selected17"]),shaMismatches=[r["key"] for r in e["reference09"] if not r["manifestMatches"]],castE10=next(r for r in e["selected17"] if r["slot"]=="cast-E-10"),ne17=nr17),ensure_ascii=True))
