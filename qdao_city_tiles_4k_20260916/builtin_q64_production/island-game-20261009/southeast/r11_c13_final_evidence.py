from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now
import sys
V=sys.argv[1] if len(sys.argv)>1 else 'v01'
T='r11_c13'; Q=ROOT/'qa'/f'{T}-{V}'; src=ROOT/'tiles'/f'{T}.candidate-{V}.png'
im=Image.open(src).convert('RGB'); a=np.array(im); rec=read(Path(str(src)+'.generation.json'))
coverage=np.zeros((4096,4096),np.uint8); sid=np.zeros((4096,4096),np.uint8); replay=np.zeros_like(a); audit=[]
selected={Path(x['file']).name for x in rec['contributions']}
for p in sorted((ROOT/'native').glob(T+'*.png')):
 d=read(Path(str(p)+'.generation.json')); rp=ROOT/d['evidence']['toolReceipt']; r=read(rp)
 prompt=Path(d['prompt']); raw=prompt.read_text(encoding='utf-8')
 checks={'nativeHash':sha(p)==d['sha256'],'sourceHash':sha(Path(d['sourceOutputPath']))==d['sourceOutputSha256']==d['sha256'],'size':Image.open(p).size==(1254,1254),'promptHash':sha(prompt)==d['promptSha256'],'receiptPromptExact':r['submittedArguments']['prompt'].replace('\r\n','\n')==raw,'referenceOrderExact':r['submittedArguments']['referenced_image_paths']==[x['file'] for x in d['references']],'referenceHashes':all(sha(Path(x['file']))==x['sha256'] for x in d['references']),'referenceCount':len(d['references'])<=5,'noResize':d['resizedAfterGeneration'] is False,'modelQualityNotClaimed':d['actualModel'] is None and d['actualQuality'] is None}
 audit.append({'file':str(p),'sha256':sha(p),'selected':p.name in selected,'receipt':str(rp),'receiptSha256':sha(rp),'checks':checks,'pass':all(checks.values())})
for i,p in enumerate(rec['contributions'],1):
 x,y,x1,y1=p['destinationBox']; b=np.array(Image.open(p['file']).convert('RGB').crop(p['sourceCrop'])); replay[y:y1,x:x1]=b; coverage[y:y1,x:x1]+=1; sid[y:y1,x:x1]=i
Image.fromarray(sid).save(Q/'source-id.png')
proof={'createdAt':now(),'candidate':str(src),'candidateSha256':sha(src),'candidateSize':[4096,4096],'allGeneratedNativeRecordCount':len(audit),'selectedNativeCount':len(selected),'rejectedOutsideNativeCount':1,'totalActualOutputs':len(audit)+1,'selectedNativeSize':[1254,1254],'selectedCoreSize':[1024,1024],'coveredPixelCount':int((coverage==1).sum()),'coverageMin':int(coverage.min()),'coverageMax':int(coverage.max()),'mismatchedPixels':int(np.any(replay!=a,axis=2).sum()),'sourceIdMap':str(Q/'source-id.png'),'sourceIdMapSha256':sha(Q/'source-id.png'),'sourceContributions':rec['contributions'],'nativeEvidenceAudit':audit,'allEvidenceChecksPass':all(x['pass'] for x in audit),'operation':'exact crop and paste only; no resizing, blending, warping, recoloring or generated final pixels','rejectedOutputs':[{'file':str(ROOT/'native/r11_c13_p11_v01.png'),'reason':'unwanted round pendant','notUsed':True},{'file':str(ROOT/'qa/r11_c13-rejected/r11_c13_p42_v01.png'),'reason':'truncated submitted prompt; miniature architecture; not ingested','notUsed':True}],'actualModel':None,'actualQuality':None}
assert proof['mismatchedPixels']==0 and proof['coveredPixelCount']==16777216 and proof['allEvidenceChecksPass']
write(Q/'source-audit.json',proof)
entries=[]
def save(name,img,parts):
 out=Q/(name+'.png'); img.save(out); entries.append({'id':name,'file':str(out),'sha256':sha(out),'size':list(img.size),'operation':'exact original-pixel crops and paste','contributions':parts})
