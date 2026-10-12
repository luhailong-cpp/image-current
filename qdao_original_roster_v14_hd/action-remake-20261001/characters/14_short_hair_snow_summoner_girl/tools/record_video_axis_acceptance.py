"""Record root's completed visual observations, not inferred test results."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,subprocess,hashlib
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
notes={
'N':'All16 newly inspected against bamboo and fixed-crop leg sequence. Both knees, ankles and shoes remain in north motion planes. N16 shows a small shoe-side change with rear push/ankle pitch, without transverse knee or toe splay; retained. Full-page normal/quarter browser review and480px16→01 loop check show coherent alternating legs.',
'NE':'NE04 airborne right ankle/boot corrected from an isolated near-vertical rear sole to NE oblique projection, preserving higher recovery knee and left support. Root reviewed03/new04/05 and old04 comparison; new white sidewall and sole axis flow with neighbors. Other15 retained; hand/crystal and fox unchanged.',
'E':'E11 airborne left boot corrected from front-facing round toe to east side profile, with heel behind and toe forward/right. Root inspected all16 leg crops, bamboo reference and pausedE11/E12 comparison; both arms remain connected, one fox left and one crystal right. Support-pair progression retained.',
'SE':'SE07 and14 previously recoiled the airborne lower leg after forward extension in06 and13. Both now continue forward through the neighboring poses with slight knee bend and natural ankle flexion. Root viewed native outputs and final16 sheet; support foot positions, torso, fox and crystal preserved.16→01 loop remains connected.',
'S':'All16 newly checked against bamboo, front-view knees and ankles remain aligned and shoes follow frontward motion with normal perspective shortening. No confirmed isolated axial flip; originals retained. Root viewed final full sheet, normal/quarter full-page browser playback and480px loop transition.',
'SW':'SW05 premature straight kick repaired to a compact bent-knee passing swing between04 and06. Boot stays in SW motion plane, support left foot at image-right and both hands retained. Root viewed04/05/06 full originals, generated repair and final16 sheet; no same-frame duplication or mirroring.',
'W':'All16 rechecked against bamboo and local anatomy evidence. Bent-knee foot pitch and toe-down recovery remain within west plane; no confirmed shoe yaw flip, originals retained. Hand connections, one fox and one crystal remain coherent. Normal/quarter and480px loop transition reviewed.',
'NW':'NW11 supporting right boot changed from isolated pure-left side view to NW shortened rear perspective matching10→12. Root viewed10/old11/new11/12/13 comparison.13–15 raised-sole exposure follows knee flexion and shin pitch without lateral foot yaw, retained. Hands, opposite leg and contact preserved.'}
changed={'E':[11],'NE':[4],'NW':[11],'SE':[7,14],'SW':[5]}
for d,note in notes.items():
 p=R/f'audit/root-{d}-preview-observations.json'
 hist=R/f'audit/video-axis-prior-root-preview-{d}.json'
 if p.exists() and not hist.exists():save(hist,read(p))
 obs={'direction':d,'normal':{'played':True,'cycleMs':1200,'canvasDisplayPx':240},'quarterSpeed':{'played':True,'cycleMs':4800,'canvasDisplayPx':240},'paused480pxFrames':[16,1]+([11,12] if d=='E' else []),'staticHighResolutionRepairFrames':changed.get(d,[]),'method':'Fresh video-axis audit: user MP4 decoded consecutive16-frame windows at6.2,8.7,13.7s; actual09 style/motion reference and every current16-frame contact sheet examined; after all6 replacements, reloaded128 current hash-versioned files in CUA all-directions, normal1200ms and quarter4800ms playback with representative full-page screenshots, paused480px16→01; E11/12 also paused separately. This is offline visual judgment, not client integration or measured hardware FPS.','observations':note,'recordedAt':datetime.now(timezone.utc).isoformat()}
 save(p,obs)
 cp=R/f'audit/contact-{d}-review.json';contact=read(cp)
 prior=R/f'audit/video-axis-prior-contact-{d}.json'
 if not prior.exists():save(prior,contact)
 contact['status']='static_pending_root_preview';contact.pop('rootPreview',None);save(cp,contact)
 subprocess.run([sys.executable,str(R/'tools/record_root_direction_preview.py'),d],check=True)
subprocess.run([sys.executable,str(R/'tools/apply_bamboo_acceptance.py'),*notes],check=True)
for d,ns in changed.items():
 for n in ns:
  p=R/f'run/{d}/{n:02}.png.generation.json';m=read(p)
  m['videoAxisRepair']['status']='passed_offline_after_fresh_sequence_review';m['videoAxisRepair']['rootReview']=f'audit/root-{d}-preview-observations.json';save(p,m)
print('8 directions /128 run frames current root acceptance recorded;6 local repairs')
