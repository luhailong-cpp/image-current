from workflow import *
from PIL import Image
import numpy as np
proposal=read(ROOT/'qa/r08_c12-r09c12-final-split-proposal.json');base=Path(proposal['r09Base']);assert sha(base)==proposal['r09BaseSha256'];up=Path(proposal['r08Candidate']);assert sha(up)==proposal['r08Sha256']
im=Image.open(base).convert('RGB');original=im.copy();rects=read(Path(str(base)+'.generation.json'))['contributions'];parts=[]
def subtract(a,b):
 x0,y0,x1,y1=a;u0,v0,u1,v1=b;ix0,iy0,ix1,iy1=max(x0,u0),max(y0,v0),min(x1,u1),min(y1,v1)
 if ix0>=ix1 or iy0>=iy1:return [a]
 return [q for q in [[x0,y0,x1,iy0],[x0,iy1,x1,y1],[x0,iy0,ix0,iy1],[ix1,iy0,x1,iy1]] if q[0]<q[2] and q[1]<q[3]]
changed=proposal['r09ChangedUnion']
for r in rects:
 for box in subtract(r['destinationBox'],changed):
  p=dict(r);x,y,_,_=r['destinationBox'];sx,sy,_,_=r['sourceCrop'];p.update({'sourceCrop':[sx+box[0]-x,sy+box[1]-y,sx+box[2]-x,sy+box[3]-y],'destination':box[:2],'destinationBox':box});parts.append(p)
for r in proposal['preciseNonOverlappingContributions']:
 src=Path(r['native']);assert sha(src)==r['sha256'];box=r['r09DestinationBox'];crop=r['r09SourceCrop'];im.paste(Image.open(src).convert('RGB').crop(crop),box[:2]);parts.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':box[:2],'destinationBox':box,'record':str(src)+'.generation.json'})
out=ROOT/'tiles/r09_c12.candidate-v03.png';assert not out.exists();im.save(out)
assert im.tobytes()==Image.open(proposal['r09CounterpartProposal']).convert('RGB').tobytes()
coverage=np.zeros((4096,4096),dtype=np.uint8);replay=Image.new('RGB',(4096,4096))
for r in parts:
 x0,y0,x1,y1=r['destinationBox'];coverage[y0:y1,x0:x1]+=1;src=Image.open(r['file']).convert('RGB').crop(r['sourceCrop']);assert src.size==(x1-x0,y1-y0);assert src.tobytes()==im.crop(r['destinationBox']).tobytes();replay.paste(src,(x0,y0))
assert np.all(coverage==1) and replay.tobytes()==im.tobytes()
write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':4096,'height':4096,'generatedAt':now(),'operation':'Exact unscaled native source rectangle hard-paste with complete once-only pixel ownership','contributions':parts,'seamShifts':read(Path(str(base)+'.generation.json')).get('seamShifts',[]),'base':str(base),'baseSha256':sha(base),'proposal':'qa/r08_c12-r09c12-final-split-proposal.json','fullCoverage':True,'pixelCoverageMin':1,'pixelCoverageMax':1,'allContributionsPixelExact':True,'actualModel':None,'actualQuality':None,'status':'candidate_pending_changed_roof_review'})
folder=ROOT/'qa/r09_c12-v03';folder.mkdir(exist_ok=True);entries=[]
def save(name,image,desc):
 p=folder/(name+'.png');image.save(p);entries.append({'id':name,'file':str(p),'sha256':sha(p),'description':desc,'status':'pending_visual_review'})
north=Image.open(up).convert('RGB')
for c in range(4):
 tile=Image.new('RGB',(1024,512));tile.paste(north.crop([c*1024,3840,(c+1)*1024,4096]),(0,0));tile.paste(im.crop([c*1024,0,(c+1)*1024,256]),(0,256));save('shared-north-'+str(c+1),tile,'100 percent native shared edge, y256')
for i,(x0,x1) in enumerate([(0,1024),(1024,2048),(1536,2560)]):save('lower-perimeter-'+str(i+1),im.crop([x0,251,x1,635]),'100 percent native repair lower perimeter y443; local y192')
save('right-perimeter',im.crop([2368,0,2752,640]),'Native right perimeter x2560; local x192')
for x in [1024,1139,1536,2048]:save('roof-join-'+str(x),im.crop([x-192,0,x+192,635]),'Original pixel roof join at localx192; lowerperimetery443')
im.resize((1024,1024),Image.Resampling.LANCZOS).save(folder/'preview.png')
write(folder/'roof-change-review.json',{'createdAt':now(),'candidate':str(out),'sha256':sha(out),'northCandidate':str(up),'northSha256':sha(up),'entries':entries,'replayAllNativePixelExact':True,'matchesCounterpartProposalPixels':True,'formalAccepted':False})
print(str(out));print(sha(out));print(len(parts))