def part(p,box,dest):
 return {'file':str(p),'sha256':sha(p),'sourceCrop':box,'destination':dest}
N=ROOT/'tiles/r10_c13.candidate-v02.png'; W=ROOT/'tiles/r11_c12.candidate-v02.png'; NW=ROOT/'tiles/r10_c12.candidate-v02.png'
ni=Image.open(N).convert('RGB'); wi=Image.open(W).convert('RGB'); nwi=Image.open(NW).convert('RGB')
for c in range(4):
 out=Image.new('RGB',(1024,512)); b1=[c*1024,3840,(c+1)*1024,4096];b2=[c*1024,0,(c+1)*1024,256];out.paste(ni.crop(b1),(0,0));out.paste(im.crop(b2),(0,256));save('north-'+str(c+1),out,[part(N,b1,[0,0]),part(src,b2,[0,256])])
for r in range(4):
 out=Image.new('RGB',(512,1024));b1=[3840,r*1024,4096,(r+1)*1024];b2=[0,r*1024,256,(r+1)*1024];out.paste(wi.crop(b1),(0,0));out.paste(im.crop(b2),(256,0));save('west-'+str(r+1),out,[part(W,b1,[0,0]),part(src,b2,[256,0])])
out=Image.new('RGB',(1024,1024)); ps=[]
for p,img,box,dest in [(NW,nwi,[3584,3584,4096,4096],[0,0]),(N,ni,[0,3584,512,4096],[512,0]),(W,wi,[3584,0,4096,512],[0,512]),(src,im,[0,0,512,512],[512,512])]:
 out.paste(img.crop(box),dest);ps.append(part(p,box,dest))
save('four-tile-junction',out,ps)
for r in range(1,4):
 for c in range(1,4):
  b=[1024*c-256,1024*r-256,1024*c+256,1024*r+256];save(f'j{r}{c}',im.crop(b),[part(src,b,[0,0])])
im.resize((1536,1536),Image.Resampling.LANCZOS).save(Q/'preview.png')
inherited=[]
for p in (ROOT/'qa/r11_c13-first-two-rows').glob('*.png'):
 dest=Q/p.name
 if dest.exists() and p.name!='preview.png':
  x=Image.open(p).convert('RGB');y=Image.open(dest).convert('RGB')
  if x.size==y.size:inherited.append({'oldFile':str(p),'newFile':str(dest),'pixelExact':bool(np.array_equal(np.array(x),np.array(y)))})
write(Q/'index.json',{'createdAt':now(),'candidate':str(src),'candidateSha256':sha(src),'sourceProof':str(Q/'source-audit.json'),'internalSeams':str(Q/'seams.json'),'rawCrops':entries,'priorFirstTwoRowCrops':inherited,'preview':str(Q/'preview.png'),'formalAccepted':False})
p=ROOT/f'progress-{T}.json';d=read(p);d.update({'status':'candidate_assembled_qa_pending','updatedAt':now(),'generatedNativeCount':len(audit),'totalActualOutputCount':len(audit)+1,'rejectedOutputCount':2,'supersededNativeCount':len(audit)-17,'usableNativeCount':16,'uniqueGeneratedPatchCoordinates':16,'fullyCovered4kCount':1,'complete4kCount':1,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'latestCandidate':str(src),'latestCandidateSha256':sha(src),'nextStep':'Inspect full raw internal/external/junction QA and independent review; coverage does not equal acceptance.'});write(p,d)
print({'candidateSha256':sha(src),'mismatchedPixels':proof['mismatchedPixels'],'allEvidenceChecksPass':proof['allEvidenceChecksPass'],'generatedOutputCount':18,'selected':16,'inheritedCrops':len(inherited),'externalAndJunctionCrops':len(entries)})

