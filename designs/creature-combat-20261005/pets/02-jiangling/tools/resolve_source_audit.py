import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for p in [root/"runtime/hit/W/05.png.generation.json",root/"records/hit-W-05.json"]:
 if not p.exists():continue
 r=json.loads(p.read_text(encoding="utf-8"))
 ref=r["references"][3]
 ref.update(sha256="851c9762db28fa662a22ff45d337813a1d4ef7e5a7a302edab23bf28fa028dc5",historicalGenerationRecord="records/hit-W-04-rejected-v1.json",availability="same-path-later-replaced",note="This call used the original hit W04 before its later AI repair; this SHA is the historical 1024 exported input, recovered and verified from its native source. It is not the current W04 SHA.")
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
for id,output in [("hit-W-04","runtime/hit/W/04.png"),("attack-W-05","runtime/attack/W/05.png")]:
 p=root/"records"/(id+"-rejected-v1.json")
 r=json.loads(p.read_text(encoding="utf-8"))
 r.update(disposition="rejected-superseded",historicalOutputReplaced=True,supersededBy=output+".generation.json",historicalFile=r.get("file"),note="The file field identifies the historical output location; that location now contains the later repair. The SHA in this record belongs to the rejected historical image.")
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
p=root/"records/cast-E-10-attempt1-rejected.json"
r=json.loads(p.read_text(encoding="utf-8"))
r.setdefault("evidence",{})["receipt"]="receipts/cast-E-10-attempt1-rejected.json"
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
p=root/"qa/source-audit.json"
r=json.loads(p.read_text(encoding="utf-8"))
r["parentResolution"]={"status":"all_four_noted_metadata_issues_resolved","details":["W hit05 historical W04 input SHA explicitly preserved in sidecar and records copy","W hit04 and attack05 rejected records explicitly marked historical replaced outputs","E cast10 rejected attempt has explicit receipt link"],"noImagePixelsChanged":True}
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print("Four historical metadata issues resolved.")

