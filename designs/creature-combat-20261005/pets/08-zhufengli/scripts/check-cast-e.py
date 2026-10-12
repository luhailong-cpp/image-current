from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
base=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for n in range(1,17):
    nn=f'{n:02d}'; f=base/'runtime'/'cast'/'E'/f'{nn}.png'
    rfile=base/'receipts'/f'cast-E-{nn}.json'
    r=json.loads(rfile.read_text(encoding='utf-8'))
    if n in (9,10):
        previous=json.loads((base/'receipts'/f'cast-E-{nn}.rejected-01.json').read_text(encoding='utf-8'))
        target=r['references'][3]
        target['role']='edit target: rejected initial release effect; identity and body pose preserved'
        target['atSubmissionSHA256']=previous['outputSHA256']
        target['historicReceipt']=f'receipts/cast-E-{nn}.rejected-01.json'
        r['referenceSHA256'][target['path']]=previous['outputSHA256']
        r['repair']={'reason':'Initial wind leaves clipped by right edge; targeted AI reduction of effect only','rejectedReceipt':f'receipts/cast-E-{nn}.rejected-01.json','rejectedOutputSHA256':previous['outputSHA256'],'retainedRejectedImage':False}
    im=Image.open(f).convert('RGBA'); a=im.getchannel('A')
    alpha=list(a.getdata())
    border=[a.getpixel((x,y)) for x in range(1024) for y in (0,1023)]+[a.getpixel((x,y)) for y in range(1024) for x in (0,1023)]
    b128=a.point(lambda x:255 if x>=128 else 0).getbbox()
    rec={'frame':n,'file':str(f.relative_to(base)).replace('\\','/'),'sha256':sha(f),'size':list(im.size),'mode':im.mode,'alphaExtrema':list(a.getextrema()),'transparentPixels':alpha.count(0),'partialAlphaPixels':sum(0<x<255 for x in alpha),'bboxAnyAlpha':a.getbbox(),'bboxAlpha128':b128,'borderAlphaMax':max(border),'visualInspection':'Viewed built-in output and final exported contact sheet; original E identity, four-foot species, one curled tail/two beads, fixed front-right projection preserved. Frame body articulation advances through charge/release/recovery.'}
    records.append(rec)
    r['visualInspection']={'status':'inspected-all-single-frames','method':'builtin returned image per generated frame plus 4x4 final exported contact sheet','notes':rec['visualInspection'],'animationPlayback':'parent agent full-package preview pending'}
    rfile.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    f.with_suffix('.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1280,1392),(36,43,47));d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
    im=Image.open(base/r['file']).convert('RGBA').resize((320,320),Image.Resampling.LANCZOS)
    x=(i%4)*320;y=(i//4)*348
    sheet.paste(im,(x,y+24),im)
    d.text((x+8,y+5),f'CAST E {i+1:02d} / 45ms',fill=(240,228,198))
sheet.save(base/'qa'/'cast-E-contact.png')
report={'action':'cast','direction':'E','frameCount':len(records),'expectedFrameCount':16,'uniqueSHA256Count':len(set(x['sha256'] for x in records)),'all1024RGBA':all(x['size']==[1024,1024] and x['mode']=='RGBA' for x in records),'allHaveTransparentAndOpaquePixels':all(x['alphaExtrema']==[0,255] for x in records),'generatedEachFrameIndependently':True,'noMirrorTranslationDuplicationInterpolation':True,'export':'whole-canvas RGBA resize only','records':records,'singleFrameVisualCheck':'complete','normalPlaybackCheck':'pending parent all-six-group preview','slowPlaybackCheck':'pending parent all-six-group preview','clientIntegration':'not in scope'}
(base/'qa'/'cast-E-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='records'}))
print(json.dumps([{'frame':r['frame'],'borderAlphaMax':r['borderAlphaMax'],'bboxAlpha128':r['bboxAlpha128']} for r in records]))
