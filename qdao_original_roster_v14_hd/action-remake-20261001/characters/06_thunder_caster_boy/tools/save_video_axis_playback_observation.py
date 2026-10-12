"""Persist compact values read from the actual CUA browser-check report."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
rows=[
 ('run/N',16,[3,3],[1200.1,1200],[4800.1,4800.2]),
 ('run/NE',16,[3,3],[1200.2,1200],[4800.1,4800.2]),
 ('run/E',16,[3,3],[1199.9,1200.1],[4800,4800.1]),
 ('run/SE',16,[3,3],[1200,1200],[4800.1,4800]),
 ('run/S',16,[3,3],[1200,1200],[4800.2,4800.1]),
 ('run/SW',16,[3,3],[1200,1200.1],[4800,4800.2]),
 ('run/W',16,[3,3],[1200,1200],[4800.1,4800]),
 ('run/NW',16,[3,3],[1200,1200],[4800.2,4800.1]),
 ('hit/E',6,[6,3],[233.3,250,233.3,233.4,249.9],[966.7,950.1]),
 ('hit/W',6,[6,3],[250,233.4,233.3,250,233.3],[966.7,950]),
 ('attack/E',12,[4,3],[350.1,366.5,366.7],[1433.3,1450.1]),
 ('attack/W',12,[3,3],[349.6,366.7],[1433.4,1450]),
 ('cast/E',16,[3,3],[716.7,716.7],[2883.3,2883.5]),
 ('cast/W',16,[3,3],[733.5,716.7],[2883.3,2883.5])
]
out={'startedAt':'2026-10-05T03:35:01.468Z','finishedAt':'2026-10-05T03:38:26.985Z','manifestGeneratedAt':'2026-10-05T03:16:40+00:00','completed':True,'passed':True,'errors':[],'sourceFrameCount':196,'intervalPrecision':'observed CUA DOM values rounded to 0.1ms for textual record','method':'Actual Codex in-app browser tab4 loaded preview/browser-check.html#autostart; app button handler starts after load; no external browser automation. Each speed sampled through at least3 actual wraps.','earlierAttempt':'records/playback_first_attempt_video_axis_20261004.json','runs':[]}
for name,n,wraps,normal,slow in rows:
 out['runs'].append({'id':name,'frameCount':n,'passed':True,'normalAllFrames':True,'slowAllFrames':True,'nonRenderable':0,'skippedTransitions':0,'steppedAllVisible':True,'pauseAtLastFrame':True,'nextWrap':0,'previousWrap':n-1,'actualWrapCounts':wraps,'hiddenSamples':[0,0],'observedWrapIntervalsMs':[{'speed':1,'ms':normal},{'speed':4,'ms':slow}]})
(R/'records/cua_playback_observed_20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('Persisted observed14 runs and real wrap intervals')
