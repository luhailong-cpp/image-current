"""Rebuild current contact/APNG/HTML previews from manifest timing; never old trials."""
from collections import defaultdict
import hashlib
import json
from PIL import Image, ImageDraw
from manifest_tools import ROOT, load_manifest
from build_preview import main as build_html


def build_artifacts(m):
    groups = defaultdict(list)
    for f in m['frames']:
        groups[(f['action'], f['direction'])].append(f)
    artifacts = []
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for (action, direction), group in groups.items():
        group.sort(key=lambda f: f['index'])
        if action == 'run':
            assert len(group) == 16 and [f['durationMs'] for f in group] == [60] * 16
        sheet = Image.new('RGB', (1200, ((len(group) + 3) // 4) * 326), '#e5e7eb')
        draw = ImageDraw.Draw(sheet)
        thumbs = []
        for i, f in enumerate(group):
            with Image.open(ROOT / f['path']) as im:
                thumb = im.resize((300, 300), Image.Resampling.LANCZOS)
            bg = Image.new('RGBA', (300, 300), '#e5e7eb')
            bg.alpha_composite(thumb)
            thumbs.append(bg.convert('RGB'))
            sheet.paste(thumbs[-1], (i % 4 * 300, i // 4 * 326))
            draw.text((i % 4 * 300 + 8, i // 4 * 326 + 302), f"{action}/{direction}/{i+1:02}  {f['durationMs']}ms", fill='black')
        sources = [{'path': f['path'], 'sha256': f['sha256']} for f in group]
        contact = ROOT / f'preview/{action}-{direction}-contact.jpg'
        sheet.save(contact, quality=90)
        artifacts.append({'path': contact.relative_to(ROOT).as_posix(), 'sha256': sha(contact), 'sources': sources, 'operation': 'inspection thumbnails only'})
        for label, multiplier in [('normal', 1), ('slow', 4)]:
            path = ROOT / f'preview/{action}-{direction}-{label}.png'
            durations = [f['durationMs'] * multiplier for f in group]
            thumbs[0].save(path, save_all=True, append_images=thumbs[1:], duration=durations, loop=0)
            artifacts.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'sources': sources, 'operation': '300px APNG preview, not game frame', 'durationsMs': durations})
    (ROOT / 'preview/derivations.json').write_text(json.dumps({'artifacts': artifacts}, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    m = load_manifest()
    assert m['timing']['runCycleMs'] == 960 and m['timing']['runFrameMs'] == 60
    assert all(f['durationMs'] == 60 for f in m['frames'] if f['action'] == 'run')
    build_artifacts(m)
    return build_html()


if __name__ == '__main__':
    raise SystemExit(main())
