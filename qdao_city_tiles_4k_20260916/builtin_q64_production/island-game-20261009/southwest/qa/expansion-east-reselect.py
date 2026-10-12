from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import native_multi_tile_repair as m
base,prefix,sourceid,oldid,*box=sys.argv[1:]
sourceid,oldid=int(sourceid),int(oldid);x0,y0,x1,y1=map(int,box)
report=m.load(ROOT/'qa'/f'{base}-report.json')
inputs=report['inputs'];gb=report['candidateGlobalBox'];src=next(s for s in inputs if s['sourceId']==sourceid)
art=np.array(Image.open(ROOT/'qa'/f'{base}-candidate-4096.png'));ids=np.array(Image.open(ROOT/'qa'/f'{base}-source-id-mask.png'))
old=art.copy();oldids=ids.copy();yy,xx=np.indices(ids.shape)
selection=(ids==oldid)&(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
ny,nx=np.where(selection);sb=src['nativeGlobalBox'];raw=np.array(Image.open(src['path']))
sx,sy=nx+gb[0]-sb[0],ny+gb[1]-sb[1]
assert sx.min()>=0 and sx.max()<1254 and sy.min()>=0 and sy.max()<1254
art[ny,nx]=raw[sy,sx];ids[ny,nx]=sourceid
assert np.array_equal(art[~selection],old[~selection])
outputs=[]
for suffix,arr in [('candidate-4096',art),('source-id-mask',ids),('selection-mask',selection.astype(np.uint8)*255)]:
    path=ROOT/'qa'/f'{prefix}-{suffix}.png';assert not path.exists();Image.fromarray(arr).save(path);outputs.append({'path':path.as_posix(),'sha256':m.sha(path),'dimensions':[4096,4096]})
validation=m.validate_pixels(art,ids,inputs,gb);validation['unchangedOutsideSelection']=True
report.update({'status':'QA native hard selection candidate; pending visual review','baseReport':str(ROOT/'qa'/f'{base}-report.json'),'outputs':outputs,'validation':validation,'selectionRule':{'onlyReplaceSourceId':oldid,'replacementSourceId':sourceid,'tileLocalBox':[x0,y0,x1,y1],'pixelCount':int(selection.sum()),'coordinateTransform':'none; exact global coordinates'}})
m.QA.joinpath(prefix+'-report.json').write_text(json.dumps(report,indent=2)+'\n')
crop=[780,2700,1420,3250]
Image.fromarray(np.concatenate((old[crop[1]:crop[3],crop[0]:crop[2]],art[crop[1]:crop[3],crop[0]:crop[2]]),1)).save(ROOT/'qa'/f'{prefix}-review-native-before-left-after-right.png')
print(json.dumps({'candidate':outputs[0],'selectedPixels':int(selection.sum()),'validation':validation}))
