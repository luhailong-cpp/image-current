"""Read-only frame inspection; writes only cast-W QA report/contact sheet."""
import json
import sys
from pathlib import Path
from PIL import Image, ImageChops
sys.dont_write_bytecode = True
from build_combat import ROOT, sha, image_metrics, contact_sheet, now

def foot_bbox(path):
    with Image.open(path) as image:
        red, green, blue, alpha = image.convert('RGBA').split()
        mask = ImageChops.multiply(ImageChops.subtract(red, green).point(lambda p: 255 if p > 20 else 0), ImageChops.subtract(green, blue).point(lambda p: 255 if p > 35 else 0))
        mask = ImageChops.multiply(mask, alpha.point(lambda p: 255 if p > 128 else 0))
        bbox = mask.crop((0, 950, 1254, 1090)).getbbox()
        return [bbox[0], bbox[1]+950, bbox[2], bbox[3]+950] if bbox else None

def main():
    baseline = foot_bbox(ROOT / 'source/design-W.png')
    selected = []
    for record_path in sorted((ROOT / 'records').glob('cast-W-*.json')):
        record = json.loads(record_path.read_text(encoding='utf-8'))
        if record.get('selected') is False or record.get('status') in ('rejected', 'superseded'):
            continue
        if record.get('action') != 'cast' or record.get('direction') != 'W':
            continue
        source = ROOT / record['file']
        with Image.open(source) as image:
            metrics = image_metrics(image)
        feet = foot_bbox(source)
        selected.append({'frame': record['frame'], 'file': record['file'], 'record': record_path.relative_to(ROOT).as_posix(), 'sha256': sha(source), 'shaMatchesRecord': sha(source) == record['sha256'], 'durationMs': 45, 'metrics': metrics, 'approxGoldFeetBBox': feet, 'approxFeetBBoxDeltaFromDesign': [feet[i] - baseline[i] for i in range(4)] if feet and baseline else None, 'actualModel': record.get('actualModel'), 'actualQuality': record.get('actualQuality')})
    selected.sort(key=lambda item: item['frame'])
    hashes = {}
    for frame in selected:
        hashes.setdefault(frame['metrics']['visiblePixelSha256'], []).append(frame['frame'])
    report = {'checkedAt': now(), 'sourceFrames': selected, 'expectedFrames': 16, 'missing': sorted(set(range(1,17))-{f['frame'] for f in selected}), 'duplicateVisiblePixels': [group for group in hashes.values() if len(group)>1], 'designFeetBBox': baseline, 'note': 'Native-source QA, not runtime export. Gold color bbox is only a coarse diagnostic, not a visual approval or an alignment instruction. No frame pixels were altered.'}
    (ROOT/'qa').mkdir(exist_ok=True)
    (ROOT/'qa/cast-W-technical.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    contact_sheet({'action':'cast','direction':'W','expectedFrames':16,'durationMs':45}, selected, ROOT/'qa/cast-W-contact.png')
    print(json.dumps({'frames':len(selected),'missing':report['missing'],'duplicates':report['duplicateVisiblePixels'],'feetDeltas':{f['frame']:f['approxFeetBBoxDeltaFromDesign'] for f in selected}},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
