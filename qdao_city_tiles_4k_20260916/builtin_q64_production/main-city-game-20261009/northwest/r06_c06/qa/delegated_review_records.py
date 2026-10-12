import hashlib, json, re
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent.parent

def save_review(stem, observations, filename, verdict):
    manifest_path = BASE / 'candidate' / (stem + '.assembly.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    entries = []
    sources = {(x['row'], x['column']): {'id': x['id'], 'file': x['file'], 'sha256': x['sha256']} for x in manifest['nativeSources']}
    for item in manifest['qa']:
        name = Path(item['file']).stem
        if name not in observations:
            continue
        v, findings = observations[name]
        path = Path(item['file'])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == item['sha256']
        if name.startswith('internal-y'):
            y, col = map(int, re.fullmatch(r'internal-y(\d+)-segment(\d+)', name).groups())
            row = y // 1024
            adjacent = [sources[row,col], sources[row+1,col]]
        else:
            x,y = map(int, re.fullmatch(r'junction-x(\d+)-y(\d+)', name).groups())
            row,col = y//1024, x//1024
            adjacent = [sources[r,c] for r,c in [(row,col),(row,col+1),(row+1,col),(row+1,col+1)]]
        entries.append({
            'id': name, 'reference': {'file': str(path), 'sha256': digest},
            'cropLTRB': item['cropLTRB'], 'pixels': item['pixels'],
            'sourceResampled': False, 'nativePixelScale': 1,
            'actuallyViewed': True, 'inspection': 'tools.view_image detail=original',
            'verdict': v, 'findings': findings, 'adjacentNativeSources': adjacent
        })
    assert len(entries) == 21, len(entries)
    output = manifest['output']
    assert hashlib.sha256(Path(output['file']).read_bytes()).hexdigest() == output['sha256']
    result = {'schemaVersion': 1, 'reviewedAtUtc': datetime.now(timezone.utc).isoformat(),
              'reviewer': '/root/east_next_tile', 'tile': 'r06_c06', 'candidate': output,
              'scope': '12 horizontal native seam crops and 9 junction native crops; vertical seams reviewed separately by root',
              'verdict': verdict, 'actuallyViewedCount': len(entries),
              'passedCount': sum(e['verdict']=='passed' for e in entries),
              'blockingCount': sum(e['verdict']=='blocked' for e in entries),
              'sourceSelectionModified': False, 'formalAccepted': False,
              'entries': entries}
    target = BASE/'qa'/filename
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'file':str(target), 'count':len(entries), 'blocked':result['blockingCount']}))

minimum = {
 'internal-y1024-segment01': ('passed', ['Continuous vertical stone joint; no orphan grout.']),
 'internal-y1024-segment02': ('passed', ['Curb and diagonal joints connect. Mild material variation is nonblocking.']),
 'internal-y1024-segment03': ('blocked', ['At crop (730,72), tile (2778,936), blue road edge steps. At crop (934,77), tile (2982,941), blue grout terminates abruptly. At crop (123,249), tile (2171,1113), gray diagonal grout terminates. Main north/south pair s01_03_fix01 / s02_03; minimum-error overlap selection cuts geometry.']),
 'internal-y1024-segment04': ('passed', ['Connected road and slab joins. Minor stone texture tone variation.']),
 'internal-y2048-segment01': ('passed', ['Horizontal stone joint and vertical T joint remain connected.']),
 'internal-y2048-segment02': ('passed', ['Vertical curb and gray diamond joints remain closed.']),
 'internal-y2048-segment03': ('blocked', ['Gray diagonal grout dead end at crop (52,124), tile (2100,2012). Main north/south pair s02_03 / s03_03.']),
 'internal-y2048-segment04': ('passed', ['Closed diamond joints; microtexture variation is nonblocking.']),
 'internal-y3072-segment01': ('passed', ['Connected diagonal slab geometry.']),
 'internal-y3072-segment02': ('passed', ['Connected gray diagonal joint; about 4 pixel nick/kink at crop (113,135) is nonblocking, not an orphan line.']),
 'internal-y3072-segment03': ('blocked', ['Gray diagonal grout dead end at crop (100,144), tile (2148,3056). Main north/south pair s03_03 / s04_03.']),
 'internal-y3072-segment04': ('passed', ['Complete gray diamond joints and unchanged red paper decoration.']),
 'junction-x1024-y1024': ('passed', ['Natural stone field; no broken grout intersection.']),
 'junction-x1024-y2048': ('passed', ['Continuous horizontal joint across intersection.']),
 'junction-x1024-y3072': ('passed', ['Connected four-way diagonal joint. Small joint edge nick near (275,136) is nonblocking.']),
 'junction-x2048-y1024': ('passed', ['Connected diagonal stone outlines; small grout-edge nick near (103,87) does not interrupt continuity.']),
 'junction-x2048-y2048': ('blocked', ['Diagonal stone grout dead end near crop (213,126), same defect as y2048 segment03; tile approximately (2101,2014).']),
 'junction-x2048-y3072': ('blocked', ['Diagonal stone grout dead end near crop (260,144), same defect as y3072 segment03; tile (2148,3056).']),
 'junction-x3072-y1024': ('blocked', ['Blue slab grout has a gap between crop approximately (70,75) and (113,80), corresponding to tile x2982..3025 around y939..944.']),
 'junction-x3072-y2048': ('passed', ['Both diagonal joints connect through offset stone corners.']),
 'junction-x3072-y3072': ('passed', ['Both diagonal joints connect through offset stone corners.']),
}

