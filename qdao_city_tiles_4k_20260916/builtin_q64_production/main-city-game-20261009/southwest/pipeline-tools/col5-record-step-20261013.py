from pathlib import Path
from datetime import datetime,timezone
import sys,json,subprocess,hashlib
B=Path(__file__).resolve().parents[1];PY=sys.executable
request_name,source,hint,observation,ingest_flag,*next_patch=sys.argv[1:]
request=Path(request_name);req=json.loads(request.read_text(encoding='utf-8-sig'));tile=req['tile'];patch=req['coordinates']['id'];attempt=request.name[len(patch)+1:-len('.request.json')]
assert tile in ['r15_c05','r16_c05','r13_c05','r14_c05']
def run(args):
    r=subprocess.run([PY,'-X','utf8',*map(str,args)],capture_output=True,text=True,encoding='utf-8');print(r.stdout,end='');print(r.stderr,end='',file=sys.stderr);r.check_returncode()
run([B/'pipeline-tools/col5-save-return-20261012b.py',tile,patch,attempt,source,hint,observation])
receipt=B/tile/'pipeline/receipts'/f'{patch}.{attempt}.receipt.json'
if ingest_flag=='yes':run([B/'native_pipeline.py',tile,'ingest','--row',req['coordinates']['row'],'--col',req['coordinates']['column'],'--attempt',attempt,'--source',source,'--receipt',receipt])
native=list((B/tile/'native').glob('*.png'))
state={'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':tile,'owner':'/root/sw_col5_resume_20261012b','status':'native_production_active','selectedNativeSlots':len(native),'plannedNativeSlots':16,'latestRequest':str(request),'latestReceipt':str(receipt),'latestReceiptSha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'observation':observation,'currentModelPolicy':req.get('currentModelPolicy'),'actualModel':None,'actualQuality':None,'formalAccepted':False,'internalAccepted':False}
out=B/tile/'pipeline'/f'lane-step-{patch}.{attempt}.json';assert not out.exists();out.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if next_patch:
    row,col=next_patch;args=[B/'native_pipeline.py',tile,'prepare','--row',row,'--col',col,'--attempt','resume-20261013-v01']
    if row=='1':
        anchors=list((B/tile/'pipeline/anchors').glob('*-bottom230.native.png'));assert len(anchors)==1;args+=['--anchor-top',anchors[0]]
    run(args)
