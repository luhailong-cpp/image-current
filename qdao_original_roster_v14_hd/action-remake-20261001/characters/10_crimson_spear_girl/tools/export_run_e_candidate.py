from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'candidate'/'run'/'E';out.mkdir(parents=True,exist_ok=True)
generated=[]
for i in range(1,17):
    folder=ROOT/'generation'/f'run-E-{i:02}'
    revision=ROOT/'generation'/f'run-E-{i:02}-v2'
    if (revision/'native.png').exists():folder=revision
    src=folder/'native.png'
    if not src.exists():continue
    native=Image.open(src).convert('RGBA')
    if native.size!=(1254,1254):raise ValueError('Unexpected native canvas; do not apply unreviewed transform')
    frame=Image.new('RGBA',(1024,1024))
    frame.alpha_composite(native.resize((860,860),Image.Resampling.LANCZOS),(14,151))
    dest=out/f'{i:02}.png';frame.save(dest)
    meta={'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','status':'candidate-export-not-visually-approved','derivedFrom':[{'file':src.relative_to(ROOT).as_posix(),'sha256':sha(src),'generationRecord':str(src.relative_to(ROOT))+'.generation.json'}],'operation':{'type':'uniform-whole-canvas-resample-and-common-translation','newPoseGenerated':False,'nativeSize':[1254,1254],'resampledCanvas':[860,860],'scale':860/1254,'translation':[14,151],'rootTarget':[512,942],'virtualSourceRoot':[(512-14)/(860/1254),(942-151)/(860/1254)],'rootMethod':'same provisional virtual ground for all frames; no per-frame foot or bbox alignment','nativeAlphaPreserved':True,'colorKeying':False,'perSubjectBBoxScaling':False},'visualAcceptance':False,'dynamicAcceptance':False}
    Path(str(dest)+'.generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    generated.append(i)
(ROOT/'candidate'/'run-E-export.json').write_text(json.dumps({'frames':generated,'count':len(generated),'missing':[i for i in range(1,17) if i not in generated],'status':'provisional registration, requires dynamic review','root':[512,942],'frameDurationMs':30},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidateExports':len(generated),'frames':generated}))
