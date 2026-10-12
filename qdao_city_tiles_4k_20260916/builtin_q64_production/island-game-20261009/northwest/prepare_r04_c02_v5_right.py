"""Guide-only current r04_c03 v5 right anchors for r04_c02."""
from pathlib import Path
import argparse,json,sys
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent
import assemble_connected_tiles as connected
import apply_native_tile_repair as repair
p=argparse.ArgumentParser();p.add_argument('--row',type=int);p.add_argument('--source-attempt',default='a01');p.add_argument('--attempt',default='a02');a=p.parse_args()
cache=Z/'guides/r04_c02_r04c03_v5_right_anchors.json'
base=Z/'tiles/r04_c03_candidate-v5_4096.png';base_record=base.with_suffix('.native-repair.json')
if not cache.exists():
 padded,proof=connected.reconstruct_padded(base,base_record);entries=[]
 for row in (1,2,3,4):
  anchor=Z/'guides'/f'r04_c02_right_r04c03_v5_s{row:02d}_01.native-anchor.png';assert not anchor.exists()
  box=[0,(row-1)*1024,1254,(row-1)*1024+1254]
  Image.fromarray(padded[box[1]:box[3],box[0]:box[2]]).save(anchor)
  x,y=proof['tileOrigin'];gb=[x-115,y+(row-1)*1024-115,x-115+1254,y+(row-1)*1024-115+1254]
  entries.append({**repair.file_info(anchor),'nativeSize':[1254,1254],'row':row,'globalBox':gb,'role':'right adjacent exact r04c03 v5 core plus original verified halo','derivedFrom':{'image':proof['image'],'record':proof['record'],'rootAssembly':proof['rootAssembly'],'paddedCropBox':box},'resizing':False,'registration':False,'pixelSynthesis':False})
 cache.write_text(json.dumps({'operation':'same-coordinate native reference crops only','sourceProof':proof,'anchors':entries},indent=2)+'\n',encoding='utf8')
if a.row is None:print(str(cache));sys.exit(0)
assert a.row in (1,2,3,4)
data=json.loads(cache.read_text(encoding='utf8'));assert data['sourceProof']['image']==repair.file_info(base) and data['sourceProof']['record']==repair.file_info(base_record)
right=next(e for e in data['anchors'] if e['row']==a.row);repair.pinned(right,Z,'right native anchor')
oldstem=f'r04_c02_s{a.row:02d}_04_{a.source_attempt}';stem=f'r04_c02_s{a.row:02d}_04_{a.attempt}'
old=json.loads((Z/'guides'/f'{oldstem}.input.json').read_text(encoding='utf8'))
guide=Z/'guides'/f'{stem}.layout-with-native.png';contact=Z/'guides'/f'{stem}.native-reference-contact.png';deriv=Z/'guides'/f'{stem}.layout-with-native.derivation.json'
ip=Z/'guides'/f'{stem}.input.json';rp=Z/'guides'/f'{stem}.references.json'
assert all(not q.exists() for q in [guide,contact,deriv,ip,rp])
im=Image.open(old['inputs'][0]['path']).convert('RGB');rim=Image.open(right['path']).convert('RGB')
assert old['globalBox'][0]+1024==right['globalBox'][0] and old['globalBox'][1]==right['globalBox'][1]
im.paste(rim.crop((0,0,230,1254)),(1024,0));im.save(guide)
ns=old['neighbor'];panels=[Image.open(n['path']).convert('RGB') for n in ns]+[rim]
Image.fromarray(np.concatenate([np.array(im) for im in panels],axis=1)).save(contact)
d={'operation':'layout-only guide with exact top/left plus current verified right tile strip','isAiGeneration':False,'sourceGuide':old['inputs'][0],'rightAnchor':right,'rightSourceCrop':[0,0,230,1254],'destination':[1024,0],'cornerRule':'current right tile wins last; original top/left retained in contact','resizingNeighbors':False,'registration':False,'pixelSynthesis':False,'output':repair.file_info(guide)}
deriv.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
inputs=[{**repair.file_info(guide),'nativeSize':[1254,1254],'role':'layout guide with actual unscaled native strips; not final art'}]+old['inputs'][1:4]+[{**repair.file_info(contact),'nativeSize':[1254*len(panels),1254],'role':'unscaled contact of '+','.join([n['direction'] for n in ns]+['right current r04c03 v5']),'derivedFrom':ns+[right]}]
out={**old,'versionStem':stem,'attempt':a.attempt,'inputs':inputs,'imageGenReferencedImagePaths':[n['path'] for n in inputs],'guideDerivation':repair.file_info(deriv),'rightVerifiedTileAnchor':right,'operation':d['operation']}
ip.write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');rp.write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf8');print(json.dumps({'stem':stem,'guide':str(guide)}))
