import json,sys
from pathlib import Path
root=Path(__file__).resolve().parent
from datetime import datetime, timezone
def write(p,j): p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if sys.argv[1]=='freeze':
    changed=[]
    for p in sorted((root/'native').glob('r09_c06_*_v1.png.generation.json')):
        if 'p01_01' in p.name: continue
        j=json.loads(p.read_text(encoding='utf-8-sig'))
        j['status']='frozen_upstream_geometry_repair'
        j['qaReason']='Wrong merchandise semantics: authoritative v10 prompt names blue/yellow fish market; this version mistakenly paints folded textile goods. Retain only as edit input until corrected native result/reference graph verified.'
        write(p,j);changed.append(p.name)
    write(root/'qa'/'r09_c06-merchandise-correction.json',{'time':datetime.now(timezone.utc).isoformat(),'evidence':str(root.parents[1]/'parallel_20261005/daylight-only-20261009/donghai-natural-stone-clear-routes-v10.prompt.txt'),'evidenceText':'blue/yellow fish market','frozenRecords':changed,'structuralOnlyUnchanged':'r09_c06_p01_01_v1','correction':'Replace folded textile merchandise with stylized fish market trays. Retain canopy and architecture geometry.'})
    print(json.dumps(changed))
elif sys.argv[1]=='request':
    patch=sys.argv[2]
    stem='r09_c06_'+patch+'_v2'
    p=root/'native'/(stem+'.request.json')
    j=json.loads(p.read_text(encoding='utf-8-sig'))
    j['references']=[{'path':(root/'native'/('r09_c06_'+patch+'_v1.png')).as_posix(),'role':'precise edit target; replace incorrect textile goods only, preserve all architectural pixels'},j['references'][0],*j['references'][1:4]]
    j['semanticCorrection']='Fish market merchandise: all folded fabric goods replaced with whole fish in shallow wooden trays. Blue awning fabric remains.'
    write(p,j)
    print(json.dumps(j['references']))
elif sys.argv[1]=='supersede':
    stem=sys.argv[2]
    old=root/'native'/(stem.replace('_v2','_v1')+'.png.generation.json')
    j=json.loads(old.read_text(encoding='utf-8-sig'));j['status']='superseded';j['supersededBy']=(root/'native'/(stem+'.png')).as_posix();write(old,j)

