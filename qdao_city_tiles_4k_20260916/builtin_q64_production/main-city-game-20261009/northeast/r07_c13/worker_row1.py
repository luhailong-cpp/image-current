"""First-row request and worker-local progress only; native ingestion uses tile_worker."""
from pathlib import Path
import json,argparse,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ZONE=HERE.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=argparse.ArgumentParser();p.add_argument('mode',choices=['request','progress']);p.add_argument('patch');p.add_argument('note',nargs='?',default='');a=p.parse_args()
assert a.patch in ['p11','p12','p13','p14'],'Exclusive first-row ownership only'
if a.mode=='request':
    context=HERE/'layout-only'/f'{a.patch}-mixed-context.png';meta=read(str(context)+'.generation.json');assert sha(context)==meta['sha256']
    for s in meta['derivedFrom']:assert sha(s['file'])==s['sha256']
    north=any(s.get('role')=='actual north native context' for s in meta['derivedFrom']);west=any(s.get('role')=='actual west native context' for s in meta['derivedFrom']);assert north and (a.patch=='p11' or west)
    bands='TOP230 and LEFT230' if west else 'TOP230 only; there is no native west neighbor'
    preserved='topmost115 pixels and leftmost115 pixels' if west else 'topmost115 pixels; repaint the blurry left edge below the top strip'
    prompt=f'''Use case: precise-object-edit. Create the exact native1254x1254 opaque map crop r07_c13/{a.patch}.
Image1 is the mixed edit target: crisp {bands} come from recorded real neighbor pixels, with repaired north candidate core authoritative. All remaining blurry pixels are only low-resolution geometry guidance to freshly paint. Images2/3/4 show approved full city geography, near-view material/daylight and Daoist Mail illustration style; they are not output framing.
{a.note}
Preserve {preserved} precisely. Continue the existing object contours through x115..300 and y115..300 naturally. Do not introduce a hard stripe edge at x230/y230 or a rectangular cutout at their intersection. Do not double or duplicate an inherited beam, eave, ridge, door, lantern, or decorative object. Honor the image1 perspective, scale, framing and exact object placement.
Render all layout-only areas into crisp real native detail: polished rounded Daoist Q illustration, restrained broad painted highlights, clean coherent construction, natural pale grey or blue-grey stone, blue-teal ceramic roof where already indicated, warm red wood and gold only where inherited. Soft upper-left daylight. Keep1254x1254 and same framing. No zoom, resize, crop, stretch, camera change, new props, blur, bokeh, smear, sharpening filter, text, UI, grid, frame, watermark or transparency. The result must be fully painted with no remaining layout blur.'''
    contract=read(ZONE.parent/'production-contract.json');refs=[str(context),contract['layoutReference'],contract['detailStyleReference'],contract['primaryStyleReference']]
    dest=HERE/'prompts'/f'{a.patch}.request.json';txt=HERE/'prompts'/f'{a.patch}.prompt.txt';assert not dest.exists() and not txt.exists()
    txt.write_text(prompt,encoding='utf-8');save(dest,{'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'referenceRoles':['exact mixed native/candidate neighbor context plus layout to paint','approved full city geography','approved material/daylight detail','primary Daoist Mail illustration style']});print(dest)
else:
    path=HERE/'worker-row1.json';state=read(path) if path.exists() else {'tile':'r07_c13','ownedPatches':['p11','p12','p13','p14'],'completed':[],'formalAcceptedCount':0,'actualModel':None,'actualQuality':None}
    native=HERE/'native'/f'{a.patch}.png'
    if native.exists() and not any(v['patch']==a.patch for v in state['completed']):
        rec=read(str(native)+'.generation.json');assert rec['nativeSize']==[1254,1254] and sha(native)==rec['sha256'];state['completed'].append({'patch':a.patch,'file':str(native),'sha256':sha(native),'nativeSize':[1254,1254],'visualNote':a.note})
    state['updatedAt']=datetime.now(timezone.utc).isoformat();state['status']='row1-complete' if len(state['completed'])==4 else 'row1-native-generation';state['inflight']=None;save(path,state);print(json.dumps({'completed':[v['patch'] for v in state['completed']],'status':state['status']}))
