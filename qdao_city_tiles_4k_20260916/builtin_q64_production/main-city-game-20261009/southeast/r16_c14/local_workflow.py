import importlib.util,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent
Z=T.parent
spec=importlib.util.spec_from_file_location('workflow',Z/'production_workflow.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
w.CONFIG=T/'records/inherited-config-snapshot-unverified.json'
AUTH=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
assert w.read(AUTH)['newArtworkGenerationAllowed'] is True
if not w.CONFIG.exists():
 previous=Z/'r16_c13/records/inherited-config-snapshot-unverified.json'
 w.atomic_json(w.CONFIG,w.read(previous),exclusive=True)
 w.atomic_json(T/'records/local-wrapper-provenance-20261013.json',{'authority':{'path':str(AUTH),'sha256':w.sha(AUTH)},'source':{'path':str(previous),'sha256':w.sha(previous)},'scope':'r16_c14 only; no shared helper or global config writes','configurationBasis':'Historical desired config snapshot only; not evidence of actual model/quality. 2026-10-13 AGENTS fallback builtin policy prevails.','actualModel':None,'actualQuality':None,'helper':{'path':str(Z/'production_workflow.py'),'sha256':w.sha(Z/'production_workflow.py')}},exclusive=True)
assert sys.argv[2]=='r16_c14'
print(json.dumps(getattr(w,sys.argv[1])(*sys.argv[2:]),ensure_ascii=False,indent=2))
