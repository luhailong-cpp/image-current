"""Private root northward production; all guide transforms are non-final."""
import argparse,json,uuid
from pathlib import Path
from PIL import Image
import r06_c14_extension as b
import root_workflow as w
Z=w.Z
A=Z.parent/'accelerated-jewelry-approach'
def atomic(p,d):
 p=Path(p);t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(p)
def configure(tile):
 b.T=tile;b.ORIGIN=((int(tile[5:])-1)*4096,(int(tile[1:3])-1)*4096)
def selected(selection,key):
 d=json.loads(Path(selection).read_text(encoding='utf-8-sig'))['patches'][key]
 f=Path(d if isinstance(d,str) else d['path']);f=f if f.is_absolute() else Z/f
 if isinstance(d,dict):assert b.sha(f)==d['sha256']
 return f
def transferred(tile,patch):
 p=A/tile/'records'/f'{patch}.selection.json'
 if not p.exists():return None
 d=json.loads(p.read_text(encoding='utf-8-sig'));f=Path(d['file']);assert b.sha(f)==d['sha256'];assert Image.open(f).size==(1254,1254)
 g=json.loads(Path(d['generationRecord']).read_text(encoding='utf-8-sig'));r,c=int(patch[-2]),int(patch[-1]);x=(int(tile[5:])-1)*4096+(c-1)*1024;y=(int(tile[1:3])-1)*4096+(r-1)*1024
 assert g['globalCoreBox']==[x,y,x+1024,y+1024] and g['globalNativeBox']==[x-115,y-115,x+1139,y+1139]
 return f
def init(tile):
 configure(tile);p=Z/'records'/f'{tile}.coordinates.json';assert not p.exists()
 x,y=b.ORIGIN;refs=[b.ref(b.C['layoutReference'],'authoritative layout'),b.ref(b.C['detailStyleReference'],'materials only'),b.ref(b.C['primaryStyleReference'],'Q Daoist style only')]
 atomic(p,{'tile':tile,'tileOrigin':[x,y],'tileCoreBox':[x,y,x+4096,y+4096],'references':refs,'patches':[b.coords(f'{tile}_p{r}{c}') for r in range(1,5) for c in range(1,5)]})
 q=Z/'records'/f'{tile}.working-selection.json';assert not q.exists();atomic(q,{})
def prep(p,south_selection):
 tile=p[:7];configure(tile);co=b.coords(p);r,c=int(p[-2]),int(p[-1]);n=1254
 im=Image.open(b.C['layoutReference']).convert('RGB').transform((n,n),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)
 pure=Z/'guides'/f'{p}.layout-only.png'
 if pure.exists():assert Image.open(pure).convert('RGB').tobytes()==im.tobytes()
 else:im.save(pure)
 d=json.loads((Z/'records'/f'{tile}.working-selection.json').read_text(encoding='utf-8-sig'))
 south=f'r{int(tile[1:3])+1:02d}_c{int(tile[5:]):02d}'
 bottom=selected(south_selection,f'{south}_p1{c}') if r==4 else Z/'native'/d[f'{tile}_p{r+1}{c}']
 west=f'r{int(tile[1:3]):02d}_c{int(tile[5:])-1:02d}'
 left=transferred(west,f'p{r}4') if c==1 else Z/'native'/d[f'{tile}_p{r}{c-1}']
 sources=[]
 for f,side in [(left,'left'),(bottom,'bottom')]:
  if f is None:continue
  a=Image.open(f).convert('RGB');assert a.size==(n,n)
  crop=[1024,0,n,n] if side=='left' else [0,0,n,230];xy=[0,0] if side=='left' else [0,1024]
  im.paste(a.crop(crop),xy);rr=b.ref(f,'exact_native_'+side+'_230px');rr.update({'cropBox':crop,'pasteAt':xy});sources.append(rr)
 gp=Z/'guides'/f'{p}.native-edge-layout.png';assert not gp.exists();im.save(gp)
 atomic(str(gp)+'.derived.json',{'purpose':'generation guide only; never final pixels','coordinates':co,'sources':[b.ref(b.C['layoutReference'],'layout')]+sources,'operation':'EXTENT bicubic overview guide plus exact opaque native anchors; bottom owns lower corners','finalArt':False})
 refs=[b.ref(b.C['layoutReference'],'full-map layout only'),b.ref(b.C['detailStyleReference'],'independent materials only'),b.ref(b.C['primaryStyleReference'],'primary style only'),b.ref(gp,'local native edge geometry guide')]
 plan={'patchId':p,'createdAtUtc':b.now(),'coordinates':co,'references':refs,'nativeEdgeSources':sources,'expectedNativeSize':[n,n],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'guideCornerOwnership':'bottom owns lower corners','southSelection':b.ref(south_selection,'pinned southern candidate selection')}
 plan.update(b.config_evidence());atomic(Z/'records'/f'{p}.plan.json',plan)
 print(json.dumps({'patch':p,'guide':str(gp),'edges':sources,'coordinates':co},ensure_ascii=False))
