from pathlib import Path
import argparse,json,hashlib,subprocess,sys
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--tile',required=True);a=p.parse_args()
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
d=read(Z/'right-current-selection-20261012.json');t=d['tiles'][a.tile];assert t['selectedCount']==16
m={'schemaVersion':1,'tileId':a.tile,'nativePixels':1254,'corePixels':1024,'haloPixels':115,'patchMatrix':[],'selectionBasis':{'path':(Z/'right-current-selection-20261012.json').as_posix(),'sha256':sha(Z/'right-current-selection-20261012.json')},'status':'explicit_native_matrix_pending_internal_and_connected_QA'}
for row in range(1,5):
 rr=[]
 for col in range(1,5):
  attempt=t['matrix'][row-1][col-1];assert attempt
  stem=f'{a.tile}_s{row:02d}_{col:02d}_{attempt}';q=Z/'native'/f'{stem}.png';g=Path(str(q)+'.generation.json');cell=next(x for x in t['cells'] if x['stem']==stem);assert sha(q)==cell['image']['sha256'] and sha(g)==cell['generationRecord']['sha256'];rr.append({'path':q.relative_to(Z).as_posix(),'generationRecord':g.relative_to(Z).as_posix(),'sha256':sha(q)})
 m['patchMatrix'].append(rr)
mp=Z/f'{a.tile}.candidate-v1.manifest.json'
with mp.open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
out=Z/'tiles'/f'{a.tile}_candidate-v1_4096.png'
subprocess.run([sys.executable,str(Z/'assemble_tile.py'),'--manifest',str(mp),'--output',str(out)],check=True)
record=out.with_suffix('.assembly.json');assert record.exists();d=read(Z/'right-current-selection-20261012.json');t=d['tiles'][a.tile];t.update(assembled4k=True,candidate={'path':out.as_posix(),'sha256':sha(out)},record={'path':record.as_posix(),'sha256':sha(record)},internalClosurePassed=False,formalAccepted=False)
(Z/'right-current-selection-20261012.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'tile':a.tile,'candidate':t['candidate'],'record':t['record']}))
