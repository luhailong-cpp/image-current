"""Immutable native internal repairs for r14_c14; no resizing, no neighboring writes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, re, shutil, sys, uuid
import numpy as np
from PIL import Image, ImageDraw
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent
R=T/'repairs'
R.mkdir(exist_ok=True)
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def js(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def png(p,im):
    with Path(p).open('xb') as f:im.save(f,format='PNG')
def art(p):
    d={'path':str(Path(p).resolve()),'sha256':sha(p)}
    try:
        with Image.open(p) as im:d['size']=list(im.size)
    except (OSError,ValueError):pass
    return d
def checked(d):need(sha(d['path'])==d['sha256'],'Hash changed: '+d['path'])
def current():
    p=R/'latest-repair.json'
    return read(p) if p.exists() else read(T/'candidate/latest-assembly.json')
def prepare(label,x,y,boxes,instruction):
    need(re.fullmatch('[a-z][a-z0-9-]*',label),'Invalid label')
    x,y=int(x),int(y);boxes=json.loads(boxes)
    need(0<=x<=2842 and 0<=y<=2842,'Crop outside core')
    for a in boxes:need(len(a)==4 and 6<=a[0]<a[2]<=1248 and 6<=a[1]<a[3]<=1248,'Bad inpaint box')
    contract=read(T.parent.parent/'production-contract.json')
    need(contract.get('newArtworkGenerationAllowed') and read(contract['productionResumeControl']).get('newArtworkGenerationAllowed'),'Generation gate')
    cur=current();checked(cur['candidate']);checked(cur['context'])
    refs=[]
    for k,h in [('layoutReference','layoutSha256'),('detailStyleReference','detailSha256'),('primaryStyleReference','primaryStyleSha256')]:
        d=art(contract[k]);need(d['sha256']==contract[h],'Reference changed');d['role']=k+' reference only';refs.append(d)
    ver=label+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]
    d=R/ver;d.mkdir()
    raw=Image.open(cur['candidate']['path']).convert('RGB').crop((x,y,x+1254,y+1254));png(d/'source-1254.png',raw)
    guide=raw.copy();draw=ImageDraw.Draw(guide)
    for a in boxes:draw.rectangle((a[0],a[1],a[2]-1,a[3]-1),fill=(255,0,255))
    png(d/'target-1254.png',guide)
    prompt="""Use case: precise-object-edit. Edit ONLY the LAST image, an exact native 1254x1254 detailed crop of our existing Taoist chibi game map. First three images are style references only; do not recreate their scenes.
