from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
stems=['r10_c04_s02_04_v02','r10_c04_s03_04_v02','r10_c04_s04_04_v01']
entries=[]
for stem in stems:
 f=ROOT/'native'/(stem+'.png')
 rec=json.loads(Path(str(f)+'.generation.json').read_text(encoding='utf-8'))
 req=json.loads((ROOT/'prompts'/(stem+'.request.json')).read_text(encoding='utf-8'))
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 with Image.open(f) as im: size=list(im.size);mode=im.mode
 assert sha==rec['sha256'] and size==[1254,1254] and mode=='RGB'
 assert len(req['references'])==5
 for ref in req['references']:
  assert hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest()==ref['sha256']
 assert (ROOT/'receipts'/(stem+'.tool.json')).exists()
 entries.append({'stem':stem,'source':f.as_posix(),'sha256':sha,'nativeGlobalBox':rec['coordinates']['nativeGlobalBox'],'coreGlobalBox':rec['coordinates']['coreGlobalBox'],'dimensions':size,'shaAndReferenceChecks':True,'topNative100':(ROOT/'qa'/(stem+'-right-column-top-native100.png')).as_posix()})
out={'status':'source_handoff_complete','formalAccepted':False,'owner':'native_pair_repair','selectedSources':entries,'checks':'All dimensions, saved source hashes, five image reference hashes, and receipt presence verified. Top seams visually reviewed at native scale.','limitations':['Straight-core top seam for sr3 has mild stone-tone change; final overlap selection needed.','External left/right and next-row final seams are pending neighboring sources and assembly.'],'rejectedSources':{'r10_c04_s02_04_v01':'premature pillar foot, omitted left railing, added flowers','r10_c04_s03_04_v01':'soft-focus lower-left gold curl, repaired in v02'},'sharedStateWrites':False}
dest=ROOT/'qa'/'r10_c04-right-column-handoff.json'
assert not dest.exists()
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))

