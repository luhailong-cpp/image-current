from pathlib import Path
from PIL import Image,ImageChops
import numpy as np,json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;B=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,o):Path(p).write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8')
def smooth(a):a=np.clip(a,0,1);return a*a*(3-2*a)
def rect_mask(roi,feathers):
 x,y=np.meshgrid(np.arange(1254),np.arange(1254));l,t,r,b=roi;fl,ft,fr,fb=feathers
 a=smooth((x-l)/fl)*smooth((r-x)/fr)*smooth((y-t)/ft)*smooth((b-y)/fb)
 return Image.fromarray(np.uint8(np.rint(255*a)),'L')
base=T/'candidate/r05_c11-4096-candidate-v1.png';im=Image.open(base).convert('RGB');steps=[]
p=T/'repairs/p11-north-net-v2/proposal.json';pr=read(p);source=Path(pr['outputCore']['file']);assert sha(source)==pr['outputCore']['sha256'];im.paste(Image.open(source),(0,0));steps.append({'operation':'paste native1024 proposal core at0,0','source':str(source),'sourceSha256':sha(source),'proposal':str(p),'proposalSha256':sha(p)})
def composite(name,box,mask,maskSpec=None):
 global im
 d=T/'repairs'/name;source=d/'native-result.png';raw=Image.open(source).convert('RGB');assert raw.size==(1254,1254)
 mp=d/'contribution-mask.png'
 if mask is not None:mask.save(mp)
 else:mask=Image.open(mp).convert('L')
 current=im.crop(box);result=Image.composite(raw,current,mask);im.paste(result,(box[0],box[1]));result.save(d/'proposal-native.png')
 steps.append({'name':name,'operation':'Image.composite(raw,current native crop,saved Lmask),no resize','tileBox':box,'source':str(source),'sourceSha256':sha(source),'sourceDimensions':list(raw.size),'mask':str(mp),'maskSha256':sha(mp),'maskSpecification':maskSpec,'generationRecord':str(d/'native-result.generation.json'),'generationRecordSha256':sha(d/'native-result.generation.json')})
composite('post-joint-v1',[1400,-115,2654,1139],rect_mask([350,70,800,900],[80,50,90,100]),{'type':'product cubic smoothstep rectangle','roi':[350,70,800,900],'featherLTRB':[80,50,90,100],'clipToTile':True,'oldNorthUnmodified':True})
composite('rope-joint-v1',[1421,950,2675,2204],rect_mask([50,200,1225,1254],[75,100,75,48]),{'type':'product cubic smoothstep rectangle','roi':[50,200,1225,1254],'featherLTRB':[75,100,75,48]})
composite('ground-halo-v6',[1305,1900,2559,3154],None)
sand=T/'repairs/sand-halo-v1/proposal.json'
if sand.exists():
 pass
out=T/'candidate/r05_c11-4096-candidate-v2.png';im.save(out);preview=im.copy();preview.thumbnail((1254,1254));preview.save(T/'qa/candidate-v2-preview.png')
manifest={'file':str(out),'sha256':sha(out),'dimensions':list(im.size),'base':str(base),'baseSha256':sha(base),'baseManifest':str(base.with_suffix('.manifest.json')),'baseManifestSha256':sha(base.with_suffix('.manifest.json')),'steps':steps,'nativePixelsResized':False,'overviewPixelsUsedInFinal':False,'actualModel':None,'actualQuality':None,'formalAccepted':False,'status':'candidate_pending_final_QA_and_sand_repair','createdAt':datetime.now(timezone.utc).isoformat()}
write(out.with_suffix('.manifest.json'),manifest)
print(json.dumps({'candidate':str(out),'sha256':sha(out),'steps':len(steps)}))
