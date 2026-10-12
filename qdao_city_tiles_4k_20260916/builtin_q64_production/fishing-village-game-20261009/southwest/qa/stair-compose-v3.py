import json,hashlib
from pathlib import Path
Z=Path(__file__).resolve().parent.parent;D=Z/'stair-rebuild';Q=Z/'qa'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
p='repair-r10_c04-sixstep-v2';a={'tile':'r10_c04','context':ref(Q/(p+'-context-native.png')),'output':{**ref(Q/(p+'-candidate-4096.png')),'cropFromContext':[115,115,4211,4211]},'nativeProvenance':ref(Q/(p+'-trace.json')),'note':'Wrapper of verified v2 exact native composition for chained localized repair; no changed pixels.'}
ap=Q/(p+'-as-base-assembly.json');ap.write_text(json.dumps(a,indent=2)+'\n')
s='r10_c04_sixstep_roadjoin_v1';r=json.loads((D/(s+'.request.json')).read_text())
m={'schemaVersion':1,'outputPrefix':'repair-r10_c04-sixstep-v3','baseAssembly':ref(ap),'expectedBaseCandidateSha256':a['output']['sha256'],'repairs':[{'id':'roadjoin','source':ref(D/(s+'-source.png')),'repair':ref(D/(s+'.png')),'generationRecord':ref(D/(s+'.png.generation.json')),'tileContextBox':r['coordinates']['tileContextBox'],'repairBounds':[420,350,800,670],'margin':30}]}
(Q/'repair-r10_c04-sixstep-v3.manifest.json').write_text(json.dumps(m,indent=2)+'\n')

