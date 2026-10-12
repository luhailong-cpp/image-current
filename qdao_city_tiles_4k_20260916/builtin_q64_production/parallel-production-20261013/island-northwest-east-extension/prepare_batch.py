from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).resolve().parent
P=Path('D:/work/image')
S=P/'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for d in ['guides','native','prompts','receipts','qa','tiles']: (R/d).mkdir(exist_ok=True)
c=json.loads((S/'production-contract.json').read_text(encoding='utf-8-sig'))
layout=Image.open(c['layoutReference']).convert('RGB')
idx=json.loads((S/'northwest/current-adopted-20261012.json').read_text(encoding='utf-8-sig'))
refs=[c['layoutReference'],c['detailStyleReference'],str(P/'designs/mail-ui-v1/01-mail-event.png'),str(P/'designs/team-ui-v2/team-ui-v2.png')]
write(R/'references.json',[{'path':p,'sha256':sha(p),'nativeSize':list(Image.open(p).size)} for p in refs])
coords=[]
for r in [3,4]:
 tile=f'r{r:02d}_c05'; west=next(x['image']['path'] for x in idx['tiles'] if x['tileId']==f'r{r:02d}_c04')
 wi=Image.open(west).convert('RGB')
 for sr in range(1,5):
  for sc in range(1,5):
   stem=f'{tile}_s{sr:02d}_{sc:02d}'
   x=4*4096+(sc-1)*1024;y=(r-1)*4096+(sr-1)*1024
   box=[x-115,y-115,x+1139,y+1139]
   rb=[v*layout.width/57344 for v in box]
   guide=layout.transform((1254,1254),Image.Transform.EXTENT,rb,Image.Resampling.BICUBIC)
   path=R/'guides'/f'{stem}.layout-only.png';guide.save(path)
   record={'id':stem,'tile':tile,'subrow':sr,'subcolumn':sc,'nativeBox':box,'coreBox':[x,y,x+1024,y+1024],'guide':str(path),'guideSha256':sha(path),'layoutOnly':True,'finalUpscalingAllowed':False}
   if sc==1:
    # Native boundary shown at original pixel size in its exact canvas location.
    ref=guide.copy(); yy=(sr-1)*1024-115; top=max(0,yy);bot=min(4096,yy+1254)
    ref.paste(wi.crop((3981,top,4096,bot)),(0,top-yy))
    bp=R/'guides'/f'{stem}.west-boundary-context.png';ref.save(bp)
    record['westBoundaryContext']=str(bp);record['westSource']=west;record['westSourceSha256']=sha(west)
    record['boundaryContextMeaning']='Leftmost 115px actual west native neighbor; remainder layout-only proxy. Not final artwork.'
   coords.append(record)
write(R/'coordinates.json',coords)
write(R/'progress.json',{'status':'preparing_first_native','tiles':['r03_c05','r04_c05'],'targetCoreCount':32,'savedNativeCount':0,'formalAcceptedCount':0,'currentPatch':coords[0]['id'],'route':'built-in image_gen','actualModel':'not_returned','updatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print(json.dumps(coords[0]))
