import argparse,json
from pathlib import Path
import root_north_20261012 as n
import r06_c14_extension as b
Z=b.Z
def select(p,v,note):
 f=Z/'native'/f'{p}-{v}.png';assert f.exists()
 q=Z/'qa'/f'{p}-{v}.central-resume-review.json';assert not q.exists()
 seams=list((Z/'qa').glob(f'{p}-{v}-exact_native_*.png'))
 n.atomic(q,{'reviewer':'/root/central_resume','createdAtUtc':b.now(),'native':b.ref(f,'provisional native candidate'),'fullNativeViewed':True,'nativeSeamsViewed':[b.ref(s,'native1:1 seam QA') for s in seams],'status':'provisional_geometry_and_available_edges_pass','note':note,'formalAccepted':False})
 s=Z/'records'/f'{p[:7]}.working-selection.json';d=json.loads(s.read_text());d[p]=f.name;n.atomic(s,d)
 print(json.dumps({'selected':f.name,'selectedCount':len(d)}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('patch');a.add_argument('--version',default='v1');a.add_argument('--note',default='Layout and available native anchor boundaries align; pending full tile QA.');x=a.parse_args();select(x.patch,x.version,x.note)
