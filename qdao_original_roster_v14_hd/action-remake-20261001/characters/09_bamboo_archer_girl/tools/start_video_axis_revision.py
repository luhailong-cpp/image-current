from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record={'startedAtUtc':datetime.now(timezone.utc).isoformat(),'feedback':'你看人家其他方向的视频很笔直，我们这个你看歪了，所以还是得继续修','source':'Latest user video/screenshot feedback relayed by orchestration thread 01a0f76f-0056-7c23-a688-10733b6b89e3','scope':'09 bamboo archer girl only; inspect eight run directions, retain correct frames and repair demonstrated knee/ankle/boot-axis twists','timing':{'count':16,'frameMs':75,'cycleMs':1200,'framesPerRelativeSupportPosition':2},'reference':'audit/video-reference-20261004/extraction.json','styleReference':'D:/work/image/designs/jubaozhai-ui/02-characters.png','referenceLimits':'Other-game video is motion-only, small/occluded sprite; no transfer of character/style, no invented fine shoe detail','priorDeliveryReceiptSha256':sha(ROOT/'audit/current-revision-delivery.json'),'beforeFrames':[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted((ROOT/'runtime').rglob('*.png'))]}
p=ROOT/'audit/video-axis-revision-before.json'
assert not p.exists(),'Do not overwrite the pre-revision snapshot.'
p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'audit/live-work-state.json').write_text(json.dumps({'state':'continuing_video_axis_repair','writeBoundary':'This character directory only','sourceRequest':'audit/video-axis-revision-before.json','assignments':{'E_NE_N':'finish_e_ne read-only targeted review','W_NW_SW':'finish_sw_nw read-only targeted review','S_SE':'finish_south read-only targeted review','root':'Source video extraction, independent assessment, confirmed repairs and final delivery'},'dynamicVisualAcceptance':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('Recorded user video feedback and pre-revision 196 image hashes.')

