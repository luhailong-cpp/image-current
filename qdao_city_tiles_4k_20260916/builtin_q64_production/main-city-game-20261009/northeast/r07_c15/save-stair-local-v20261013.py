from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,shutil
T=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
name='stair-local-v20261013';receipt=read(T/'receipts'/(name+'.receipt.json'));src=Path(receipt['sourceOutputPath'])
dst=T/'native/repairs'/(name+'.png');assert not dst.exists();shutil.copy2(src,dst)
im=Image.open(dst).convert('RGB');assert im.size==(1254,1254)
request=T/'prompts'/(name+'.request.json');payload=read(request)
save(Path(str(dst)+'.generation.json'),{'file':str(dst),'sha256':sha(dst),'generatedAt':receipt['receivedAt'],'nativeSize':[1254,1254],'tool':'image_gen','route':'builtin','sourceOutputPath':str(src),'actualModel':None,'actualQuality':None,'resized':False,'assetRole':'native local repair; not an additional selected core','prompt':str(T/'prompts'/(name+'.prompt.txt')),'request':str(request),'evidence':str(T/'receipts'/(name+'.receipt.json')),'references':[{'file':p,'sha256':sha(p)} for p in payload['referenced_image_paths']]})
base=T/'qa/core-baseline/4310c2993aead148fef7/r07_c15-core-baseline.candidate.png'
can=Image.open(base).convert('RGB')
post=T/'native/repairs/post-local-v20261013.png'
pim=Image.open(post).convert('RGB');proi=[610,160,980,1000];sroi=[520,510,800,850]
can.paste(pim.crop(proi),(2450+proi[0],300+proi[1]))
can.paste(im.crop(sroi),(380+sroi[0],2450+sroi[1]))
out=T/'candidates/r07_c15.local-repairs-v20261013.png';assert not out.exists();can.save(out)
q=T/'qa/local-repair-20261013'
for n,box in [('post-composed-review-v2',[2450,300,3704,1554]),('stair-composed-review-v1',[380,2450,1634,3704])]:
    f=q/(n+'.png');assert not f.exists();can.crop(box).save(f)
layers=[{'file':str(post),'sha256':sha(post),'targetOrigin':[2450,300],'crop':proi},{'file':str(dst),'sha256':sha(dst),'targetOrigin':[380,2450],'crop':sroi}]
save(q/'local-repairs-composition-v1.json',{'baseCandidate':str(base),'baseSha256':sha(base),'layers':layers,'operation':'integer source crop and paste only; no resampling, feathering, filters or hand-painted pixels','candidate':str(out),'candidateSha256':sha(out),'nativeSize':[4096,4096],'status':'review_pending'})
print(json.dumps({'candidate':str(out),'sha256':sha(out)}))
