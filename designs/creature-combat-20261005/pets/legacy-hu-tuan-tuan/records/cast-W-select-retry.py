from pathlib import Path
import json, argparse
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('frame',choices=['02','03','08','09','10','11','12','13','14','15','16']);p.add_argument('retry');p.add_argument('reason');a=p.parse_args()
folder=ROOT/'runtime/cast/W'
old=folder/(a.frame+'.png');new=folder/(a.frame+'-'+a.retry+'.png')
oldrec=old.with_suffix('.png.generation.json');newrec=new.with_suffix('.png.generation.json')
for path in (old,new,oldrec,newrec):
    path.resolve().relative_to(ROOT)
    if not path.exists():raise RuntimeError(str(path))
rejected=json.loads(oldrec.read_text(encoding='utf-8'))
rejected.update(status='rejected-and-pixels-removed',reason=a.reason)
(ROOT/'records'/('rejected-cast-W-'+a.frame+'.generation.json')).write_text(json.dumps(rejected,ensure_ascii=False,indent=2),encoding='utf-8')
chosen=json.loads(newrec.read_text(encoding='utf-8'));chosen['file']='runtime/cast/W/'+a.frame+'.png';chosen['selectedRetry']=a.retry;chosen['selectionReason']=a.reason
old.write_bytes(new.read_bytes())
oldrec.write_text(json.dumps(chosen,ensure_ascii=False,indent=2),encoding='utf-8')
new.unlink();newrec.unlink()
print(old)
