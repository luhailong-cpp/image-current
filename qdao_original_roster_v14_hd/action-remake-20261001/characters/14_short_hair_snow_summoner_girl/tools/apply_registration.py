"""Apply ONE shared affine scale + integer translation using reviewed anatomical roots.
No per-frame fitting, sole detection, pose changes, mirroring or frame synthesis.
"""
import argparse, hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SCALE=0.80
TARGET=(512,942)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def apply(regpath, dry=False):
    regpath=Path(regpath).resolve()
    if ROOT not in regpath.parents: raise ValueError('Registration outside character')
    reg=json.loads(regpath.read_text(encoding='utf-8-sig'))
    if float(reg['globalScale'])!=SCALE or list(reg['targetRoot'])!=list(TARGET): raise ValueError('Global transform mismatch')
    results=[]
    for row in reg['frames']:
        p=(ROOT/row['file']).resolve()
        if ROOT not in p.parents: raise ValueError('Frame outside character')
        meta=Path(str(p)+'.generation.json')
        old=json.loads(meta.read_text(encoding='utf-8-sig'))
        current=sha(p)
        done=old.get('registrationTransform',{})
        if done.get('inputSha256')==row['sha256'] and done.get('outputSha256')==current:
            results.append({'file':row['file'],'status':'already_applied'});continue
        if current!=row['sha256']: raise ValueError('Source SHA changed: '+row['file'])
        im=Image.open(p).convert('RGBA')
        if im.size!=(1024,1024): raise ValueError('Expected normalized 1024 source')
        sx,sy=row['srcRoot'];tx=round(TARGET[0]-SCALE*sx);ty=round(TARGET[1]-SCALE*sy)
        b=im.getchannel('A').point(lambda x:255 if x>8 else 0).getbbox()
        predicted=[SCALE*b[0]+tx,SCALE*b[1]+ty,SCALE*b[2]+tx,SCALE*b[3]+ty]
        if min(predicted[:2])<2 or max(predicted[2:])>1022:
            raise ValueError('Transform risks clipping: '+row['file']+' '+str(predicted))
        rec={'file':row['file'],'status':'dry_run' if dry else 'applied','inputSha256':current,'sourceRoot':[sx,sy],'targetRoot':list(TARGET),'globalScale':SCALE,'integerTranslation':[tx,ty],'rootRoundingError':[SCALE*sx+tx-TARGET[0],SCALE*sy+ty-TARGET[1]],'predictedContentBounds':predicted,'registrationFile':regpath.relative_to(ROOT).as_posix(),'method':'one global affine scale; manually reviewed anatomical root; no per-frame bbox fitting or sole alignment','recordedAt':datetime.now(timezone.utc).isoformat()}
        if not dry:
            # Premultiplied colour avoids dark transparency fringes.
            out=im.convert('RGBa').transform((1024,1024),Image.Transform.AFFINE,(1/SCALE,0,-tx/SCALE,0,1/SCALE,-ty/SCALE),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0)).convert('RGBA')
            out.save(p)
            rec['outputSha256']=sha(p)
            old['preRegistrationExport']={k:old.get(k) for k in ('sha256','operation','review','recordedAt')}
            old['sha256']=rec['outputSha256'];old['registrationTransform']=rec
            old['review']={'status':'pending_final_dynamic_review'}
            meta.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
        results.append(rec)
    report={'registration':str(regpath.relative_to(ROOT)),'globalScale':SCALE,'targetRoot':list(TARGET),'dryRun':dry,'frames':results}
    if not dry: regpath.with_name(regpath.stem+'.applied.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'registration':str(regpath.relative_to(ROOT)),'frames':len(results),'dryRun':dry,'applied':sum(r['status']=='applied' for r in results),'alreadyApplied':sum(r['status']=='already_applied' for r in results)}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('registration');p.add_argument('--dry-run',action='store_true');a=p.parse_args();apply(a.registration,a.dry_run)
