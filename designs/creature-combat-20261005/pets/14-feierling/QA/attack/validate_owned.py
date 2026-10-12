from PIL import Image
from pathlib import Path
import json,hashlib,datetime
base=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for direction,n in [('E',12),('W',6)]:
    for i in range(1,n+1):
        frame=f'{i:02}'
        file=base/'runtime'/'attack'/direction/(frame+'.png')
        gen=base/'generation'/'attack'/direction/(frame+'.generation.json')
        m=json.loads(gen.read_text(encoding='utf-8'))
        with Image.open(file) as im:
            a=im.getchannel('A'); hist=a.histogram()
            records.append({'direction':direction,'frame':frame,'file':str(file),'sha256':sha(file),'record':str(gen),'size':list(im.size),'mode':im.mode,'alphaMinMax':list(a.getextrema()),'bboxAlpha1':a.getbbox(),'bboxAlpha32':a.point(lambda v:255 if v>=32 else 0).getbbox(),'nativeSize':[m['native']['width'],m['native']['height']],'nativeSHA':m['native']['sha256'],'model':m['actualModel'],'quality':m['actualQuality'],'recordShaMatches':m['exported']['sha256']==sha(file),'promptExists':Path(m['prompt']).exists()})
for frame in ['07','08']:
    file=base/'generation'/'attack'/'E'/(frame+'.rejected-attempt-01.generation.json')
    m=json.loads(file.read_text(encoding='utf-8'))
    m['status']='rejected_replaced'
    m['reason']='E07 insufficient down-right palm extension; E08 discontinuous lateral palm path' 
    m['nativeSavedPath']=None
    m['runtimeFileRetained']=False
    m['retentionNote']='Workspace native and runtime file were replaced after successful AI repair; original source SHA and tool path retained as text provenance, no image backup created.'
    m['prompt']=str(file.parent/(frame+'.rejected-attempt-01.prompt.txt'))
    file.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
mfile=base/'generation'/'attack'/'E'/'07.generation.json'
m=json.loads(mfile.read_text(encoding='utf-8'))
m['references'][-1]['historicalOnly']=True
m['references'][-1]['currentPathReplaced']=True
mfile.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
report={'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'subagent-owned attack E01-12 and W01-06 only; W07-12 produced by root','expectedCount':18,'actualCount':len(records),'uniqueSHA':len(set(r['sha256'] for r in records)),'sizeModePass':all(r['size']==[1024,1024] and r['mode']=='RGBA' for r in records),'alphaPass':all(r['alphaMinMax']==[0,255] for r in records),'evidencePass':all(r['recordShaMatches'] and r['promptExists'] for r in records),'records':records,'visualStatus':'All 18 generated full frames viewed individually through image_gen results; final contact sheets reviewed separately. E07/E08 targeted repair accepted. Dynamic playback not yet performed by this subagent.','clientIntegration':'not performed','remainingRisks':['Footprint varies modestly at E02-E04 wind-up; inspect slow playback before acceptance.','Native alpha contains faint nonzero pixels near canvas borders; alpha32 bbox is better subject-edge diagnostic.','Root will apply direction-wide final export transform and regenerate final hashes.']}
(base/'QA'/'attack'/'validation-owned18.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['actualCount','uniqueSHA','sizeModePass','alphaPass','evidencePass']},ensure_ascii=False))

