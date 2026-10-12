"""Local exact native repair records for r10_c06. No resampling, max2px seam."""
from pathlib import Path
from PIL import Image
import json, hashlib, sys, importlib.util, shutil
import numpy as np
from datetime import datetime, timezone
T=Path(__file__).resolve().parent.parent
R=T/'repairs-20261011'
BASE=T/'pipeline/output/5c4d9d81c6fcc1ca/r10_c06.candidate.png'
CONTRACT=T.parent.parent/'production-contract.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
def prepare(name,box,source,content):
 out=R/name;out.mkdir(parents=True,exist_ok=True)
 image=Image.open(source).convert('RGB')
 assert image.size==(4096,4096) and box[2]-box[0]==box[3]-box[1]==1254
 crop=out/'input.png';image.crop(box).save(crop)
 con=read(CONTRACT);refs=[str(crop),con['layoutReference'],con['detailStyleReference'],con['primaryStyleReference']]
 prompt='Use case: precise-object-edit. Native game-map local repair. EDIT IMAGE 1 ONLY at exactly 1254x1254 pixels. '+content+'\nImage 2 is approved overall map geometry context, image 3 approved daylight materials, image 4 approved Daoist chibi style. They are references only. Do not copy their framing, UI, text, people, roofs or layout into this extreme close crop. Preserve same exact crop, camera, shadows and edge geometry. All content outside specified repair area must remain exactly unchanged. No new objects, no zoom/reframe, no blur. Clean polished hand-painted game art, quiet stone surfaces, no photographic depth blur, veins or cellular stone. Preserve opaque RGB. Output only the repaired Image 1.'
 (out/'prompt.txt').write_text(prompt,encoding='utf-8')
 req={'repair':name,'prompt':prompt,'promptFile':str(out/'prompt.txt'),'promptSha256':sha(out/'prompt.txt'),'referenced_image_paths':refs,'references':[{'file':r,'sha256':sha(r),'role':role} for r,role in zip(refs,['exact native edit target','approved geometry','approved daylight materials','approved primary style'])],'transparent_background':False,'preparedAtUtc':now(),'inputCandidate':str(source),'inputCandidateSha256':sha(source),'candidateBox':box,'coordinates':{'contextWorldBox':[box[0]+20480,box[1]+36864,box[2]+20480,box[3]+36864],'nativeCoreBox':[115,115,1139,1139]},'requestedNativePixels':[1254,1254],'actualModel':None,'actualQuality':None,'sourceResampling':False}
 write(out/'request.json',req)
 return req
def ingest(name,toolpath,hint):
 out=R/name;req=read(out/'request.json');s=Path(toolpath)
 im=Image.open(s);assert im.size==(1254,1254),im.size
 dest=out/'native.png';assert not dest.exists();shutil.copyfile(s,dest)
 rec={**req,'file':str(dest),'sha256':sha(dest),'sourceOutput':str(s),'sourceOutputSha256':sha(s),'actualNativePixels':list(im.size),'actualModel':None,'actualQuality':None,'receivedAtUtc':now(),'toolOutputHint':hint,'status':'returned_image_pending_visual_review'}
 write(out/'generation.json',rec);write(out/'receipt.json',{'status':'returned_image','output_hint':hint,'sourceOutput':str(s),'sha256':sha(s),'actualNativePixels':list(im.size),'actualModel':None,'actualQuality':None,'atUtc':now()})
 return rec
def apply(name):
 out=R/name;req=read(out/'generation.json');source=Path(req['inputCandidate'])
 assert sha(source)==req['inputCandidateSha256']
 for r in req['references']:assert sha(r['file'])==r['sha256']
 assert sha(req['file'])==req['sha256']
 a=np.array(Image.open(source).convert('RGB'));box=req['candidateBox'];l,t,r,b=box
 n=np.array(Image.open(req['file']).convert('RGB'))
 spec=importlib.util.spec_from_file_location('native_quilting',T.parent/'local_repairs.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
 blended,metrics=q.quilt(a[t:b,l:r].copy(),n,2)
 result=a.copy();result[t:b,l:r]=blended
 assert np.array_equal(result[0],a[0]) and np.array_equal(result[-1],a[-1]) and np.array_equal(result[:,0],a[:,0]) and np.array_equal(result[:,-1],a[:,-1])
 dest=out/'r10_c06.candidate.png';Image.fromarray(result).save(dest,optimize=True)
 report={'status':'candidate_repair_applied_pending_review','repair':name,'input':str(source),'inputSha256':sha(source),'output':str(dest),'outputSha256':sha(dest),'generationRecord':str(out/'generation.json'),'generationRecordSha256':sha(out/'generation.json'),'candidateBox':box,'quilting':metrics,'sourceResampling':False,'featherRadiusPixels':2,'dimensions':[4096,4096],'outerEdgesUnchanged':True,'pixelsChanged':int(np.any(result!=a,axis=2).sum()),'atUtc':now()}
 write(out/'assembly.json',report);return report
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='apply':print(json.dumps(apply(sys.argv[2]),ensure_ascii=False))
 elif mode=='ingest':print(json.dumps(ingest(sys.argv[2],sys.argv[3],sys.argv[4]),ensure_ascii=False))

