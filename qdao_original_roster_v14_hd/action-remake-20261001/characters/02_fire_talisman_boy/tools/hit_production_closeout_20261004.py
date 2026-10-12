import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

r = Path(__file__).resolve().parents[1]
now = datetime.datetime.now(ZoneInfo('America/New_York')).isoformat()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

inv = read(r / 'inventory-hit.json')
local_evidence = 'records/run-S-landing-independent-review-20261004.json'
slots = {('S', n) for n in (1, 7, 8, 9, 15, 16)} | {('SW', n) for n in (1, 7, 8, 15, 16)}
accepted = []
for frame in inv['frames']:
    if frame['action'] == 'run' and (frame['direction'], frame['frame']) in slots:
        actual_sha = hashlib.sha256((r / frame['path']).read_bytes()).hexdigest()
        assert actual_sha == frame['sha256'], frame['path']
        frame['visual_status'] = 'local_anatomy_independently_reviewed_sequence_pending'
        frame['visual_evidence'] = local_evidence
        accepted.append({k: frame[k] for k in ('direction', 'frame', 'path', 'source_record', 'sha256')})
assert len(accepted) == 11
write(r / 'inventory-hit.json', inv)
write(r / local_evidence, {
    'schema': 1, 'recordedAt': now, 'timezone': 'America/New_York',
    'reviewer': '/root', 'source': '本协作聊天主代理独立实看后的原文消息',
    'landing8': '根已看最新previews/run-S-contact.png、run-SW-contact.png及hit E/W全套；S/SW07/08/15/16双腿和落平动作成立。',
    'continuation3': '根已全尺寸查看S01/S09/SW01最新正式PNG：鞋平、两条腿不串位、持手正确，单图接受。S01放大先对照16/02，不马上再生；我做最终序列复核。',
    'selectedFrames': accepted,
    'limitation': '独立局部静态接受；完整1200ms与慢速序列由主代理最终复核。S01整体大小须看16→01→02，未提前自动重画或像素缩放。未运行客户端验收。'
})
p = r / 'records/run-S-reference09-differences-and-repair-20261003.json'
j = read(p)
j['updatedAt'] = now
j['repairs']['S'].update({'1': 'attempt3', '9': 'attempt5'})
j['repairs']['SW']['1'] = 'attempt5'
j['differenceBefore'].append({'area': '落地后的承重延续', 'finding': '首8张落地段修订后，S01/S09及SW01旧前鞋仍抬前掌，形成重复落地；3槽真实AI改为平底承重延续，SW09原已有平底保留。'})
j['actualViewedAfter'] = '11张生成结果分别实看；07/15初接触，08/16压缩，01/09延续承重。两腿连贯、后腿收起；S鞋向前、SW左下，五卡及右扇左铃保持。主代理独立确认8张落地，另全尺寸接受S01/S09/SW01。'
j['independentReview'] = local_evidence
j['unresolved'] = ['1200ms及慢速完整循环尚待主代理最终实播', 'S01整体较旧稿放大，需要主代理16→01→02连续对照；不主动扩大修订范围', '本分工未运行客户端验收']
write(p, j)
print(json.dumps({'inventory_count': len(inv['frames']), 'independently_reviewed_landing_count': len(accepted), 'evidence': local_evidence}, ensure_ascii=False))
