from workflow import *
import numpy as np
q=ROOT/'qa/r12_c13-material-v04-20261013';q.mkdir(exist_ok=False)
base=ROOT/'tiles/r12_c13.candidate-sol-20261013-v03-local-ownership.png';new=ROOT/'native/r12_c13_floor_material_whole_v01.png'
meta=read(Path(str(base)+'.generation.json'));proof=read(Path(meta['sourcePixelProof']))
out=ROOT/'tiles/r12_c13.candidate-sol-20261013-v04-material.png';assert not out.exists()
im=Image.open(base).convert('RGB');im.paste(Image.open(new).convert('RGB').crop((115,115,1139,1139)),(512,1536));im.save(out)
ids=np.asarray(Image.open(proof['sourceIdMap'])).copy();sid=max(s['sourceId'] for s in meta['sources'])+1;ids[1536:2560,512:1536]=sid
ip=q/'source-id.png';Image.fromarray(ids).save(ip)
sources=meta['sources']+[{'sourceId':sid,'file':str(new),'sha256':sha(new),'sourceCoreCrop':[115,115,1139,1139],'tileRelativeOrigin':[397,1421],'destinationCore':[512,1536,1536,2560]}]
sources=[s for s in sources if np.any(ids==s['sourceId'])]
arr=np.asarray(im);checks=[]
for s in sources:
 ox,oy=s['tileRelativeOrigin'];yy,xx=np.where(ids==s['sourceId']);a=np.asarray(Image.open(s['file']).convert('RGB'));bad=int(np.count_nonzero(np.any(arr[yy,xx]!=a[yy-oy,xx-ox],axis=1)));core=bool(np.all((xx-ox>=115)&(xx-ox<1139)&(yy-oy>=115)&(yy-oy<1139)));assert core and bad==0
 checks.append({'sourceId':s['sourceId'],'file':s['file'],'sha256':sha(Path(s['file'])),'ownedPixels':len(xx),'mismatchedPixels':bad,'allOwnedPixelsWithin1024Core':core})
pr={'candidate':str(out),'candidateSha256':sha(out),'sourceIdMap':str(ip),'sourceIdSha256':sha(ip),'sourceIdCount':len(sources),'coveredPixels':int(np.count_nonzero(ids)),'unownedPixels':int(np.count_nonzero(ids==0)),'mismatchedPixels':0,'checks':checks,'resampled':False,'blended':False,'RGBModified':False};write(q/'source-pixel-proof.json',pr)
write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':4096,'height':4096,'sources':sources,'baseCandidate':str(base),'baseCandidateSha256':sha(base),'operation':'exact registered 1024 core replacement; RGB source pixels unchanged','sourcePixelProof':str(q/'source-pixel-proof.json'),'sourceIdMap':str(ip),'status':'pending_visual_review','formalAccepted':False,'internalAccepted':False,'createdAt':now()})
oldqa=read(ROOT/'qa/r12_c13-floor-ownership-20261013/candidate-v03-actual-qa.json');changed=[];reused=[]
for e in oldqa['internalSeams']+oldqa['junctions']:
 crop=im.crop(tuple(e['box']));prev=Image.open(e['file']).convert('RGB')
 if np.array_equal(np.asarray(crop),np.asarray(prev)):reused.append(e);continue
 f=q/(e['id']+'.png');crop.save(f);changed.append({'id':e['id'],'box':e['box'],'file':str(f),'sha256':sha(f)})
boundaries=[]
for name,box in [('repair-north',[512,1408,1536,1664]),('repair-south',[512,2432,1536,2688]),('repair-west',[384,1536,640,2560]),('repair-east',[1408,1536,1664,2560]),('whole-object',[397,1421,1651,2675])]:
 f=q/(name+'.png');im.crop(tuple(box)).save(f);boundaries.append({'id':name,'box':box,'file':str(f),'sha256':sha(f)})
write(q/'qa-manifest.json',{'candidate':str(out),'candidateSha256':sha(out),'changed':changed,'reusedUnchangedFromV03':reused,'newSourceBoundaries':boundaries,'status':'pending_visual_review'})
print(json.dumps({'candidate':str(out),'sha256':sha(out),'mismatchedPixels':0,'sources':len(sources),'changedQA':len(changed),'reusedQA':len(reused),'qa':str(q)}))
