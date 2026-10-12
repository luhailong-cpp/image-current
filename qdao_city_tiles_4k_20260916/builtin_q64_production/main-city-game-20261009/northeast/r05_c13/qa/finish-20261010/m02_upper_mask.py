from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rid='m02-upper-v1';source=HERE/'source'/f'{rid}.png';inp=HERE/'inputs'/f'{rid}.png'
a=Image.open(inp).convert('RGB');b=Image.open(source).convert('RGB');assert a.size==b.size==(1254,1254)
y,x=np.mgrid[0:1254,0:1254]
wx=np.minimum(np.clip((x-200)/320,0,1),np.clip((1040-x)/300,0,1))
wy=np.minimum(np.clip((y-60)/130,0,1),np.clip((1000-y)/100,0,1))
mask=Image.fromarray(np.rint(wx*wy*255).astype('uint8'),'L');d=ImageDraw.Draw(mask)
for pts in [[(80,10),(540,251),(916,483)],[(0,328),(426,198)],[(540,251),(1080,103)],[(916,483),(234,737)],[(234,737),(393,906)],[(393,906),(1253,906)],[(0,1007),(1253,1007)],[(393,906),(393,1007)],[(689,906),(689,1007)],[(1023,906),(1023,1007)]]:d.line(pts,fill=0,width=24)
d.rectangle([210,260,510,450],fill=0)
mp=HERE/'review'/f'{rid}-material-mask.png';mask.save(mp)
out=a.copy();out.paste(b,(0,0),mask);out.save(HERE/'review'/f'{rid}-material-proposal.png')
save(HERE/'records'/f'{rid}.generation.json',{'id':rid,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'file':str(source),'sha256':sha(source),'pixels':list(b.size),'route':'builtin image_gen','actualModel':None,'actualQuality':None,'returnedFields':['image_url','output_hint'],'submittedArgumentsRecord':str(HERE/'prompts'/f'{rid}.request.json'),'inputRecord':str(HERE/'records'/f'{rid}.input.json'),'sourceOutput':{'file':'C:/Users/luyua/.codex/generated_images/01a125b1-e6a1-7dd0-8917-d2762cbd4eb8/exec-6093a7c3-8bfb-47da-afaa-c97b543f1f4b.png','sha256':sha(source)},'sourceResampling':False})
save(HERE/'records'/f'{rid}.material-proposal.json',{'id':rid,'source':str(source),'sourceSha256':sha(source),'mask':str(mp),'maskSha256':sha(mp),'pasteOrigin':[1421,2300],'maskNonzeroBox':list(mask.getbbox()),'method':'AI painted pale-stone material with scalar edge weights, original grout and paper excluded','noImageBlur':True,'noSourceResampling':True,'noGeometryWarp':True,'originalGroutPreserved':True,'outsideMaskPixelIdentical':True,'candidateChanged':False})
print(sha(source))
