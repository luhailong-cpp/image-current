"""Build a read-only-of-pets delivery index; never infer art approval from file count."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ACTIONS = [('hit', '受击', 6, 40), ('attack', '普攻', 12, 30), ('cast', '施法', 16, 45)]
roster = json.loads((ROOT / 'roster.json').read_text(encoding='utf-8-sig'))
review_path = HERE / 'review-status.json'
reviews = json.loads(review_path.read_text(encoding='utf-8-sig')) if review_path.exists() else {}
entries = []
checksums = []
for item in roster['entries']:
    folder = ROOT / 'pets' / item['slug']
    groups = []
    present = 0
    missing = []
    for action, label, count, duration in ACTIONS:
        for direction in ['E', 'W']:
            frames = []
            for i in range(1, count + 1):
                p = folder / 'runtime' / action / direction / f'{i:02}.png'
                exists = p.is_file()
                rel = p.relative_to(ROOT).as_posix()
                sha = hashlib.sha256(p.read_bytes()).hexdigest() if exists else None
                frames.append({'frame': i, 'url': '../' + rel, 'sha256': sha, 'exists': exists})
                if exists:
                    present += 1
                    checksums.append(f'{sha}  {rel}')
                else:
                    missing.append(rel)
            groups.append({'action': action, 'label': label, 'direction': direction,
                           'durationMs': duration, 'frames': frames})
    preview = next((p for p in [folder / 'preview/index.html', folder / 'preview.html'] if p.is_file()), None)
    docs = {n: '../' + (folder / n).relative_to(ROOT).as_posix()
            for n in ['README.md', 'STATUS.md', 'MERGE_HANDOFF.md', 'manifest.json'] if (folder / n).is_file()}
    review = reviews.get(item['slug'], {'state': 'pending', 'note': '等待最终验收记录'})
    # Approval applies only to the exact reviewed bytes, never to later replacement frames.
    fingerprint = hashlib.sha256('\n'.join(f['sha256'] or 'missing' for g in groups for f in g['frames']).encode()).hexdigest()
    approved = review.get('state') in {'reviewed', 'reviewed-with-notes', 'passed', 'complete', 'completed'}
    if approved and (present != 68 or not review.get('fingerprint') or review['fingerprint'] != fingerprint):
        review = {**review, 'state': 'pending', 'note': '缺少当前完整图片的验收绑定，需复核；' + review.get('note', '')}
    elif review.get('fingerprint') and review['fingerprint'] != fingerprint:
        review = {**review, 'state': 'pending', 'note': '图片已更新，需复核最新版本；' + review.get('note', '')}
    entries.append({'slug': item['slug'], 'name': item['name'], 'present': present, 'expected': 68,
                    'missing': missing, 'fingerprint': fingerprint, 'review': review, 'groups': groups,
                    'preview': '../' + preview.relative_to(ROOT).as_posix() if preview else None, 'docs': docs})
data = {'builtAtUTC': datetime.now(timezone.utc).isoformat(), 'scope': 'Image原有20个形象；三种战斗动作；不含移动',
        'expectedFrames': len(entries) * 68, 'presentFrames': sum(e['present'] for e in entries),
        'clientIntegrated': False, 'entries': entries}
data['materialsReady'] = all(e['present'] == 68 and e['review']['state'] != 'pending' for e in entries)
data['playbackUnverified'] = [e['name'] for e in entries if e['review']['state'] in {'materials-ready-playback-unverified', 'materials-ready-playback-partially-verified'}]
(HERE / 'inventory.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(HERE / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='utf-8')
template = (HERE / 'preview.template.html').read_text(encoding='utf-8')
(HERE / 'index.html').write_text(template.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')), encoding='utf-8')
lines = ['# Image 原有宠物战斗动作交付', '', '[统一动作预览](index.html) · [异机合并说明](MERGE_HANDOFF.md) · [本轮独立复核](audits/README.md)', '',
         f"正式图片：{data['presentFrames']}/{data['expectedFrames']}。这是数量统计，验收结论以各只记录为准。", '',
         '每只E斜前、W真实斜后；受击各6帧×40ms，普攻各12帧×30ms，施法各16帧×45ms。客户端未接入。', '']
if data['materialsReady']:
    lines += ['20只素材与配套交付已完成，已确认的本轮修图问题均已处理。', '']
if data['playbackUnverified']:
    lines += ['尚未完成完整连播验证：' + '、'.join(data['playbackUnverified']) + '。文件、来源和静态复核已经完成，已核验的播放范围和工具限制详见各只记录；其余个别动作的残余观察项也保留在记录中。', '']
lines += ['| 宠物 | 图片 | 当前验收 | 说明 |', '| --- | --- | --- | --- |']
for e in entries:
    link = f"[交付说明]({e['docs']['README.md']})" if 'README.md' in e['docs'] else '整理中'
    lines.append(f"| {e['name']} | {e['present']}/68 | {e['review']['note'].replace('|', '/')} | {link} |")
lines += ['', '统一预览直接引用各只正式PNG，不复制素材；支持原速、0.25倍、暂停与逐帧，缺帧会显式显示。',
          '图片来源、逐图模型/质量证据和接入参数保存在各只manifest与README。未知的实际型号/质量不以配置目标冒充。',
          '独立怪物包的Image子目录尚未获得确认，本交付未加入其他来源的怪物。',
          '', '刷新统计：使用项目可用Python执行本目录 build_delivery.py。美术通过状态只能在实际复核后更新 review-status.json。']
(HERE / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({'present': data['presentFrames'], 'expected': data['expectedFrames'], 'missing': {e['name']: e['missing'] for e in entries if e['missing']}}, ensure_ascii=False))
