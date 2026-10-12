import sys
sys.dont_write_bytecode=True
import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
z=Path(__file__).resolve().parent.parent;q=z/'qa'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def write(p,v):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
t=read(q/'repair-r11_c05-internal-v1-trace.json')
old=q/'r11_c05-internal-visual-audit-v1.json';a=read(old)
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r11_c05','status':'internal_visual_qa_passed','reviewer':'root','candidate':t['candidate'],'context':t['context'],'trace':ref(q/'repair-r11_c05-internal-v1-trace.json'),'priorNative39WindowAudit':ref(old),'validation':'All 39 original native windows were visually reviewed; unchanged areas retain previous pass. One local cylinder-foot issue repaired and full 1254px source-aligned after crop visually reviewed at native scale. Smooth gold band and cylinder silhouette; no visible local boundary break.','repairAfterViewed':ref(q/'repair-r11_c05-internal-v1-cylinder-foot-after-100pct.png'),'issues':[],'externalJoinsVerified':False}
ap=q/'r11_c05-internal-visual-audit-v2.json';write(ap,audit)
subprocess.run([sys.executable,'-B',str(q/'adopt-internal-audit.py'),str(ap)],check=True)
manifest={'outputPrefix':'pair-r10c05-c06-current-v1','inputs':[{'tile':'r10_c05','context':ref(q/'block2x2-r09r10c05c06-v1-r10_c05-context-native.png')},{'tile':'r10_c06','context':ref(q/'pair-r10r11c06-final-v5-r10_c06-context-native.png')}],'provenance':[ref(q/'block2x2-r09r10c05c06-v1-trace.json'),ref(q/'pair-r10r11c06-final-v5-trace.json')]}
mp=q/'pair-r10c05-c06-current-v1.manifest.json';write(mp,manifest)
subprocess.run([sys.executable,'-B',str(q/'native-pair-compose.py'),'--manifest',str(mp)],check=True)
pt=read(q/'pair-r10c05-c06-current-v1-trace.json')
bm={'outputPrefix':'block2x2-r10r11c05c06-v1','topJoint':pt['context'],'southwest':t['context'],'southeast':ref(q/'pair-r10r11c06-final-v5-r11_c06-context-native.png'),'provenance':[ref(q/'pair-r10c05-c06-current-v1-trace.json'),ref(ap),ref(q/'pair-r10r11c06-final-v5-trace.json')],'globalContextBox':[16269,36749,24691,45171],'tiles':['r10_c05','r10_c06','r11_c05','r11_c06']}
bp=q/'block2x2-r10r11c05c06-v1.manifest.json';write(bp,bm)
subprocess.run([sys.executable,'-B',str(q/'block2x2-generic-compose.py'),'--manifest',str(bp)],check=True)
