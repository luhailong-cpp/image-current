"""Versioned native repair preparation, exact crop composition and replay.

Does not generate, publish, edit active sources, or change tile progress.
"""
import argparse, hashlib, importlib.util, json, shutil, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageFilter

T = Path(__file__).resolve().parent
Z = T.parent
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p, obj):
    with Path(p).open('x', encoding='utf-8') as f: json.dump(obj, f, ensure_ascii=False, indent=2)
def art(p):
    p=Path(p); a={'path':str(p),'sha256':sha(p)}
    if p.suffix.lower()=='.png':
        with Image.open(p) as im: a.update(size=list(im.size),format=im.format)
    return a
def checked(a):
    assert sha(a['path'])==a['sha256'], a['path']
def png(p, im):
    assert not Path(p).exists(),p
    im.save(p)
def ints(s): return [int(v) for v in s.split(',')]

def prepare(label, box, paste, instruction, previous=None):
    box=ints(box);paste=ints(paste)
    assert box[2]-box[0]==box[3]-box[1]==1254
    assert 0<=box[1]<box[3]<=4096 and -625<=box[0]<box[2]<=4096
    if previous:
        prev=read(previous);base=prev['candidate'];ctx=prev['context']
    else:
        initial=read(T/'candidate/latest-assembly.json');base=initial['candidate'];ctx=initial['context']
    checked(base);checked(ctx)
    westprogress=read(Z/'r13_c14/progress.json');west=art(westprogress['candidate'])
    assert west['sha256']=='89c0bd8fcf2a507c90a1b690a2e0911a8b490f195820502eb026c56f298bc2d4'
    version='structure-'+label+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]
    d=T/'repairs'/version;d.mkdir(parents=True,exist_ok=False)
    target=Image.new('RGB',(1254,1254));assembly=[]
    if box[0]<0:
        cut=-box[0];source=[4096-cut,box[1],4096,box[3]]
        target.paste(Image.open(west['path']).convert('RGB').crop(source),(0,0))
        assembly.append({'source':west,'crop':source,'paste':[0,0]})
        source=[0,box[1],box[2],box[3]]
        target.paste(Image.open(base['path']).convert('RGB').crop(source),(cut,0))
        assembly.append({'source':base,'crop':source,'paste':[cut,0]})
    else:
        target=Image.open(base['path']).convert('RGB').crop(box)
        assembly.append({'source':base,'crop':box,'paste':[0,0]})
    assert target.size==(1254,1254)
    png(d/'target-native-1254.png',target)
    contract=read(Z.parent/'production-contract.json');write(d/'contract-snapshot.json',contract)
    paths=[contract[k] for k in ['layoutReference','detailStyleReference','primaryStyleReference']]+[str(d/'target-native-1254.png')]
    prompt=('Use case: precise-object-edit. Output exactly 1254x1254 opaque pixels. Images 1-3 are approved layout/material style references only. LAST image 4 is the sole edit target, an actual unscaled crop of existing artwork. '+instruction+' Preserve the same crop and pixel registration. Do not change scale, zoom, reframe, replace the whole object, add props, text, marks, or a border. Keep existing daylight, wood hue, brush-grain scale, object silhouettes and contact shadows except the explicitly broken structure being repaired. Keep the outermost 100 pixels unchanged unless the named repair crosses that edge. Return only the repaired native crop.')
    (d/'prompt.txt').write_text(prompt,encoding='utf-8')
    request={'prompt':prompt,'referenced_image_paths':paths,'transparent_background':False};write(d/'request.json',request)
    assert 0<=paste[0]<paste[2]<=1254 and 0<=paste[1]<paste[3]<=1254
    dest=[box[0]+paste[0],box[1]+paste[1],box[0]+paste[2],box[1]+paste[3]]
    assert 0<=dest[0]<dest[2]<=4096 and 0<=dest[1]<dest[3]<=4096
    prep=dict(schemaVersion=1,version=version,preparedAt=now(),sourceCandidate=base,sourceContext=ctx,immutableWest=west,target=art(d/'target-native-1254.png'),sourcePixelAssembly=assembly,repairBoxIn4096=box,nativeSourceCrop=paste,pasteBoxIn4096=dest,references=[art(p) for p in paths],prompt=art(d/'prompt.txt'),request=art(d/'request.json'),contract=art(d/'contract-snapshot.json'),resized=False,formalAccepted=False)
    write(d/'preparation.json',prep)
    return {'version':version,'directory':str(d),'request':request}

def ingest(version, source, receipt):
    d=T/'repairs'/version;m=read(d/'preparation.json');source=Path(source)
    with Image.open(source) as im:
        assert im.format=='PNG' and im.size==(1254,1254),'Must be actual native 1254 PNG; never resize'
    p=d/'native-1254.png';assert not p.exists();shutil.copyfile(source,p)
    r=read(receipt);assert r.get('status','').startswith('succeeded')
    write(d/'generation.json',dict(version=version,ingestedAt=now(),originalGeneratedSource=art(source),native=art(p),receipt=art(receipt),preparation=art(d/'preparation.json'),requestedTool='builtin image_gen',actualModel=None,actualQuality=None,resizedAfterGeneration=False,finalArtUpscaled=False,status='succeeded_pending_visual_QA',formalAccepted=False))
    return art(p)

