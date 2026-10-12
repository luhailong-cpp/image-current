"""Merge explicitly selected, hash-verified native edits into the runtime export list."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selection=read(ROOT/'grounding-selection.json')
merged=[]
for name in sys.argv[1:]:
    path=(ROOT/name).resolve()
    assert path.is_relative_to(ROOT/'provenance/bamboo-reference-20261003')
    review=read(path)
    for frame in review.get('frames',review.get('selected',[])):
        source=(ROOT/(frame.get('file') or frame['source'])).resolve()
        assert source.resolve().is_relative_to(ROOT/'generation/bamboo-reference-20261003')
        assert sha(source)==frame['sha256']
        record=(ROOT/frame['generationRecord']).resolve()
        assert record.is_relative_to(ROOT/'generation/bamboo-reference-20261003')
        assert read(record)['sha256']==frame['sha256']
        if frame.get('generationRecordSha256'):
            assert sha(record)==frame['generationRecordSha256']
        selection[frame['slot']]={
            'source':source.relative_to(ROOT).as_posix(),
            'reason':frame.get('notes',frame.get('staticReview','Bamboo-reference lower-limb correction.')),
            'editInputSnapshot':'provenance/bamboo-reference-20261003/before-manifest.json',
            'selectionReview':path.relative_to(ROOT).as_posix()}
        merged.append(frame['slot'])
(ROOT/'grounding-selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'merged':merged,'totalRevisedSlots':len(selection)}))
