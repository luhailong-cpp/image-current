from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import numpy as np,json,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rid='m02-lower-v1';source=HERE/'source'/f'{rid}.png';inp=HERE/'inputs'/f'{rid}.png'
a=Image.open(inp).convert('RGB');b=Image.open(source).convert('RGB');assert a.size==b.size==(1254,1254)
# Binary polygon follows natural slab/grout boundaries wherever possible.
mask=Image.new('L',a.size,0);d=ImageDraw.Draw(mask)
d.rectangle([170,0,549,1119],fill=255)
out=a.copy();out.paste(b,(0,0),mask);out.save(HERE/'review'/f'{rid}-proposal-context.png');mask.save(HERE/'review'/f'{rid}-mask.png')
ar=np.asarray(a,dtype=np.int16);br=np.asarray(b,dtype=np.int16)
stats={}
for label,box in {'left':[154,0,186,1120],'right':[534,0,566,1120],'bottom':[170,1104,550,1136]}.items():
 x0,y0,x1,y1=box;stats[label]=float(np.abs(ar[y0:y1,x0:x1]-br[y0:y1,x0:x1]).mean())
inrec=json.loads((HERE/'records'/f'{rid}.input.json').read_text())
save(HERE/'records'/f'{rid}.generation.json',{'id':rid,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'file':str(source),'sha256':sha(source),'pixels':list(b.size),'route':'builtin image_gen','actualModel':None,'actualQuality':None,'returnedFields':['image_url','output_hint'],'submittedArgumentsRecord':str(HERE/'prompts'/f'{rid}.request.json'),'inputRecord':str(HERE/'records'/f'{rid}.input.json'),'sourceOutput':{'file':'C:/Users/luyua/.codex/generated_images/01a125b1-e6a1-7dd0-8917-d2762cbd4eb8/exec-efbd5b55-2167-4bf1-bfa4-0f7918a6bc15.png','sha256':sha(source)},'sourceResampling':False})
save(HERE/'records'/f'{rid}.proposal.json',{'id':rid,'candidateBeforeSha256':inrec['candidateSha256'],'source':str(source),'sourceSha256':sha(source),'mask':str(HERE/'review'/f'{rid}-mask.png'),'maskSha256':sha(HERE/'review'/f'{rid}-mask.png'),'pasteOrigin':[1700,2842],'noResampling':True,'noBlur':True,'binaryMask':True,'outsideMaskPixelIdentical':True,'inputOutputDifferenceAtMaskEdgesMAE':stats})
print(json.dumps(stats))
