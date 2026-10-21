"""Register one returned root core; append immutable selection and next guide."""
import argparse,json,subprocess,sys
from pathlib import Path
import native_batch as n
B=Path(__file__).resolve().parent.parent
def run(args):
    r=subprocess.run([sys.executable,'-B',str(B/'tools'/args[0]),*args[1:]],capture_output=True,text=True,encoding='utf-8')
    if r.returncode: raise RuntimeError(r.stderr or r.stdout)
    return json.loads(r.stdout)
p=argparse.ArgumentParser();p.add_argument('--tile',required=True);p.add_argument('--patch',required=True);p.add_argument('--event',required=True);p.add_argument('--prev',required=True);p.add_argument('--number',type=int,required=True);p.add_argument('--next');p.add_argument('--neighbor',action='append',default=[]);a=p.parse_args()
stem='root-'+a.tile.replace('_','')+'-'+a.patch
r=run(['receipt_register.py','--event-id',a.event,'--request','requests/'+stem+'-v001.request.json','--prompt','prompts/'+stem+'-v001.txt','--version',stem+'-native-v001'])
prev=(B/'selections'/a.prev).resolve();assert prev.is_relative_to(B)
s=json.loads(prev.read_text(encoding='utf-8-sig'));assert s['tile']==a.tile and a.patch not in s['patches']
s['patches'][a.patch]={k:r[k] for k in ['record','sha256','recordSha256']}
s['selectionVersion']='root-'+a.tile.replace('_','')+'-choice-v'+str(a.number).zfill(3)
out=B/'selections'/(s['selectionVersion']+'.json')
with out.open('x',encoding='utf-8') as f:json.dump(s,f,ensure_ascii=False,indent=2)
result={'registration':r,'selection':str(out),'selectedCount':len(s['patches'])}
if a.next:
    args=['native_batch.py','guide','--tile',a.tile,'--patch',a.next,'--selection',str(out)]
    for neighbor in a.neighbor:args+=['--selection',str(B/'selections'/neighbor)]
    args+=['--version','root-'+a.tile.replace('_','')+'-'+a.next+'-guide-v001']
    result['nextGuide']=run(args)
print(json.dumps(result,ensure_ascii=False))
