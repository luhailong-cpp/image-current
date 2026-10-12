from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
from playback_evidence import load_playback_review, PLAYBACK_RECORD
root=Path(__file__).resolve().parents[1]
playback=load_playback_review(root)
rows=[]
for p in sorted((root/"previews").glob("*.webp")):
 action,direction,speed=p.stem.split("-");expectedCount={"hit":6,"attack":12,"cast":16}[action];ms={"hit":40,"attack":30,"cast":45}[action]*(4 if speed=="slow025" else 1)
 im=Image.open(p);durations=[];hashes=[]
 for n in range(im.n_frames):
  im.seek(n);im.load();durations.append(im.info.get("duration"));hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
 rows.append(dict(file=p.relative_to(root).as_posix(),frames=im.n_frames,expectedFrames=expectedCount,durationsMs=durations,expectedDurationMs=ms,uniqueDecodedFrames=len(set(hashes)),correct=im.n_frames==expectedCount and durations==[ms]*expectedCount and len(set(hashes))==expectedCount))
report=dict(checkedAt=datetime.now(timezone.utc).isoformat(),method="decode every frame from animated WebP and verify frame count/durations/unique decoded pixels",status="passed" if len(rows)==12 and all(r["correct"] for r in rows) else "incomplete-or-failed",expectedAnimationFiles=12,actualAnimationFiles=len(rows),outputs=rows,visualContinuousPlayback=f"independent_record: {PLAYBACK_RECORD}" if playback else "not_observed",limitation="Timed file structure verification is not an observed continuous playback.")
(root/"qa"/"preview-frame-stream.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(dict(status=report["status"],files=len(rows),correct=sum(r["correct"] for r in rows))))
