"""Prepare native-size inpaint guides and replay east-only local composites.

The magenta hole is a generation guide, never a deliverable source. No resampling.
"""
import sys
sys.dont_write_bytecode = True
from repair_west_seams import *
from PIL import ImageDraw

def prepare_mask(label, y, hole, crop, instruction):
    hole=[int(v) for v in hole.split(',')];crop=[int(v) for v in crop.split(',')]
    need(hole[0]<=625 and crop[0]>=625 and all(0<=v<=1254 for v in hole+crop),'Invalid guide or native crop')
    original=prepare(label,y,instruction)
    od=T/'repairs'/original['version'];m=read(od/'preparation.json')
    version=original['version']+'-masked';d=T/'repairs'/version;d.mkdir(exist_ok=False)
    raw=Image.open(m['target']['path']).convert('RGB');png(d/'source-core-only-1254.png',raw)
    guide=raw.copy();ImageDraw.Draw(guide).rectangle((hole[0],hole[1],hole[2]-1,hole[3]-1),fill=(255,0,255));png(d/'target-inpaint-guide-1254.png',guide)
    prompt=f'''Edit the LAST image only. Fill the solid magenta rectangular hole with seamless continuation of the surrounding original artwork. Magenta means missing pixels, not a painted object. Leave every visible non-magenta object at exactly its current position. Output the same opaque native1254x1254 crop, no zoom, no scaling, no new objects or text.
{instruction}
The hole must join all existing contours where they enter its four sides. Treat the visible LEFT endpoints as fixed; do not move them or regularize the overall object. Paint only the missing fragment. Match neighboring color, texture and light. The first3 images are reference style only. This is a cropped fragment, not a complete scene.'''
    cy=1696 if y>2000 else 0
    object_context=Image.new('RGB',(4296,2400));object_context.paste(Image.open(WEST).convert('RGB').crop((1000,cy,4096,cy+2400)),(0,0));object_context.paste(Image.open(m['sourceCandidate']['path']).convert('RGB').crop((0,cy,1200,cy+2400)),(3096,0));png(d/'full-object-core-context-unscaled.png',object_context)
    prompt=prompt.replace('The first3 images are reference style only.','The first3 images are reference style only. The penultimate image is the unscaled whole-object context for understanding existing geometry; never change its framing into the small target.')
    (d/'prompt.txt').write_text(prompt,encoding='utf8')
    refs=m['references'][:3]+[{**artifact(d/'full-object-core-context-unscaled.png'),'role':'Unscaled full-object core context only','sourcePixelAssembly':[{'source':m['immutableWest'],'crop':[1000,cy,4096,cy+2400],'paste':[0,0]},{'source':m['sourceCandidate'],'crop':[0,cy,1200,cy+2400],'paste':[3096,0]}]}]+[{**artifact(d/'target-inpaint-guide-1254.png'),'role':'LAST IMAGE: native-size inpaint guide; magenta is a temporary hole only'}]
    request={'prompt':prompt,'referenced_image_paths':[r['path'] for r in refs],'transparent_background':False};js(d/'request.json',request)
    m.update(version=version,preparedAt=now(),target={**artifact(d/'source-core-only-1254.png'),'role':'Exact source pixel assembly before guide hole'},references=refs,prompt=str(d/'prompt.txt'),promptSha256=sha(d/'prompt.txt'),request=str(d/'request.json'),requestSha256=sha(d/'request.json'),guideHole=hole,guideFillRGB=[255,0,255],nativeSourceCrop=crop,pasteBoxIn4096=[crop[0]-625,y+crop[1],crop[2]-625,y+crop[3]],preparationMethod='Exact unscaled core composite plus documented solid-color temporary inpaint guide. Only native generated art is composited.',unusedUnmaskedPreparation=str(od/'preparation.json'))
    js(d/'preparation.json',m)
    return {'version':version,'request':str(d/'request.json'),'target':str(d/'target-inpaint-guide-1254.png')}

