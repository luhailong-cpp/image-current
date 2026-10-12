"""One fixed export transform per direction; never creates motion or aligns frames."""
import json, hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
R=Path(__file__).resolve().parents[1]
SPECS={'hit':6,'attack':12,'cast':16}
TRANSFORMS={'E':{'scaledCanvas':[768,768],'offset':[43,230],'referenceSupportApprox':[625,949]},'W':{'scaledCanvas':[768,768],'offset':[210,253],'referenceSupportApprox':[403,919]}}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    targets=[R/'runtime'/a/d/f'{i:02}.png' for a,n in SPECS.items() for d in ('E','W') for i in range(1,n+1)]
    assert all(p.is_file() for p in targets), 'All 68 independent generated frames must exist before final export'
    assert not (R/'records/final-registration.json').exists(), 'Already registered; do not apply twice'
    entries=[]
    for p in targets:
        d=p.parent.name; a=p.parent.parent.name; t=TRANSFORMS[d]; recp=p.with_suffix('.png.generation.json'); rec=json.loads(recp.read_text(encoding='utf-8-sig'))
        oldsha=sha(p); oldrec=dict(rec); removed=f'removed/intermediate/{a}/{d}/{p.name}'
        oldrec.update(file=removed,originalRuntimePath=p.relative_to(R).as_posix(),imageRetention='overwritten by final registered export; textual evidence retained')
        history=R/'records/pre-registration'/f'{a}-{d}-{p.stem}.json'; save(history,oldrec)
        im=Image.open(p).convert('RGBA'); assert im.size==(1024,1024)
        out=Image.new('RGBA',(1024,1024)); out.paste(im.resize((768,768),Image.Resampling.LANCZOS),tuple(t['offset'])); out.save(p)
        rec.update(sha256=sha(p),derivedFrom={'file':removed,'sha256':oldsha,'generationRecord':history.relative_to(R).as_posix(),'deleted':True,'deletionReason':'intermediate runtime pixels replaced by uniformly registered final export'},operation={'type':'fixed-direction-full-canvas-scale-and-pad','inputSize':[1024,1024],'scaledCanvas':[768,768],'outputSize':[1024,1024],'offsetPixels':t['offset'],'scale':0.75,'resample':'Lanczos','direction':d,'sameForAllThreeActions':True,'perFrameAlignment':False,'alpha':'preserved, no thresholding','nominalAnchorTop':[512,942],'pivotBottom':[0.5,0.08]})
        rec['finalExportAt']=datetime.now(ZoneInfo('America/New_York')).isoformat(); rec['visualStatus']='pending final registered playback review'; save(recp,rec)
        entries.append({'file':p.relative_to(R).as_posix(),'beforeSha256':oldsha,'afterSha256':rec['sha256'],'direction':d})
    save(R/'records/final-registration.json',{'date':datetime.now(ZoneInfo('America/New_York')).isoformat(),'transforms':TRANSFORMS,'calibration':'One visual support calibration from each neutral direction anchor; coordinates approximate painted support. Applied identically to every action and frame in that direction. Frame-specific recoil is preserved, not re-aligned.','nominalAnchorTop':[512,942],'entries':entries})
    print('Registered 68 frames with two fixed transforms; no animation frames generated or duplicated.')
if __name__=='__main__': main()
