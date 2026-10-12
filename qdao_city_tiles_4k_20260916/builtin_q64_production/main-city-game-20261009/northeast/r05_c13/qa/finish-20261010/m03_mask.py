from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import numpy as np,json,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rid='m03-road-v1';source=HERE/'source'/f'{rid}.png';inp=HERE/'inputs'/f'{rid}.png'
a=Image.open(inp).convert('RGB');b=Image.open(source).convert('RGB');assert a.size==b.size==(1254,1254)
y,x=np.mgrid[0:1254,0:1254]
wx=np.minimum(np.clip((x-80)/430,0,1),np.clip((1080-x)/390,0,1))
wy=np.minimum(np.clip((y-60)/110,0,1),np.clip((1194-y)/110,0,1))
mask=Image.fromarray(np.rint(wx*wy*255).astype('uint8'),'L')
d=ImageDraw.Draw(mask)
# Exact original grout/bevels, paper and gold ornament retain their old pixels.
for pts in [[(747,0),(747,910)],[(1018,0),(1018,1005)],[(0,477),(747,477)],[(747,240),(1253,240)],[(747,655),(1253,655)],[(747,869),(1253,869)],[(0,906),(747,906)],[(0,1002),(1253,1002)],[(0,1163),(1253,1163)],[(529,906),(529,1002)],[(1174,906),(1174,1002)],[(225,1002),(225,1253)]]:
 d.line(pts,fill=0,width=20)
d.rectangle([327,180,446,270],fill=0)
d.rectangle([650,82,721,153],fill=0)
d.rectangle([1180,790,1253,1010],fill=0)
mp=HERE/'review'/f'{rid}-material-mask.png';mask.save(mp)
out=a.copy();out.paste(b,(0,0),mask);out.save(HERE/'review'/f'{rid}-material-proposal.png')
save(HERE/'records'/f'{rid}.generation.json',{'id':rid,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'file':str(source),'sha256':sha(source),'pixels':list(b.size),'route':'builtin image_gen','actualModel':None,'actualQuality':None,'returnedFields':['image_url','output_hint'],'submittedArgumentsRecord':str(HERE/'prompts'/f'{rid}.request.json'),'inputRecord':str(HERE/'records'/f'{rid}.input.json'),'sourceOutput':{'file':'C:/Users/luyua/.codex/generated_images/01a125b1-e6a1-7dd0-8917-d2762cbd4eb8/exec-07cafb61-6dc2-4a6f-b3ce-71c3288502fd.png','sha256':sha(source)},'sourceResampling':False})
rec={'id':rid,'source':str(source),'sourceSha256':sha(source),'mask':str(mp),'maskSha256':sha(mp),'pasteOrigin':[2445,2300],'maskNonzeroBox':list(mask.getbbox()),'method':'AI painted stone material with scalar edge weights, original grout and paper excluded','noImageBlur':True,'noSourceResampling':True,'noGeometryWarp':True,'originalGroutPreserved':True,'outsideMaskPixelIdentical':True,'candidateChanged':False}
save(HERE/'records'/f'{rid}.material-proposal.json',rec)
print(json.dumps({'dimensions':b.size,'sha256':sha(source)}))
