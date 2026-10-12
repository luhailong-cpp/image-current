from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=read(T/'canopy-edge-v1-selected.json');mid=read(T/'joint-edge-color-v1-selected.json');final=read(T/'colorpass-selected.json')
records=[]
for pid,rel in base['patches'].items():
 src=T/rel;aa=np.asarray(Image.open(src),dtype=np.float32);mp=T/mid['patches'][pid];result=np.asarray(Image.open(mp))
 replay=aa.copy();nx=28672+(int(pid[2])-1)*1024-115;ny=36864+(int(pid[1])-1)*1024-115
 if mp!=src:
  d=read(mp.with_suffix('.png.derivation.json'));assert sha(src)==d['baseSha256']
  for f in d['fields']:
   assert sha(f['path'])==f['sha256'];field=np.load(f['path'])['additiveRgb'];b=f['globalBox']
   x,y,x1,y1=max(nx,b[0]),max(ny,b[1]),min(nx+1254,b[2]),min(ny+1254,b[3])
   if x<x1 and y<y1:replay[y-ny:y1-ny,x-nx:x1-nx]+=field[y-b[1]:y1-b[1],x-b[0]:x1-b[0]]
 replay=np.uint8(np.clip(np.rint(replay),0,255));assert np.array_equal(replay,result)
 fp=T/final['patches'][pid];out=np.asarray(Image.open(fp),dtype=np.float32)
 maximum=float(np.abs(out-aa).max());assert maximum<=40
 records.append({'patch':pid,'geometrySource':str(src),'geometrySourceSha256':sha(src),'jointColorOutput':str(mp),'jointColorOutputSha256':sha(mp),'jointColorReplayedExactly':True,'final':str(fp),'finalSha256':sha(fp),'maxCumulativeRGBChangeFromGeometry':maximum})
ordinary_checks=all(read(str(T/final['patches'][pid])+'.derivation.json')['correctionEvidence']['reconstructionPixelsExactlyMatch'] for pid in final['patches'])
report={'tile':'r10_c08','patches':records,'allJointColorFieldsReconstruct':True,'ordinaryColorFieldsReconstructReportedByProducer':ordinary_checks,'ordinaryColorEvidence':str(T/'processed/colorpass/colorpass-report.json'),'maxCumulativeRGBChangeFromGeometry':max(r['maxCumulativeRGBChangeFromGeometry'] for r in records),'resamplingApplied':False,'geometryAcceptanceClaimed':False}
(T/'qa/color-pipeline-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'allJointColorFieldsReconstruct':True,'maxCumulative':report['maxCumulativeRGBChangeFromGeometry']}))
