"""Record one returned tool PNG and make its versioned native overlay candidate."""
from pathlib import Path
import argparse,json,hashlib,subprocess,sys
B=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(__doc__);p.add_argument('--id',required=True);p.add_argument('--source',required=True);a=p.parse_args()
R=B/'repairs/r13c06-water-seams-v1';rp=R/(a.id+'-v01.request.json');q=json.loads(rp.read_text(encoding='utf-8-sig'))
def run(args):
 z=subprocess.run([sys.executable,'-B']+args,capture_output=True,text=True)
 if z.returncode:print(z.stdout);print(z.stderr);raise SystemExit(z.returncode)
 return json.loads(z.stdout)
rec=run([str(B/'scripts/record-repair-v1.py'),'--request',str(rp),'--source',a.source,'--output',str(R/(a.id+'-v01.native.png'))])
base=Path(q['baseAssembly']['path']);assert hashlib.sha256(base.read_bytes()).hexdigest()==q['baseAssembly']['sha256']
m=json.loads(base.read_text());x,y,x1,y1=q['source']['contextCropBox'];w,h=m['context']['dimensions']
flags=[]
if x==0:flags.append('--open-left')
if y==0:flags.append('--open-top')
if x1==w:flags.append('--open-right')
if y1==h:flags.append('--open-bottom')
result=run([str(B/'scripts/apply-native-repair-v2.py'),'--base-assembly',str(base),'--base-sha256',q['baseAssembly']['sha256'],'--repair-generation',rec['record'],'--repair-generation-sha256',rec['recordSha256'],'--output-dir',f'qa/r13-c06-water-repair-{a.id}-v1']+flags)
print(json.dumps({'native':rec,'assembly':{k:result[k] for k in ('outputDirectory','assemblySha256','repairSourceId','selectedRepairPixels')},'mismatches':result['sourceReplay']['mismatches'],'uncovered':result['sourceReplay']['uncovered'],'visualQa':'pending'}))
