from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
r=Path('D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian');p=r/'provenance/cast/E'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
rows=[]; seen=set()
for i in range(1,17):
    n=f'{i:02}';f=r/'runtime/cast/E'/f'{n}.png';im=Image.open(f)
    j=json.loads((p/f'{n}.generation.json').read_text(encoding='utf8'))
    a=im.getchannel('A'); hist=a.histogram()
    assert im.size==(1024,1024) and im.mode=='RGBA'
    assert sha(f)==j['sha256'] and sha(f) not in seen
    seen.add(sha(f))
    assert hist[0]>0 and hist[255]>0
    assert all(Path(x['path']).exists() for x in j['references'])
    assert Path(j['prompt']).exists() and Path(j['evidence']['receipt']).exists()
    assert j['actualModel'] is None and j['actualQuality'] is None
    assert j['operation']['resize']==[920,920] and j['operation']['paste']==[52,37]
    rows.append({'frame':i,'file':str(f),'sha256':sha(f),'size':list(im.size),'mode':im.mode,'alphaExtrema':a.getextrema(),'transparentPixels':hist[0],'partialAlphaPixels':sum(hist[1:255]),'opaquePixels':hist[255],'bbox':a.getbbox(),'record':str(p/f'{n}.generation.json')})
for page in range(2):
    sheet=Image.new('RGB',(1280,700),(51,58,61));d=ImageDraw.Draw(sheet)
    for k in range(8):
        i=page*8+k+1
        im=Image.open(r/'runtime/cast/E'/f'{i:02}.png').resize((320,320),Image.Resampling.LANCZOS)
        x=(k%4)*320;y=(k//4)*350
        sheet.paste(im,(x,y+25),im)
        d.text((x+10,y+5),f'CAST E {i:02}',fill=(245,245,220))
    sheet.save(p/f'inspection-{page+1}.jpg',quality=93)
report={'action':'cast','direction':'E','count':len(rows),'expected':16,'durationMs':45,'totalDurationMs':720,'technicalChecks':'passed','uniqueShaCount':len(seen),'frames':rows,'singleFrameVisualInspected':list(range(1,17)),'dynamicPreview':'pending root combined preview','clientIntegration':'not tested','notes':['09 initial candidate rejected for exaggerated left-mallet jump; correction is current09.','Potential normal/slow review focus: 01->02 frame lift, 10->11 lowering, 13->14 chime length and ring settling; no per-frame positional correction applied.']}
(p/'technical-progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
j=json.loads((p/'09.rejected1.generation.json').read_text(encoding='utf8'))
j.update({'file':None,'historicalRuntimeFile':str(r/'runtime/cast/E/09.png'),'retentionState':'rejected; runtime replaced by accepted corrected09','prompt':str(p/'09.rejected1.prompt.txt')})
j['evidence']['receipt']=str(p/'09.rejected1.receipt.json');j['derivedFrom']['nativeFile']=str(p/'_inprogress/09.rejected1.png');j['visualQA']['accepted']=False;j['visualQA']['rejectionReason']='Excessive left mallet outward jump immediately after contact'
(p/'09.rejected1.generation.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
j=json.loads((p/'09.attempt1.failure.json').read_text(encoding='utf8'));j['prompt']='09.rejected1.prompt.txt';(p/'09.attempt1.failure.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'count':len(rows),'uniqueSHA':len(seen),'technical':'passed','all1024RGBA':True,'allProvenanceReferencesPresent':True}))
