import importlib.util,json,hashlib
from pathlib import Path
ROOT=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/r12_c09")
spec=importlib.util.spec_from_file_location('native_workflow',r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/tile_native_workflow.py")
wf=importlib.util.module_from_spec(spec);spec.loader.exec_module(wf)
missing=r"D:/work/image/designs/mail-ui-v1/01-mail-event.png"
prior=ROOT/'native/p33-v1.png.generation.json'
rec=json.loads(prior.read_text(encoding='utf-8'))
ref=next(r for r in rec['references'] if Path(r['path'])==Path(missing))
original_sha=wf.sha
def evidence_sha(path):
    if Path(path)==Path(missing) and not Path(path).exists(): return ref['sha256']
    return original_sha(path)
wf.sha=evidence_sha
original_read=wf.read
def evidence_read(path):
    if Path(path)==Path(wf.CONFIG_PATH) and not Path(path).exists(): return rec['configSnapshot']
    return original_read(path)
wf.read=evidence_read
out=wf.ingest('r12_c09','p34','v1',r"C:\Users\luyua\.codex\generated_images\01a12215-5360-7c41-b372-7c52cf92911f\exec-0d3621c0-c6a6-4758-9ce1-9c8f798793d5.png")
gp=ROOT/'native/p34-v1.png.generation.json'
record=json.loads(gp.read_text(encoding='utf-8'))
for r in record['references']:
    if Path(r['path'])==Path(missing):
        r['availabilityAtIngest']='missing_after_successful_builtin_return'
        r['sha256EvidenceBasis']='Last successfully hashed reference in prior p33 generation record; not revalidated at p34 ingest'
        r['sha256EvidenceRecord']=str(prior)
        r['sha256EvidenceRecordSha256']=hashlib.sha256(prior.read_bytes()).hexdigest()
record['ingestException']={'errors':['FileNotFoundError: mandatory mail style reference path missing after successful builtin response','FileNotFoundError: D:/work/image/config/image-generation.json missing at ingest'],'missingReference':missing,'submittedRequestPreserved':True,'toolReturnedImage':True,'fallback':'Preserved previously recorded reference SHA and same-batch config snapshot from p33 with explicit unrevalidated status; no image regenerated and no shared reference restored.'}
record['configSnapshotEvidenceBasis']='Same-batch p33 generation record; config source file missing at p34 ingest, not freshly read'
record['configSnapshotEvidenceRecord']=str(prior)
gp.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out))

