from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now
s=read(ROOT/'selection-r11_c11.json');versions=s['patchVersions'];missing=[f'{r}{c}'for r in range(1,5)for c in range(1,5)if f'{r}{c}'not in versions]
for rc,msg in {'31':'application network permission was revoked','42':'http 401 Unauthorized: Missing bearer or basic authentication in header'}.items():
 f=ROOT/'receipts'/f'r11_c11_p{rc}_v01-attempt-1-error.json'
 if not f.exists():write(f,{'tool':'image_gen.imagegen','recordedAt':now(),'status':'failed_no_output','error':msg})
qa=ROOT/'qa'/'r11_c11-partial13';qa.mkdir(exist_ok=True)
im=Image.new('RGBA',(4096,4096),(0,0,0,0));entries=[]
for rc,v in versions.items():
 r,c=map(int,rc);f=ROOT/'native'/f'r11_c11_p{rc}_{v}.png';native=Image.open(f).convert('RGBA');assert native.size==(1254,1254)
 dest=[(c-1)*1024,(r-1)*1024];im.paste(native.crop((115,115,1139,1139)),dest)
 entries.append({'patch':rc,'file':str(f),'sha256':sha(f),'sourceCrop':[115,115,1139,1139],'destination':dest,'destinationBox':[dest[0],dest[1],dest[0]+1024,dest[1]+1024]})
out=ROOT/'tiles'/'r11_c11.partial-13of16.png';im.save(out)
for e in entries:assert np.array_equal(np.array(Image.open(e['file']).convert('RGBA').crop(e['sourceCrop'])),np.array(im.crop(e['destinationBox'])))
write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':4096,'height':4096,'operation':'exact unscaled native cores; transparent missing coordinates, not completed artwork','contributions':entries,'fullCoverage':False,'missingPatches':missing,'candidateOnly':True,'allSelectedPixelsExact':True})
im.resize((1024,1024),Image.Resampling.LANCZOS).save(qa/'partial-preview.png')
index={'source':str(out),'sha256':sha(out),'missing':missing,'reviewedAt':now(),'external':[],'seams':[],'junctions':[]}
def save(name,img,cat,rec):
 f=qa/f'{name}.png';img.save(f);rec.update({'id':name,'file':str(f),'sha256':sha(f),'status':'pending_visual_review'});index[cat].append(rec)
for r in range(1,5):
 for c in range(1,4):
  if f'{r}{c}' in versions and f'{r}{c+1}' in versions:
   box=[c*1024-256,(r-1)*1024,c*1024+256,r*1024];save(f'h{r}{c}',im.crop(box),'seams',{'crop':box})
for r in range(1,4):
 for c in range(1,5):
  if f'{r}{c}' in versions and f'{r+1}{c}' in versions:
   box=[(c-1)*1024,r*1024-256,c*1024,r*1024+256];save(f'v{r}{c}',im.crop(box),'seams',{'crop':box})
for r in range(1,4):
 for c in range(1,4):
  if all(f'{rr}{cc}' in versions for rr in [r,r+1] for cc in [c,c+1]):
   box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];save(f'j{r}{c}',im.crop(box),'junctions',{'crop':box})
npath=ROOT/'tiles'/'r10_c11.candidate-v04.png';epath=ROOT/'tiles'/'r11_c12.candidate-v02.png';nepath=ROOT/'tiles'/'r10_c12.candidate-v02.png'
n=Image.open(npath).convert('RGBA');e=Image.open(epath).convert('RGBA');ne=Image.open(nepath).convert('RGBA')
for i in range(4):
 a=[i*1024,3840,(i+1)*1024,4096];b=[i*1024,0,(i+1)*1024,256];q=Image.new('RGBA',(1024,512));q.paste(n.crop(a),(0,0));q.paste(im.crop(b),(0,256));save(f'north-{i+1}',q,'external',{'sources':[{'file':str(npath),'sha256':sha(npath),'crop':a,'destination':[0,0]},{'file':str(out),'sha256':sha(out),'crop':b,'destination':[0,256]}]})
 a=[3840,i*1024,4096,(i+1)*1024];b=[0,i*1024,256,(i+1)*1024];q=Image.new('RGBA',(512,1024));q.paste(im.crop(a),(0,0));q.paste(e.crop(b),(256,0));save(f'east-{i+1}',q,'external',{'sources':[{'file':str(out),'sha256':sha(out),'crop':a,'destination':[0,0]},{'file':str(epath),'sha256':sha(epath),'crop':b,'destination':[256,0]}]})
q=Image.new('RGBA',(512,512));specs=[(npath,n,[3840,3840,4096,4096],[0,0]),(nepath,ne,[0,3840,256,4096],[256,0]),(out,im,[3840,0,4096,256],[0,256]),(epath,e,[0,0,256,256],[256,256])]
for _,src,box,dest in specs:q.paste(src.crop(box),dest)
save('northeast-four-tile-junction',q,'external',{'sources':[{'file':str(p),'sha256':sha(p),'crop':box,'destination':dest}for p,_,box,dest in specs]})
write(qa/'index.json',index)
p=read(ROOT/'progress-r11_c11.json');p.update({'status':'partial_local_qa_generation_waiting_root_resume_result','generatedNativeCount':len(list((ROOT/'native').glob('r11_c11_*.png'))),'selectedCoordinateCount':len(versions),'missingPatches':missing,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'partialFile':str(out),'partialSha256':sha(out),'inFlightRequests':[],'networkErrors':{'p31':'permission revoked','p42':'HTTP401 missing auth'},'nextStep':'Local review of partial valid seams plus all north/east external crops; resume missing31/41/42 only when root confirms actual restored output.','updatedAt':now()});write(ROOT/'progress-r11_c11.json',p)
write(ROOT/'continuation-round-left-20261011.json',{'resumedAt':now(),'currentCoordinate':'r11_c11','actualOutputsSinceResume':['21','33','44','32','43'],'output':str(ROOT/'native'/'r11_c11_p21_v01.png'),'hash':sha(ROOT/'native'/'r11_c11_p21_v01.png'),'source':read(ROOT/'native'/'r11_c11_p21_v01.png.generation.json')['sourceOutputPath'],'generatedNativeCount':p['generatedNativeCount'],'selectedCoordinateCount':len(versions),'missing':missing,'inFlight':[],'errors':p['networkErrors'],'status':p['status']})
print({'partial':str(out),'sha256':sha(out),'missing':missing,'validInternalSeams':len(index['seams']),'validJunctions':len(index['junctions']),'northEastCrops':len(index['external'])})
