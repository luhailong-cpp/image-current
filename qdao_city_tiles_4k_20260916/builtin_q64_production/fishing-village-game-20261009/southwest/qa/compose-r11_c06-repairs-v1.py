import sys
sys.dont_write_bytecode=True
import json,importlib.util,subprocess
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
a=read(z/'qa/full-tile-r11_c06-assembly.json');jobs=read(z/'qa/r11_c06-repair-jobs-v1.json')
prefix='repair-r11_c06-internal-v1'
m={'schemaVersion':1,'outputPrefix':prefix,'baseAssembly':ref(z/'qa/full-tile-r11_c06-assembly.json'),'expectedBaseCandidateSha256':a['output']['sha256'],'repairs':[]}
for j in jobs:
 stem=j['stem'];p=z/'native'/f'{stem}.png';g=z/'native'/f'{stem}.png.generation.json'
 m['repairs'].append({**{k:j[k] for k in ['source','tileContextBox','repairBounds','margin']},'id':j['id'].lower(),'repair':ref(p),'generationRecord':ref(g)})
manifest=z/'qa'/f'{prefix}-manifest-v2.json';assert not manifest.exists();prod.write(manifest,m)
subprocess.run([sys.executable,'-B',str(z/'qa/repair-compose.py'),'--manifest',str(manifest)],check=True)
tr=read(z/'qa'/f'{prefix}-trace.json');new=Image.open(tr['candidate']['path']);old=Image.open(a['output']['path']);context=Image.open(tr['context']['path'])
qa=[];inherited=[]
for entry in a['qa']:
 box=entry['sourceBox'];before=np.array(old.crop(box));after=np.array(new.crop(box))
 if np.array_equal(before,after):inherited.append(entry);continue
 suffix=Path(entry['file']).name.replace('full-tile-r11_c06-','');p=z/'qa'/f'{prefix}-{suffix}';assert not p.exists();new.crop(box).save(p);qa.append({**ref(p),'sourceBox':box,'role':'affected original native seam QA'})
repairs=[]
for j in jobs:
 box=[v+115 for v in j['tileContextBox']];p=z/'qa'/f'{prefix}-{j["id"]}-result-native.png';assert not p.exists();context.crop(box).save(p);repairs.append({**ref(p),'contextBox':box,'role':'complete native repair boundary QA'})
prev=z/'qa'/f'{prefix}-composition-preview.png';assert not prev.exists();im=new.copy();im.thumbnail((1400,1400));im.save(prev)
prod.write(z/'qa'/f'{prefix}-qa-index.json',{'trace':ref(z/'qa'/f'{prefix}-trace.json'),'candidate':tr['candidate'],'context':tr['context'],'affectedQa':qa,'inheritedQa':inherited,'repairQa':repairs,'preview':ref(prev),'previewRole':'inspection-only downscale; not final pixels'})
print(json.dumps({'affected':len(qa),'inherited':len(inherited),'repairBoundaries':len(repairs),'qaPaths':[q['path'] for q in qa]}))
