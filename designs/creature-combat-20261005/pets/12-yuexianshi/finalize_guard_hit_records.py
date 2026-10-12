import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
items=[]
for p in sorted((ROOT/"records/hit-W").glob("*.guardfix-20261008*.receipt.json")):
    if "root" in p.name:continue
    receipt=json.loads(p.read_text(encoding="utf-8"))
    tag=p.name.removesuffix(".receipt.json")
    candidate=ROOT/"records/hit-W"/f"{tag}.generation.json"
    job=ROOT/"records/hit-W"/f"{tag}.job.json"
    if receipt.get("candidateOnly",False):
        for record in [candidate,job]:
            if record.exists():
                d=json.loads(record.read_text(encoding="utf-8"))
                d["visualStatus"]="rejected-local-continuity-review"
                record.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    src=Path(receipt["source"])
    items.append({"path":str(src),"sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"nativeGenerationRecord":candidate.relative_to(ROOT).as_posix(),"receipt":p.relative_to(ROOT).as_posix(),"disposition":receipt.get("disposition","selected guard stance repair"),"exists":src.exists()})
result={"preparedAt":datetime.now(timezone.utc).isoformat(),"scope":"only this hit-W agent's actual native outputs","policy":"Do not delete until root final selected exports, source references and metadata verification complete.","deletionPerformed":False,"items":items}
(ROOT/"records/hit-W/guardfix-20261008-native-cleanup-list.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"nativeCandidates":len(items),"allRecorded":all((ROOT/x["nativeGenerationRecord"]).exists() for x in items)}))

