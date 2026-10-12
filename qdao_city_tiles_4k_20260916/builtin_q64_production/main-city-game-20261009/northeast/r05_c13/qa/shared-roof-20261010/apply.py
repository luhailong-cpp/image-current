from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,argparse
from datetime import datetime,timezone
B=Path(__file__).resolve().parent;T=B.parents[1];Z=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
check='--check' in __import__('sys').argv
target=T/'candidates/r05_c13.candidate.png';side=Path(str(target)+'.generation.json')
priorpath=B/'pre-roof-generation.json';B.mkdir(exist_ok=True)
if not priorpath.exists():
 assert sha(target)=='5322cfcd3254b15441e66ecc1fd1103cb96d10c9efc659e7b9afdc555e8b6dc4'
 save(priorpath,read(side))
prior=read(priorpath);op=prior['operation'];south=op['priorRecipe'];core=south['priorRecipe']
for k,h in [('baseline','baselineSha256'),('repair','repairSha256'),('mask','maskSha256')]:assert sha(core[k])==core[h]
im=Image.open(core['baseline']).convert('RGB');im.paste(Image.open(core['repair']).convert('RGB'),tuple(core['pasteOrigin']),Image.open(core['mask']).convert('L'))
for e in south['southBorderRepairs']:
 assert sha(e['source']['file'])==e['source']['sha256'];r=e['operation']
 m=None
 if e['mask']:
  assert sha(e['mask']['file'])==e['mask']['sha256'];m=Image.open(e['mask']['file']).convert('L').crop(r['maskCrop'])
 im.paste(Image.open(e['source']['file']).convert('RGB').crop(r['sourceCrop']),tuple(r['destinationTileXY']),m)
for e in op['materialRepairs']:
 assert sha(e['source'])==e['sourceSha256'];assert sha(e['mask'])==e['maskSha256']
 im.paste(Image.open(e['source']).convert('RGB'),tuple(e['pasteOrigin']),Image.open(e['mask']).convert('L'))
before=im.copy()
p=Z/'r06_c13/qa/finish-20261010/records/roof-cross-seam-v1.material-proposal.json';r=read(p)
assert sha(r['source'])==r['sourceSha256'];assert sha(r['mask'])==r['maskSha256']
e=next(o for o in r['integerTileOperations'] if o['tile']=='r05_c13')
m=Image.open(r['mask']).convert('L').crop(e['maskCrop']);s=Image.open(r['source']).convert('RGB').crop(e['sourceCrop'])
im.paste(s,tuple(e['destinationTileXY']),m)
u=Image.new('L',im.size);u.paste(m.point(lambda v:255 if v else 0),tuple(e['destinationTileXY']))
assert ImageChops.difference(Image.composite(before,im,u),before).getbbox() is None
if check:
 assert ImageChops.difference(im,Image.open(target).convert('RGB')).getbbox() is None
 print(json.dumps({'pixelIdenticalFullReplay':True,'candidateSha256':sha(target)}));raise SystemExit
assert sha(target)==prior['sha256'],'Concurrent change'
im.save(target)
im.crop((2810,3660,3350,4096)).save(B/'north-roof-join-after-100pct.png')
before.crop((2810,3660,3350,4096)).save(B/'north-roof-join-before-100pct.png')
record={**prior,'sha256':sha(target),'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'operation':{'type':'full original native repair replay then shared blue-roof north material crop','priorRecipe':op,'priorRecipeRecord':str(priorpath),'priorRecipeRecordSha256':sha(priorpath),'proposal':str(p),'proposalSha256':sha(p),'source':r['source'],'sourceSha256':r['sourceSha256'],'mask':r['mask'],'maskSha256':r['maskSha256'],'cropOperation':e,'noImageBlur':True,'noSourceResampling':True,'noGeometryWarp':True,'outsideMaskPixelIdentical':True},'derivedFrom':prior['derivedFrom']+[{'file':r['source'],'sha256':r['sourceSha256'],'generationRecord':str(p.parent/'roof-cross-seam-v1.generation.json')}],'formalAccepted':False,'southBorderReview':'blue roof north half integrated; combined final south seam review pending'}
save(side,record)
save(B/'integration.json',{'candidate':str(target),'candidateSha256':sha(target),'sourceReplay':str(B/'apply.py'),'outsideMaskPixelIdentical':True,'previousRepairChainPreserved':True,'visualStatus':'pending north crop review and complete south seam review','formalAccepted':False})
print(json.dumps({'candidateSha256':sha(target),'afterCrop':str(B/'north-roof-join-after-100pct.png')}))

