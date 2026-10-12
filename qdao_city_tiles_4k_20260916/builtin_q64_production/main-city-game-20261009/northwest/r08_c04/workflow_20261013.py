from pathlib import Path
import sys,json
from PIL import Image
T=Path(__file__).resolve().parent; Z=T.parent; sys.path.insert(0,str(Z))
import production_v2 as p
TILE='r08_c04';N=Z/'r07_c04/candidate/r07_c04-candidate-native-bridges-2268d482e68c2928/candidate.png';NH='12a5ba0622b6ba365a7e89971a7d7682065f1194bdefe6c2d6141c28cece9a20'
ref=lambda f:{'file':str(f),'sha256':p.sha(f)}
def prepare(pid,version):
 reserved={x for b in p.read(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')['batches'] if b['map']=='main-city-game-20261009' and b['status']=='allocated_root_reserved' for x in b['tiles']};assert TILE not in reserved
 info=p.prepare(TILE,pid,version,'north,west');base=Image.open(T/'layout-only'/(pid+'.layout-only.png')).convert('RGB');target=info['worldBox'];anchors=[]
 for a in p.read(info['derivation'])['nativeNeighbors']:
  if a['tile']==TILE:
   nb=a['worldBox']; trusted=[nb[0]+115,nb[1]+115,nb[2]-115,nb[3]-115]; hit=p.overlap(target,trusted)
   if not hit:continue
   a=dict(a);a['sourceBox']=[hit[0]-nb[0],hit[1]-nb[1],hit[2]-nb[0],hit[3]-nb[1]];a['targetBox']=[hit[0]-target[0],hit[1]-target[1],hit[2]-target[0],hit[3]-target[1]];a['overlapWorldBox']=hit;a['anchorPolicy']='Only selected core pixels are authoritative; neighbor halo is not fixed artwork'
   base.paste(Image.open(a['file']).convert('RGB').crop(a['sourceBox']),a['targetBox'][:2]);anchors.append(a)
 assert p.sha(N)==NH;intersection=p.overlap(target,p.tile_box('r07_c04'))
 if intersection:
  box=p.tile_box('r07_c04');src=[intersection[0]-box[0],intersection[1]-box[1],intersection[2]-box[0],intersection[3]-box[1]];dst=[intersection[0]-target[0],intersection[1]-target[1],intersection[2]-target[0],intersection[3]-target[1]];base.paste(Image.open(N).convert('RGB').crop(src),dst[:2]);anchors.append({'tile':'r07_c04','file':str(N),'sha256':NH,'sourceBox':src,'targetBox':dst,'sourceResampled':False})
 f=T/'layout-only'/f'{pid}_{version}.actual-final-guide.png';p.save_png(f,base);p.write_json(f.with_suffix('.png.derivation.json'),{'role':'layout-only with exact native neighbor anchors; never production art','file':str(f),'sha256':p.sha(f),'nativeAnchors':anchors,'worldBox':target,'guideOnly':True,'originalGuide':info},replace=False);print(json.dumps({'guide':str(f),'worldBox':target,'nativeAnchors':anchors}))
def qa(identifier):
 pid=identifier[:6];r=int(pid[1:3]);c=int(pid[4:6]);source=T/'native'/(identifier+'.png');v=p.validate_native(source,T,pid);core=Image.open(source).convert('RGB').crop((115,115,1139,1139));D=T/'qa/source-review'/identifier;D.mkdir(parents=True,exist_ok=False);pieces={'target':core};refs={'target':ref(source)}
 for role,rr,cc in [('north',r-1,c),('west',r,c-1),('northwest',r-1,c-1)]:
  if 1<=rr<=4 and 1<=cc<=4:
   f=p.selected_path(T,f's{rr:02d}_{cc:02d}')
   if f.exists():pieces[role]=Image.open(f).convert('RGB').crop((115,115,1139,1139));refs[role]=ref(f)
  elif rr==0 and 1<=cc<=4:
   pieces[role]=Image.open(N).convert('RGB').crop(((cc-1)*1024,3072,cc*1024,4096));refs[role]=dict(ref(N),sourceCoreLTRB=[(cc-1)*1024,3072,cc*1024,4096])
 defs={'north-seam':((1024,320),[('north',(0,864,1024,1024),(0,0)),('target',(0,0,1024,160),(0,160))]),'west-seam':((320,1024),[('west',(864,0,1024,1024),(0,0)),('target',(0,0,160,1024),(160,0))]),'northwest-junction':((320,320),[('northwest',(864,864,1024,1024),(0,0)),('north',(0,864,160,1024),(160,0)),('west',(864,0,1024,160),(0,160)),('target',(0,0,160,160),(160,160))])};crops=[]
 for name,(size,parts) in defs.items():
  if not all(role in pieces for role,_,_ in parts):continue
  im=Image.new('RGB',size)
  for role,b,xy in parts:im.paste(pieces[role].crop(b),xy)
  f=D/(name+'.png');p.save_png(f,im);crops.append(dict(ref(f),name=name,parts=parts,nativePixelScale=1))
 p.write_json(D/'manifest.json',{'source':v,'neighbors':refs,'crops':crops,'actuallyViewed':False,'formalAccepted':False},replace=False);print({'source':str(source),'cropCount':len(crops)})
cmd=sys.argv[1]
if cmd=='prepare':prepare(*sys.argv[2:])
elif cmd=='qa':qa(sys.argv[2])
elif cmd=='request':print(p.record_request(TILE,sys.argv[2],T/'planned'/(sys.argv[2]+'.parameters.json')))
elif cmd=='select-issue':
 identifier,note=sys.argv[2:4];D=T/'qa/source-review'/identifier;m=p.read(D/'manifest.json');p.write_json(D/'review.json',{'source':m['source'],'reviewer':'/root','actuallyViewed':True,'viewedCrops':[dict(file=c['file'],sha256=c['sha256']) for c in m['crops']],'status':'selected_with_local_issue','finding':note,'fullTileInternalQAPassed':False,'formalAccepted':False},replace=False);print(p.record_selection(TILE,identifier[:6],identifier,note,str(D/'review.json')))
elif cmd=='select':
 identifier,note=sys.argv[2:4];D=T/'qa/source-review'/identifier;m=p.read(D/'manifest.json');p.write_json(D/'review.json',{'source':m['source'],'reviewer':'/root','actuallyViewed':True,'cropReviews':[dict(file=c['file'],sha256=c['sha256'],status='passed') for c in m['crops']],'status':'passed_available_local_neighbors','finding':note,'fullTileInternalQAPassed':False,'formalAccepted':False},replace=False);print(p.record_selection(TILE,identifier[:6],identifier,note,str(D/'review.json')))
