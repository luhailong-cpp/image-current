"""Only r03_c02 guide/reference crops; final art is never synthesized here."""
from pathlib import Path
import argparse,json,sys
import numpy as np
from PIL import Image

Z=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Z))
import assemble_connected_tiles as connected
import apply_native_tile_repair as repair

p=argparse.ArgumentParser();p.add_argument('--row',type=int,required=True);p.add_argument('--source-attempt',default='a01');p.add_argument('--attempt',default='a02');a=p.parse_args()
assert a.row in (2,3,4)
cache=Z/'guides/r03_c02_r03c03_v5_right_anchors.json'
base=Z/'tiles/r03_c03_candidate-v5_4096.png';base_record=base.with_suffix('.native-repair.json')
if not cache.exists():
 padded,proof=connected.reconstruct_padded(base,base_record)
 entries=[]
 for row in (2,3,4):
  anchor=Z/'guides'/f'r03_c02_right_r03c03_v5_s{row:02d}_01.native-anchor.png'
  assert not anchor.exists()
  box=[0,(row-1)*1024,1254,(row-1)*1024+1254]
  Image.fromarray(padded[box[1]:box[3],box[0]:box[2]]).save(anchor)
  x,y=proof['tileOrigin'];global_box=[x-115,y+(row-1)*1024-115,x-115+1254,y+(row-1)*1024-115+1254]
  entries.append({**repair.file_info(anchor),'nativeSize':[1254,1254],'row':row,'globalBox':global_box,'role':'right adjacent unscaled native projection: exact r03c03 v5 core plus original verified halo','derivedFrom':{'image':proof['image'],'record':proof['record'],'rootAssembly':proof['rootAssembly'],'paddedCropBox':box},'resizing':False,'registration':False,'pixelSynthesis':False})
 cache.write_text(json.dumps({'operation':'same-coordinate native reference crops only','sourceProof':proof,'anchors':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data=json.loads(cache.read_text(encoding='utf-8'));assert data['sourceProof']['image']==repair.file_info(base) and data['sourceProof']['record']==repair.file_info(base_record)
right=next(e for e in data['anchors'] if e['row']==a.row);assert repair.pinned(right,Z,'right native anchor')['sha256']==right['sha256']
source_stem=f'r03_c02_s{a.row:02d}_04_{a.source_attempt}';stem=f'r03_c02_s{a.row:02d}_04_{a.attempt}'
old=json.loads((Z/'guides'/f'{source_stem}.input.json').read_text(encoding='utf-8'))
guide=Z/'guides'/f'{stem}.layout-with-native.png';contact=Z/'guides'/f'{stem}.native-reference-contact.png';deriv=Z/'guides'/f'{stem}.layout-with-native.derivation.json'
input_path=Z/'guides'/f'{stem}.input.json';refs_path=Z/'guides'/f'{stem}.references.json'
assert all(not q.exists() for q in (guide,contact,deriv,input_path,refs_path))
image=Image.open(old['inputs'][0]['path']).convert('RGB');right_image=Image.open(right['path']).convert('RGB')
assert old['globalBox'][0]+1024==right['globalBox'][0] and old['globalBox'][1]==right['globalBox'][1]
image.paste(right_image.crop((0,0,230,1254)),(1024,0));image.save(guide)
neighbors=old['neighbor'];panels=[Image.open(n['path']).convert('RGB') for n in neighbors]+[right_image]
Image.fromarray(np.concatenate([np.array(im) for im in panels],axis=1)).save(contact)
derivation={'operation':'layout-only guide with native left/top anchors plus verified v5 right native strip','isAiGeneration':False,'sourceGuide':old['inputs'][0],'rightAnchor':right,'rightSourceCrop':[0,0,230,1254],'destination':[1024,0],'cornerRule':'verified current right tile wins last; unchanged left/top source panels remain in contact','resizingNeighbors':False,'registration':False,'feathering':False,'pixelSynthesis':False,'output':repair.file_info(guide)}
deriv.write_text(json.dumps(derivation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
guide_info={**repair.file_info(guide),'nativeSize':[1254,1254],'role':'layout-only guide; exact native top/left strips and latest v5 right strip; not final art'}
contact_info={**repair.file_info(contact),'nativeSize':[1254*len(panels),1254],'role':'unscaled full neighbor contact: '+', '.join([n['direction'] for n in neighbors]+['right current r03c03 v5']),'derivedFrom':neighbors+[right]}
inputs=[guide_info]+old['inputs'][1:4]+[contact_info]
out={**old,'versionStem':stem,'attempt':a.attempt,'inputs':inputs,'imageGenReferencedImagePaths':[n['path'] for n in inputs],'guideDerivation':repair.file_info(deriv),'rightVerifiedTileAnchor':right,'operation':derivation['operation']}
input_path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');refs_path.write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'stem':stem,'input':str(input_path),'guide':str(guide),'rightTile':data['sourceProof']['image']}))
