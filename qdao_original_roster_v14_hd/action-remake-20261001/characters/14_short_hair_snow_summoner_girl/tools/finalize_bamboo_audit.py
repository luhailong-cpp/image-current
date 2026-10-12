"""Close aggregate records after eight explicit, hash-bound visual reviews and technical delivery checks."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from contact_validation import validate_contact
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(R/'manifest.json');root=read(R/'audit/bamboo-root-acceptance.json');qa=read(R/'audit/technical-qa.json')
assert set(root['directions'])=={'N','NE','E','SE','S','SW','W','NW'}
assert m['exported']==m['visualPassed']==m['anchor']['registeredFrames']==196
assert qa['technicalPass']==196 and not qa['duplicateExports'] and not qa['duplicateNativeSources']
for d,review in root['directions'].items():
 validate_contact(R,d)
 assert review['status']=='accepted_offline_after_user_feedback'
 for f in review['frames']:assert sha(R/f['file'])==f['sha256']
now=datetime.now(timezone.utc).isoformat()
requirement=read(R/'audit/spatial-contact-requirement.json')
requirement['status']='verified_against_final_artwork'
requirement['verifiedAt']=now
requirement['evidence']='audit/bamboo-root-acceptance.json and audit/contact-{direction}-review.json; all eight current PNG sets checked'
save(R/'audit/spatial-contact-requirement.json',requirement)
old=read(R/'audit/final-visual-review.json')
base=read(R/'audit/bamboo-baseline.json')['frames']
changed={d:[n for n in range(1,17) if sha(R/'run'/d/f'{n:02d}.png')!=base[f'run/{d}/{n:02d}']['sha256']] for d in root['directions']}
final={'schemaVersion':2,'status':'passed_offline_after_user_feedback_and_bamboo_reference_repair','reviewedAt':now,'count':196,'runCount':128,'changedRunCount':sum(map(len,changed.values())),'changedFrames':changed,'reference':'../09_bamboo_archer_girl/runtime/run (read-only actual images, not metadata approval)','userFeedback':old.get('userFeedback'),'reopenedAt':old.get('reopenedAt'),'scope':['all16 contact-sheet sequences in all8 directions','actual09 reference comparison','selected full-resolution hands, feet and identity-scale checks','normal240px and quarter-speed browser previews with representative screenshots and loop stepping','SHA-bound independent anatomy/source reviews'],'playback':{'normalCycleMs':1200,'frameCount':16,'frameDurationMs':75,'uniform':True,'quarterSpeedCycleMs':4800,'hardwareFpsMeasured':False},'ground':[512,942],'identityScale':0.8,'registrationEvidence':'per-frame .generation.json; direct registered edits preserve original scale without second0.8','rootAcceptance':'audit/bamboo-root-acceptance.json','records':'review.json','technicalAudit':'audit/technical-qa.json','remainingKnownArtFixes':[],'clientValidated':False,'limitations':['Offline review only; game world velocity, world-root, shadow and event integration untested.','Robe and held fox intentionally occlude some limb segments; continuity reviewed across neighboring frames.'],'previousOfflineReview':old.get('previousOfflineReview')}
save(R/'audit/final-visual-review.json',final)
final['additionalUserFeedback']=old.get('additionalUserFeedback')
final['spatialContactRequirement']={'source':'audit/spatial-contact-requirement.json','positionsPerSupportFoot':4,'distinctPosesPerPosition':2,'continuousContactFramesPerSupportFoot':8,'durationPerPositionMs':150,'frameDurationMs':75,'contactsByDirection':{d:validate_contact(R,d)['contacts'] for d in root['directions']},'positionPairsByDirection':{d:validate_contact(R,d)['positionPairs'] for d in root['directions']}}
save(R/'audit/final-visual-review.json',final)
player={'recordedAt':now,'status':'passed_current_preview_code_and_offline_visual_review','normalRunCycleMs':1200,'durationMs':75,'frames':16,'quarterSpeedCycleMs':4800,'predecodeAllRunFrames':True,'hashVersionedImages':True,'normalAndQuarterPreviewEvidence':'audit/bamboo-root-acceptance.json','sourceTimingBoundaryEvidence':'audit/uniform-timing-verification.json','method':'Visible browser representative screenshots, stepping and control state plus source-function boundary tests; not video capture or hardware refresh measurement','clientValidated':False,'files':{f:sha(R/f) for f in ['index.html','all-directions.html','timing-grounding.html','bamboo-reference.html','run-timing.json']}}
save(R/'audit/bamboo-final-browser-review.json',player)
pp=R/'audit/player-code-review.json'
prior=read(pp) if pp.exists() else {}
save(pp,{'status':'superseded_by_current_1200ms_bamboo_review','currentEvidence':'audit/bamboo-final-browser-review.json','supersededRecord':prior})
print(json.dumps({'status':final['status'],'formalCount':196,'changedRunCount':final['changedRunCount'],'remainingKnownArtFixes':[],'clientValidated':False}))
