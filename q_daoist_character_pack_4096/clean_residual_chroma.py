"""Remove only residual magenta key-color pixels after RGBA resampling.

This deterministic matting step never redraws character art. Records retain the
raw generator and primary processor provenance plus this additional operation.
"""
from pathlib import Path
import argparse,hashlib,json,io,time
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('ids',nargs='+')
 parser.add_argument('--distance',type=int,default=155)
 args=parser.parse_args()
 if not 130<=args.distance<=170:parser.error('Keep distance in the conservative 130-170 key range')
 for stem in args.ids:
  if not stem.replace('_','').isalnum():parser.error('Use existing portrait stems only')
  p=ROOT/f'{stem}.png';rp=ROOT/'records'/f'{stem}.json';record=json.loads(rp.read_text(encoding='utf-8'))
  before=hashlib.sha256(p.read_bytes()).hexdigest()
  with Image.open(p) as im:
   assert im.mode=='RGBA' and im.size==(4096,4096)
   array=np.array(im)
  diff=array[:,:,:3].astype(np.int32)-np.array([255,0,255],dtype=np.int32)
  mask=(np.sum(diff*diff,axis=2)<=args.distance**2)&(array[:,:,3]>0)
  affected=int(np.count_nonzero(mask))
  if affected:
   array[mask]=[0,0,0,0]
   final=Image.fromarray(array)
   encoded=io.BytesIO();final.save(encoded,format='PNG',optimize=True)
   for attempt in range(12):
    try:p.write_bytes(encoded.getvalue());break
    except OSError:
     if attempt==11:raise
     time.sleep(0.25)
   record['additional_chroma_cleanup']={'script':'clean_residual_chroma.py','key_rgb':[255,0,255],'rgb_euclidean_distance_max':args.distance,'affected_nontransparent_pixels':affected,'method':'Set only residual pixels near the known magenta key to transparent black after RGBA resampling. No shape drawing, recoloring or geometric transformation.','sha256_before':before}
  with Image.open(p) as final:
   alpha=final.getchannel('A');assert alpha.getextrema()==(0,255)
   bounds=list(alpha.getbbox());assert min(bounds[0],bounds[1],4096-bounds[2],4096-bounds[3])>16
  record['subject_bounds']=bounds;record['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  rp.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps({'file':p.name,'affected_pixels':affected,'alpha_range':[0,255],'bounds':bounds},ensure_ascii=False))
if __name__=='__main__':main()