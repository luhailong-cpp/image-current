import argparse, json, hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--id', required=True)
parser.add_argument('--source', required=True)
parser.add_argument('--action', choices=['hit','attack','cast'])
parser.add_argument('--direction', choices=['E','W'], required=True)
parser.add_argument('--frame', type=int)
parser.add_argument('--reference', action='append', default=[])
parser.add_argument('--receipt', default='')
args = parser.parse_args()
assert all(c.isalnum() or c in '-_' for c in args.id)
dest = ROOT / 'source' / (args.id + '.png')
record = ROOT / 'records' / (args.id + '.json')
prompt = ROOT / 'prompts' / (args.id + '.txt')
assert prompt.is_file(), prompt
assert not dest.exists() and not record.exists(), 'Non-destructive ingest: choose a fresh id'
dest.parent.mkdir(exist_ok=True)
record.parent.mkdir(exist_ok=True)
shutil.copy2(args.source, dest)
with Image.open(dest) as im:
    width, height, mode, fmt = im.width, im.height, im.mode, im.format
data = {
    'kind': 'frame' if args.action else 'design', 'id': args.id,
    'file': dest.relative_to(ROOT).as_posix(),
    'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
    'generatedAt': datetime.now(timezone.utc).isoformat(),
    'timestampBasis': 'observed after successful tool return and file ingestion',
    'width':width, 'height':height, 'mode':mode, 'format':fmt,
    'tool':'image_gen.imagegen', 'route':'builtin',
    'configSnapshot':json.loads((ROOT.parents[3] / 'config/image-generation.json').read_text(encoding='utf-8-sig')),
    'submittedParameters':{'model':None,'quality':None,'transparent_background':True},
    'actualModel':None, 'actualQuality':None,
    'unverifiedReason':'宿主管理，工具未开放model/quality参数且返回未披露，无可核实版本质量元数据。',
    'prompt':prompt.relative_to(ROOT).as_posix(),
    'references':[{'path':r,'purpose':'原身份' if '03_yun_jiu' in r else '主要已确认画法与材质' if 'attribute-panels' in r else '同方向身份、比例、锚点与前帧姿态连续性'} for r in args.reference],
    'evidence':{'outputHint':args.receipt,'returnedSourcePath':args.source,'sourceSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'returnedModel':None,'returnedQuality':None},
    'direction':args.direction, 'visualStatus':'pending individual and playback review'
}
if args.action: data.update(action=args.action,frame=args.frame)
record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
print(json.dumps({'file':str(dest),'record':str(record),'width':width,'height':height,'mode':mode},ensure_ascii=False))
