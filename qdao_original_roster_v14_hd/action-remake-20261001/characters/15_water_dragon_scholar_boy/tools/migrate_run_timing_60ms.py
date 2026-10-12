"""Apply the latest explicit in-chat 60ms correction; retain old timing evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json, re, hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    timing=read(ROOT/'audit/run-timing.json')
    p=ROOT/'audit/run-timing-change-60ms-20261005.json'
    if not p.exists():
        save(p,{'recordedAt':datetime.now(timezone.utc).isoformat(),'authority':'用户在本角色聊天最新纠正，优先于共享批次README中75ms旧要求。','userQuote':'不是已经改成60ms 一帧了吗','previousTiming':timing,'newFrameMs':60,'newCycleMs':960,'pairMs':120,'scope':'run only; combat and sprite pixels unchanged'})
    names=['apply_revised_frames.py','build_delivery.py','finalize_review.py','final_delivery_check.py',
           'publish_static_review.py','record_video_axis_result.py','render_review_board.py',
           'render_run_overview.py','render_sequence_previews.py','set_run_timing.py',
           'update_support_annotations.py','update_progress.py','write_current_handoff.py']
    for name in names:
        path=ROOT/'tools'/name
        text=path.read_text(encoding='utf-8')
        text=text.replace('uniform1200','uniform960')
        text=re.sub(r'(?<!\d)1200(?!\d)','960',text)
        text=re.sub(r'(?<!\d)75(?!\d)','60',text)
        if name in ['publish_static_review.py','record_video_axis_result.py','update_support_annotations.py','write_current_handoff.py']:
            text=re.sub(r'(?<!\d)150(?!\d)','120',text)
        text=text.replace('GIF以80/70ms交替表示60ms，共960ms','GIF直接以60ms逐帧编码，共960ms')
        path.write_text(text,encoding='utf-8')
    print('Updated current execution scripts to60ms; prior timing evidence retained.')
if __name__=='__main__': main()
