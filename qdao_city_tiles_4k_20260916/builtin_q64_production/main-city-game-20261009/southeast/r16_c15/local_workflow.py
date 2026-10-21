import importlib.util,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;Z=T.parent
spec=importlib.util.spec_from_file_location('workflow',Z/'production_workflow.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
w.CONFIG=T/'records/inherited-config-snapshot-unverified.json'
AUTH=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
assert w.read(AUTH)['newArtworkGenerationAllowed'] is True
if not w.CONFIG.exists():
 previous=Z/'r16_c14/records/inherited-config-snapshot-unverified.json'
 w.atomic_json(w.CONFIG,w.read(previous),exclusive=True)
 w.atomic_json(T/'records/local-wrapper-provenance-20261013.json',{'authority':{'path':str(AUTH),'sha256':w.sha(AUTH)},'source':{'path':str(previous),'sha256':w.sha(previous)},'scope':'r16_c15 only; no shared helper or global config writes','configurationBasis':'Historical desired config snapshot only; no evidence of actual model/quality. Current AGENTS fallback builtin policy prevails.','actualModel':None,'actualQuality':None,'helper':{'path':str(Z/'production_workflow.py'),'sha256':w.sha(Z/'production_workflow.py')}},exclusive=True)
assert sys.argv[2]=='r16_c15'
original_outer=w.outer_anchor
def core_only_outer(tile,co,direction):
 result=original_outer(tile,co,direction)
 if result is None:return None
 image,evidence=result
 if '/' not in evidence['neighbor']:return result
 x0,y0,x1,y1=evidence['sourceCrop'];tx,ty,_,_=evidence['target']
 a,b,c,d=max(x0,115),max(y0,115),min(x1,1139),min(y1,1139)
 assert a<c and b<d
 image=image.crop((a-x0,b-y0,c-x0,d-y0))
 evidence['sourceCrop']=[a,b,c,d];evidence['target']=[tx+a-x0,ty+b-y0,tx+c-x0,ty+d-y0]
 evidence['reliability']='native PATCH CORE ONLY clipped [115,115,1139,1139]; no external halo; neighbor art QA pending'
 return image,evidence
w.outer_anchor=core_only_outer
print(json.dumps(getattr(w,sys.argv[1])(*sys.argv[2:]),ensure_ascii=False,indent=2))
