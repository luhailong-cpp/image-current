import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
now=datetime.now(timezone.utc).isoformat()
rp=z/'production-resume-20261012.json'
if not rp.exists():
 prod.write(rp,{'schemaVersion':1,'resumedAtUtc':now,'status':'active','authority':ref(Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')),'historicalFreeze':ref(z/'migration-freeze-20261011.json'),'preserveAllOriginals':True,'versionedNewImageNames':True,'builtinOnly':True,'gitOperationsAllowed':False,'firstNewNativeOutput':None,'breakpoints':{'root':'r11_c06 internal39 QA then north join','stair_rebuild':'r10_c03 remaining6 then internal/shared joins','finish_r10c05':'r10_c07 2x2 joint repair then r11_c07','art_qa':'r08_c06 targeted repair and south join then r08_c05'}})
p=read(z/'progress.json');p.update({'status':'active_art_production','updatedAtUtc':now,'nextStep':'Continue saved native QA and targeted repairs; complete missing coordinate patches. Historical migration freeze is superseded for live production.','productionResume':ref(rp),'currentMilestone':'8 art exports; 11 coordinates covered; native QA and shared joins active','inFlightImagegenCount':0})
prod.write(z/'progress.json',p)
preview=z/'qa/r11_c06-resume-composition-preview-v1.png'
if not preview.exists():
 im=Image.open(z/'qa/full-tile-r11_c06-candidate-4096.png');im.thumbnail((1400,1400));im.save(preview)
 prod.write(preview.with_suffix('.json'),{'role':'inspection only; never final pixels','source':ref(z/'qa/full-tile-r11_c06-candidate-4096.png'),'operation':'thumbnail to 1400 for composition inspection'})
a=read(z/'qa/full-tile-r11_c06-assembly.json')
print(json.dumps({'resume':ref(rp),'preview':preview.as_posix(),'assemblyKeys':list(a),'qaCount':len(a.get('qa',[]))}))
