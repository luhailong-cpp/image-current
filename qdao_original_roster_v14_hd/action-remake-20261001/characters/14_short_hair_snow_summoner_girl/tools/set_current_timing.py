"""Update uniform timing; without an argument preserve the current duration."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json

R = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--frame-ms', type=int)
args = parser.parse_args()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

timing = read(R/'run-timing.json')
ms = args.frame_ms if args.frame_ms is not None else timing['frameDurationMs']
assert ms > 0
count = timing['frameCount']
cycle = count * ms
now = datetime.now(timezone.utc).isoformat()
reason = f'用户指定每帧{ms}ms；{count}帧均匀播放，完整循环{cycle}ms。'
timing.update(updatedAt=now, defaultCycleMs=cycle, frameDurationMs=ms,
              uniform=True, selectionReason=reason)
for direction, group in timing['directions'].items():
    group.update(cycleMs=cycle, durationsMs=[ms]*count,
                 status=f'uniform_{ms}ms_user_selected')
    p = R/group['phaseReview']
    review = read(p)
    review.update(selectedCycleMs=cycle, durationsMs=[ms]*count,
                  timingUpdatedAt=now, timingReason=reason)
    for row in review['frames']:
        row['durationMs'] = ms
    save(p, review)
    p = R/'audit'/f'contact-{direction}-review.json'
    contact = read(p)
    for key in ['cycleDurationMs', 'cycleMs']:
        if key in contact:
            contact[key] = cycle
    contact['frameDurationMs'] = ms
    if 'durationMs' in contact:
        contact['durationMs'] = ms
    for row in contact['frames']:
        if 'durationMs' in row:
            row['durationMs'] = ms
    if 'timing' in contact:
        for key in ['frameMs', 'frameDurationMs', 'durationMs']:
            if key in contact['timing']:
                contact['timing'][key] = ms
        for key in ['cycleMs', 'runCycleMs', 'cycleDurationMs']:
            if key in contact['timing']:
                contact['timing'][key] = cycle
    contact['timingUpdatedAt'] = now
    contact['timingReview'] = 'audit/timing-60ms-update.json'
    # Preserve rootPreview as historical evidence of playback at its recorded speed.
    save(p, contact)
p = R/'audit/spatial-contact-requirement.json'
spatial = read(p)
spatial.update(frameDurationMs=ms, pairDurationMs=ms*2, cycleMs=cycle, timingUpdatedAt=now,
               timingReview='audit/timing-60ms-update.json')
save(p, spatial)
save(R/'run-timing.json', timing)
print(json.dumps({'runFrameMs': ms, 'runCycleMs': cycle, 'combatTimingChanged': False}))
