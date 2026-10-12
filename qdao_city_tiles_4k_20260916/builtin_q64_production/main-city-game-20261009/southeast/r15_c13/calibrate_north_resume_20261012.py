from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent;R=T/'repairs-resume-20261012';Q=R/'local-qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
mp=Q/'trial-roof-mid-wood-left-roof-right-stone-relief-v2.json';m=json.loads(mp.read_text());p=Path(m['trial']['path']);cur=np.asarray(Image.open(p).convert('RGB')).copy()
north=T.parent/'r14_c13/candidate/r14_c13-4k-north-v6.png';a=np.asarray(Image.open(north).convert('RGB')).astype(float)
height=354;width=3254
# Exact-boundary photometric stitching only: source texture/geometry are unchanged.
# Harmonic extension of the RGB residual, with a zero residual at row354.
diff=a[-1,:width]-cur[0,:width].astype(float)+np.clip(a[-1,:width]-a[-2,:width],-3,3)
diff=np.clip(diff,-40,40)
diff[-160:]*=np.linspace(1,0,160)[:,None]
extended=np.concatenate([diff,diff[::-1]],axis=0);spectrum=np.fft.rfft(extended,axis=0);freq=2*np.pi*np.fft.rfftfreq(len(extended))
field=np.zeros((height,width,3),np.float32)
for y in range(height):
 decay=np.exp(-freq*y)*(1-y/height)
 field[y]=np.fft.irfft(spectrum*decay[:,None],n=len(extended),axis=0)[:width]
fp=R/'north-overlap-photometric-field-v1.npy';np.save(fp,field)
cur[:height,:width]=np.rint(np.clip(cur[:height,:width].astype(float)+field,0,255)).astype('uint8')
out=Q/'trial-north-calibrated-and-stone-v2.png';Image.fromarray(cur).save(out)
for i,x in enumerate([0,1024,2048,3072]):
 join=Image.new('RGB',(1024,700));join.paste(Image.fromarray(a.astype('uint8')).crop((x,3796,x+1024,4096)),(0,0));join.paste(Image.fromarray(cur).crop((x,0,x+1024,400)),(0,300));join.save(Q/('calibrated-north-quarter-'+str(i+1)+'.png'))
info={'parentManifest':{'path':str(mp),'sha256':sha(mp)},'operation':'add_float32_RGB_photometric_stitching_field_then_round_clip_uint8','field':{'path':str(fp),'sha256':sha(fp),'shape':list(field.shape),'targetXY':[0,0]},'fieldMethod':'RGB boundary residual from immutable northern last row plus clipped one-row gradient; clamp40; last160 columns fade; Fourier harmonic extension to zero by south row354; no warp, no resize, no blur of artwork','maxCorrection':float(np.max(np.abs(field))),'correctionPercentiles':np.percentile(np.abs(field),[50,90,99]).tolist(),'northSource':{'path':str(north),'sha256':sha(north)},'trial':{'path':str(out),'sha256':sha(out)},'resampled':False}
(Q/'trial-north-calibrated-and-stone-v2.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
