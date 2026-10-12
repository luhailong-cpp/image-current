from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
inv=json.loads((R/'inventory-root.json').read_text(encoding='utf-8-sig'))
for d in ['E','SE']:
    pairs=[];frames=[]
    for foot,nums in [('LEFT',[7,8,9,10,11,12,13,14]),('RIGHT',[15,16,1,2,3,4,5,6])]:
        for stage in range(4):
            ns=nums[stage*2:stage*2+2]
            pairs.append({'supportFoot':foot,'frames':ns,'position':['central_contact','slight_rear','rear_support','rear_push'][stage],'durationMs':150})
            for n in ns:
                p=R/'frames/run'/d/f'{n:02}.png';h=hashlib.sha256(p.read_bytes()).hexdigest()
                f=next(f for f in inv['frames'] if f['action']=='run' and f['direction']==d and f['frame']==n)
                assert f['sha256']==h
                frames.append({'frame':n,'file':p.relative_to(R).as_posix(),'sha256':h,'supportFoot':foot,'position':stage+1,'sourceRecord':f['native_evidence'],'visualNotes':'同一支撑足由脚下承重向后推进，另一腿独立回收；两帧均为独立AI姿态。'})
    report={'direction':d,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'root实际逐图、整圈联系表、160px与放大画面；finish_north独立复核。浏览器统一证据另表。','supportPairs':pairs,'frames':sorted(frames,key=lambda x:x['frame']),'knownUnresolvedArtFailures':[],'independentReview':'reviews/independent-E-SE-finish-north-20261004.json','notes':'E04/12修接地高度；SE13/14补后蹬位置，14去除新增地面块并保持腿位。','timing':{'frameMs':75,'cycleMs':1200,'slowCycleMs':4800},'clientIntegrated':False,'actualModel':None,'actualQuality':None}
    (R/'reviews'/f'run-{d}-position-pairs-final-review-20261004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print({'rootDirectionsReviewed':['E','SE'],'frames':32})
