from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
W=R/'full-limb-review-20261004/references'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):
    data.update(file=p.relative_to(R).as_posix(),sha256=sha(p))
    Path(str(p)+'.generation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sample=json.loads((W/'reference-continuous-08.jpg.generation.json').read_text(encoding='utf-8'))
save(W/'reference-first-frame.jpg',{'operation':'first decoded video frame exported as JPEG; no image synthesis','derivedFrom':sample['derivedFrom'],'timeSeconds':0})
for direction in ['N','S']:
    inputs=[]
    for i in range(1,17):
        p=R/f'runtime/run/{direction}/{i:02}.png'
        inputs.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'generationRecord':p.relative_to(R).as_posix()+'.generation.json'})
    save(W/f'{direction}-feet-audit.jpg',{'operation':'fixed-coordinate lower limb contact sheet for visual inspection','crop':[330,640,690,1000],'derivedFrom':inputs})
for p in W.glob('reference-continuous-*.jpg'):
    meta=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
    save(p,meta)
print('Completed derived-reference image provenance')
