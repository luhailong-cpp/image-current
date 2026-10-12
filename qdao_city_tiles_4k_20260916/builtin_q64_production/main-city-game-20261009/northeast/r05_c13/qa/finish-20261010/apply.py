"""Replay M01 + south repairs then native material edits, without resizing."""
from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,argparse
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;TILE=HERE.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
target=TILE/'candidates/r05_c13.candidate.png';side=Path(str(target)+'.generation.json')
priorfile=HERE/'records/pre-finish-generation.json'
if not priorfile.exists():
 assert sha(target)=='e56703e6af101b62306e1ff5ad4fccde7c8df2524ffd37417257a72b9b3bf746'
 save(priorfile,read(side))
prior=read(priorfile);op=prior['operation'];core=op['priorRecipe']
for k,h in [('baseline','baselineSha256'),('repair','repairSha256'),('mask','maskSha256')]:assert sha(core[k])==core[h]
im=Image.open(core['baseline']).convert('RGB');im.paste(Image.open(core['repair']).convert('RGB'),tuple(core['pasteOrigin']),Image.open(core['mask']).convert('L'))
for entry in op['southBorderRepairs']:
 assert sha(entry['source']['file'])==entry['source']['sha256']
 src=Image.open(entry['source']['file']).convert('RGB');oper=entry['operation']
 m=None
 if entry['mask']:
  assert sha(entry['mask']['file'])==entry['mask']['sha256'];m=Image.open(entry['mask']['file']).convert('L').crop(oper['maskCrop'])
 im.paste(src.crop(oper['sourceCrop']),tuple(oper['destinationTileXY']),m)
before=im.copy();union=Image.new('L',im.size,0);applied=[]
for rid in ['m02-lower-v1','m03-road-v1','m02-upper-v1']:
 p=HERE/'records'/f'{rid}.material-proposal.json';r=read(p)
 assert sha(r['source'])==r['sourceSha256'];assert sha(r['mask'])==r['maskSha256']
 src=Image.open(r['source']).convert('RGB');m=Image.open(r['mask']).convert('L');assert src.size==m.size==(1254,1254)
 im.paste(src,tuple(r['pasteOrigin']),m)
 part=Image.new('L',im.size,0);part.paste(m.point(lambda t:255 if t else 0),tuple(r['pasteOrigin']));union=ImageChops.lighter(union,part)
 applied.append({'id':rid,'recipe':str(p),'source':r['source'],'sourceSha256':r['sourceSha256'],'mask':r['mask'],'maskSha256':r['maskSha256'],'pasteOrigin':r['pasteOrigin'],'generationRecord':str(HERE/'records'/f'{rid}.generation.json')})
assert ImageChops.difference(Image.composite(before,im,union),before).getbbox() is None
assert ImageChops.difference(before.crop((0,3981,4096,4096)),im.crop((0,3981,4096,4096))).getbbox() is None
if args.check:
 assert ImageChops.difference(im,Image.open(target).convert('RGB')).getbbox() is None
 print(json.dumps({'pixelIdenticalReplay':True,'candidateSha256':sha(target)}));raise SystemExit
expected=read(HERE/'records/integration.json')['sha256'] if (HERE/'records/integration.json').exists() else prior['sha256']
assert sha(target)==expected,'Candidate changed concurrently; do not overwrite'
im.save(target)
record={**prior,'sha256':sha(target),'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'operation':{'type':'prior native/M01/south recipe replay then three AI-painted stone material masks','priorRecipeRecord':str(priorfile),'priorRecipeRecordSha256':sha(priorfile),'priorRecipe':op,'materialRepairs':applied,'sourceResampling':False,'blurUsed':False,'geometryWarp':False,'originalGroutRetained':True},'derivedFrom':prior['derivedFrom']+[{'file':r['source'],'sha256':r['sourceSha256'],'generationRecord':r['generationRecord']} for r in applied],'formalAccepted':False,'internalReview':str(HERE/'review.json')}
save(side,record)
out=HERE/'after';out.mkdir(exist_ok=True)
crops=read(HERE/'before-manifest.json')['crops'];changed=[]
for c in crops:
 dest=out/Path(c['file']).name;im.crop(c['box']).save(dest)
 if ImageChops.difference(Image.open(c['file']).convert('RGB'),Image.open(dest).convert('RGB')).getbbox() is not None:changed.append(dest.name)
save(HERE/'records/integration.json',{'candidate':str(target),'sha256':sha(target),'sourceReplay':str(HERE/'apply.py'),'pixelIdenticalReplayVerified':True,'outsideMaskPixelIdentical':True,'southFlowersAndGoldPixelsUnchanged':True,'nativeAndSelectionUnchanged':True,'operations':applied,'changedQACrops':changed,'formalAccepted':False})
print(json.dumps({'candidateSha256':sha(target),'changedQACrops':changed}))
