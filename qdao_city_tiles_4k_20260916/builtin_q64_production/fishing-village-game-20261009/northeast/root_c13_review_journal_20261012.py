import argparse,json
from pathlib import Path
import root_workflow as w
import r06_c14_extension as b
Z=w.Z;Q=Z/'qa'/'r05_c13-sol-v3';C=Z/'tiles'/'r05_c13.candidate-sol-v3.png';PIN='1a7ddce4f85656179a54b3a7b9d542560fd6efa22e7fb6286ae5feedd9cf9aa0'
q=argparse.ArgumentParser();q.add_argument('viewed',nargs='+');q.add_argument('--note',required=True);a=q.parse_args();assert b.sha(C)==PIN
f=Q/'root-independent-review-journal-20261012.json';d=json.loads(f.read_text(encoding='utf-8-sig')) if f.exists() else {'reviewer':'root','candidate':b.ref(C,'stable candidate'),'viewed':{},'internalNativeQAPassed':None,'formalAccepted':False}
for name in a.viewed:
 p=Q/(name+'.native-1to1.png');assert p.is_file();d['viewed'][name]=dict(b.ref(p,'root directly viewed native QA'),observations=a.note,viewedAtUtc=b.now())
d['updatedAtUtc']=b.now();d['viewedCount']=len(d['viewed']);w.atomic(f,d);print(json.dumps({'candidateSha256':PIN,'rootDirectlyViewed':len(d['viewed'])}))
