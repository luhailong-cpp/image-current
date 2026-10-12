from native_work import *
import sys
ident=sys.argv[1]
for a in sys.argv[2:]:
 p=ZONE/'qa'/f'{a}__{ident}.json'
 if not p.exists():p=ZONE/'qa'/f'{ident}__{a}.json'
 q=read(p);q.update(status='passed_cross_tile_core_segment_only' if a.split('_p')[0]!=ident.split('_p')[0] else 'passed_internal_only',reviewedAtUtc=now(),reviewer='root',geometryChecks={'visibleContours':'pass'},color='pass',scope='root direct1:1 join image plus four-way corner when applicable; individual1024 segment')
 write(p,q)
p=ZONE/'native'/f'{ident}.png.generation.json';q=read(p);q.update(status='usable_native_candidate',internalSeams='root reviewed current neighboring joins and corner',externalSeams='reviewed available core segments; others pending');write(p,q)
tile='_'.join(ident.split('_')[:2]);sp=ZONE/f'selection-{tile}.json';s=read(sp) if sp.exists() else {'tileId':tile,'cores':[[None]*4 for _ in range(4)],'overlays':[],'formalAccepted':False}
n=patch(ident)['coreWorldBox'];row=(n[1]%4096)//1024;col=(n[0]%4096)//1024;s['cores'][row][col]=ident;s['updatedAtUtc']=now();write(sp,s)
print(json.dumps({'id':ident,'sha256':q['sha256'],'selected':[row+1,col+1]}))

