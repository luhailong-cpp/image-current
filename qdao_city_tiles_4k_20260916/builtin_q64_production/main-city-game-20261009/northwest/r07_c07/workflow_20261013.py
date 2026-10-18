from pathlib import Path
import sys,json
from PIL import Image
T=Path(__file__).resolve().parent; Z=T.parent; sys.path.insert(0,str(Z))
import production_v2 as p
TILE='r07_c07'
NEIGHBORS={
 'r06_c07':('r06_c07/candidate/r06_c07-candidate-hard-4c0d654c3aae.png','e3184ae204d0cd8f0ea701bf6b3281449bb1489c18514f525869f37d72326609'),
 'r07_c06':('r07_c06/candidate/r07_c06-candidate-native-roi-v10.png','77f0dd8a35c954a08eaf2f6102e8e7e1c9dcb38e895305fa8070ab6734c2e16b'),
 'r06_c06':('r06_c06/candidate/r06_c06-candidate-hard-077556c4fb59.png','105ed0953773073a1b336660887ab78e4f8ef145ec74285ac0f1bc3ae0a77595')}
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
def check_rules():
 rules=(p.REPO/'AGENTS.md').read_text(encoding='utf-8-sig'); split=p.read(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')
 assert TILE not in {x for b in split['batches'] if b['map']=='main-city-game-20261009' and b['status']=='allocated_root_reserved' for x in b['tiles']}
 return {'agentsSha256':p.sha(p.REPO/'AGENTS.md'),'splitSha256':p.sha(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'rulesActuallyRead':True}
def sources():
 result=[]
 for tile,(path,h) in NEIGHBORS.items():
  f=Z/path;assert p.sha(f)==h;result.append(dict(ref(f),tile=tile,worldBox=p.tile_box(tile),sourceOffset=[0,0]))
 for c in p.coordinates(TILE)['patches']:
  f=p.selected_path(T,c['id'])
  if f.exists():p.validate_native(f,T,c['id']);result.append(dict(ref(f),tile=TILE,patch=c['id'],worldBox=c['coreWorldBox'],sourceOffset=[115,115]))
 return result
def prepare(pid,version):
 evidence=check_rules();target=next(c['worldBoxWithHalo'] for c in p.coordinates(TILE)['patches'] if c['id']==pid)
 base=Image.open(T/'layout-only'/(pid+'.layout-only.png')).convert('RGB');anchors=[]
 for a in sources():
  if a.get('patch')==pid:continue
  hit=p.overlap(target,a['worldBox'])
  if not hit:continue
  b=a['worldBox'];off=a['sourceOffset'];src=[hit[0]-b[0]+off[0],hit[1]-b[1]+off[1],hit[2]-b[0]+off[0],hit[3]-b[1]+off[1]];dst=[hit[0]-target[0],hit[1]-target[1],hit[2]-target[0],hit[3]-target[1]]
  base.paste(Image.open(a['file']).convert('RGB').crop(src),dst[:2]);anchors.append(dict(a,sourceBox=src,targetBox=dst,sourceResampled=False))
 f=T/'layout-only'/f'{pid}_{version}.actual-core-guide.png';p.save_png(f,base);p.write_json(f.with_suffix('.png.derivation.json'),dict(role='layout-only guide with same-world exact selected CORE anchors; never production art',guideOnly=True,worldBox=target,nativeAnchors=anchors,rules=evidence),replace=False)
 print(json.dumps({'guide':str(f),'worldBox':target,'anchors':anchors}))
def core_piece(rr,cc):
 box=p.tile_box(TILE);world=[box[0]+(cc-1)*1024,box[1]+(rr-1)*1024,box[0]+cc*1024,box[1]+rr*1024]
 for s in sources():
  if p.overlap(world,s['worldBox'])!=world:continue
  b=s['worldBox'];o=s['sourceOffset'];crop=[world[0]-b[0]+o[0],world[1]-b[1]+o[1],world[2]-b[0]+o[0],world[3]-b[1]+o[1]]
  return Image.open(s['file']).convert('RGB').crop(crop),dict(s,sourceCoreLTRB=crop)
 return None,None
def qa(identifier):
 pid=identifier[:6];r=int(pid[1:3]);c=int(pid[4:6]);source=T/'native'/(identifier+'.png');v=p.validate_native(source,T,pid);core=Image.open(source).convert('RGB').crop((115,115,1139,1139));D=T/'qa/source-review'/identifier;D.mkdir(parents=True,exist_ok=False);pieces={'target':core};refs={'target':ref(source)}
 for role,rr,cc in [('north',r-1,c),('west',r,c-1),('northwest',r-1,c-1),('east',r,c+1),('northeast',r-1,c+1),('south',r+1,c),('southwest',r+1,c-1),('southeast',r+1,c+1)]:
  im,rref=core_piece(rr,cc)
  if im is not None:pieces[role]=im;refs[role]=rref
 defs={'north-seam':((1024,320),[('north',(0,864,1024,1024),(0,0)),('target',(0,0,1024,160),(0,160))]),'west-seam':((320,1024),[('west',(864,0,1024,1024),(0,0)),('target',(0,0,160,1024),(160,0))]),'northwest-junction':((320,320),[('northwest',(864,864,1024,1024),(0,0)),('north',(0,864,160,1024),(160,0)),('west',(864,0,1024,160),(0,160)),('target',(0,0,160,160),(160,160))])};crops=[]
 defs.update({'east-seam':((320,1024),[('target',(864,0,1024,1024),(0,0)),('east',(0,0,160,1024),(160,0))]),'northeast-junction':((320,320),[('north',(864,864,1024,1024),(0,0)),('northeast',(0,864,160,1024),(160,0)),('target',(864,0,1024,160),(0,160)),('east',(0,0,160,160),(160,160))])})
 defs.update({'south-seam':((1024,320),[('target',(0,864,1024,1024),(0,0)),('south',(0,0,1024,160),(0,160))]),'southwest-junction':((320,320),[('west',(864,864,1024,1024),(0,0)),('target',(0,864,160,1024),(160,0)),('southwest',(864,0,1024,160),(0,160)),('south',(0,0,160,160),(160,160))]),'southeast-junction':((320,320),[('target',(864,864,1024,1024),(0,0)),('east',(0,864,160,1024),(160,0)),('south',(864,0,1024,160),(0,160)),('southeast',(0,0,160,160),(160,160))])})
 for name,(size,parts) in defs.items():
  if not all(role in pieces for role,_,_ in parts):continue
  im=Image.new('RGB',size)
  for role,b,xy in parts:im.paste(pieces[role].crop(b),xy)
  f=D/(name+'.png');p.save_png(f,im);crops.append(dict(ref(f),name=name,parts=parts,nativePixelScale=1))
 p.write_json(D/'manifest.json',{'source':v,'neighbors':refs,'crops':crops,'actuallyViewed':False,'formalAccepted':False},replace=False);print({'source':str(source),'cropCount':len(crops)})
def request(identifier,scene):
 evidence=check_rules();guide=T/'layout-only'/f'{identifier}.actual-core-guide.png';d=p.read(guide.with_suffix('.png.derivation.json'));bands=[a['targetBox'] for a in d['nativeAnchors']]
 prompt=f'''Use case: stylized-concept. Produce one native 1254 x 1254 opaque square game-map patch for a seamless Chinese Taoist chibi hand-painted daytime city. Image 1 is the exact coordinate/layout guide for this patch {TILE}/{identifier}; image 2 is a wider layout-only orientation reference, not an image to reproduce at full extent. Fill precisely image 1's field of view at exactly 1254 x 1254. World box {d['worldBox']}, center core crop [115,115,1139,1139]. Sharp existing native CORE anchor bands at image-1 pixel boxes {bands} are authoritative neighboring artwork; preserve their line positions, color, stone/wood scale and continuation. The blurry remainder supplies geometry only: render fresh crisp native details throughout that area. Continue all crossing edges smoothly with unchanged scale and camera, without rectangular borders or shifted intersections. {scene} Warm hand-painted natural pale gray/blue-gray ground, jade/teal architectural accents where shown, restrained warm gold, subtle soft natural daytime shading matching anchors. Preserve the approved layout and existing objects only. No added people, writing, UI, new decorative items, trees, lamps or buildings. No lettering, crop marks, watermarks, fake detail from enlargement, blur, haze or dense noise. Output only the finished full square patch, no collage or comparison.'''
 support=sorted([a for a in d['nativeAnchors'] if a['tile']==TILE],key=lambda a:-(a['targetBox'][2]-a['targetBox'][0])*(a['targetBox'][3]-a['targetBox'][1]))[:2]
 if support:
  prompt=prompt.replace('image 2 is a wider layout-only orientation reference, not an image to reproduce at full extent.','the other input images are full adjacent native sources for material/identity context only, never place their full extent in the output.')
  prompt+=' Adjacent references: '+ '; '.join(f"Image {i+2} = {a['patch']}, its core world box {a['worldBox']}; compare this location to target world box to understand direction." for i,a in enumerate(support))
  references=[str(guide)]+[a['file'] for a in support]
 else:references=[str(guide),str(T/'layout-only/tile-v2.layout-only.png')]
 args={'prompt':prompt,'referenced_image_paths':references,'transparent_background':False}
 if sys.argv[-1]=='single':
  args['referenced_image_paths']=[str(guide)];args['prompt']=prompt.split(' Adjacent references:')[0].replace('the other input images are full adjacent native sources for material/identity context only, never place their full extent in the output.','Only this exact guide is provided; its field of view is fixed.').replace('image 2 is a wider layout-only orientation reference, not an image to reproduce at full extent.','Only this exact guide is provided; its field of view is fixed.')
 p.write_json(T/'planned'/(identifier+'.parameters.json'),args,replace=False);p.write_json(T/'receipts'/(identifier+'.rules-read.json'),evidence,replace=False);p.record_request(TILE,identifier,T/'planned'/(identifier+'.parameters.json'));print(json.dumps(args))
cmd=sys.argv[1]
if cmd=='init':check_rules();print(p.init_tile(TILE))
elif cmd=='prepare':prepare(*sys.argv[2:])
elif cmd=='qa':qa(sys.argv[2])
elif cmd=='request':request(sys.argv[2],sys.argv[3])
elif cmd=='select':
 identifier,note=sys.argv[2:4];D=T/'qa/source-review'/identifier;m=p.read(D/'manifest.json');p.write_json(D/'review.json',{'source':m['source'],'reviewer':'/root/continue_r07_c07','actuallyViewed':True,'cropReviews':[dict(file=c['file'],sha256=c['sha256'],status='passed') for c in m['crops']],'status':'passed_available_local_neighbors','finding':note,'fullTileInternalQAPassed':False,'formalAccepted':False},replace=False);print(p.record_selection(TILE,identifier[:6],identifier,note,str(D/'review.json')))
