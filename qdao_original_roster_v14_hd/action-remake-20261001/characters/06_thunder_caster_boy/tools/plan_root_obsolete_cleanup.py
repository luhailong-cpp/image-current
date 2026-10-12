"""List only root-owned obsolete native PNGs; preserve all text provenance and current natives."""
from pathlib import Path
import json,re,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
current=set();exports=[]
for p in (R/'runtime').glob('*/*/*.png.generation.json'):
 d=json.loads(p.read_text(encoding='utf-8-sig'))
 for x in d.get('derivedFrom',[]):
  if isinstance(x,dict) and x.get('file'):current.add((R/x['file']).resolve())
 out=p.with_name(p.name.removesuffix('.generation.json'))
 exports.append({'file':out.relative_to(R).as_posix(),'exists':out.is_file(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest() if out.is_file() else None})
pattern=re.compile(r'^(?:hit_[EW]|run_(?:S|SE|NW))_\d{2}_v\d+\.png$')
files=[]
for p in (R/'work').glob('*.png'):
 if not pattern.match(p.name) or p.resolve() in current:continue
 record=p.with_name(p.name+'.generation.json')
 if not record.exists():continue
 files.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'textRecord':record.relative_to(R).as_posix(),'reason':'本角色root已淘汰native；现有runtime与当前被选native齐全，历史来源文字保留；在途root调用只引用runtime'})
plan={'time':datetime.now(timezone.utc).isoformat(),'scope':'root-owned hit E/W and run S/SE/NW work PNG only','keepCurrentNative':True,'files':files,'exportCheck':exports,'executed':False}
(R/'records/root_obsolete_cleanup_plan_20261004.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'obsoleteImages':len(files),'bytes':sum((R/x['file']).stat().st_size for x in files),'allExportsExist':all(x['exists'] for x in exports)}))
