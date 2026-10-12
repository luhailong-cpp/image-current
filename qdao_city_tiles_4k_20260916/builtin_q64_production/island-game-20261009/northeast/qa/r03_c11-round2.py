from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
mode, ident=sys.argv[1:3]
assert ident.startswith('r03_c11_')
if mode=='accept':
    seams=sys.argv[3:]
    for s in seams:
        p=ZONE/'qa'/f'{s}.json'; q=read(p); q.update(status='passed_visual_native_geometry_and_color',reviewedAtUtc=now(),geometryChecks={'manualAt100percent':True,'visibleDiscontinuity':False}); write(p,q)
    p=ZONE/'native'/f'{ident}.png.generation.json'; q=read(p); q.update(status='passed_internal_native_and_recorded_joins',qa=(ZONE/'qa'/f'{ident}.audit.json').as_posix()); write(p,q)
    write(ZONE/'qa'/f'{ident}.audit.json',{'id':ident,'sha256':q['sha256'],'status':q['status'],'nativeSize':[1254,1254],'evidence':seams,'actualModel':None,'actualQuality':None,'resized':False,'feathered':False,'reviewedAtUtc':now()})
    p=ZONE/'selection-r03_c11.json'; sel=read(p); coord=ident.split('_p')[1].split('_v')[0].split('_'); r,c=map(int,coord); sel['cores'][r-1][c-1]=ident; sel['updatedAtUtc']=now(); write(p,sel)
    p=ZONE/'qa/r03_c11-progress.json'; q=read(p)
    for k in ['generated','accepted']:
        if ident not in q[k]:q[k].append(ident)
    q.update(status='active_native_generation_and_repairs',currentId=ident,updatedAtUtc=now(),selectedCoreIds=sel['cores']); write(p,q)
    print(ident+' accepted and selected locally')
