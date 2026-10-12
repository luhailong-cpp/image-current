import json, sys, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    selection=json.loads((ROOT/'selected-patches.json').read_text(encoding='utf-8-sig'))
    if len(sys.argv)>1:
        for stem in sys.argv[1:]:
            patch=stem.split('-')[0]
            p=ROOT/'native'/f'{stem}.png'
            assert Image.open(p).size==(1254,1254)
            selection['patches'][patch]=f'native/{stem}.png'
        save(ROOT/'selected-patches.json',selection)
    plan=json.loads((ROOT/'coordinate-plan.json').read_text(encoding='utf-8-sig'))
    entries={p['id']:p for p in plan['patches']}
    qa=ROOT/'qa';qa.mkdir(exist_ok=True)
    out=ROOT/'candidate';out.mkdir(exist_ok=True)
    canvas=Image.new('RGB',(4096,4096),(65,65,65))
    arrays={}; sources=[]
    for pid,rel in sorted(selection['patches'].items()):
        im=Image.open(ROOT/rel).convert('RGB'); p=entries[pid]
        assert im.size==(1254,1254)
        box=(115,115,1139,1139);x=(p['subcolumn']-1)*1024;y=(p['subrow']-1)*1024
        canvas.paste(im.crop(box),(x,y))
        arrays[pid]=np.array(im)
        sources.append({'patch':pid,'path':str(ROOT/rel),'sha256':sha(ROOT/rel),'nativeDimensions':list(im.size),'sourceCrop':list(box),'destination':[x,y,x+1024,y+1024],'sourceGlobalBox':p['globalBox'],'generationRecord':str(ROOT/(rel+'.generation.json'))})
    full=len(sources)==16
    cp=out/('r11_c09-native-candidate-4096.png' if full else 'r11_c09-partial-4096.png')
    canvas.save(cp)
    canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(qa/'candidate-preview-1024.png')
    seams=[]
    for r in range(1,5):
        for c in range(1,5):
            a=f'p{r}{c}'
            if a not in arrays: continue
            for axis,b in [('vertical',f'p{r}{c+1}'),('horizontal',f'p{r+1}{c}')]:
                if b not in arrays: continue
                aa,bb=arrays[a],arrays[b]
                if axis=='vertical':
                    strip=np.concatenate([aa[115:1139,1011:1139],bb[115:1139,115:243]],axis=1)
                    ov1,ov2=aa[115:1139,1024:1254],bb[115:1139,:230]
                else:
                    strip=np.concatenate([aa[1011:1139,115:1139],bb[115:243,115:1139]],axis=0)
                    ov1,ov2=aa[1024:1254,115:1139],bb[:230,115:1139]
                name=f'{a}-{b}-{axis}.png';Image.fromarray(strip).save(qa/name)
                diff=np.abs(ov1.astype(float)-ov2.astype(float))
                seams.append({'pair':[a,b],'axis':axis,'qaNativeStrip':str(qa/name),'sameCoordinateOverlapMeanAbsoluteRGB':float(diff.mean()),'medianAbsoluteRGB':float(np.median(diff)),'interpretation':'Diagnostic includes geometry and texture; not pure color error and not pass criterion.'})
    for r in range(1,4):
        for c in range(1,4):
            ids=[f'p{r}{c}',f'p{r}{c+1}',f'p{r+1}{c}',f'p{r+1}{c+1}']
            if all(i in arrays for i in ids):
                x=c*1024;y=r*1024;canvas.crop((x-192,y-192,x+192,y+192)).save(qa/f'cross-r{r}c{c}-native.png')
    manifest={'tile':'r11_c09','status':'unscaled_candidate_pending_internal_and_external_review' if full else 'incomplete_native_generation','formalAccepted':False,'dimensions':[4096,4096],'nativePatchCount':len(sources),'requiredNativePatchCount':16,'layoutOnlyPixelsInFinal':False,'resizeFinalArtwork':False,'resampleFinalArtwork':False,'sourceCrop':[115,115,1139,1139],'candidate':str(cp),'candidateSha256':sha(cp),'sources':sources,'internalSeams':seams,'externalSeams':'not yet reviewed','preview':'QA-only downsample, never final artwork','createdAt':datetime.now(timezone.utc).isoformat()}
    save(out/'manifest.json',manifest)
    save(ROOT/'progress.json',{'tile':'r11_c09','status':manifest['status'],'generatedNativeCount':len(list((ROOT/'native').glob('*.png'))),'usableNativeCount':len(sources),'complete4kCandidateCount':int(full),'formalAcceptedCount':0,'errors':[{'patch':'p12-v1','issue':'Repeated left-neighbor composition; not selected'}],'updatedAt':datetime.now(timezone.utc).isoformat()})
    print(json.dumps({'selected':len(sources),'seams':len(seams),'candidate':str(cp),'sha256':sha(cp)}))
if __name__=='__main__':main()
