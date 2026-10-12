"""Update run annotations to the reviewed continuous-support selection; no pixel edits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    manifest = read(ROOT/'manifest.json')
    index = read(ROOT/'sources-index.json')
    now = datetime.now(timezone.utc).isoformat()
    annotations = {}
    for direction in ('N','NE','E','SE','S','SW','W','NW'):
        order = [15,16,1,2,3,4,5,6,7,8,9,10,11,12,13,14] if direction in ('N','S','NW','SW') else [16,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        first = 'right' if direction == 'SW' else 'left'
        for i, frame in enumerate(order):
            foot = first if i < 8 else ('right' if first == 'left' else 'left')
            annotations[f'run-{direction}-{frame:02d}'] = {
                'supportFoot': foot,
                'positionSegment': i % 8 // 2 + 1,
                'frameWithinPair': i % 2 + 1,
                'pairDurationMs': 120,
                'interpretation': '同一支撑足沿行进轴在连续相对位置各用两张独立姿态过渡，每位置120ms，然后换足。',
                'evidenceScope': 'static_sequence_review_only',
                'anatomicalFootConfidence': 'medium' if direction == 'SE' and frame in (8,9,10) else 'reviewed_static'
            }
    def amend(row, name):
        if name not in annotations: return
        if 'event' in row and 'legacyEvent' not in row: row['legacyEvent'] = row['event']
        a = annotations[name]
        row['event'] = f"{a['supportFoot']}_support_position_{a['positionSegment']}_{a['frameWithinPair']}"
        row['supportSequence'] = a
    for row in manifest['frames']:
        amend(row, row['slot'])
        # Receipt-path repairs update text hashes only; source/output pixel identity must remain exact.
        origin = row['derivedFrom']; gp = ROOT/origin['generationRecord']; g = read(gp)
        d = read(ROOT/row['derivedRecord'])
        assert g['sha256'] == origin['sha256'] == d['derivedFrom']['sha256']
        assert d['sha256'] == row['sha256'] == sha(ROOT/row['output'])
        assert d['originalGenerationRecord'] == g
        origin['generationRecordSha256'] = sha(gp)
        assert d['derivedFrom'] == origin
        if row['slot'] in annotations:
            path = ROOT/row['derivedRecord']; amend(d, row['slot']); write(path,d)
    for row in index['frames']:
        amend(row, f"{row['action']}-{row['direction']}-{row['frame']:02d}")
    write(ROOT/'sources-index.json', index)
    manifest['selectionSha256'] = sha(ROOT/'sources-index.json')
    manifest['annotationUpdatedAt'] = now
    manifest['inventoryScope'] = 'historical_source_inventory; current slot choices are frames[].source and sources-index.json'
    if 'reviewFinalizedAt' in manifest:
        manifest['supersededReviewFinalizedAt'] = manifest.pop('reviewFinalizedAt')
    manifest['sourceRetention']['currentDesignPolicy'] = '当前入选且仍存在的原生图保留用于待完成动态复核；淘汰源图及中间图清理，来源文字保留。'
    manifest['sourceRetention']['executionRecords'] = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'audit').glob('retention-executed*.json'))
    manifest['sourceRetention']['note'] = 'source、inventory及逐图来源中的路径记录原生成历史，不承诺历史源像素留存；清理与留存以executionRecords各批次记录和当前技术检查为准。当前入选原生设计在动态复核完成前保留。'
    write(ROOT/'manifest.json', manifest)
    # Current authoritative per-group selection records; historical nested audit snapshots stay untouched.
    for path in (ROOT/'audit').glob('*selection.json'):
        data = read(path)
        if not isinstance(data,dict) or not isinstance(data.get('frames'),list): continue
        for row in data['frames']:
            if all(k in row for k in ('action','direction','frame')):
                amend(row, f"{row['action']}-{row['direction']}-{row['frame']:02d}")
        write(path,data)
    timing = read(ROOT/'audit/run-timing.json')
    timing['status'] = 'pending_final_dynamic_review'
    timing['note'] = '当前修复版已导出并完成静态逐帧复核；60ms×16=960ms。最新动态观感尚未验收，客户端未接入。'
    for p in timing['profiles']: p['status'] = 'pending_final_dynamic_review'
    write(ROOT/'audit/run-timing.json',timing)
    write(ROOT/'audit/current-support-sequence.json', {'updatedAt':now,'scope':'annotations_only_no_pixel_changes','frames':annotations,'legacyEventsPreserved':True,'dynamicApproval':'pending_final_dynamic_review'})
    write(ROOT/'audit/current-slot-selection.json', {'updatedAt':now,'frames':[{'slot':r['slot'],'source':r['source'],'sourceSha256':r['derivedFrom']['sha256'],'output':r['output'],'outputSha256':r['sha256']} for r in manifest['frames']], 'authority':'manifest.json; nested archer-reference selection snapshots are historical unless their SHA matches this mapping'})
    historical = ROOT/'audit/archer-reference/root-e-se-groundpairs-selection.json'
    if historical.is_file():
        h = read(historical)
        h['status'] = 'superseded_selection_snapshot'
        h['supersededBy'] = 'audit/current-slot-selection.json'
        h['noteOnLaterEdits'] = '本记录为当时选帧，不改写历史；后续E11和SE06/07/14局部边缘修复以当前manifest与逐槽导出记录为准。'
        write(historical,h)
    print('Updated 128 support annotations, retained legacy events; no image edits.')

if __name__ == '__main__': main()