def prepare_component(label,y,instruction):
    original=prepare(label,y,instruction);od=T/'repairs'/original['version'];m=read(od/'preparation.json');version=original['version']+'-component';d=T/'repairs'/version;d.mkdir(exist_ok=False)
    left=150;raw=Image.new('RGB',(1254,1254));raw.paste(Image.open(WEST).convert('RGB').crop((4096-left,y,4096,y+1254)),(0,0));raw.paste(Image.open(m['sourceCandidate']['path']).convert('RGB').crop((0,y,1254-left,y+1254)),(left,0));png(d/'target-complete-east-component-1254.png',raw)
    full=Image.new('RGB',(4296,2400));full.paste(Image.open(WEST).convert('RGB').crop((1000,0,4096,2400)),(0,0));full.paste(Image.open(m['sourceCandidate']['path']).convert('RGB').crop((0,0,1200,2400)),(3096,0));png(d/'full-object-core-context-unscaled.png',full)
    prompt=f'''Edit the LAST image only, native1254x1254 same crop. First3 are style references. Penultimate image is unscaled complete-object context. The LAST image contains the complete right-hand umbrella sector and its surrounding wood/stone, at actual resolution. LEFT150 columns are fixed neighboring artwork. RIGHT1104 columns are editable new-tile artwork.
{instruction}
Keep every visible contour entering from the LEFT150 columns fixed in position, color, thickness, and tangent. Continue those actual contours through the entire RIGHT sector, which may be repainted as needed. The old right red/cream stripe path is incorrect: replace its complete path; do not preserve the old right stripe endpoint just to make a small patch. Preserve the outer umbrella footprint, pole location, nearby wall and deck layout. Do not redesign or regularize the fixed left half of the umbrella. Keep its handmade slight irregularity. No new spokes or props, no zoom, no complete-scene redraw, no text. Keep top/bottom/rightmost60px of background aligned. Return one opaque1254x1254 image.'''
    (d/'prompt.txt').write_text(prompt,encoding='utf8');refs=m['references'][:3]+[{**artifact(d/'full-object-core-context-unscaled.png'),'role':'Unscaled complete parasol context'}]+[{**artifact(d/'target-complete-east-component-1254.png'),'role':'LAST sole edit target; native unscaled left150 fixed and right1104 editable'}];request={'prompt':prompt,'referenced_image_paths':[x['path'] for x in refs],'transparent_background':False};js(d/'request.json',request)
    assembly=[{'path':str(WEST),'sha256':WEST_SHA,'sourceCrop':[4096-left,y,4096,y+1254],'targetBox':[0,0,left,1254]},{'path':m['sourceCandidate']['path'],'sha256':m['sourceCandidate']['sha256'],'sourceCrop':[0,y,1254-left,y+1254],'targetBox':[left,0,1254,1254]}]
    m.update(version=version,preparedAt=now(),target=artifact(d/'target-complete-east-component-1254.png'),references=refs,prompt=str(d/'prompt.txt'),promptSha256=sha(d/'prompt.txt'),request=str(d/'request.json'),requestSha256=sha(d/'request.json'),sourcePixelAssembly=assembly,guideHole=None,nativeSourceCrop=[left,0,1254,1254],repairBoxIn4096=[-left,y,1254-left,y+1254],pasteBoxIn4096=[0,y,1254-left,y+1254],seamBand=64,preparationMethod='Whole new-tile object component with fixed150px west native core and complete-object unscaled reference; no halo',unusedUnmaskedPreparation=str(od/'preparation.json'))
    js(d/'preparation.json',m);return {'version':version,'request':str(d/'request.json'),'target':m['target']['path']}

