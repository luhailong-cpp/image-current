"""One fixed export transform per direction, shared by all three actions.
Does not invent poses, interpolate frames, or align individual feet.
"""
from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone

BASE=Path(__file__).resolve().parents[1]
STATE=BASE/'export-registration.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    if STATE.exists():raise SystemExit('Already registered; do not transform twice.')
    expected=[BASE/'runtime'/a/d/f'{i:02d}.png' for a,n in [('hit',6),('attack',12),('cast',16)] for d in ['E','W'] for i in range(1,n+1)]
    assert all(p.is_file() for p in expected),'Missing runtime frame'
    transforms={'E':{'resizedCanvas':[840,840],'offset':[24,130],'referenceAnchor':[595,990]},'W':{'resizedCanvas':[840,840],'offset':[114,151],'referenceAnchor':[485,965]}}
    items=[]; records=[]
    # Validate every source before the first write.
    for p in expected:
        action,direction=p.parts[-3:-1];rp=p.with_suffix('.png.generation.json')
        if not rp.exists():rp=BASE/'provenance'/action/direction/(p.stem+'.generation.json')
        r=read(rp);assert r.get('sha256',r.get('export',{}).get('sha256'))==sha(p),(p,'source record mismatch')
        with Image.open(p) as im:assert im.size==(1024,1024) and im.mode=='RGBA'
    for p in expected:
        action,direction=p.parts[-3:-1]; idx=p.stem
        rp=p.with_suffix('.png.generation.json')
        if not rp.exists():rp=BASE/'provenance'/action/direction/(idx+'.generation.json')
        r=read(rp);old=sha(p)
        t=transforms[direction]
        im=Image.open(p).convert('RGBA');assert im.size==(1024,1024)
        visible=im.getchannel('A').point(lambda x:255 if x>16 else 0).getbbox()
        scaled=im.resize((840,840),Image.Resampling.LANCZOS)
        out=Image.new('RGBA',(1024,1024));out.alpha_composite(scaled,tuple(t['offset']))
        out.save(p);new=sha(p)
        history={'file':p.relative_to(BASE).as_posix(),'sha256':old,'width':1024,'height':1024,'operationBeforeRegistration':r.get('operation',r.get('export',{}).get('operation')),'replacedBy':new,'retained':False}
        r.setdefault('exportHistory',[]).append(history)
        r['sha256']=new;r['file']=p.relative_to(BASE).as_posix()
        r['width']=1024;r['height']=1024;r['format']='PNG';r['mode']='RGBA'
        r['operation']={'type':'whole_canvas_direction_fixed_export','inputSize':[1024,1024],'resizedCanvas':[840,840],'uniformScale':840/1024,'offset':t['offset'],'outputSize':[1024,1024],'perFrameAlignment':False,'allActionsShareTransform':True,'sourceBeforeExportSha256':old,'registration':'export-registration.json'}
        if isinstance(r.get('export'),dict):r['export'].update(width=1024,height=1024,sha256=new,alphaBBox=out.getchannel('A').getbbox(),operation=r['operation'])
        r['anchor']={'pixel':[512,942],'pivot':[0.5,0.08],'basis':'manual two-foot contact projection midpoint of direction attack01; approximate +/-15 source pixels','referenceBeforeExport':t['referenceAnchor'],'referenceAfterExport':[t['referenceAnchor'][0]*840/1024+t['offset'][0],t['referenceAnchor'][1]*840/1024+t['offset'][1]],'individualFeetForcedToAnchor':False}
        records.append((rp,r))
        items.append({'file':p.relative_to(BASE).as_posix(),'beforeSha256':old,'afterSha256':new,'sourceRecord':rp.relative_to(BASE).as_posix(),'direction':direction,'visibleBBoxBefore':visible,'visibleBBoxAfter':out.getchannel('A').point(lambda x:255 if x>16 else 0).getbbox()})
    mapping={str((BASE/i['file']).resolve()).lower():i for i in items}
    for rp,r in records:
        for ref in r.get('references',[]):
            if not isinstance(ref,dict):continue
            raw=ref.get('path',ref.get('file'))
            if not raw:continue
            p=Path(raw);p=p if p.is_absolute() else BASE/p
            item=mapping.get(str(p.resolve()).lower())
            if item and ref.get('sha256')==item['beforeSha256']:
                ref['historicalRevision']={'sha256AtGeneration':ref['sha256'],'currentSha256':item['afterSha256'],'change':'same path subsequently received shared direction export transform','record':'export-registration.json','pixelsAtGenerationRetained':False}
        rp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    STATE.write_text(json.dumps({'performedAt':datetime.now(timezone.utc).isoformat(),'purpose':'fixed direction scale and anchor export only, not pose creation','transforms':transforms,'inputCoordinateSystem':[1024,1024],'outputCoordinateSystem':[1024,1024],'perFrameAlignment':False,'sourceBackupsRetained':False,'targetAnchor':[512,942],'frames':items},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'registered':len(items),'transforms':transforms},ensure_ascii=False))
if __name__=='__main__':main()
