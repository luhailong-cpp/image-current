import sys
sys.dont_write_bytecode=True
import json,importlib.util,subprocess
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
def verify(r):
 p=Path(r['path']);assert prod.sha(p)==r['sha256'],p
def viewed(names):return [{**ref(z/'qa'/n),'result':'pass','reviewer':'root','viewedAtNativeScale':True} for n in names]
def save(p,a):
 assert not p.exists(),p
 prod.write(p,a)
def check_tiles(tiles):
 for t in tiles:
  verify(t['candidate']);verify(t['context'])
  a=Image.open(t['candidate']['path']).convert('RGB');b=Image.open(t['context']['path']).convert('RGB')
  assert a.size==(4096,4096) and b.size==(4326,4326)
  assert a.tobytes()==b.crop((115,115,4211,4211)).tobytes(),t['tile']
def export(tp,ap):
 subprocess.run([sys.executable,'-B',str(z/'qa/export-reviewed-versioned.py'),str(tp),str(ap)],check=True)
common={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'passed','reviewer':'root','scope':'Current native artwork and recorded internal/shared edges; remaining exterior neighbors still require later joint review.','runtimeGateActive':False,'all49TilesComplete':False}
h=read(z/'qa/r10_c03-final-art-handoff-v1.json')
for k in ['internalQa','joinAudit','trace']:verify(h[k])
tiles=[{'tile':c['tile'],'candidate':c,'context':next(q for q in h['contexts'] if q['tile']==c['tile'])} for c in h['candidates']]
check_tiles(tiles)
tp=z/'qa/block2x2-r09r10c03c04-v1-export-trace.json'
save(tp,{'createdAtUtc':common['createdAtUtc'],'sourceTrace':h['trace'],'handoff':ref(z/'qa/r10_c03-final-art-handoff-v1.json'),'tiles':tiles,'method':'Schema normalization only; native image files unchanged','nativePixelsResampled':False})
ap=z/'qa/block2x2-r09r10c03c04-v1-root-adoption-audit.json'
save(ap,{**common,'trace':ref(tp),'delegatedInternalAudit':h['internalQa'],'delegatedComplete21WindowJoinAudit':h['joinAudit'],'rootNativeSpotChecks':viewed(['block2x2-r09r10c03c04-v1-central-junction-100pct.png','block2x2-r09r10c03c04-v1-west-shared-3-100pct.png','block2x2-r09r10c03c04-v1-south-shared-2-100pct.png']),'compositionPreviewViewed':ref(z/'qa/block2x2-r09r10c03c04-v1-r10_c03-root-composition-preview.png'),'findings':['Detailed delegated 39-window internal and 21-window join passes accepted. Root inspected center, canopy and lantern joins and whole r10c03 composition; no blocking defect observed.'],'mechanical':{'allHashesVerified':True,'allCoresExactIntegerCropOfContext':True,'noImageResizeOnExport':True}})
export(tp,ap)
h=read(z/'qa/r10_c07-joint-handoff-20261012.json');verify(h['trace']);verify(h['audit']);check_tiles(h['tiles'])
tp=Path(h['trace']['path']);ap=z/'qa/block2x2-r09r10c06c07-v2-root-adoption-audit.json'
save(ap,{**common,'trace':ref(tp),'delegatedCompleteJoinAudit':h['audit'],'rootNativeSpotChecks':viewed(['block2x2-r09r10c06c07-v2-lamp-after-100pct.png','block2x2-r09r10c06c07-v2-grout-after-100pct.png','block2x2-r09r10c06c07-v2-notch-after-100pct.png','block2x2-r09r10c06c07-v2-central-junction-100pct.png']),'compositionPreviewViewed':ref(z/'qa/block2x2-r09r10c06c07-v2-r10_c07-root-composition-preview.png'),'findings':['Root independently inspected all three complete native repair crops, center junction and whole r10c07 composition. Lamp reflection and stone grout are coherent. Other windows inherit delegated reviewed pass.'],'mechanical':{'allHashesVerified':True,'allCoresExactIntegerCropOfContext':True,'noImageResizeOnExport':True}})
export(tp,ap)
tp=z/'qa/pair-r10r11c06-final-v5-trace.json';tr=read(tp);check_tiles(tr['tiles']);ap=z/'qa/pair-r10r11c06-final-v5-root-adoption-audit.json'
save(ap,{**common,'trace':ref(tp),'internalR11c06Audit':ref(z/'qa/r11_c06-internal-visual-audit-v2.json'),'previousR10c06JoinAudit':ref(z/'qa/block2x2-r09r10c06c07-v2-root-adoption-audit.json'),'rootNativeSpotChecks':viewed([f'pair-r10r11c06-final-v5-shared-part{i:02d}-100pct.png' for i in range(1,6)]+['pair-r10r11c06-final-v5-lantern-post-after-100pct.png','pair-r10r11c06-final-v5-east-endpoint-100pct.png']),'compositionPreviewViewed':ref(z/'qa/pair-r10r11c06-final-v5-r11_c06-root-composition-preview.png'),'findings':['All five original-scale shared-edge crops pass. Full native lantern repair contour reviewed; original post and exposed rear rail retained. Endpoint against current r10c07 remains visually coherent.','Future r11c07 corner and other exterior neighbors remain subject to four-tile QA.'],'mechanical':{'allHashesVerified':True,'allCoresExactIntegerCropOfContext':True,'noImageResizeOnExport':True}})
export(tp,ap)
subprocess.run([sys.executable,'-B',str(z/'qa/refresh-current-ledger.py')],check=True)