def compose_mask(version):
    d=T/'repairs'/version;m=read(d/'preparation.json');g=read(d/'generation.json')
    need(not (d/'visual-review.json').exists() or read(d/'visual-review.json').get('status')!='rejected','Rejected source')
    for item in [m['sourceCandidate'],m['sourceContext'],m['immutableWest'],g['native']]:checked(item['path'],item['sha256'])
    checked(g['receipt'],g['receiptSha256']);checked(d/'preparation.json',g['preparationSha256'])
    base=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));x0,y0,x1,y1=m['pasteBoxIn4096'];gen=np.array(Image.open(g['native']['path']).convert('RGB').crop(m['nativeSourceCrop']));old=base[y0:y1,x0:x1].copy()
    h,w=old.shape[:2];band=min(m.get('seamBand',20),h//4,w//4);module,algo=algorithm();alpha=np.full((h,w),255,np.uint8)
    top=module.minimum_vertical_seam(old[:band].transpose(1,0,2),gen[:band].transpose(1,0,2));bottom=module.minimum_vertical_seam(old[-band:].transpose(1,0,2),gen[-band:].transpose(1,0,2));right=module.minimum_vertical_seam(old[:,-band:],gen[:,-band:])
    alpha[:band]=np.where(np.arange(band)[:,None]>=top[None,:],255,0);alpha[-band:]=np.minimum(alpha[-band:],np.where(np.arange(band)[:,None]<bottom[None,:],255,0).astype(np.uint8));alpha[:,-band:]=np.minimum(alpha[:,-band:],np.where(np.arange(band)[None,:]<right[:,None],255,0).astype(np.uint8))
    alpha=np.array(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1)));alpha[:1]=0;alpha[-1:]=0;alpha[:,-1:]=0
    result=base.copy();result[y0:y1,x0:x1]=((old.astype(np.uint32)*(255-alpha[:,:,None])+gen.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
    png(d/'alpha-east-only.png',Image.fromarray(alpha))
    with (d/'seam-paths.npz').open('xb') as f:np.savez_compressed(f,top=top,bottom=bottom,right=right)
    p=T/'candidate'/f'r13_c14-4k-repaired-{version}.png';png(p,Image.fromarray(result));context=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));context[115:4211,115:4211]=result;cp=T/'candidate'/f'r13_c14-context-repaired-{version}.png';png(cp,Image.fromarray(context))
    out={'schemaVersion':2,'version':version,'composedAt':now(),'tile':'r13_c14','sourceCandidate':m['sourceCandidate'],'sourceContext':m['sourceContext'],'immutableWest':m['immutableWest'],'native':g['native'],'nativeGenerationRecord':artifact_script(d/'generation.json'),'preparation':artifact_script(d/'preparation.json'),'candidate':artifact(p),'context':artifact(cp),'nativeSourceCrop':m['nativeSourceCrop'],'pasteBoxIn4096':m['pasteBoxIn4096'],'alpha':artifact(d/'alpha-east-only.png'),'seamPaths':artifact_script(d/'seam-paths.npz'),'seamAlgorithm':algo,'compositor':artifact_script(Path(__file__)),'sourcePixelAssembly':m['sourcePixelAssembly'],'operation':'Unscaled native rectangular crop, east only. Minimum-error paths in20px top/bottom/right context; Gaussian1px feather; uint32 rounded alpha. Outer pixels unchanged.','resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'repaired_candidate_pending_visual_QA','formalAccepted':False}
    js(d/'composition.json',out);replay_mask(version)
    preview=Image.open(m['target']['path']).convert('RGB');left=-m['repairBoxIn4096'][0];preview.paste(Image.fromarray(result).crop((0,m['repairBoxIn4096'][1],1254-left,m['repairBoxIn4096'][3])),(left,0));png(d/'review-composed-original-west.png',preview)
    return out['candidate']

def replay_mask(version):
    d=T/'repairs'/version;m=read(d/'composition.json');p=read(d/'preparation.json')
    for k in ['sourceCandidate','sourceContext','immutableWest','native','nativeGenerationRecord','preparation','alpha','seamPaths','candidate','context']:checked(m[k]['path'],m[k]['sha256'])
    raw=Image.new('RGB',(1254,1254))
    for s in m['sourcePixelAssembly']:
        checked(s['path'],s['sha256']);raw.paste(Image.open(s['path']).convert('RGB').crop(s['sourceCrop']),tuple(s['targetBox'][:2]))
    need(np.array_equal(np.array(raw),np.array(Image.open(p['target']['path']).convert('RGB'))),'Target replay failed')
    guide=raw.copy();h=p['guideHole']
    if h:ImageDraw.Draw(guide).rectangle((h[0],h[1],h[2]-1,h[3]-1),fill=tuple(p['guideFillRGB']))
    if p.get('guidePolygon'):ImageDraw.Draw(guide).polygon([tuple(v) for v in p['guidePolygon']],fill=tuple(p['guideFillRGB']))
    need(np.array_equal(np.array(guide),np.array(Image.open(p['references'][-1]['path']).convert('RGB'))),'Guide replay failed')
    result=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));x0,y0,x1,y1=m['pasteBoxIn4096'];old=result[y0:y1,x0:x1].copy();gen=np.array(Image.open(m['native']['path']).convert('RGB').crop(m['nativeSourceCrop']));a=np.array(Image.open(m['alpha']['path']))[:,:,None];result[y0:y1,x0:x1]=((old.astype(np.uint32)*(255-a)+gen.astype(np.uint32)*a+127)//255).astype(np.uint8)
    need(np.array_equal(result,np.array(Image.open(m['candidate']['path']).convert('RGB'))),'Candidate replay failed');ctx=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));ctx[115:4211,115:4211]=result;need(np.array_equal(ctx,np.array(Image.open(m['context']['path']).convert('RGB'))),'Context replay failed');checked(WEST,WEST_SHA)
    return {'replayed':True,'candidateSha256':m['candidate']['sha256'],'westUnchanged':True}

def retain(version):
    d=T/'repairs'/version;v=read(d/'visual-review.json');need(v.get('status')=='local_pass','Explicit local visual pass required');replay_mask(version);m=read(d/'composition.json');tmp=T/'repairs'/('latest-repair-'+uuid.uuid4().hex+'.tmp');js(tmp,m);tmp.replace(T/'repairs/latest-repair.json');return m['candidate']

if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True);q=s.add_parser('prepare_mask');q.add_argument('label');q.add_argument('y',type=int);q.add_argument('hole');q.add_argument('crop');q.add_argument('instruction')
    q=s.add_parser('ingest');q.add_argument('version');q.add_argument('source');q.add_argument('receipt')
    q=s.add_parser('prepare_component');q.add_argument('label');q.add_argument('y',type=int);q.add_argument('instruction')
    for n in ['compose_mask','replay_mask','retain']:q=s.add_parser(n);q.add_argument('version')
    a=vars(p.parse_args());cmd=a.pop('cmd');print(json.dumps(globals()[cmd](**a),ensure_ascii=False,indent=2))
