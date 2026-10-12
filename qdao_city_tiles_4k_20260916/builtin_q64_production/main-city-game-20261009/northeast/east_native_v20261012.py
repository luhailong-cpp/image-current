"""Versioned east-lane built-in evidence and selection; tile-local writes only."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib
Z=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 assert p.resolve().is_relative_to(T.resolve())
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['audit','request','receipt','select']);ap.add_argument('--tile',required=True);ap.add_argument('--patch');ap.add_argument('--note');ap.add_argument('--source');ap.add_argument('--hint',default='');a=ap.parse_args()
T=Z/a.tile
assert T.parent==Z and 1<=int(a.tile[1:3])<=8 and int(a.tile[5:7]) in (15,16) and a.tile!='r07_c15'
if a.mode=='audit':
 missing=[]
 for f in sorted((T/'receipts').glob('*.receipt.json')):
  d=read(f);src=d.get('sourceOutputPath');stem=f.name.removesuffix('.receipt.json')
  if src and Path(src).is_file() and not (T/'native'/(stem+'.png')).exists():missing.append({'version':stem,'source':src,'receipt':str(f)})
 print(json.dumps({'tile':a.tile,'successfulUnIngested':missing},ensure_ascii=False));raise SystemExit(0)
v=a.patch+'-v20261012';pf=T/'prompts'/(v+'.prompt.txt');rf=T/'prompts'/(v+'.request.json');rec=T/'receipts'/(v+'.receipt.json')
if a.mode=='request':
 assert not pf.exists() and not rf.exists() and not (T/'native'/(v+'.png')).exists()
 target=T/'layout-only'/(a.patch+'-mixed-context.png');meta=read(Path(str(target)+'.generation.json'));assert sha(target)==meta['sha256']
 for s in meta['derivedFrom']:assert sha(Path(s['file']))==s['sha256']
 c=read(Z.parent/'production-contract.json');refs=[str(target),c['layoutReference'],c['detailStyleReference'],c['primaryStyleReference']]
 directions=[s['role'].split()[1] for s in meta['derivedFrom'] if s['role'].startswith('actual ')];bounds={'west':'x0..230','east':'x1024..1254','north':'y0..230','south':'y1024..1254'};locked=', '.join(bounds[d]+' '+d for d in directions)
 prompt=f'''Use case: precise-object-edit. Edit Image1 at exactly1254x1254. Change ONLY the blurry unpainted area into crisp native artwork for northeast/{a.tile}/{a.patch}. Do not redraw the image or redesign its scene.
Image1 is the ONLY composition and edit target. LOCK ALL SHARP SOURCE STRIPS UNCHANGED: {locked}. They are actual finished neighboring pixels, not stylistic suggestions. Keep their exact pixel positions, camera angles, edge endpoints, perspective, objects and textures. Paint only blurry pixels, extending every incoming line smoothly with no step, gap or rotation. Do not move, expand or redraw any sharp strip. Blurry enlarged layout is only positional guidance and must become newly painted crisp native detail. Images2/3/4 are supporting approved overall Daoist town, material detail, and user Q Daoist style references only; never import their composition, props, UI, portraits or night lighting.
{a.note}
Lock the camera, geographic positions, scale, inherited silhouettes and material boundaries. Continue actual roof grooves, beam edges, leaves and masonry joint endpoints across the transition without doubling or inventing objects. Sharp strips at west x0..230, east x1024..1254, north y0..230, south y1024..1254, where present, are continuity constraints. They are not scene borders. The halo115 is actual scenery; central crop[115,115,1139,1139] will be used unchanged. No abrupt collage cut, step, doubled trim, smeared blending or flattened band. Bright soft upper-left daylight; crisp rounded hand-painted Q Daoist game detail, cyan/turquoise roofs, vermilion wood, gold trim, natural varied pale gray-blue stone. Maintain functional layout and walkable lanes. Keep only existing indicated festive details; red/gold architecture accents and sparse spent paper remnants, no overall red ground. No added isolated trees, pots, lanterns, characters, lettering, UI, watermark, grid or frame. No blur, enlargement, zoom, camera shift or transparency. Output exactly1254x1254 complete native square.'''
 pf.write_text(prompt,encoding='utf-8');save(rf,{'prompt':prompt,'referenced_image_paths':refs,'referenceRoles':['exact mixed-coordinate edit target with actual all-direction native neighbor continuity','approved overall daylight layout and style','approved close daylight material detail','user-approved Daoist Q style only'],'transparent_background':False,'canonicalPatch':a.patch,'versionedId':v})
 p=T/'tile-progress.json';d=read(p) if p.exists() else {};d.update(tile=a.tile,owner='/root/east_finish_20261012',updatedAt=now(),inflightRequests=[v],unsavedSuccessfulOutputs=[],status='native-generation',actualModel=None,actualQuality=None,formalAcceptedCount=0);save(p,d)
 print(json.dumps({'request':str(rf),'prompt':prompt,'referenced_image_paths':refs},ensure_ascii=False))
elif a.mode=='receipt':
 assert not rec.exists();assert Path(a.source).is_file()
 save(rec,{'tool':'image_gen','route':'builtin','returnedAt':now(),'sourceOutputPath':a.source,'output_hint':a.hint,'actualModel':None,'actualQuality':None,'prompt':str(pf),'request':str(rf),'canonicalPatch':a.patch,'versionedId':v})
elif a.mode=='select':
 image=T/'native'/(v+'.png');d=read(Path(str(image)+'.generation.json'));assert d['sha256']==sha(image) and d['nativeSize']==[1254,1254] and not d['resized'] and rec.exists()
 f=T/'selected-native.json';s=read(f) if f.exists() else {};assert a.patch not in s;s[a.patch]=image.name;save(f,s)
 f=T/'tile-progress.json';p=read(f) if f.exists() else {};p.update(tile=a.tile,owner='/root/east_finish_20261012',updatedAt=now(),selectedCoreCount=len(s),remainingCoreCount=16-len(s),generatedNativeCount=len(list((T/'native').glob('*.png'))),inflightRequests=[],unsavedSuccessfulOutputs=[],lastCompletedPatch=a.patch,lastCompletedNative=str(image),lastCompletedSha256=d['sha256'],status='native-production',nextStep='Continue actual available neighbors, then native seam and intersection review.',actualModel=None,actualQuality=None,formalAcceptedCount=0);save(f,p);print(json.dumps({'tile':a.tile,'patch':a.patch,'file':str(image),'sha256':d['sha256'],'selectedCoreCount':len(s)}))
