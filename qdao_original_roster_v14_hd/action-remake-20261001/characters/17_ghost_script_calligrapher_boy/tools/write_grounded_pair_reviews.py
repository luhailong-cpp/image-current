from pathlib import Path
from PIL import Image
import json,hashlib,datetime
b=Path(__file__).resolve().parents[1]
vs=json.loads((b/'review/grounded-pair-working-selection.json').read_text())
obs=json.loads((b/'review/grounded-pair-observations-20261004.json').read_text(encoding='utf-8'))
metrics={m['key']:m for m in json.loads((b/'review/grounded-pair-working-metrics.json').read_text())}
positions=['ahead_of_hip_landing','under_hip_weight_bearing','behind_hip_weight_bearing','farther_behind_broad_forefoot']
for direction,versions in vs.items():
    frames=[]
    for i,v in enumerate(versions,1):
        key=f'run-{direction}-{i:02d}-v{v}'; p=b/'staging'/f'{key}.png'
        im=Image.open(p); sha=hashlib.sha256(p.read_bytes()).hexdigest()
        rec=json.loads(p.with_suffix('.png.generation.json').read_text(encoding='utf-8-sig'))
        assert sha==rec['sha256'],key
        assert im.mode=='RGBA' and im.width==im.height and im.width>=1024,key
        assert not any(metrics[key]['edgeAlphaGT128'].values()),key
        frames.append({'n':i,'slot':f'run-{direction}-{i:02d}','key':key,'file':str(p).replace('\\','/'),'selectedFile':str(p).replace('\\','/'),'sha256':sha,'nativeSize':list(im.size),'mode':im.mode,'generationRecord':str(p.with_suffix('.png.generation.json')).replace('\\','/'),'durationMs':75,'actualObservedSupport':'right' if i<=8 else 'left','targetPositionSegment':positions[((i-1)%8)//2],'actualObservation':obs[direction][i-1],'handIdentity':'anatomical_right_brush_left_scroll','blueSpiritCount':2,'alphaEdgeGT128':metrics[key]['edgeAlphaGT128'],'staticLimbCandidate':True,'formalPass':False,'formalDynamicPass':False})
    segments=[]
    for n in range(0,16,2):
        segments.append({'frames':[n+1,n+2],'supportFoot':'right' if n<8 else 'left','intendedPosition':positions[(n%8)//2],'pairDurationMs':150,'distinctIndependentImages':frames[n]['sha256']!=frames[n+1]['sha256'],'observed':obs[direction][n:n+2]})
    data={'character':'17_ghost_script_calligrapher_boy','action':'run','direction':direction,'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'complete_16_selected_candidates_pending_integrated_playback','supersedes':'Earlier flight/4-contact schedules; latest same-foot eight-frame support requirement. Existing older files remain history until final export and cleanup.','latestUserRequirement':'同一只支撑脚连续推进，每个相对位置两张独立姿态，再换另一脚。','timing':{'frameCount':16,'uniformFrameMs':75,'cycleMs':1200},'counts':{'expected':16,'selected':16,'staticLimbCandidates':16,'formalVisualPassed':0,'formalDynamicPassed':0},'reviewEvidence':['Native source/result images inspected directly','Fixed whole-canvas 240px contact sheet; no bbox fitting','PNG/generation SHA and square RGBA checks','All selected edge alpha >128 counts zero'],'contactSheet':str(b/'review'/f'grounded-pair-working-{direction}-240.png').replace('\\','/'),'selectedForSequenceReview':frames,'twoFrameSegments':segments,'remainingReview':['Full 1200ms loop and phase joins must be played in parent final preview; this file does not claim playback acceptance.','NE support progression is compact and not every prompt coordinate was hit; evaluate perceived continuous support at 240px.' if direction=='NE' else 'E16 free heel approaches the support plane before E01; evaluate clean foot switch at 240px.','Existing coloured edge pixels are preserved; no alpha-cleaning algorithm, whole-image alignment, copied held frame, or timing alteration was used.'],'formalPass':False,'clientNotIntegrated':True}
    out=b/'review'/f'review-run-{direction}-grounded-pairs-20261004.json'
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(str(out))

