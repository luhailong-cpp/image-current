from workflow import *
import re,numpy as np
q=ROOT/'qa/r14_c12-partial-local-20261013';q.mkdir(exist_ok=True)
d=read(ROOT/'progress-r14_c12.json');versions=d['workingVersions'];im=Image.new('RGB',(4096,4096),(96,96,96));ids=np.zeros((4096,4096),dtype=np.uint8);sources=[]
for rc,v in sorted(versions.items()):
 r,c=map(int,rc);f=ROOT/'native'/f'r14_c12_p{rc}_{v}.png';a=Image.open(f).convert('RGB');assert a.size==(1254,1254);x=(c-1)*1024;y=(r-1)*1024;sid=len(sources)+1
 im.paste(a.crop((115,115,1139,1139)),(x,y));ids[y:y+1024,x:x+1024]=sid;sources.append({'id':sid,'coordinate':rc,'file':str(f),'sha256':sha(f),'originInTile':[x-115,y-115]})
rgb=np.array(im);replay=[]
for s in sources:
 yy,xx=np.where(ids==s['id']);a=np.array(Image.open(s['file']).convert('RGB'));ox,oy=s['originInTile'];m=int(np.any(rgb[yy,xx]!=a[yy-oy,xx-ox],axis=1).sum());assert m==0;replay.append({'id':s['id'],'ownedPixels':len(xx),'mismatch':m})
im.save(q/'partial-layout-review-only.png');Image.fromarray(ids).save(q/'source-id.png')
entries=[];junctions=[]
for r in range(1,5):
 for c in range(1,4):
  if f'{r}{c}' in versions and f'{r}{c+1}' in versions:
   b=[c*1024-256,(r-1)*1024,c*1024+256,r*1024];f=q/f'h{r}{c}.png';im.crop(b).save(f);entries.append({'id':f'h{r}{c}','file':str(f),'sourceCrop':b,'sha256':sha(f),'status':'pending_visual_review'})
for r in range(1,4):
 for c in range(1,5):
  if f'{r}{c}' in versions and f'{r+1}{c}' in versions:
   b=[(c-1)*1024,r*1024-256,c*1024,r*1024+256];f=q/f'v{r}{c}.png';im.crop(b).save(f);entries.append({'id':f'v{r}{c}','file':str(f),'sourceCrop':b,'sha256':sha(f),'status':'pending_visual_review'})
for r in range(1,4):
 for c in range(1,4):
  if all(f'{rr}{cc}' in versions for rr,cc in [(r,c),(r,c+1),(r+1,c),(r+1,c+1)]):
   b=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];f=q/f'j{r}{c}.png';im.crop(b).save(f);junctions.append({'id':f'j{r}{c}','file':str(f),'sourceCrop':b,'sha256':sha(f),'status':'pending_visual_review'})
horizontal=[e for e in entries if e['id'][0]=='h'];vertical=[e for e in entries if e['id'][0]=='v'];contacts=[]
for prefix,arr,w,h,cols,rows in [('h',horizontal,512,1024,4,2),('v',vertical[:6],1024,512,2,3),('v2',vertical[6:],1024,512,2,2),('j',junctions,512,512,3,2)]:
 contact=Image.new('RGB',(cols*w,rows*h),(96,96,96))
 for i,e in enumerate(arr):contact.paste(Image.open(e['file']).convert('RGB'),((i%cols)*w,(i//cols)*h))
 f=q/f'contact-{prefix}.png';contact.save(f);contacts.append({'file':str(f),'sha256':sha(f),'order':[e['id'] for e in arr],'resampled':False})
north=Image.open(ROOT/'tiles/r13_c12.candidate-sol-20261013-v01.png').convert('RGB');contact=Image.new('RGB',(2048,1024));northcuts=[]
for c in range(4):
 cut=Image.new('RGB',(1024,512));cut.paste(north.crop((c*1024,3840,(c+1)*1024,4096)),(0,0));cut.paste(im.crop((c*1024,0,(c+1)*1024,256)),(0,256));f=q/f'actual-north-{c+1}.png';cut.save(f);contact.paste(cut,((c%2)*1024,(c//2)*512));northcuts.append({'file':str(f),'sha256':sha(f),'status':'pending_visual_review'})
contact.save(q/'contact-actual-north.png')
write(q/'partial-proof-and-review-queue.json',{'tile':'r14_c12','sources':sources,'sourceReplay':replay,'knownCoveredPixels':int((ids!=0).sum()),'unknownPixels':int((ids==0).sum()),'sourcePixelMismatch':0,'complete4kCandidate':False,'missingCoordinates':['33','43'],'partialImageForReviewOnly':str(q/'partial-layout-review-only.png'),'unknownAreaIsGreyPlaceholderNotFinalArt':True,'knownInternalSeams':entries,'knownJunctions':junctions,'contacts':contacts,'actualNorthCuts':northcuts,'northCandidate':str(ROOT/'tiles/r13_c12.candidate-sol-20261013-v01.png'),'northSha256':sha(ROOT/'tiles/r13_c12.candidate-sol-20261013-v01.png'),'formalAccepted':False,'newGenerationPerformed':False,'createdAtUtc':now()})
rows=[];coords={};problems=[]
for f in sorted((ROOT/'native').glob('*.png')):
 item={'file':str(f),'sha256':sha(f)};mf=Path(str(f)+'.generation.json')
 try:
  image=Image.open(f);image.load();item.update(dimensions=list(image.size),mode=image.mode)
  if image.size!=(1254,1254):problems.append({'file':str(f),'problem':'unexpected_native_dimensions'})
  if mf.exists():
   meta=read(mf);item['metadataSha256Matches']=meta.get('sha256')==item['sha256'];item['actualModel']=meta.get('actualModel');item['actualQuality']=meta.get('actualQuality')
   if not item['metadataSha256Matches']:problems.append({'file':str(f),'problem':'metadata_sha256_mismatch'})
  else:problems.append({'file':str(f),'problem':'native_metadata_missing'})
  m=re.fullmatch(r'(r\d{2}_c\d{2})_p([1-4][1-4])_(v\d+)\.png',f.name)
  if m:coords.setdefault(m[1],set()).add(m[2]);item.update(tile=m[1],coordinate=m[2],version=m[3])
 except Exception as e:problems.append({'file':str(f),'problem':str(e)})
 rows.append(item)
inventory={'createdAtUtc':now(),'nativeFileCount':len(rows),'allNativeDimensionsAndMetadataAuditProblems':problems,'rawCoordinatesWithAnySavedVersion':{tid:sorted(cs) for tid,cs in coords.items()},'rawCoordinateCount':sum(len(cs) for cs in coords.values()),'rawVersionsAreNotAcceptance':True,'entries':rows,'newGenerationPerformed':False,'newGenerationOnHold':read(ROOT/'production-resume-20261012.json')['generationModelRequirement'],'formalAccepted':False}
write(ROOT/'saved-native-inventory-20261013.json',inventory)
print(json.dumps({'nativeFiles':len(rows),'auditProblems':len(problems),'rawCoordinatesAnyVersion':inventory['rawCoordinateCount'],'r14PartialCoveredPixels':int((ids!=0).sum()),'r14PartialSeams':len(entries),'r14PartialJunctions':len(junctions),'r14MissingCoordinates':['33','43'],'newGenerationPerformed':False}))
