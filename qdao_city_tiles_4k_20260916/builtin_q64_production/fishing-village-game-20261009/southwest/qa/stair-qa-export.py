import sys,json,hashlib
from pathlib import Path
from PIL import Image
Q=Path(__file__).resolve().parent;Z=Q.parent
prefix=sys.argv[1];old=json.loads((Q/'repair-r10_c04-sixstep-v1-qa-manifest.json').read_text(encoding='utf-8-sig'))
src=Q/(prefix+'-candidate-4096.png');im=Image.open(src);context=Image.open(Q/(prefix+'-context-native.png'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r={'source':src.as_posix(),'sourceSha256':sha(src),'qa':[]}
for e in old['qa'][:39]:
 p=Q/(Path(e['file']).name.replace('repair-r10_c04-sixstep-v1',prefix));b=e['sourceBox'];im.crop(b).save(p)
 r['qa'].append({**e,'file':p.as_posix(),'sha256':sha(p),'samePixelsAsV1':sha(p)==e['sha256']})
m=json.loads((Q/(prefix+'.manifest.json')).read_text(encoding='utf-8-sig'))
for item in m['repairs']:
 b=[v+115 for v in item['tileContextBox']];p=Q/(prefix+'-'+item['id']+'-after-100pct.png');context.crop(b).save(p)
 r['qa'].append({'file':p.as_posix(),'sha256':sha(p),'sourceContextBox':b,'role':'whole repair and mask boundary QA','operation':'integer crop only'})
out=Q/(prefix+'-qa-manifest.json');out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'qaManifest':out.as_posix(),'changed':[Path(x['file']).name for x in r['qa'][:39] if not x['samePixelsAsV1']]}))

