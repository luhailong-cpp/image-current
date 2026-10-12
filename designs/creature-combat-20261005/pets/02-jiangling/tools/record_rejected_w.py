from pathlib import Path
import hashlib, json, sys
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
frame, attempt, source, reason = sys.argv[1:5]
source = Path(source)
receipt_path = ROOT / 'receipts' / f'cast-W-{frame}.json'
receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
tag = f'cast-W-{frame}-rejected-{attempt}'
prompt_copy = ROOT / 'prompts' / f'{tag}.txt'
prompt_copy.write_text(receipt['prompt'], encoding='utf-8')
receipt_copy = ROOT / 'receipts' / f'{tag}.json'
receipt_copy.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
with Image.open(source) as im:
    record = {'file': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'generatedAt': receipt['completedAt'], 'width': im.width, 'height': im.height, 'format': im.format, 'mode': im.mode, 'tool': 'image_gen.imagegen', 'route': 'builtin', 'configSnapshot': json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')), 'submittedParameters': {'model': None, 'quality': None, 'transparent_background': True, 'referenced_image_paths': receipt['refs']}, 'actualModel': None, 'actualQuality': None, 'unverifiedReason': '宿主管理，工具未披露 model/quality，无可核实模型元数据。', 'evidence': {'receipt': receipt_copy.relative_to(ROOT).as_posix()}, 'prompt': prompt_copy.relative_to(ROOT).as_posix(), 'references': [{'path': p, 'role': 'Original W/E identity, approved style, prior W frame respectively'} for p in receipt['refs']], 'status': 'rejected', 'rejectionReason': reason, 'retainedAsFinal': False, 'cleanupStatus': 'native outside allowed write scope; final retention handled by root'}
(ROOT / 'records' / f'{tag}.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(tag)
