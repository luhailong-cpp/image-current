import importlib.util, sys, json, hashlib
from pathlib import Path
from datetime import datetime, timezone
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent
Z=T.parent
spec=importlib.util.spec_from_file_location('workflow', Z/'production_workflow.py')
w=importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
w.CONFIG=T/'records'/'inherited-config-snapshot-unverified.json'
AUTH=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
assert w.read(AUTH)['newArtworkGenerationAllowed'] is True
if not w.CONFIG.exists():
    previous=Z/'r15_c13/records/p01_01_v20261011T091927_bfbc96db.preparation.json'
    old=w.read(previous)
    w.atomic_json(w.CONFIG,old['configSnapshot'],exclusive=True)
    w.atomic_json(T/'records/local-wrapper-provenance-20261012.json',{
      'createdAt':w.now(),'authority':{'path':str(AUTH),'sha256':w.sha(AUTH)},
      'wrapperScope':'r16_c13 only; shared helper and global config untouched',
      'configurationBasis':'historical desired configuration snapshot; NOT actual returned model/quality',
      'source':{'path':str(previous),'sha256':w.sha(previous)},
      'configSnapshotPath':str(w.CONFIG),'configSnapshotSha256':w.sha(w.CONFIG),
      'actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,
      'helper':{'path':str(Z/'production_workflow.py'),'sha256':w.sha(Z/'production_workflow.py')}
    },exclusive=True)
assert sys.argv[2]=='r16_c13'
result=getattr(w,sys.argv[1])(*sys.argv[2:])
print(json.dumps(result,ensure_ascii=False,indent=2))

