"""Persist a builtin tool result without altering the generated pixels."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
job = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
dest = (ROOT / job['file']).resolve()
assert dest.is_relative_to(ROOT)
source = Path(job['hostOutput'])
assert source.is_file()
if dest.exists():
    raise FileExistsError(dest)
dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, dest)
with Image.open(dest) as im:
    im.load()
    dimensions = list(im.size)
    mode = im.mode
    alpha = list(im.getchannel('A').getextrema()) if 'A' in im.getbands() else None
stamp = datetime.datetime.fromtimestamp(source.stat().st_mtime, datetime.timezone.utc)
job.update({
    'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
    'generatedAt': stamp.astimezone(datetime.timezone(datetime.timedelta(hours=-4))).isoformat(),
    'generatedAtEvidence': 'host PNG mtime, exact service timestamp not disclosed',
    'nativeSize': dimensions, 'mode': mode, 'format': 'PNG', 'alphaExtrema': alpha,
    'configSnapshot': json.loads((ROOT.parents[3] / 'config/image-generation.json').read_text(encoding='utf-8-sig')),
    'tool': 'image_gen.imagegen', 'route': 'builtin',
    'actualModel': None, 'actualQuality': None,
    'unverifiedReason': '宿主管理；工具未披露实际型号/质量，不将配置目标当作实际返回证据。',
    'visualStatus': 'pending_review', 'dynamicAccepted': False, 'exported': False
})
Path(str(dest) + '.generation.json').write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'file': str(dest), 'size': dimensions, 'mode': mode, 'sha256': job['sha256']}))