def compose(version):
    d=T/'repairs'/version;m=read(d/'preparation.json');g=read(d/'generation.json')
    for a in [m['sourceCandidate'],m['sourceContext'],m['immutableWest'],g['native'],g['receipt'],g['preparation']]: checked(a)
    algorithm=Z/'assemble_candidate.py';spec=importlib.util.spec_from_file_location('seam_algorithm',algorithm);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    result=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));x0,y0,x1,y1=m['pasteBoxIn4096'];old=result[y0:y1,x0:x1].copy();new=np.array(Image.open(g['native']['path']).convert('RGB').crop(m['nativeSourceCrop']))
    h,w=old.shape[:2];band=min(32,h//4,w//4);alpha=np.full((h,w),255,np.uint8);paths={}
    for edge in ['top','bottom','left','right']:
        if edge=='left' and x0==0: continue
        if edge in ['top','bottom']:
            a=old[:band] if edge=='top' else old[-band:];b=new[:band] if edge=='top' else new[-band:];s=mod.minimum_vertical_seam(a.transpose(1,0,2),b.transpose(1,0,2));vals=np.arange(band)[:,None];mask=np.where(vals>=s[None,:],255,0) if edge=='top' else np.where(vals<s[None,:],255,0)
            if edge=='top':alpha[:band]=np.minimum(alpha[:band],mask)
            else:alpha[-band:]=np.minimum(alpha[-band:],mask)
        else:
            a=old[:,:band] if edge=='left' else old[:,-band:];b=new[:,:band] if edge=='left' else new[:,-band:];s=mod.minimum_vertical_seam(a,b);vals=np.arange(band)[None,:];mask=np.where(vals>=s[:,None],255,0) if edge=='left' else np.where(vals<s[:,None],255,0)
            if edge=='left':alpha[:,:band]=np.minimum(alpha[:,:band],mask)
            else:alpha[:,-band:]=np.minimum(alpha[:,-band:],mask)
        paths[edge]=s
    alpha=np.array(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1)));alpha[0]=0;alpha[-1]=0;alpha[:,-1]=0
    if x0>0:alpha[:,0]=0
    result[y0:y1,x0:x1]=((old.astype(np.uint32)*(255-alpha[:,:,None])+new.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
    png(d/'alpha.png',Image.fromarray(alpha))
    with (d/'seam-paths.npz').open('xb') as f:np.savez_compressed(f,**paths)
    p=d/'candidate-4096.png';png(p,Image.fromarray(result));context=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));context[115:4211,115:4211]=result;cp=d/'context-4326.png';png(cp,Image.fromarray(context))
    out=dict(schemaVersion=1,version=version,composedAt=now(),sourceCandidate=m['sourceCandidate'],sourceContext=m['sourceContext'],immutableWest=m['immutableWest'],native=g['native'],generation=art(d/'generation.json'),preparation=art(d/'preparation.json'),nativeSourceCrop=m['nativeSourceCrop'],pasteBoxIn4096=m['pasteBoxIn4096'],alpha=art(d/'alpha.png'),seamPaths=art(d/'seam-paths.npz'),algorithm=art(algorithm),compositor=art(__file__),candidate=art(p),context=art(cp),operation='Exact native crop; minimum-error paths in 32px perimeter bands; Gaussian radius1 alpha; uint32 rounded blending. No resampling, warping or transform.',resized=False,formalAccepted=False,status='independent_candidate_pending_local_visual_QA')
    write(d/'composition.json',out);replay(version)
    target=Image.open(m['target']['path']).convert('RGB');target.paste(Image.fromarray(result).crop(m['pasteBoxIn4096']),tuple(m['nativeSourceCrop'][:2]));png(d/'review-composed-1254.png',target)
    return out

def replay(version):
    d=T/'repairs'/version;m=read(d/'composition.json');prep=read(d/'preparation.json')
    for k in ['sourceCandidate','sourceContext','immutableWest','native','generation','preparation','alpha','seamPaths','candidate','context']: checked(m[k])
    target=Image.new('RGB',(1254,1254))
    for s in prep['sourcePixelAssembly']:
        checked(s['source']);target.paste(Image.open(s['source']['path']).convert('RGB').crop(s['crop']),tuple(s['paste']))
    assert np.array_equal(np.array(target),np.array(Image.open(prep['target']['path']).convert('RGB')))
    result=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));x0,y0,x1,y1=m['pasteBoxIn4096'];old=result[y0:y1,x0:x1].copy();new=np.array(Image.open(m['native']['path']).convert('RGB').crop(m['nativeSourceCrop']));a=np.array(Image.open(m['alpha']['path']))[:,:,None];result[y0:y1,x0:x1]=((old.astype(np.uint32)*(255-a)+new.astype(np.uint32)*a+127)//255).astype(np.uint8)
    assert np.array_equal(result,np.array(Image.open(m['candidate']['path']).convert('RGB')))
    ctx=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));ctx[115:4211,115:4211]=result;assert np.array_equal(ctx,np.array(Image.open(m['context']['path']).convert('RGB')))
    record=dict(replayedAt=now(),candidateSha256=m['candidate']['sha256'],contextSha256=m['context']['sha256'],exactPixels=True,nativeSize=[1254,1254],neighborCoreUnchanged=True,formalAccepted=False)
    if not (d/'replay.json').exists():write(d/'replay.json',record)
    return record

if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
    q=s.add_parser('prepare');q.add_argument('label');q.add_argument('box');q.add_argument('paste');q.add_argument('instruction');q.add_argument('--previous')
    q=s.add_parser('ingest');q.add_argument('version');q.add_argument('source');q.add_argument('receipt')
    for n in ['compose','replay']:q=s.add_parser(n);q.add_argument('version')
    args=vars(p.parse_args());cmd=args.pop('cmd');print(json.dumps(globals()[cmd](**args),ensure_ascii=False,indent=2))
