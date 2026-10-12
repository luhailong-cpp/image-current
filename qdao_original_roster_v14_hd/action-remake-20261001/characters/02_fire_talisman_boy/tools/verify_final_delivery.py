"""Verify current final files and rendered preview timing without modifying images."""
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageSequence
R=Path(__file__).resolve().parents[1]
def read(p): return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
tech=read('previews/technical-report.json')
review=read('reviews/final-review.json')
audit=read('reviews/full-source-chain-audit.json')
contacts=read('previews/contact-sources.json')
assert tech['offline_materials_complete']
assert tech['technical_pass_frames']==196 and tech['technical_failure_frames']==0
assert not review['knownUnresolvedArtFailures']
assert audit['pass'] and audit['summary']['fileSourceChainPassCount']==196
entries=[e for s in tech['sequences'] for e in s['entries']]
assert len(entries)==196 and len({e['path'] for e in entries})==196
current={e['path']:sha(e['path']) for e in entries}
assert all(current[e['path']]==e['sha256'] for e in entries)
assert all(current[e['path']]==e['sha256'] for e in review['frames'])
assert all(current[e['formal']['path']]==e['formal']['sha256'] for e in audit['frames'])
assert all(current[e['file']]==e['sha256'] for e in contacts['sources'])
with (R/'MERGE_FILES.csv').open(encoding='utf-8-sig',newline='') as fp:
    merge_rows=list(csv.DictReader(fp))
assert len(merge_rows)==196 and all(current[e['path']]==e['sha256'] for e in merge_rows)
gif_checks=[]
for seq in tech['sequences']:
    for speed,meta in seq['animations'].items():
        rel='previews/'+meta['file']
        with Image.open(R/rel) as im:
            durations=[frame.info.get('duration') for frame in ImageSequence.Iterator(im)]
        assert len(durations)==seq['expected'],rel
        assert sum(durations)==sum(meta['requested_durations_ms']),rel
        gif_checks.append({'file':rel,'sha256':sha(rel),'frames':len(durations),'durationMs':sum(durations)})
assert len(gif_checks)==28
with Image.open(R/'previews/run-eight-directions.gif') as im:
    over=[frame.info.get('duration') for frame in ImageSequence.Iterator(im)]
assert len(over)==16 and sum(over)==960
assert len(list((R/'frames').rglob('*.png')))==196
timing=read('animation-timing.json')
assert timing['run']['frameMs']==60 and timing['run']['cycleMs']==960 and timing['run']['uniform']
result={
'verifiedAtUtc':datetime.now(timezone.utc).isoformat(),
'formalFrames':196,'sequences':14,'technicalPass':196,'offlineMaterialsComplete':True,
'previewGifCount':28,'allFormalAndPreviewSourceHashesCurrent':True,
'runNormalMs':960,'runFrameMs':60,'runUniform':True,
'runEightDirectionGif':{'file':'previews/run-eight-directions.gif','sha256':sha('previews/run-eight-directions.gif'),'frames':len(over),'durationMs':sum(over)},
'clientIntegrated':False,
'actualModelAndQuality':'not disclosed by built-in image_gen; unconfirmed',
'cleanup':'Earlier batch deletion was blocked by automatic approval review; no bypass or retry.',
'scope':'File/source hash agreement and preview frame/duration verification. Visual review and browser sampling recorded separately; no client runtime claim.',
'evidence':{p:sha(p) for p in ['inventory.json','reviews/final-review.json','reviews/full-source-chain-audit.json','reviews/full-limb-browser-20261005.json','reviews/full-limb-final-20261005.json','previews/contact-sources.json','MERGE_FILES.csv','MERGE_HANDOFF.md']},
'previewGifs':gif_checks}
(R/'reviews/delivery-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['formalFrames','technicalPass','previewGifCount','allFormalAndPreviewSourceHashesCurrent','clientIntegrated']},ensure_ascii=False))
