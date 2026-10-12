from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
stems=['r10_c04_s02_03_v02','r10_c04_s03_03_v01','r10_c04_s04_03_v01']
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
  assert hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest()==ref['sha256'],ref['path']
 assert (ROOT/'receipts'/(stem+'.tool.json')).exists()
 qa={}
 for edge in ['top','right']:
  check=ROOT/'qa'/(stem+'-right-column-'+edge+'-native100.png')
  assert check.exists()
  qa[edge]=check.as_posix()
 entries.append({'stem':stem,'source':f.as_posix(),'sha256':sha,'nativeGlobalBox':rec['coordinates']['nativeGlobalBox'],'coreGlobalBox':rec['coordinates']['coreGlobalBox'],'dimensions':size,'shaAndReferenceChecks':True,'native100':qa})
out={'status':'source_handoff_complete','formalAccepted':False,'owner':'native_pair_repair','selectedSources':entries,'allOwnSelectedSources':['r10_c04_s02_03_v02','r10_c04_s03_03_v01','r10_c04_s04_03_v01','r10_c04_s02_04_v02','r10_c04_s03_04_v02','r10_c04_s04_04_v01'],'checks':'Native dimensions, saved source hashes, all five reference hashes and receipts verified for each source. All three TOP and all three RIGHT straight-core seams visually reviewed at native scale.','limitations':['Some straight-core stone material value differences remain in sr2/sr3; review after final overlap-path selection.','LEFT and next-row joins remain pending neighboring sources and assembly.'],'rejectedSources':{'r10_c04_s02_03_v01':'Artificial railing kink/value rectangle and expanded grass patch repaired in selected v02.'},'referenceAudit':'qa/r10_c04_s02_03_v01-guide-collision-audit.json preserves planned metadata and evidence for guide replacement before v01 generation; selected v02 uses recorded native v01 directly.','sharedStateWrites':False}
dest=ROOT/'qa'/'r10_c04-col3-handoff.json';assert not dest.exists()
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))

