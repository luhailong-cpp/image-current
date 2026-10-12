from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,numpy as np
d=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach/r05_c11/repairs/ground-halo-v1');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=read(d/'request.json');der=read(d/'target-derivation.json');raw=d/'native-result.png';im=Image.open(raw).convert('RGB');target=Image.open(d/'target-native.png').convert('RGB');assert im.size==target.size==(1254,1254)
g={'recordedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','file':str(raw),'sha256':sha(raw),'dimensions':[1254,1254],'prompt':req['prompt'],'references':[{'file':p,'sha256':sha(p)} for p in req['referenced_image_paths']],'requestedModel':None,'actualModel':None,'actualQuality':None,'paidApiUsed':False,'nativePixelsResized':False,'tile':'r05_c11','tileLocalBox':der['tileLocalBox'],'globalNativeBox':der['globalPixelBox'],'purpose':'Repair vertical guide halo discontinuity near tile x1933 through net and paving.'}
(d/'native-result.generation.json').write_text(json.dumps(g,indent=2)+'\n',encoding='utf-8')
x=np.arange(1254)[None,:];y=np.arange(1254)[:,None]
ax=np.minimum(np.clip((x-475)/65,0,1),np.clip((780-x)/70,0,1))
ay=np.minimum(np.clip((y-100)/50,0,1),np.clip((930-y)/30,0,1))
mask=Image.fromarray(np.uint8(np.rint(ax*ay*255)),'L');mask.save(d/'contribution-mask.png')
out=Image.composite(im,target,mask);out.save(d/'proposal-native.png')
q=d/'qa';q.mkdir(exist_ok=True)
out.crop((420,0,835,1100)).save(q/'repaired-band-native.png')
out.crop((400,480,900,980)).save(q/'ground-junction-native.png')
proposal={'tile':'r05_c11','targetTileBox':der['tileLocalBox'],'source':str(raw),'sourceSha256':sha(raw),'mask':str(d/'contribution-mask.png'),'maskSha256':sha(d/'contribution-mask.png'),'proposal':str(d/'proposal-native.png'),'proposalSha256':sha(d/'proposal-native.png'),'operation':'Pillow Image.composite(source, original target, saved L mask); final candidate same composite on tile crop at targetTileBox; all pixels outside mask preserved.','nativePixelsResized':False,'candidateChanged':False,'status':'awaiting_native_mask_boundary_QA'}
(d/'proposal.json').write_text(json.dumps(proposal,indent=2)+'\n',encoding='utf-8');print(json.dumps({'rawSha256':sha(raw),'proposal':str(d/'proposal-native.png')}))

