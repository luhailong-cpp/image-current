#!/usr/bin/env python3
"""Write an exact source index and cleanup candidates; never modify images."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

cleanup_record = ROOT / 'cleanup-record.json'
if cleanup_record.is_file() and load(cleanup_record).get('status') == 'completed':
    raise SystemExit('Cleanup is already complete; refusing to overwrite its executed plan. Use verify_handoff.py.')

manifest = load(ROOT / 'manifest.json')
report = load(ROOT / 'technical-validation.json')
rows = ['# 灵玥逐图来源索引', '',
        '本索引对应生成时的正式帧。目标是 GPT Image 2.5 / max；实际提交型号/质量选择器与实际返回型号/质量均为 null（未披露）。完整 prompt、参考、原生尺寸、源 SHA、receipt 和固定导出操作见每图记录。', '',
        f'技术报告时间：{report["generatedAt"]}。正式帧 {report["presentCount"]}/68。', '',
        '| 图片 | 逐图记录 | SHA256 | 实际型号/质量 |',
        '|---|---|---|---|']
runtime_snapshot = {}
current_references = set()
for frame in manifest['frames']:
    path = ROOT / frame['file']
    if not path.is_file():
        continue
    actual_sha = digest(path)
    if actual_sha != frame['sha256']:
        raise RuntimeError(f'Frame changed since audit: {frame["file"]}; rebuild delivery first')
    record_path = ROOT / frame['generationRecord']
    record = load(record_path)
    if record['sha256'] != actual_sha:
        raise RuntimeError(f'Stale generation record: {frame["file"]}')
    runtime_snapshot[frame['file']] = actual_sha
    rows.append(f'| [{frame["file"]}]({frame["file"]}) | [记录]({frame["generationRecord"]}) | `{actual_sha}` | `{record.get("actualModel")}` / `{record.get("actualQuality")}`（未确认） |')
    ancestors = record.get('derivedFrom', [])
    if isinstance(ancestors, dict):
        ancestors = [ancestors]
    for ref in [*record.get('references', []), *ancestors]:
        value = ref.get('path', ref.get('file')) if isinstance(ref, dict) else ref
        if value:
            p = Path(value)
            if not p.is_absolute():
                p = ROOT / p
            current_references.add(p.resolve())

(ROOT / 'SOURCE_INDEX.md').write_text('\n'.join(rows).replace('`None`', '`null`') + '\n', encoding='utf-8')
extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
legacy_previews = {
    'E-cast-contact-01-08.png', 'E-cast-contact-09-16.png', 'E-cast-feet-contact.png',
    'E-hit-support-repair-contact.png', 'W-attack-contact.png', 'W-attack-normal.webp',
    'W-attack-slow.webp', 'W-hit-contact.png', 'W-hit-normal.webp', 'W-hit-slow.webp'
}
candidates = []
for path in sorted((ROOT / 'receipts').glob('*')):
    # Explicit pre-audited historical names only; never sweep a newly created QA image.
    if path.name not in legacy_previews or path.suffix.lower() not in extensions or not path.is_file():
        continue
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise RuntimeError('Cleanup candidate escaped task directory')
    relative = path.relative_to(ROOT).as_posix()
    refs = []
    for text_path in ROOT.rglob('*.md'):
        if path.name in text_path.read_text(encoding='utf-8-sig'):
            refs.append(text_path.relative_to(ROOT).as_posix())
    candidates.append({'file': relative, 'sha256': digest(path), 'bytes': path.stat().st_size,
                       'reason': 'historical QA contact sheet or old animated preview; current runtime and root preview supersede it',
                       'referencedByCurrentGeneration': resolved in current_references,
                       'historicalMarkdownReferences': refs,
                       'action': 'retain_pending_final_review' if resolved in current_references else 'delete_after_final_review'})
plan = {'generatedAt': datetime.now(timezone.utc).isoformat(),
        'status': 'candidates_only_no_images_deleted', 'taskRoot': str(ROOT),
        'preconditions': ['current formal frame and source references verified', 'current manifest SHA unchanged',
                          'no candidate is a current generation reference', 'preserve current design/runtime and necessary qa'],
        'retained': ['runtime/**/*.png', 'design/*.png', 'qa/*', 'all prompts/receipts/generation text'],
        'excludedFromWriteScope': ['shared Image identity/style references', 'host .codex/generated_images cache', 'sibling/client repositories'],
        'runtimeSha256': runtime_snapshot, 'candidates': candidates,
        'candidateBytes': sum(item['bytes'] for item in candidates)}
(ROOT / 'cleanup-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'sourceIndexFrames': len(runtime_snapshot), 'cleanupCandidates': len(candidates),
                  'cleanupCandidateBytes': plan['candidateBytes'], 'deletedImages': 0}, ensure_ascii=False))
