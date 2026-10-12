"""Record completed root contact-sheet observations, without accepting unfinished directions."""
from pathlib import Path
from revise_feet_20261003 import ROOT,read,save,sha,now
REV=ROOT/'review/run-grounding-20261004'
files=['selection-east.json','selection-front.json','selection-north.json','selected-west.json','selection-south.json','selection-southeast.json','selection-root-southeast.json']
selected={}
for file in files:
    d=read(REV/file);assert d['staticReviewed'];selected.update(d['selected'])
notes={
 'E':'Near right support progresses from front to under-body, rear drive and extended terminal forefoot in01-08; far left in09-16. E heel-to-toe axis retained. Edited04/12 re-establish under-body load;06-08/14-16 extend calf instead of folding prematurely. Both hands and daggers retained.',
 'S':'Front-view toe axes face camera. A screen-right leg supports first half, B screen-left second. Rear toe contacts in05-08/13-16 read higher on screen due depth; paired edits extend shins and keep the opposite front boot raised/sole exposed. No forced same-y grounding.',
 'N':'Back-view heels stay aligned north. Screen-right support first half and screen-left second. N06-v2 connects05 through07-08 at comparable rear depth; each calf remains extended while opposite leg is folded for forward swing.',
 'NE':'Right support first half and left second. NE07-v2 removes former lateral return between06 and08. Knees, calves and forefoot follow the NE track. Raised rear heel can expose sole; that alone does not imply flight.',
 'W':'Left-facing boots follow W throughout.04/12 retain underbody support;05-08 and13-16 extend the original support behind while opposite knee/boot swings forward. W04-v2 and07-v2 selected; no added ground line visible.',
 'NW':'New01 heel/toe landing agrees with02 at front depth. Left support through08 and right through16.06/07-v2 preserve correct leg instead of crossed/misassigned rejects.07 has16-23px lowest-pixel variation relative to neighbors; this is not a sole-contact measurement. Reviewed extended calf and forefoot orientation, not mechanically aligned lowest pixels.',
 'SW':'First-half screen-left rear support continues from05 through06-v2 and07/08-v2; raised heel/extended ankle make the forefoot read down the SW axis. Large front boot remains the opposite swing leg. Second-half14-16 retain opposite support, with gradually extended rear leg. Both hands keep their daggers; no outward boot yaw.',
 'SE':'Full16 candidate sequence reviewed after both halves corrected. A near hip beneath blue tassel supports01-08; B far hip under long gold-edged panel supports09-16.05-v1/06-v2/07-v4/08-v2 preserve near-thigh rear drive while far leg swings;13-v3/14-16-v2 use a visible central overlap so the near airborne thigh crosses in front of the far support thigh.12-v1 retains underbody load. SE07-v3 whole-body shift was rejected. Foot axes project SE, with rear contact higher on-screen due depth. This is a2D contour/overlap interpretation, not skeletal or physical measurement.'}
out={}
for d,note in notes.items():
    frames={}
    for i in range(1,17):
        key=f'run_{d}_{i:02}';p=Path(selected.get(key,ROOT/f'frames/run/{d}/{i:02}.png'))
        if not p.is_absolute():p=ROOT/p
        frames[key]={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'candidate':key in selected}
    out[d]={'staticSequenceReviewed':True,'method':'Root viewed all16 cells at300px whole-canvas scale; edited natives viewed individually by root/generating agent. This is static pose/sequence review, not uninterrupted motion capture.', 'notes':note,'frames':frames}
save(REV/'root-candidate-sequence-audit.json',{'at':now(),'directions':out,'pendingDirections':[],'formalAcceptance':False,'clientTested':False})
print('Recorded all eight actual candidate contact-sheet reviews; export/playback acceptance separate.')
