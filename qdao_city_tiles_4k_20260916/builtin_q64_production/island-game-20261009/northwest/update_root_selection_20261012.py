from pathlib import Path
import hashlib,json,argparse
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def rec(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
ap=argparse.ArgumentParser();ap.add_argument('--tile',required=True);ap.add_argument('--row',type=int,required=True);ap.add_argument('--col',type=int,required=True);ap.add_argument('--attempt',required=True);a=ap.parse_args();assert 1<=a.row<=4 and 1<=a.col<=4
p=Z/'root-current-selection-20261012.json'
d=read(p) if p.exists() else {'schemaVersion':1,'agent':'root','tiles':{}}
t=d['tiles'].setdefault(a.tile,{'matrix':[[None]*4 for _ in range(4)],'assembled4k':False,'internalClosurePassed':False,'formalAccepted':False,'cells':[],'selectedCount':0,'requiredCount':16})
stem=f'{a.tile}_s{a.row:02d}_{a.col:02d}_{a.attempt}';q=Z/'native'/f'{stem}.png';g=q.with_suffix('.png.generation.json');receipt=Z/'receipts'/f'{stem}.receipt.json';generation=read(g);assert generation['sha256']==rec(q)['sha256'] and generation['nativeWidth']==generation['nativeHeight']==1254 and generation['route']=='builtin'
t['matrix'][a.row-1][a.col-1]=a.attempt
cell={'stem':stem,'image':rec(q),'generationRecord':rec(g),'receipt':rec(receipt),'selection':'provisional_pending_assembly_and_internal_QA'}
t['cells']=[x for x in t['cells'] if x['stem'].rsplit('_',1)[0]!=stem.rsplit('_',1)[0]]+[cell];t['selectedCount']=len(t['cells'])
d['updatedAtUtc']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'tile':a.tile,'selectedCount':t['selectedCount'],'record':rec(p)}))