Fill ONLY the solid magenta rectangular holes with continuous original pavement. Magenta marks missing pixels and is not part of the artwork. Preserve every visible non-magenta pixel, exact framing, scale, objects, lighting, stone colors and crisp detail. Do not zoom, pan, refit the whole lattice or invent additional joints. The visible grout endpoints entering every hole from its sides are fixed. Reconstruct each affected stone slab as a coherent closed shape. Connect the matching fixed grout ends with one clean continuous groove of the same width, edge highlight, shadow and angle. No dangling lines, offsets, doubled seams, missing segments, narrow slivers, blur or decorative masking. Where a diagonal changes slightly, make a smooth natural connection only inside the hole. Preserve red paper and existing shadows exactly. No new paper, foliage, wood, buildings, blue road bands, text, UI or marks.
Output one opaque native 1254x1254 PNG at the same framing, no scaling.
SPECIFIC REPAIR:
"""+instruction
    (d/'prompt.txt').write_text(prompt,encoding='utf-8')
    refs.append({**art(d/'target-1254.png'),'role':'LAST IMAGE only edit target: documented magenta-hole native guide'})
    req={'prompt':prompt,'referenced_image_paths':[a['path'] for a in refs],'transparent_background':False};js(d/'request.json',req)
    js(d/'preparation.json',{'version':ver,'tile':'r14_c14','preparedAt':now(),'sourceCandidate':cur['candidate'],'sourceContext':cur['context'],'sourceCropIn4096':[x,y,x+1254,y+1254],'rawTarget':art(d/'source-1254.png'),'guide':art(d/'target-1254.png'),'guideHoles':boxes,'guideFillRGB':[255,0,255],'references':refs,'request':art(d/'request.json'),'prompt':art(d/'prompt.txt'),'tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'resized':False,'status':'prepared_not_generated','formalAccepted':False})
    return {'version':ver,'request':str(d/'request.json'),'rawTarget':str(d/'source-1254.png'),'target':str(d/'target-1254.png')}
def ingest(version,source,receipt):
    d=R/version;m=read(d/'preparation.json');s=Path(source);rc=Path(receipt);r=read(rc)
    need(r.get('tool')=='image_gen.imagegen' and re.fullmatch('succeeded(?:_pending_[a-z0-9_]+)?',r.get('status','')),'Truthful builtin success receipt required')
    need(r.get('actualModel') is None and 'actualModel' in r and r.get('actualQuality') is None and 'actualQuality' in r,'Unknown actual model/quality must be explicit null')
    for a in m['references']+[m['request'],m['prompt'],m['rawTarget']]:checked(a)
    with Image.open(s) as im:
        im.load();need(im.format=='PNG' and im.size==(1254,1254) and im.mode in ['RGB','RGBA'],'Output must be native1254 opaquePNG, no resize')
        if im.mode=='RGBA':need(im.getextrema()[3]==(255,255),'Transparent output not allowed')
    dest=d/'native.png';need(not dest.exists(),'Immutable native exists')
    with s.open('rb') as f,dest.open('xb') as g:shutil.copyfileobj(f,g)
    need(sha(s)==sha(dest),'Copy mismatch')
    if rc.resolve()!=(d/'receipt.json').resolve():
        with rc.open('rb') as f,(d/'receipt.json').open('xb') as g:shutil.copyfileobj(f,g)
    js(d/'generation.json',{'version':version,'ingestedAt':now(),'tool':'image_gen.imagegen','route':'builtin','native':art(dest),'originalOutput':art(s),'receipt':art(d/'receipt.json'),'preparation':art(d/'preparation.json'),'references':m['references'],'actualModel':None,'actualQuality':None,'resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'native_repair_pending_composition_review','formalAccepted':False})
    return art(dest)
def compose(version):
    d=R/version;m=read(d/'preparation.json');g=read(d/'generation.json');cur=current()
    for a in [g['native'],g['originalOutput'],g['receipt'],g['preparation'],cur['candidate'],cur['context']]:checked(a)
    base=np.array(Image.open(cur['candidate']['path']).convert('RGB'));raw=np.array(Image.open(m['rawTarget']['path']).convert('RGB'))
    x,y,x1,y1=m['sourceCropIn4096'];old=base[y:y1,x:x1].copy();gen=np.array(Image.open(g['native']['path']).convert('RGB'))
    alpha=np.zeros((1254,1254),dtype=np.uint8)
    for a,b,c,e in m['guideHoles']:
        # include four unchanged native context pixels around each inpainted hole;
        # only outer two pixels transition, all hole pixels use actual native paint.
        a,b,c,e=a-4,b-4,c+4,e+4
        yy,xx=np.mgrid[b:e,a:c]
        dist=np.minimum.reduce([xx-a,yy-b,c-1-xx,e-1-yy])
        alpha[b:e,a:c]=np.maximum(alpha[b:e,a:c],np.uint8(np.clip(dist/2,0,1)*255))
    need(np.array_equal(old[alpha>0],raw[alpha>0]),'Overlapping repair changed; prepare fresh')
    need(not np.any((gen[:,:,0]==255)&(gen[:,:,1]==0)&(gen[:,:,2]==255)&(alpha>0)),'Magenta guide remains in applied region')
    new=base.copy();aa=alpha[:,:,None].astype(np.uint32)
    new[y:y1,x:x1]=((old.astype(np.uint32)*(255-aa)+gen.astype(np.uint32)*aa+127)//255).astype(np.uint8)
    full=np.zeros((4096,4096),bool);full[y:y1,x:x1]=alpha>0
    need(np.array_equal(new[~full],base[~full]),'Outside repair changed')
    png(d/'alpha.png',Image.fromarray(alpha));out=T/'candidate'/('r14_c14-4k-repaired-'+version+'.png');png(out,Image.fromarray(new))
    ctx=np.array(Image.open(cur['context']['path']).convert('RGB'));need(ctx.shape==(4326,4326,3),'Context shape');ctx[115:4211,115:4211]=new
    cp=T/'candidate'/('r14_c14-context-repaired-'+version+'.png');png(cp,Image.fromarray(ctx))
    cm={'version':version,'tile':'r14_c14','composedAt':now(),'sourceCandidate':cur['candidate'],'sourceContext':cur['context'],'candidate':art(out),'context':art(cp),'nativeGeneration':art(d/'generation.json'),'preparation':art(d/'preparation.json'),'native':g['native'],'nativeSourceCrop':[0,0,1254,1254],'placementIn4096':m['sourceCropIn4096'],'alpha':art(d/'alpha.png'),'compositor':art(Path(__file__)),'rule':'Documented magenta holes plus4px real native context; outer2px linear alpha transition; integer uint32 rounded composition; NO resizing, blur, or neighbor writes','outsideRepairUnchanged':True,'formalAccepted':False,'status':'repaired_candidate_pending_visual_review'}
    js(d/'composition.json',cm);replay(version);png(d/'review-composed-1254.png',Image.fromarray(new[y:y1,x:x1]))
    return {'version':version,'review':str(d/'review-composed-1254.png'),'candidate':cm['candidate']}
def replay(version):
    d=R/version;m=read(d/'composition.json');prep=read(d/'preparation.json');g=read(d/'generation.json')
    for k in ['sourceCandidate','sourceContext','candidate','context','nativeGeneration','preparation','native','alpha','compositor']:checked(m[k])
    for a in prep['references']+[prep['sourceCandidate'],prep['sourceContext'],prep['rawTarget'],prep['guide'],prep['request'],prep['prompt'],g['originalOutput'],g['receipt']]:checked(a)
    x,y,x1,y1=prep['sourceCropIn4096'];raw=Image.open(prep['sourceCandidate']['path']).convert('RGB').crop((x,y,x1,y1))
    need(np.array_equal(np.array(raw),np.array(Image.open(prep['rawTarget']['path']).convert('RGB'))),'Raw target replay')
    dr=ImageDraw.Draw(raw)
    for a,b,c,e in prep['guideHoles']:dr.rectangle((a,b,c-1,e-1),fill=tuple(prep['guideFillRGB']))
    need(np.array_equal(np.array(raw),np.array(Image.open(prep['guide']['path']).convert('RGB'))),'Guide replay')
    base=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));gen=np.array(Image.open(m['native']['path']).convert('RGB'));a=np.array(Image.open(m['alpha']['path']))[:,:,None].astype(np.uint32)
    base[y:y1,x:x1]=((base[y:y1,x:x1].astype(np.uint32)*(255-a)+gen.astype(np.uint32)*a+127)//255).astype(np.uint8)
    need(np.array_equal(base,np.array(Image.open(m['candidate']['path']).convert('RGB'))),'Candidate replay')
    ctx=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));ctx[115:4211,115:4211]=base
    need(np.array_equal(ctx,np.array(Image.open(m['context']['path']).convert('RGB'))),'Context replay')
    return {'replayed':True,'candidateSha256':m['candidate']['sha256']}
def retain(version):
    d=R/version;v=read(d/'visual-review.json');need(v.get('status')=='local_pass','Explicit local visual pass required');replay(version);m=read(d/'composition.json')
    temp=R/('latest-'+uuid.uuid4().hex+'.tmp');js(temp,m);temp.replace(R/'latest-repair.json')
    return m['candidate']
if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
    q=s.add_parser('prepare')
    for a in ['label','x','y','boxes','instruction']:q.add_argument(a)
    q=s.add_parser('ingest')
    for a in ['version','source','receipt']:q.add_argument(a)
    for n in ['compose','replay','retain']:q=s.add_parser(n);q.add_argument('version')
    a=vars(p.parse_args());f=a.pop('cmd');print(json.dumps(globals()[f](**a),ensure_ascii=False,indent=2))

