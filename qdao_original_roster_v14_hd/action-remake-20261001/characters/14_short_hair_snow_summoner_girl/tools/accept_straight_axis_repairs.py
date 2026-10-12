"""Record completed human/agent visual observations, then bind them to current files."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,sys
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
at=datetime.now(timezone.utc).isoformat()
repairs={'attack/E/05.png':'d6f81b3bf2225020a8271b0a615b3084be1376d7ab43a69ee13485e3fe1f6341','attack/E/06.png':'9b3a0d9dcd9ac5a0ea6db88b77d594c8beef814b5cf861958636df18c1fd3219','run/SW/06.png':'1003c3d69b59f5fac3dad52acbe21f0013469ebdcc71c87761f62a7f6e1ab832'}
for f,h in repairs.items():assert sha(R/f)==h
assert (R/'audit/straight-axis-SW06-repair-peer.json').exists()
rv=read(R/'review.json')
for f,h in repairs.items():
    if not f.startswith('attack/'):continue
    key=f[:-4]
    rv[key]={'sha256':h,'visualStatus':'passed','reviewedAt':at,'reviewer':'root; independent peer north_run','scope':'Full-size current PNG plus E04/07 neighbors; fresh hash-versioned index normal and quarter-speed playback, paused512px E05→06. Offline visual review, not hardware FPS measurement or client integration.','notes':'Rear support toe now points E with heel behind and natural knee/cuff connection; kept attack stance, forward boot, two arms, left-held fox and right crystal.','clientValidated':False,'followupAudit':'audit/straight-axis-final-review.json'}
save(R/'review.json',rv)
c=read(R/'audit/contact-SW-review.json')
c['positionPairs'][2]['observations'] += ' 最新SW06仅后撑左靴鞋头/踝连接转回西南方向，仍是P3连续后移的第二张独立姿态，膝弯和支撑落点保留。'
save(R/'audit/contact-SW-review.json',c)
preview={'direction':'SW','normal':{'played':True,'cycleMs':1200,'canvasDisplayPx':240},'quarterSpeed':{'played':True,'cycleMs':4800,'canvasDisplayPx':240},'paused480pxFrames':[16,1,6],'staticHighResolutionRepairFrames':[6],'method':'2026-10-05 fresh straight-axis review: every current run frame actually inspected in directional static audits; root reloaded all128 current hash-versioned frames in CUA all-directions, played normal1200ms and quarter4800ms with representative screenshots, paused480px16→01 and06. SW05/06/07 original full-size files and final repair also viewed. Offline visual judgment, not measured rendering FPS or client integration.','observations':'SW06 rear support left boot previously faced nearly S/front; local AI correction restores SW down-left toe with heel behind/right, intermediate between05 and07. Original support knee, hip, landing point, right free leg, left fox and right crystal retained. Four spatial support pairs and16×75ms remain. N16 watch-only sole-side change was also checked in15/16/01 native images, slow playback and paused16→01: shank and shoe tilt together without isolated lateral flick.','recordedAt':at}
save(R/'audit/root-SW-preview-observations.json',preview)
subprocess.run([sys.executable,str(R/'tools/record_root_direction_preview.py'),'SW'],check=True)
subprocess.run([sys.executable,str(R/'tools/apply_bamboo_acceptance.py'),'SW'],check=True)
for f,h in repairs.items():
    p=Path(str(R/f)+'.generation.json');m=read(p)
    m['straightAxisRepair']['status']='passed_offline_after_static_and_browser_review'
    m['straightAxisRepair']['reviewedAt']=at
    m['review']={'status':'passed_offline','reviewedAt':at,'source':'review.json','sha256':h,'clientValidated':False}
    save(p,m)
print('Three repaired frames accepted against current SHA; SW contact/review/grounding synchronized.')
