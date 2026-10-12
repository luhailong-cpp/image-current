from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest/work-r02_c04')
D=B/'resume-20261012-v02'; Q=D/'qa'; m=json.loads((D/'joint.assembly.json').read_text()); rgb=np.asarray(Image.open(D/'joint.context.png')).copy(); ids=np.asarray(Image.open(D/'joint.source-id.png')).copy(); ox,oy=m['globalBox'][:2]
s=next(s for s in m['sources'] if s['sourceId']==63); a=np.asarray(Image.open(s['file'])); box=[15245,6930,15520,7270]; x0,y0,x1,y1=box
src=a[y0-s['globalNativeBox'][1]:y1-s['globalNativeBox'][1],x0-s['globalNativeBox'][0]:x1-s['globalNativeBox'][0]]; old=rgb[y0-oy:y1-oy,x0-ox:x1-ox]; oldids=ids[y0-oy:y1-oy,x0-ox:x1-ox]; mask=np.isin(oldids,[64,63,54,60]); old[mask]=src[mask]; oldids[mask]=63
Image.fromarray(rgb[6948-oy:7388-oy,15140-ox:15580-ox]).save(Q/'junction-3-3.reseam-try-v01.png')
Image.fromarray(rgb[6800-oy:7480-oy,14900-ox:15700-ox]).save(Q/'junction-3-3.reseam-wide-try-v01.png')
Image.fromarray(mask.astype(np.uint8)*255).save(Q/'junction-3-3.reseam-try-v01.mask.png')
json.dump({'globalBox':box,'sourceId':63,'pixels':int(mask.sum()),'sourceFile':s['file'],'status':'visual-trial-not-final','resampled':False},open(Q/'junction-3-3.reseam-try-v01.json','w'),indent=2)