def westqa():
 C=Z/'tiles'/'r05_c12.candidate-root-v2.png';assert b.sha(C)=='c1cc52322b48022a885146e66424e88461f2d3a685f63401f21dd66c0493ce33'
 Q=Z/'qa'/'r05_c12-root-v2'/'west-neighbor-QA';Q.mkdir(exist_ok=True);items=[]
 left={r:transferred('r05_c11',f'p{r}4') for r in range(1,5)};assert all(left.values())
 def qa(name,size,pieces):
  f=Q/(name+'.png');assert not f.exists();a=Image.new('RGB',size);src=[]
  for p,box,xy in pieces:a.paste(Image.open(p).convert('RGB').crop(box),xy);src.append(dict(b.ref(p,'native QA source'),cropBox=box,pasteAt=xy))
  a.save(f);items.append(dict(b.ref(f,'native1:1 QA'),sources=src,operation='exact integer crop and opaque paste',resized=False))
 for r in range(1,5):
  y=(r-1)*1024;qa(f'west-segment-r{r}',(256,1024),[(left[r],[1011,115,1139,1139],[0,0]),(C,[0,y,128,y+1024],[128,0])])
 for r in range(1,4):
  y=r*1024;qa(f'west-junction-r{r}',(512,512),[(left[r],[883,883,1139,1139],[0,0]),(left[r+1],[883,115,1139,371],[0,256]),(C,[0,y-256,256,y+256],[256,0])])
 atomic(Q/'manifest.json',{'candidate':b.ref(C,'root-v2 candidate'),'qa':items,'formalAccepted':False,'visualReview':'pending','neighborSelectionStatus':'candidate_pending_seam_QA','southwestJunction':'pending r06_c11 stable candidate'})
 print(str(Q))
def context(tile):
 configure(tile);x,y=b.ORIGIN;box=[int(x*1254/57344)-30,int(y*1254/57344)-25,int((x+4096)*1254/57344)+25,int((y+4096)*1254/57344)+25]
 f=Z/'guides'/f'{tile}.context-layout-only-root-v1.png';assert not f.exists();a=Image.open(b.C['layoutReference']).convert('RGB').crop(box);a.resize((a.width*6,a.height*6),Image.Resampling.NEAREST).save(f)
 atomic(str(f)+'.derived.json',{'purpose':'wider map context only; never final pixels','source':b.ref(b.C['layoutReference'],'layout only'),'sourceBox':box,'operation':'integer crop then nearest 6x for readability','finalArt':False});print(str(f))
def repair(p,version,target):
 plan=json.loads((Z/'records'/f'{p}.plan.json').read_text(encoding='utf-8-sig'));a=Image.open(target).convert('RGB');assert a.size==(1254,1254)
 for e in plan['nativeEdgeSources']:
  im=Image.open(e['path']).convert('RGB');a.paste(im.crop(e['cropBox']),e['pasteAt'][:2])
 gp=Z/'guides'/f'{p}-{version}.repair-native-guide.png';assert not gp.exists();a.save(gp)
 atomic(str(gp)+'.derived.json',{'purpose':'native repair guide only; not final pixels','coordinates':plan['coordinates'],'sources':[b.ref(target,'native target')]+plan['nativeEdgeSources'],'operation':'integer crop and opaque paste of existing edge anchors onto native target','finalArt':False})
 plan['references']=plan['references'][:3]+[b.ref(target,'exact native edit target'),b.ref(gp,'native repair geometry guide')];plan['createdAtUtc']=b.now();plan['repairTarget']=b.ref(target,'native target');plan['repairGuide']=b.ref(gp,'neighbor geometry guide');plan.update(b.config_evidence());pp=Z/'records'/f'{p}-{version}.plan.json';assert not pp.exists();atomic(pp,plan);print(str(gp))
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('op');q.add_argument('patch',nargs='?');q.add_argument('--south-selection');q.add_argument('--version');q.add_argument('--target');a=q.parse_args()
 if a.op=='init':init(a.patch)
 elif a.op=='prepare':prep(a.patch,a.south_selection)
 elif a.op=='westqa':westqa()
 elif a.op=='context':context(a.patch)
 elif a.op=='repair':repair(a.patch,a.version,a.target)
 elif a.op=='ingest':raise RuntimeError('use base ingestion with recorded source/version')
