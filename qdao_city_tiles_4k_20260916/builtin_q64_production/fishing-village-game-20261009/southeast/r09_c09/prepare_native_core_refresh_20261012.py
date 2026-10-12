import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
pid,version=sys.argv[1:3]
sel=json.loads((R/'selected-patches.json').read_text());plan=json.loads((R/'coordinate-plan.json').read_text())
coord=next(x for x in plan['patches'] if x['id']==pid)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
original=R/sel['patches'][pid];image=Image.open(original).convert('RGB')
canvas=Image.open(R/'qa/full-resume-20261012-v1/candidate-4096.png')
r,c=int(pid[1])-1,int(pid[2])-1;ox,oy=c*1024-115,r*1024-115
box=[max(0,ox),max(0,oy),min(4096,ox+1254),min(4096,oy+1254)]
image.paste(canvas.crop(box),(box[0]-ox,box[1]-oy))
base=R/'layout-only'/f'{pid}-{version}-actual-core-target.png';image.save(base)
maskbox=[115,990,300,1139] if pid=='p23' else [115,985,285,1139]
guide=R/'layout-only'/f'{pid}-{version}-actual-core-hole-guide.png'
rgba=image.convert('RGBA');ImageDraw.Draw(rgba).rectangle([maskbox[0],maskbox[1],maskbox[2]-1,maskbox[3]-1],fill=(255,255,255,0));rgba.save(guide)
sourcepieces=[]
for qid,rel in sel['patches'].items():
 qr,qc=int(qid[1])-1,int(qid[2])-1;qx,qy=qc*1024,qr*1024
 xx0,yy0,xx1,yy1=max(box[0],qx),max(box[1],qy),min(box[2],qx+1024),min(box[3],qy+1024)
 if xx0<xx1 and yy0<yy1:sourcepieces.append({'patch':qid,'file':str(R/rel),'sha256':sha(R/rel),'sourceCrop':[xx0-qx+115,yy0-qy+115,xx1-qx+115,yy1-qy+115],'pasteAt':[xx0-ox,yy0-oy]})
record={'file':str(base),'sha256':sha(base),'dimensions':[1254,1254],'operation':'exact selected native CORE copies at native coordinates; source halos are not trusted inside a new core; no resizing','classification':'mechanical edit target input only; not new art','nativeBoxGlobal':coord['globalBox'],'coreSources':sourcepieces,'outsideTileFallback':{'file':str(original),'sha256':sha(original),'description':'only image area outside known full4096 tile core footprint'},'canvas':str(R/'qa/full-resume-20261012-v1/candidate-4096.png'),'canvasSha256':sha(R/'qa/full-resume-20261012-v1/candidate-4096.png')}
save(str(base)+'.derivation.json',record)
save(str(guide)+'.derivation.json',{'file':str(guide),'sha256':sha(guide),'source':str(base),'sourceSha256':sha(base),'dimensions':[1254,1254],'operation':'clear RGB white and alpha zero only in the faulty own-core rectangle; all surrounding core RGB unchanged','holeNative':maskbox,'classification':'mechanical input only'})
detail=('crisp yellow-green leaves and the fixed blue ridge upper silhouette in its left-bottom core' if pid=='p23' else 'the continuous diagonal ridge shadow and curved blue roof tiles in its left-bottom core')
prompt=f'''Use case: precise-object-edit. Image1 is one native1254x1254 game-world patch with a small transparent hole in its own core at {maskbox}. Reconstruct ONLY that hole as {detail}. Every surrounding opaque pixel is fixed actual selected neighbor CORE art at the correct coordinates, not an approximate enlarged guide. Connect every contour entering the hole at its exact fixed endpoint. Keep all opaque art geometry, tile widths/courses/grout/white highlights, leaf clusters, branches and ground seams at exactly their existing positions. Do not reframe or redraw the whole scene. Image2 is the same exact coordinate target before making the hole; its blurry/squared source strip inside the hole is a fault, not a style to preserve. The new hole art must naturally connect the fixed 115px left and bottom neighbor-core strips. No copied blurred halo rectangle or new horizontal rectangular boundary. Image3(A) authoritative full-map layout only, image4(B) independent daylight material style, image5(C) approved mail-daoist QDaoist painterly style. Keep the same crisp bright daylight game appearance. No objects added or moved, NPC/UI/text/grid/border, fog/grain/blur. Output opaque RGB native1254x1254 at the same footprint, 115px halo and center exact1024 core.'''
promptfile=R/f'{pid}-{version}.prompt.txt';promptfile.write_text(prompt,encoding='utf-8')
refs=[str(guide),str(base)]+[x['path'] for x in plan['references']]
roles={'1':'Exact native actual CORE neighbors with hole over own faulty core region','2':'Exact coordinate target before hole; faulty source strip inside hole must be repaired','3':'Authoritative full map layout only','4':'Independent daylight material style','5':'Approved QDaoist style only'}
req={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'referenceRoles':roles,'createdAt':datetime.now(timezone.utc).isoformat(),'referenceEvidence':[{'path':p,'sha256':sha(p),'role':roles[str(i)]} for i,p in enumerate(refs,1)]}
save(R/f'{pid}-{version}.request.json',req)
print(json.dumps({'pid':pid,'version':version,'guide':str(guide),'base':str(base),'hole':maskbox}))