hard = {
 'internal-y1024-segment01': ('passed', ['Continuous vertical stone joint and lower horizontal joint. Natural grain varies slightly across the source boundary.']),
 'internal-y1024-segment02': ('passed', ['Curb and diagonal slab joins are connected across the center cut.']),
 'internal-y1024-segment03': ('passed', ['Previously clipped blue road edge and blue/gray grout now connect fully. No orphan grout at the former minimum-error defect locations.']),
 'internal-y1024-segment04': ('passed', ['Blue road, cream curb and gray diagonal slabs retain complete joined geometry.']),
 'internal-y2048-segment01': ('passed', ['Horizontal joint and vertical T joints are continuous.']),
 'internal-y2048-segment02': ('passed', ['Curb, horizontal slabs and gray diamond junction remain connected.']),
 'internal-y2048-segment03': ('passed', ['Former left gray diagonal dead end now reaches the vertical curb. Blue rectangular slab joints are complete.']),
 'internal-y2048-segment04': ('passed', ['All visible diagonal joints form complete diamond corners.']),
 'internal-y3072-segment01': ('passed', ['Complete diagonal slab joints and four-way intersections.']),
 'internal-y3072-segment02': ('passed', ['Diagonal slab joints, curb and gray four-way intersection are connected. Previous small notch is absent.']),
 'internal-y3072-segment03': ('passed', ['Former left gray diagonal dead end now reaches the curb. Blue road joints and right gray joints are continuous.']),
 'internal-y3072-segment04': ('passed', ['Continuous gray slab joints and complete intersections; red paper decoration remains intact.']),
 'junction-x1024-y1024': ('passed', ['Continuous natural stone field; no artificial grout endpoint.']),
 'junction-x1024-y2048': ('passed', ['Horizontal stone joint is uninterrupted through the junction crop.']),
 'junction-x1024-y3072': ('passed', ['Complete four-way diamond intersection.']),
 'junction-x2048-y1024': ('passed', ['Complete diagonal stone outline; former minimum-error nick is absent.']),
 'junction-x2048-y2048': ('passed', ['Gray diagonal grout reaches the cream curb. Former orphan endpoint is removed by the center source cut.']),
 'junction-x2048-y3072': ('passed', ['Gray diagonal grout reaches the cream curb with no dead end.']),
 'junction-x3072-y1024': ('passed', ['Blue slab grout is continuous through the previous gap; curb and blue corner connect.']),
 'junction-x3072-y2048': ('passed', ['Connected offset diagonal stone corners; slight grain variation is nonblocking.']),
 'junction-x3072-y3072': ('passed', ['Complete four-way stone intersection; no orphan grout.']),
}

if __name__ == '__main__':
    save_review('r06_c06-candidate-minimum-error-11a5a56c171b', minimum,
                'horizontal-junction-review-11a5a56c171b.json', 'blocked_historical_candidate')
    save_review('r06_c06-candidate-hard-077556c4fb59', hard,
                'horizontal-junction-review-hard-077556c4fb59.json', 'passed')
