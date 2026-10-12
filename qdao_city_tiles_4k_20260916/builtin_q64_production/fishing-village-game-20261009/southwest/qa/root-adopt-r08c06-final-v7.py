import sys
sys.dont_write_bytecode=True
import json,importlib.util,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
def verify(r):
 assert prod.sha(r['path'])==r['sha256'],r['path']
def save(p,v):
 assert not p.exists()
 prod.write(p,v)
h=read(z/'qa/r08c06-south-final-v7-handoff.json');verify(h['artQa']);verify(h['finalTrace'])
tiles=[{'tile':t,**v} for t,v in h['delivery'].items()]
arr={}
old={e['tile']:e for e in read(z/'art-delivery-index.json')['artAccepted']}
for t in tiles:
 verify(t['candidate']);verify(t['context'])
 a=np.array(Image.open(t['candidate']['path']).convert('RGB'));b=np.array(Image.open(t['context']['path']).convert('RGB'));arr[t['tile']]=b
 assert a.shape==(4096,4096,3) and b.shape==(4326,4326,3)
 assert np.array_equal(a,b[115:4211,115:4211])
 if t['tile'] in ['r09_c05','r09_c06','r09_c07']:
  prev=np.array(Image.open(old[t['tile']]['nativeContext']['path']).convert('RGB'))
  assert np.array_equal(prev[751:],b[751:])
assert np.array_equal(arr['r08_c06'][-230:],arr['r09_c06'][:230])
assert np.array_equal(arr['r09_c05'][:,-230:],arr['r09_c06'][:,:230])
assert np.array_equal(arr['r09_c06'][:,-230:],arr['r09_c07'][:,:230])
tp=z/'qa/r08c06-south-final-v7-export-trace.json'
save(tp,{'createdAtUtc':prod.now(),'sourceTrace':h['finalTrace'],'handoff':ref(z/'qa/r08c06-south-final-v7-handoff.json'),'tiles':tiles,'method':'Schema normalization only; original native image files unchanged','nativePixelsResampled':False})
ap=z/'qa/r08c06-south-final-v7-root-adoption-audit.json'
save(ap,{'createdAtUtc':prod.now(),'status':'passed','reviewer':'root','trace':ref(tp),'delegatedArtQa':h['artQa'],'rootNativeSpotChecks':[{'file':ref(z/'qa'/('r08c06-south-final-v7-'+n+'-100pct.png')),'result':'pass','viewedAtNativeScale':True} for n in ['south-shared-part05','east-shared-top-halo','north-south-corner']],'compositionPreviewViewed':ref(z/'qa/r08c06-south-final-v7-root-composition-preview.png'),'findings':['All three final native lantern corner views pass; rib, collar, hanging tassel, wooden supports and edges remain continuous. Whole r08c06 composition viewed and accepted.','Remaining original-scale checks inherit delegated audit, including nine affected internal windows and unchanged prior passes.'],'mechanical':{'allCoreAndContextHashesVerified':True,'allCoresExactNativeContextCrop':True,'threeNeighbor230PixelOverlapsExact':True,'allThreeExistingNeighborsRows751DownUnchanged':True},'scope':'Recorded artwork internal/shared joins; remaining exterior neighbors pending later joint review','runtimeGateActive':False})
subprocess.run([sys.executable,'-B',str(z/'qa/export-reviewed-versioned.py'),str(tp),str(ap)],check=True)
subprocess.run([sys.executable,'-B',str(z/'qa/refresh-current-ledger.py')],check=True)

