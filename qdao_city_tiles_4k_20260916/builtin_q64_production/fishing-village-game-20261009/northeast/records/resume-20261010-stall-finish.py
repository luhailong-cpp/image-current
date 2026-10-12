from pathlib import Path
from PIL import Image
import json,hashlib,datetime,shutil
B=Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p,role): return {'path':str(p),'sha256':sha(p),'role':role}
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=Path('C:/Users/luyua/.codex/generated_images/01a12561-477e-77c1-aabe-f981f8b424eb/exec-abd3eaf4-a436-4b57-ab7f-8b2ec156fdd5.png')
dst=B/'native/resume-20261010-stall-v1.png';shutil.copy2(src,dst)
im=Image.open(dst).convert('RGB');assert im.size==(1254,1254)
req=json.loads((B/'records/resume-20261010-stall-v1.submission.json').read_text(encoding='utf-8'))
req.update({'file':str(dst),'sha256':sha(dst),'nativeSize':list(im.size),'copiedFrom':str(src),'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receiptFile':str(B/'records/resume-20261010-stall-v1.receipt.json'),'metadata':im.info,'isAIGenerated':True,'usable':False,'formalAccepted':False,'status':'pending_native_edge_visual_review'})
write(str(dst)+'.generation.json',req)
p34=B/'native/r06_c12_p34-v1.png';p44=B/'native/r06_c12_p44-v1.png'
a=Image.open(p34).convert('RGB');z=Image.open(p44).convert('RGB')
combo=Image.new('RGB',(1254,2278));combo.paste(a.crop((0,0,1254,1139)),(0,0));combo.paste(z.crop((0,115,1254,1254)),(0,1139));combo.paste(im,(0,512))
for name,box in [('upper',[0,384,1254,640]),('lower',[0,1638,1254,1894]),('core',[0,1011,1254,1267])]:
 p=B/f'qa/resume-20261010-stall-v1-{name}-boundary.png';combo.crop(box).save(p)
 write(str(p)+'.derived.json',{'purpose':'native 1:1 QA only','source':rec(dst,'actual generation'),'neighborSources':[rec(p34,'upper source'),rec(p44,'lower source')],'composition':'1254x2278 top core at y0..1139, bottom at1139..2278; repair opaque pasted at y512..1766','cropBox':box,'resized':False})
for name,leftfile,y0 in [('left-top','r06_c12_p33-v1.png',0),('left-bottom','r06_c12_p43-v1.png',1024)]:
 l=Image.open(B/'native'/leftfile).convert('RGB');right=combo.crop((0,y0,1254,y0+1254));stripe=Image.new('RGB',(256,1254));stripe.paste(l.crop((1011,0,1139,1254)),(0,0));stripe.paste(right.crop((115,0,243,1254)),(128,0));stripe.save(B/f'qa/resume-20261010-stall-v1-{name}-boundary.png')
write(B/'records/resume-20261010-stall-v1-contribution.json',{'status':'proposal_only_not_selected','source':rec(dst,'native actual generated contribution'),'worldBox':[48013,22925,49267,24179],'backPastePlan':[{'patch':'p34','repairSourceBox':[0,0,1254,742],'destinationBox':[0,512,1254,1254]},{'patch':'p44','repairSourceBox':[0,512,1254,1254],'destinationBox':[0,0,1254,742]}],'selectedCoreFilesChanged':False,'newGenerationCount':1,'formalAccepted':False})
print(json.dumps({'output':str(dst),'size':list(im.size),'sha256':sha(dst)}))
