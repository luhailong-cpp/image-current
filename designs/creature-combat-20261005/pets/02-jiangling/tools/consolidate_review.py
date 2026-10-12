import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from playback_evidence import load_playback_review, PLAYBACK_RECORD, PLAYBACK_SEQUENCE, PENDING_SEQUENCE
root=Path(__file__).resolve().parents[1]
playback=load_playback_review(root)
frames=[]
for action,count in [("hit",6),("attack",12),("cast",16)]:
 for direction in ["E","W"]:
  evidence="qa/E-hit-attack-visual.json" if direction=="E" and action!="cast" else "qa/cast-E-validation.json" if direction=="E" else "qa/technical-cast-W-reviewed.json" if action=="cast" else "qa/W-hit-attack-visual.json"
  assert (root/evidence).exists(),evidence
  for n in range(1,count+1):
   p=root/"runtime"/action/direction/f"{n:02d}.png"
   frame=dict(file=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),stillReview="reviewed",sequenceReview=PLAYBACK_SEQUENCE if playback else PENDING_SEQUENCE,clientReview="not_tested",evidence=evidence)
   if playback:
    frame["sequenceEvidence"]=PLAYBACK_RECORD
   frames.append(frame)
report=dict(pet="02-jiangling",name="绛铃",reviewedAt=datetime.now(timezone.utc).isoformat(),framesReviewed=68,stillReview="all_final_frames_reviewed",parentReview="All six final numbered contact sheets actually inspected; root directly inspected every generated E hit/attack frame and selected exported W/cast detail frames; subagents actually viewed every owned final frame.",checks=["existing identity and approved painted finish","E lower-right front / W upper-left true rear","two arms, two legs, no wings/tail","anatomical right fan, left empty","three fan-edge jade bells","pose progression and independently drawn return poses","full subject and effects retained inside canvas"],repairs=["hit E04 early left-arm recovery and stray puff repaired","hit W04 rebound pose repaired","attack W05 wrong-hand candidate replaced","cast E10 effect margin repaired","cast W10 wrong-hand attempt rejected, effect margin further repaired"],continuousPlayback=dict(status="not_observed",reason="Browser security policy rejected file: protocol and explicitly prohibited workarounds/alternate browser surfaces. No circumvention attempted.",provided="preview.html plus 6 normal and 6 slow025 animated WebP files",fileStreamCheck="qa/preview-frame-stream.json",warning="Decoded frame/duration verification and ordered stills are not continuous playback observation."),clientReview="not_tested; client and sibling repositories not read",frames=frames)
if playback:
 report["continuousPlayback"]={key:playback[key] for key in ("status","reviewer","reviewedAt","method","limitations","sessionRecord","groups") if key in playback}
 report["continuousPlayback"].update(record=PLAYBACK_RECORD,fileStreamCheck="qa/preview-frame-stream.json",warning="Separate manual observation of normal and 0.25-speed live samples; file decoding does not constitute visual observation.")
(root/"qa/visual-review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("Consolidated actual still review for 68 final frames; native playback evidence:",bool(playback))
