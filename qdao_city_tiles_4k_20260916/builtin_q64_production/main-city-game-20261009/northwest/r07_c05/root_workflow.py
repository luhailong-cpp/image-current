from pathlib import Path
import sys,json,argparse,re
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production_v2 as p
ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','ingest']);ap.add_argument('--id');ap.add_argument('--patch');ap.add_argument('--version',default='');ap.add_argument('--reason',default='Native output directly inspected; full seam and junction QA pending.');a=ap.parse_args()
t='r07_c05';d=p.ZONE/t
if a.action=='ingest':
 receipt=d/'receipts'/(a.id+'.host-result.json');r=p.read(receipt)
 host=re.search(r'as ([^\r\n]+?\.png) by default',r['output_hint']).group(1)
 result=p.ingest(t,a.id,host,receipt);p.record_selection(t,a.id[:6],a.id,a.reason);print(json.dumps(result))
else:
 result=p.prepare(t,a.patch,a.version,'north,west');print(json.dumps({k:result[k] for k in ['guide','nativeAnchors','missingNeighborSlots']}))
