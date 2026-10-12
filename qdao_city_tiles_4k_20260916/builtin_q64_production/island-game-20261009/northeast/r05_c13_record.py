from native_work import *
import sys,re
mode,ident=sys.argv[1:3]
reason=' '.join(sys.argv[3:])
p=ZONE/'native'/f'{ident}.png.generation.json'
rec=read(p)
rec.update(status='usable_internal_reviewed' if mode=='accept' else 'rejected_preserved',internalSeams='passed_reviewed_available_neighbors' if mode=='accept' else 'failed',reviewNote=reason,reviewedAtUtc=now())
write(p,rec)
if mode=='accept':
 s=ZONE/'selection-r05_c13.json'
 sel=read(s) if s.exists() else {'tileId':'r05_c13','cores':[[None]*4 for _ in range(4)],'overlays':[],'actualModel':None,'actualQuality':None}
 r,c=map(int,re.search(r'_p(\d{2})_(\d{2})',ident).groups());sel['cores'][r-1][c-1]=ident;sel['updatedAtUtc']=now();write(s,sel)
 for q in (ZONE/'qa').glob('*__'+ident+'.json'):
  d=read(q);d.update(status='passed_visual_100pct',geometryChecks={'note':reason},reviewedAtUtc=now());write(q,d)
write(ZONE/'qa'/f'{ident}.review.json',{'id':ident,'sha256':sha(ZONE/'native'/f'{ident}.png'),'status':rec['status'],'note':reason,'reviewedAtUtc':now(),'formalAccepted':False})
print(ident,rec['status'])

