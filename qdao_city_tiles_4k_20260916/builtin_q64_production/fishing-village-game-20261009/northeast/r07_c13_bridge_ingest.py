import json,hashlib,sys,shutil,datetime
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
name,version,src=sys.argv[1:4];stem=name+'-'+version
plan=read(Z/'records'/(name+'-plan.json'));rp=Z/'records'/(stem+'.receipt.json');rc=read(rp)
assert rc['tool']=='image_gen.imagegen';assert rc['request']['referenced_image_paths']==[a['path']for a in plan['references']]
pp=Z/'records'/(stem+'.prompt.txt');pp.write_text(rc['request']['prompt'],encoding='utf-8')
dst=Z/'native'/(stem+'.png');assert not dst.exists();shutil.copy2(src,dst);im=Image.open(dst).convert('RGB');assert im.size==(1254,1254)
record={**plan,'file':str(dst),'sha256':sha(dst),'width':1254,'height':1254,'nativeSize':[1254,1254],'format':'PNG','tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'generatedAt':None,'observedAtUtc':rc['observedAtUtc'],'timeEvidence':'Observed tool return only, exact generation time undisclosed','unverifiedReason':'Host managed tool exposes no model or quality selectors or response metadata','prompt':ref(pp),'receipt':ref(rp),'source':ref(src),'nativeResizePerformed':False,'formalAccepted':False,'usable':False,'status':'candidate_pending_review'}
write(str(dst)+'.generation.json',record)
ctx=Image.open(plan['qaContext']).convert('RGB');assert ctx.size==(1510,1510);q=[]
for side in ['top','bottom','left','right']:
 out=Image.new('RGB',(1254,256)if side in ['top','bottom']else(256,1254))
 if side=='top':out.paste(ctx.crop((128,0,1382,128)),(0,0));out.paste(im.crop((0,0,1254,128)),(0,128))
 elif side=='bottom':out.paste(im.crop((0,1126,1254,1254)),(0,0));out.paste(ctx.crop((128,1382,1382,1510)),(0,128))
 elif side=='left':out.paste(ctx.crop((0,128,128,1382)),(0,0));out.paste(im.crop((0,0,128,1254)),(128,0))
 else:out.paste(im.crop((1126,0,1254,1254)),(0,0));out.paste(ctx.crop((1382,128,1510,1382)),(128,0))
 qp=Z/'qa'/(stem+'-'+side+'.native-1to1.png');out.save(qp);q.append(ref(qp))
 write(str(qp)+'.derived.json',{'file':str(qp),'sha256':sha(qp),'sources':[ref(dst),ref(plan['qaContext'])],'operation':'Exact native crop and opaque paste, seam local128','side':side})
write(Z/'records'/(stem+'.outer-qa.json'),{'native':ref(dst),'fullEdges':q,'review':'pending','formalAccepted':False})
print(json.dumps({'native':ref(dst),'qa':q}))
