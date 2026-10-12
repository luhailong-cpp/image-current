#!/usr/bin/env python3
"""Validate final review bindings and deliverable links; never modifies images."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text(encoding='utf-8-sig'))
errors=[]
binding=load(ROOT/'receipts/final-review-frame-binding.json')
frames=binding.get('frames',[])
if len(frames)!=68: errors.append('Final review must bind exactly 68 frames')
for item in frames:
    for field,sha_field in [('file','sha256'),('generationRecord','generationRecordSha256')]:
        path=(ROOT/item[field]).resolve()
        if not path.is_relative_to(ROOT): errors.append(f'Path outside task: {item[field]}')
        elif not path.is_file() or digest(path)!=item[sha_field]: errors.append(f'Review binding mismatch: {item[field]}')
required=['README.md','STATUS.md','MERGE_HANDOFF.md','SOURCE_INDEX.md','manifest.json',
          'technical-validation.json','preview.html','hit-E-review.md','attack-E-review.md',
          'cast-E-review.md','W-hit-attack-review.md','cast-W-review.md','playback-review.md',
          'cleanup-plan.json','cleanup-record.json']
for file in required:
    if not (ROOT/file).is_file(): errors.append(f'Missing deliverable: {file}')
checked=0
for file in ['README.md','STATUS.md','MERGE_HANDOFF.md','SOURCE_INDEX.md']:
    path=ROOT/file
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
        if '://' in target or target.startswith('#'): continue
        target=unquote(target.strip('<>').split('#')[0])
        resolved=(path.parent/target).resolve()
        checked+=1
        if not resolved.is_file(): errors.append(f'Broken link in {file}: {target}')
technical=load(ROOT/'technical-validation.json')
if not technical.get('technicalPassed'): errors.append('Image technical audit did not pass')
cleanup_path=ROOT/'cleanup-record.json'
deleted=0
if cleanup_path.is_file():
    cleanup=load(cleanup_path)
    if cleanup.get('status')!='completed': errors.append('Cleanup did not complete')
    if digest(ROOT/'cleanup-plan.json')!=cleanup.get('planSha256'): errors.append('Cleanup plan changed after execution')
    for item in cleanup.get('files',[]):
        path=(ROOT/item['file']).resolve()
        if not path.is_relative_to(ROOT): errors.append(f'Cleanup path escaped task: {item["file"]}')
        elif path.exists() or not item.get('removed'): errors.append(f'Cleanup not reflected on disk: {item["file"]}')
        else: deleted+=1
report={'generatedAt':datetime.now(timezone.utc).isoformat(),'deliveryTechnicalPassed':not errors,
        'reviewBoundFrameCount':len(frames),'reviewBoundGenerationRecords':len(frames),
        'checkedCoreMarkdownLinks':checked,'removedHistoricalPreviewImages':deleted,
        'errors':errors,'manualReviewSource':'playback-review.md',
        'scope':'asset delivery and review evidence consistency only; not client integration or every-display-frame video verification'}
(ROOT/'delivery-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
