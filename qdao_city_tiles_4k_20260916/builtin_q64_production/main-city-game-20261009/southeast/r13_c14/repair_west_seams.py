"""Immutable1254 built-in repair evidence and replay for r13_c14 west seam only.

Never generates images, writes neighboring tiles, changes progress, or accepts art.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, re, shutil, sys, uuid
import numpy as np
from PIL import Image, ImageFilter

sys.dont_write_bytecode = True
T = Path(__file__).resolve().parent
Z = T.parent
WEST = Z / 'r13_c13/candidate/r13_c13-4k-candidate-repaired.png'
WEST_SHA = 'db5f956694c700b16094eb532ad9097e8a54f4a19d14797325f6fbd0ca18971f'
CONTRACT = Z.parent / 'production-contract.json'
CONFIG = Z.parents[3] / 'config/image-generation.json'

def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok, msg):
    if not ok: raise ValueError(msg)
def js(p, data):
    with Path(p).open('x', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
def png(p, im):
    with Path(p).open('xb') as f: im.save(f, format='PNG')
def artifact(p):
    with Image.open(p) as im: size=list(im.size)
    return {'path':str(Path(p).resolve()),'sha256':sha(p),'size':size}
def checked(p, digest):
    need(sha(p)==digest, f'Source changed: {p}')
def current():
    if (T/'repairs/latest-repair.json').exists():
        m=read(T/'repairs/latest-repair.json')
        return m['candidate'], m['context']
    m=read(T/'candidate/latest-assembly.json')
    return m['candidate'],m['context']

def prepare(label, y, instruction):
    need(re.fullmatch('[a-z][a-z0-9-]*',label), 'Invalid repair label')
    need(0<=y<=2842, '1254 crop must stay within formal4096 core vertically')
    contract=read(CONTRACT); resume=read(contract['productionResumeControl'])
    need(contract.get('newArtworkGenerationAllowed') is True and resume.get('newArtworkGenerationAllowed') is True, 'Production gate not released')
    checked(WEST,WEST_SHA)
    base,context=current(); checked(base['path'],base['sha256']);checked(context['path'],context['sha256'])
    need(Path(base['path']).resolve().is_relative_to(T), 'Base candidate must belong to r13_c14')
    refs=[]
    for key,hkey,role in [('layoutReference','layoutSha256','whole-city approved geometry reference only'),('detailStyleReference','detailSha256','approved close-up material style only'),('primaryStyleReference','primaryStyleSha256','approved illustration style only')]:
        checked(contract[key],contract[hkey]); refs.append({**artifact(contract[key]),'role':role})
    version='west-'+label+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]
    d=T/'repairs'/version;d.mkdir(parents=True,exist_ok=False)
    target=Image.new('RGB',(1254,1254))
    with Image.open(WEST) as im: target.paste(im.convert('RGB').crop((3471,y,4096,y+1254)),(0,0))
    with Image.open(base['path']) as im: target.paste(im.convert('RGB').crop((0,y,629,y+1254)),(625,0))
    target_path=d/'target-core-only-1254.png';png(target_path,target)
    target_evidence={**artifact(target_path),'role':'LAST IMAGE, sole edit target:625px unchanged west formal core +629px current east formal core; no halo/no resize'}
    prompt=f'''Use case: precise-object-edit.
Asset: one opaque native1254x1254 game-map repair, tightly cropped partial objects, same camera and framing.
Inputs1/2/3 are style/layout references ONLY. Input4 THE LAST IMAGE is the ONLY EDIT TARGET. Do not recreate a reference scene, zoom out, recenter, fit a complete object, or change the crop.
The LAST target is an exact unscaled composite of neighboring formal game tiles. Its LEFT625 columns x0..624 are approved immutable artwork. Its RIGHT629 columns x625..1253 are the current adjacent tile and need local continuity correction. The dividing vertical line x625 is a TILE BOUNDARY, not an object edge. No unreliable halo is present.
PRIMARY CHANGE: {instruction}
Preserve the entire LEFT625 columns pixel-aligned and unchanged. Let their complete object geometry dictate continuation to the RIGHT. Repair only the necessary right-side geometry/material; preserve the existing rightmost96 columns and top/bottom80 rows wherever compatible, so this crop rejoins the surrounding existing east artwork. Do not preserve a visible seam simply because it occurs at x625.
Preserve original handmade geometry. Do not refit circles, straighten existing curves, move bamboo spokes, or beautify the left side. Existing LEFT endpoints are the authority even when a right-side curve must change its curvature to match them. Only repaint the necessary right-side region. No duplicated rim or detached fragments.
For stone/wood: continue existing grout, board edges, shadow and material value across x625 without restarting a grid or inventing a border. Keep connected original structures, no new objects.
Style: existing clean bright rounded Taoist chibi hand-painted game artwork, natural stone and warm wood, soft daylight. Retain local reference finish, restrained texture and current material scale. No characters, UI, labels, watermarks, frames, diagram marks, new buildings or props.
Output exactly one1254x1254 opaque native image. This is a giant detail crop of artwork, not world-scale or capacity evidence. Core repair box in east-tile coordinates [-625,{y},629,{y+1254}].'''
    if label.endswith('-precise'):
        prompt=f'''Edit only the LAST image, at its existing native1254x1254 resolution and exact framing. The first3 images are style references only.
{instruction}
The LEFT625 columns are immutable neighbor context, not an editable area. All pixels outside the described small RIGHT-side patch must remain at the same coordinates and appearance. Copy those pixels, do not regenerate, regularize, or improve them. Output the same1254x1254 crop. No new objects, no text, no scaling.'''
    pp=d/'prompt.txt'
    with pp.open('x',encoding='utf-8') as f:f.write(prompt)
    request={'prompt':prompt,'referenced_image_paths':[r['path'] for r in refs]+[str(target_path)],'transparent_background':False}
    js(d/'request.json',request)
    meta={'schemaVersion':1,'version':version,'preparedAt':now(),'tile':'r13_c14','tool':'image_gen.imagegen','route':'builtin','sourceCandidate':base,'sourceContext':context,'immutableWest':artifact(WEST),'sourcePixelAssembly':[{'path':str(WEST),'sha256':WEST_SHA,'sourceCrop':[3471,y,4096,y+1254],'targetBox':[0,0,625,1254]},{'path':base['path'],'sha256':base['sha256'],'sourceCrop':[0,y,629,y+1254],'targetBox':[625,0,1254,1254]}],'target':target_evidence,'references':refs+[target_evidence],'repairBoxIn4096':[-625,y,629,y+1254],'pasteBoxIn4096':[0,y,629,y+1254],'instruction':instruction,'prompt':str(pp),'promptSha256':sha(pp),'request':str(d/'request.json'),'requestSha256':sha(d/'request.json'),'configSnapshot':read(CONFIG),'contractSnapshot':contract,'contractSha256':sha(CONTRACT),'actualModel':None,'actualQuality':None,'resized':False,'status':'prepared_not_generated','formalAccepted':False}
    js(d/'preparation.json',meta)
    return {'version':version,'target':str(target_path),'request':str(d/'request.json')}

def ingest(version, source, receipt):
    d=T/'repairs'/version; m=read(d/'preparation.json');src=Path(source).resolve();rc=Path(receipt).resolve();r=read(rc)
    status=r.get('status','');need(status=='succeeded' or re.fullmatch(r'succeeded_pending_[a-z0-9_]+',status), 'Truthful success receipt required')
    need(not any(w in status for w in ['failed','rejected','error','cancel']), 'Failed receipt')
    for key in ['actualModel','actualQuality']:need(key in r,'Receipt must explicitly record unknown actual model/quality as null')
    checked(m['request'],m['requestSha256']);checked(m['prompt'],m['promptSha256'])
    for ref in m['references']:checked(ref['path'],ref['sha256'])
    with Image.open(src) as im:
        need(im.format=='PNG' and im.size==(1254,1254), 'Actual native1254 PNG required; no resize permitted');im.load()
        need(im.mode in ['RGB','RGBA'],'Unsupported output mode')
        if im.mode=='RGBA':need(im.getextrema()[3]==(255,255),'Output must be opaque')
    output=d/'native.png'; saved=d/'receipt.json'
    need(not output.exists() and not (d/'generation.json').exists(),'Immutable native version already exists')
    if rc!=saved.resolve():
        with rc.open('rb') as f,saved.open('xb') as g:shutil.copyfileobj(f,g)
    with src.open('rb') as f,output.open('xb') as g:shutil.copyfileobj(f,g)
    need(sha(output)==sha(src),'Byte copy mismatch')
    js(d/'generation.json',{'version':version,'ingestedAt':now(),'tool':'image_gen.imagegen','route':'builtin','native':artifact(output),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'receipt':str(saved),'receiptSha256':sha(saved),'preparation':str(d/'preparation.json'),'preparationSha256':sha(d/'preparation.json'),'promptSha256':m['promptSha256'],'requestSha256':m['requestSha256'],'references':m['references'],'configSnapshot':m['configSnapshot'],'actualModel':r['actualModel'],'actualQuality':r['actualQuality'],'backendModelVerified':False,'unverifiedReason':'Builtin route has no exposed model/quality selectors; configuration target is not actual backend evidence.','resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'native_pending_visual_review','formalAccepted':False})
    return artifact(output)

def algorithm():
    p=Z/'assemble_candidate.py';spec=importlib.util.spec_from_file_location('seam_algorithm_readonly',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module,artifact_script(p)
def artifact_script(p):return {'path':str(p),'sha256':sha(p)}

def compose(version):
    d=T/'repairs'/version;m=read(d/'preparation.json');g=read(d/'generation.json');checked(g['native']['path'],g['native']['sha256']);checked(g['receipt'],g['receiptSha256']);checked(d/'preparation.json',g['preparationSha256'])
    if (d/'visual-review.json').exists():
        need(read(d/'visual-review.json').get('status')!='rejected','Visually rejected repair cannot be composed')
    for item in [m['sourceCandidate'],m['sourceContext'],m['immutableWest']]:checked(item['path'],item['sha256'])
    base=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));generated=np.array(Image.open(g['native']['path']).convert('RGB'))[:,625:1254]
    y=m['pasteBoxIn4096'][1]; old=base[y:y+1254,:629].copy()
    module,algo=algorithm();band=64;h,w=old.shape[:2];alpha=np.ones((h,w),np.uint8)*255
    top=module.minimum_vertical_seam(old[:band].transpose(1,0,2),generated[:band].transpose(1,0,2))
    bottom=module.minimum_vertical_seam(old[-band:].transpose(1,0,2),generated[-band:].transpose(1,0,2))
    right=module.minimum_vertical_seam(old[:,-band:],generated[:,-band:])
    alpha[:band]=np.where(np.arange(band)[:,None]>=top[None,:],255,0)
    alpha[-band:]=np.minimum(alpha[-band:],np.where(np.arange(band)[:,None]<bottom[None,:],255,0).astype(np.uint8))
    alpha[:,-band:]=np.minimum(alpha[:,-band:],np.where(np.arange(band)[None,:]<right[:,None],255,0).astype(np.uint8))
    alpha=np.array(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(2)))
    alpha[:2]=0;alpha[-2:]=0;alpha[:,-2:]=0
    blend=((old.astype(np.uint32)*(255-alpha[:,:,None])+generated.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
    result=base.copy();result[y:y+1254,:629]=blend
    need(np.array_equal(result[:,629:],base[:,629:]),'Pixels outside east repair changed')
    p=T/'candidate'/f'r13_c14-4k-repaired-{version}.png';png(p,Image.fromarray(result))
    context=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));need(context.shape==(4326,4326,3),'Context must be4326');context[115:4211,115:4211]=result
    cp=T/'candidate'/f'r13_c14-context-repaired-{version}.png';png(cp,Image.fromarray(context));png(d/'alpha-east-only.png',Image.fromarray(alpha))
    with (d/'seam-paths.npz').open('xb') as f:np.savez_compressed(f,top=top,bottom=bottom,right=right)
    manifest={'schemaVersion':1,'version':version,'composedAt':now(),'tile':'r13_c14','sourceCandidate':m['sourceCandidate'],'sourceContext':m['sourceContext'],'immutableWest':m['immutableWest'],'native':g['native'],'nativeGenerationRecord':artifact_script(d/'generation.json'),'preparation':artifact_script(d/'preparation.json'),'candidate':artifact(p),'context':artifact(cp),'operation':'Select native output columns625:1254 only; top,bottom,right minimum-error seams within64px border and Gaussian2px feather; integer uint32 rounded alpha blend. Never paste into west tile.','pasteBoxIn4096':m['pasteBoxIn4096'],'nativeSourceCrop':[625,0,1254,1254],'alpha':artifact(d/'alpha-east-only.png'),'seamPaths':artifact_script(d/'seam-paths.npz'),'seamAlgorithm':algo,'sourcePixelAssembly':m['sourcePixelAssembly'],'contextOperation':'Paste corrected formal4096 at [115,115,4211,4211] in prior4326; outer halo unchanged and remains QA pending.','resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'repaired_candidate_pending_visual_QA','formalAccepted':False}
    js(d/'composition.json',manifest)
    replay(version)
    pointer=T/'repairs/latest-repair.json'; temp=T/'repairs'/('latest-repair-'+uuid.uuid4().hex+'.tmp');js(temp,manifest);temp.replace(pointer)
    return {'candidate':manifest['candidate'],'context':manifest['context'],'manifest':str(d/'composition.json')}

def replay(version):
    d=T/'repairs'/version;m=read(d/'composition.json');prep=read(d/'preparation.json')
    for item in [m['sourceCandidate'],m['sourceContext'],m['immutableWest'],m['native'],m['alpha'],m['preparation'],m['nativeGenerationRecord']]:checked(item['path'],item['sha256'])
    target=Image.new('RGB',(1254,1254))
    for source in m['sourcePixelAssembly']:
        checked(source['path'],source['sha256'])
        with Image.open(source['path']) as im:target.paste(im.convert('RGB').crop(source['sourceCrop']),tuple(source['targetBox'][:2]))
    need(np.array_equal(np.array(target),np.array(Image.open(prep['target']['path']).convert('RGB'))),'Target pixel replay failed')
    result=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));patch=np.array(Image.open(m['native']['path']).convert('RGB'))[:,625:1254];alpha=np.array(Image.open(m['alpha']['path']));y=m['pasteBoxIn4096'][1];old=result[y:y+1254,:629].copy()
    result[y:y+1254,:629]=((old.astype(np.uint32)*(255-alpha[:,:,None])+patch.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
    need(np.array_equal(result,np.array(Image.open(m['candidate']['path']).convert('RGB'))),'Candidate replay failed');checked(m['candidate']['path'],m['candidate']['sha256'])
    context=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));context[115:4211,115:4211]=result
    need(np.array_equal(context,np.array(Image.open(m['context']['path']).convert('RGB'))),'Context replay failed');checked(m['context']['path'],m['context']['sha256']);checked(WEST,WEST_SHA)
    return {'replayed':True,'westUnchanged':True,'candidateSha256':m['candidate']['sha256']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True)
    q=s.add_parser('prepare');q.add_argument('label');q.add_argument('y',type=int);q.add_argument('instruction')
    q=s.add_parser('ingest');q.add_argument('version');q.add_argument('source');q.add_argument('receipt')
    for name in ['compose','replay']:q=s.add_parser(name);q.add_argument('version')
    a=vars(p.parse_args());cmd=a.pop('cmd');print(json.dumps(globals()[cmd](**a),ensure_ascii=False,indent=2))
