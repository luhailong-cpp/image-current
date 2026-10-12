from production import *
sys.path.insert(0,str(B))
from assemble_r03_c03 import append_hard
D=W/'base-v1';D.mkdir(exist_ok=True);Q=D/'qa';Q.mkdir(exist_ok=True);sources={};strips=[];sids=[];cuts=[]
for r in range(1,5):
 for c in range(1,5):
  p=native(r,c);assert p;p=p.resolve();gp=Path(str(p)+'.generation.json');g=read(gp);key=(r-1)*4+c
  assert sha(p)==g['sha256'];assert [g['width'],g['height']]==[1254,1254] and not g['nativeScaleResampled'];assert g['route']=='builtin'
  req=read(g['evidence']['request']);prompt=Path(g['prompt']).read_text(encoding='utf-8-sig').strip();assert prompt==req['prompt'].strip()
  assert [q['file'] for q in g['references']]==req['referenced_image_paths']
  for q in g['references']:assert sha(q['file'])==q['sha256']
  assert all(str(ref).replace('\\','/') in [str(q['file']).replace('\\','/') for q in g['references']] for ref in REFS)
  sources[key]={'sourceId':key,'row':r,'column':c,'file':str(p),'sha256':sha(p),'globalNativeBox':g['globalNativeBox'],'generationRecord':str(gp),'generationRecordSha256':sha(gp)};im=np.asarray(Image.open(p).convert('RGB'));ii=np.full(im.shape[:2],key,np.uint16)
  if c==1:strip=im;sid=ii
  else:strip,sid,cut=append_hard(strip,sid,im,ii,f'row{r} col{c-1}-{c}');cuts.append(cut)
 strips.append(strip);sids.append(sid)
a=strips[0];ids=sids[0]
for r in range(1,4):
 a,ids,cut=append_hard(a.transpose(1,0,2),ids.T,strips[r].transpose(1,0,2),sids[r].T,f'row{r}-{r+1}');a=a.transpose(1,0,2);ids=ids.T;cuts.append(cut)
m=read(B/'work-r03_c02/west-final/final-joint.assembly.json');south=np.asarray(Image.open(southern_context()));currentids=np.asarray(Image.open(m['sourceIdFile']));gy,gx=np.indices(south.shape[:2]);gx+=8077;gy+=8077;si=currentids[np.clip(gy-8192,0,4095),np.clip(gx-4096,0,8191)].astype(np.uint16)+10000
for k in np.unique(si):sources[int(k)]={**m['sources'][str(k-10000)],'sourceId':int(k)}
a,ids,cut=append_hard(a.transpose(1,0,2),ids.T,south.transpose(1,0,2),si.T,'r02-r03');a=a.transpose(1,0,2);ids=ids.T;cuts.append(cut)
checks=[]
for k in np.unique(ids):
 s=sources[int(k)];im=np.asarray(Image.open(s['file']));yy,xx=np.nonzero(ids==k);b=s['globalNativeBox'];sx=xx+8077-b[0];sy=yy+3981-b[1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(a[yy,xx],im[sy,sx]);checks.append({'sourceId':int(k),'pixels':int(len(yy)),'mismatches':0})
p=D/'full-pair.png';ip=D/'source-id.png';Image.fromarray(a).save(p);Image.fromarray(ids).save(ip);tile=Image.fromarray(a[115:4211,115:4211]);tile.save(D/'r02_c03.candidate.png');Image.fromarray(ids[115:4211,115:4211]).save(D/'r02_c03.source-id.png')
write(D/'assembly.json',{'globalBox':[8077,3981,12403,9331],'candidate':{'file':str(p),'sha256':sha(p)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'sources':sources,'seams':cuts,'proof':{'pixels':int(ids.size),'mismatches':0,'contributions':checks},'status':'16-native-candidate-pending-all-seam-review','formalAccepted':False})
preview=tile.copy();preview.thumbnail((1536,1536),Image.Resampling.LANCZOS);preview.save(D/'overview-preview-only.png')
for j in range(4):
 v=Image.new('RGB',(1260,1024));h=Image.new('RGB',(1024,1260))
 for k in range(1,4):
  v.paste(tile.crop((1024*k-210,1024*j,1024*k+210,1024*(j+1))),((k-1)*420,0));h.paste(tile.crop((1024*j,1024*k-210,1024*(j+1),1024*k+210)),(0,(k-1)*420))
 v.save(Q/f'v-{j+1}.png');h.save(Q/f'h-{j+1}.png')
 Image.fromarray(a).crop((115+j*1024,3980,115+(j+1)*1024,4580)).save(Q/f'south-{j+1}.png')
sheet=Image.new('RGB',(1500,1500))
for j in range(1,4):
 for k in range(1,4):sheet.paste(tile.crop((k*1024-250,j*1024-250,k*1024+250,j*1024+250)),((k-1)*500,(j-1)*500))
sheet.save(Q/'nine-junctions.png')
print(json.dumps({'pixels':int(ids.size),'mismatches':0,'sources':len(checks),'candidate':str(D/'r02_c03.candidate.png')}))
