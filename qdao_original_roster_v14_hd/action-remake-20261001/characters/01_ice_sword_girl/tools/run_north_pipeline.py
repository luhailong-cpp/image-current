"""Private N/NE/NW asset registrar and full-canvas exporter; never generates pixels."""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil, subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def normalized(x):
    if isinstance(x,dict): return {k:normalized(v) for k,v in x.items()}
    if isinstance(x,list): return [normalized(v) for v in x]
    if isinstance(x,str): return x.replace('\\','/')
    return x
def write(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(normalized(x),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def register(d,f,v):
    assert d in ['N','NE','NW']
    stem=f'run-{d}{f:02}-v{v}'; rec=ROOT/'sources'/(stem+'.receipt.json'); r=read(rec)
    target=ROOT/'drafts/run'/d/f'{f:02}-v{v}.png'; target.parent.mkdir(parents=True,exist_ok=True)
    src=Path(r['sourceOutput']); assert src.is_file()
    if target.exists(): assert sha(target)==sha(src),'Refusing different overwrite'
    else: shutil.copyfile(src,target)
    im=Image.open(target); im.load(); assert im.mode=='RGBA' and min(im.size)>=1024 and im.getchannel('A').getextrema()==(0,255)
    subprocess.run([sys.executable,str(ROOT/'tools/record_frame.py'),str(target.relative_to(ROOT)),str(rec.relative_to(ROOT)),str((ROOT/'sources'/(stem+'.prompt.txt')).relative_to(ROOT))],check=True)
    gr=target.with_name(target.name+'.generation.json'); g=read(gr);g['visualReview']=dict(r['visualReview'],clientRuntimeVerified=False);write(gr,g)
    print(json.dumps({'file':str(target.relative_to(ROOT)),'size':im.size,'alpha':im.getchannel('A').getextrema(),'sha256':sha(target)}))
def export(d):
    assert d in ['N','NE','NW']
    selected=[]
    for f in range(1,17):
        options=list((ROOT/'drafts/run'/d).glob(f'{f:02}-v*.png'))
        if not options: continue
        eligible=[]
        for p in options:
            g=read(p.with_name(p.name+'.generation.json'))
            if g['visualReview']['status'].startswith('retain'):eligible.append((int(p.stem.split('-v')[-1]),p,g))
        if not eligible:continue
        _,p,g=max(eligible,key=lambda x:x[0]);im=Image.open(p).convert('RGBA');dest=ROOT/'candidate/run'/d/f'{f:02}.png';dest.parent.mkdir(parents=True,exist_ok=True)
        assert im.width==im.height and im.width>=1024
        im.resize((1024,1024),Image.Resampling.LANCZOS).save(dest)
        native=list(im.size);gen={'schemaVersion':1,'file':str(dest.relative_to(ROOT)),'sha256':sha(dest),'exportedAt':datetime.now(timezone.utc).isoformat(),'derivedFrom':{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'generationRecord':str(p.with_name(p.name+'.generation.json').relative_to(ROOT))},'nativeFrameSize':native,'outputFrameSize':[1024,1024],'operation':{'name':'whole_canvas_uniform_downscale','scale':1024/im.width,'translation':[0,0],'crop':None,'perFrameBboxScaling':False,'lowestPixelGrounding':False},'actualModel':g['actualModel'],'actualQuality':g['actualQuality'],'configSnapshot':g['configSnapshot'],'visualReview':g['visualReview']};write(dest.with_name(dest.name+'.generation.json'),gen)
        selected.append({'frame':f,'path':str(dest.relative_to(ROOT)),'sourcePath':str(p.relative_to(ROOT)),'sha256':sha(dest),'sourceSha256':sha(p),'nativeSize':native,'generationRecord':str(dest.with_name(dest.name+'.generation.json').relative_to(ROOT)),'status':'selected_for_preview','plannedPhase':g['visualReview'].get('plannedPhase'),'actualPhase':g['visualReview'].get('actualPhase'),'actualContact':g['visualReview'].get('actualContact'),'notes':g['visualReview']['notes'],'durationMs':75,'actualModel':None,'actualQuality':None})
    write(ROOT/'review'/f'run-{d}-selection.json',{'schemaVersion':1,'characterId':'01_ice_sword_girl','direction':d,'updatedAt':datetime.now(timezone.utc).isoformat(),'canvasSize':[1024,1024],'root':{'status':'provisional','definition':'Fixed full canvas; no per-frame registration. Actual support geometry reviewed visually; shared character virtual root handled by parent.'},'timing':{'cycleMs':1200,'frameDurationsMs':[75]*16,'status':'user_requested_1200ms_uniform','formalClientTimingConfirmed':False},'frames':selected,'artStatus':'needs_sequence_review','clientIntegrated':False,'clientRuntimeVerified':False,'formalExportCount':0})
    print(json.dumps({'direction':d,'candidateCount':len(selected),'selection':f'review/run-{d}-selection.json'}))
if __name__=='__main__':
    if sys.argv[1]=='register':register(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]))
    elif sys.argv[1]=='export':export(sys.argv[2])
