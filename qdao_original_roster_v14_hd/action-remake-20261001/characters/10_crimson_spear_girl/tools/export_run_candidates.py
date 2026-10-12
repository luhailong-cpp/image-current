from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
inv=json.loads((ROOT/'candidate-inventory.json').read_text(encoding='utf-8'))
cfg=json.loads((ROOT/'candidate/registration.json').read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for direction,reg in cfg['directions'].items():
    out=ROOT/'candidate/run'/direction
    out.mkdir(parents=True,exist_ok=True)
    for f in inv['groups'].get('run/'+direction,[]):
        src=ROOT/f['url'][3:]
        native=Image.open(src).convert('RGBA')
        if list(native.size)!=cfg['nativeCanvas']:raise ValueError('Unexpected native canvas '+str(src))
        frame=Image.new('RGBA',tuple(cfg['exportCanvas']))
        frame.alpha_composite(native.resize(tuple(cfg['resampledCanvas']),Image.Resampling.LANCZOS),tuple(reg['translation']))
        dest=out/f"{f['frame']:02}.png";frame.save(dest)
        scale=cfg['resampledCanvas'][0]/cfg['nativeCanvas'][0]
        meta={'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','status':'candidate-export-not-visually-approved','derivedFrom':[{'file':src.relative_to(ROOT).as_posix(),'sha256':sha(src),'generationRecord':str(src.relative_to(ROOT))+'.generation.json'}],'operation':{'type':'uniform-whole-canvas-resample-and-direction-common-translation','newPoseGenerated':False,'nativeSize':list(native.size),'resampledCanvas':cfg['resampledCanvas'],'scale':scale,'translation':reg['translation'],'rootTarget':cfg['rootTarget'],'virtualSourceRoot':[(cfg['rootTarget'][j]-reg['translation'][j])/scale for j in range(2)],'rootMethod':reg['basis'],'nativeAlphaPreserved':True,'colorKeying':False,'perSubjectBBoxScaling':False},'visualAcceptance':False,'dynamicAcceptance':False}
        Path(str(dest)+'.generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        records.append({'direction':direction,'frame':f['frame'],'file':meta['file'],'sha256':meta['sha256'],'source':f['url'][3:]})
(ROOT/'candidate/run-export-inventory.json').write_text(json.dumps({'status':cfg['status'],'frames':records,'count':len(records),'frameDurationMs':75,'selectedCycleMs':1200,'phaseWeightsApplied':False,'root':[512,942]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidateExports':len(records),'groups':{d:sum(r['direction']==d for r in records) for d in cfg['directions']}}))

