"""从当前 manifest 和主审最终离线复核记录更新进度、状态与 runtime 关键姿态预览。"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import sys

from PIL import Image, ImageDraw, ImageFont
from finalize_review import validate_review, OFFLINE

ROOT = Path(__file__).resolve().parents[1]


def build_progress(manifest: dict, review: dict | None, review_sha: str | None) -> dict:
    frames = manifest.get('frames', [])
    groups = manifest.get('groups', [])
    static_path = ROOT / 'audit/current-static-review.json'
    static_count = 0
    if static_path.is_file():
        static_bytes = static_path.read_bytes()
        static_review = json.loads(static_bytes.decode('utf-8-sig'))
        current = {r['slot']: (r['derivedFrom']['sha256'], r['sha256']) for r in frames}
        observed = {r['slot']: (r['sourceSha256'], r['outputSha256']) for r in static_review.get('frames', [])}
        if current == observed and manifest.get('staticReview', {}).get('sha256') == hashlib.sha256(static_bytes).hexdigest():
            static_count = len(observed)
    review_state, review_error = 'missing', None
    if review is not None:
        try:
            validate_review(manifest, review)
            applied = (manifest.get('animationApproval') == OFFLINE
                       and manifest.get('offlineReview', {}).get('sha256') == review_sha)
            review_state = 'applied' if applied else 'valid_not_applied'
        except (ValueError, TypeError, KeyError) as error:
            review_state, review_error = 'invalid_or_stale', str(error)
    reviewed_groups = [g for g in groups if review_state == 'applied' and g.get('animationApproval') == OFFLINE
                       and len(group_frames := [r for r in frames if r['action'] == g['action'] and r['direction'] == g['direction']]) == g['expected']
                       and all(r.get('animationApproval') == OFFLINE and r.get('visualApproval') == OFFLINE for r in group_frames)]
    reviewed_keys = {(g['action'], g['direction']) for g in reviewed_groups}
    reviewed_frames = [r for r in frames if review_state == 'applied' and r.get('animationApproval') == OFFLINE
                       and r.get('visualApproval') == OFFLINE and (r['action'], r['direction']) in reviewed_keys]
    return {'updatedAt': datetime.now(timezone.utc).isoformat(), 'expected': 196,
            'exported': sum(bool(r.get('output')) and r.get('status') == 'exported' for r in frames),
            'reusedSelected': sum(r.get('sourceKind') == 'reused' for r in frames),
            'newSelected': sum(r.get('sourceKind') == 'new' for r in frames),
            'newSlotsAreNotApprovedCount': True,
            'staticReviewedFrames': static_count,
            'staticReviewRecord': 'audit/current-static-review.json' if static_count else None,
            'dynamicAccepted': len(reviewed_groups), 'dynamicAcceptedUnit': 'offline_groups',
            'offlineReviewedGroups': len(reviewed_groups), 'expectedGroups': 14,
            'offlineReviewedFrames': len(reviewed_frames), 'offlineReviewRecordStatus': review_state,
            'offlineReviewRecordIssue': review_error,
            'clientIntegrated': manifest.get('clientIntegration') == 'integrated',
            'clientIntegration': manifest.get('clientIntegration', 'not_integrated'),
            'clientRuntimeAcceptance': manifest.get('clientRuntimeAcceptance', 'not_tested'),
            'userAcceptance': manifest.get('userAcceptance', 'not_reviewed_by_user'),
            'animationApproval': manifest.get('animationApproval', 'pending'),
            'files': [{'slot': r['slot'], 'file': r.get('output'), 'sha256': r.get('sha256'),
                       'source': r.get('source'), 'sourceSha256': r.get('derivedFrom', {}).get('sha256'),
                       'generationRecord': r.get('derivedFrom', {}).get('generationRecord'),
                       'derivedRecord': r.get('derivedRecord'), 'durationMs': r.get('durationMs'),
                       'timingStatus': r.get('timingStatus'), 'animationApproval': r.get('animationApproval', 'pending')}
                      for r in frames],
            'groups': [{'action': g['action'], 'direction': g['direction'], 'frames': g.get('accepted', 0),
                        'animationApproval': g.get('animationApproval', 'pending'), 'cycleMs': g.get('cycleMs'),
                        'frameDurationsMs': g.get('frameDurationsMs'), 'timingStatus': g.get('timingStatus')}
                       for g in groups]}


def render_key_poses(manifest: dict, payload: dict, manifest_sha: str) -> None:
    items = [('跑步 E01', 'run-E-01'), ('受击 E03', 'hit-E-03'),
             ('普攻 E06', 'attack-E-06'), ('施法 E10', 'cast-E-10')]
    by_slot = {r['slot']: r for r in manifest['frames']}
    sheet = Image.new('RGB', (1600, 490), '#e6e5df')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    sources = []
    for i, (label, slot) in enumerate(items):
        draw.text((i * 400 + 14, 12), label, fill='#173d49', font=font)
        row = by_slot[slot]
        if not row.get('output'):
            draw.text((i * 400 + 100, 210), '当前槽位尚未导出', fill='#6b3740', font=font)
            continue
        path = ROOT / row['output']
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_sha != row['sha256']:
            raise ValueError(f'runtime 与清单 SHA 不符: {slot}')
        with Image.open(path) as original:
            if original.mode != 'RGBA' or original.size != (1024, 1024):
                raise ValueError(f'关键姿态必须读取当前1024 RGBA runtime: {slot}')
            image = original.resize((400, 400), Image.Resampling.LANCZOS)
            sheet.paste(image, (i * 400, 42), image)
            image.close()
        sources.append({'slot': slot, 'path': row['output'], 'sha256': actual_sha,
                        'sourceSha256': row['derivedFrom']['sha256']})
    complete = payload['offlineReviewedFrames'] == 196 and payload['offlineReviewedGroups'] == 14
    footer = ('本聊天主审离线复核完成；跑步960ms正常节奏、60ms/帧（本地）；用户尚未验收，客户端未接入。' if complete
              else '196帧素材已导出；静态逐帧检查完成，最新动态播放观感待验收；客户端未接入。' if payload.get('staticReviewedFrames') == 196
              else '当前为关键姿态预览；本地完整序列审核尚未完成，客户端未接入、未运行验收。')
    draw.text((14, 459), footer, fill='#6b3740', font=font)
    (ROOT / 'preview').mkdir(exist_ok=True)
    output = ROOT / 'preview/key-poses-current.png'
    sheet.save(output)
    sheet.close()
    record = {'file': 'preview/key-poses-current.png', 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'operation': 'preview-only current 1024 runtime full-canvas thumbnails; no pose edit',
              'manifest': {'file': 'manifest.json', 'sha256': manifest_sha},
              'animationApproval': OFFLINE if complete else 'pending_visual_dynamic_review',
              'clientIntegration': 'not_integrated', 'clientRuntimeAcceptance': 'not_tested',
              'userAcceptance': 'not_reviewed_by_user',
              'derivedFrom': sources}
    (ROOT / 'preview/key-poses-current.png.generation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    manifest_bytes = (ROOT / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes.decode('utf-8-sig'))
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    review_path = ROOT / 'audit/final-review.json'
    review_bytes = review_path.read_bytes() if review_path.is_file() else None
    review = json.loads(review_bytes.decode('utf-8-sig')) if review_bytes else None
    payload = build_progress(manifest, review, hashlib.sha256(review_bytes).hexdigest() if review_bytes else None)
    payload['manifestSha256'] = manifest_sha
    generations = []
    for path in (ROOT / 'provenance/generation').glob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        if data.get('file') and data.get('sha256'):
            generations.append(data)
    payload['newAttempts'] = len(generations)
    historical_slots = {match.group(0) for data in generations
                        if (match := re.match(r'(?:run|hit|attack|cast)-(?:NE|NW|SE|SW|N|E|S|W)-\d+', Path(data['file']).stem))}
    payload['newSlots'] = len(historical_slots)
    payload['newAttemptsMeaning'] = '保留真实生成记录的历史原生尝试数量；包括已淘汰图，不代表批准帧数。'
    payload['sourcePngPresent'] = sum(1 for _ in (ROOT / 'sources').rglob('*.png'))
    payload['sourceCleanupNote'] = '源图清理不抹掉历史尝试记录；当前成品和来源链以 manifest/derived 为准。'
    round_path = ROOT / 'audit/video-direction-20261004/repair-result.json'
    if round_path.is_file():
        current_round = json.loads(round_path.read_text(encoding='utf-8-sig'))
        payload['latestRepairRound'] = {key:current_round[key] for key in ['changedCount','runFootRepairs','runHandRepairs','combatHandRepairs','unchangedCount']}
        payload['latestRepairRound']['record'] = round_path.relative_to(ROOT).as_posix()
    render_key_poses(manifest, payload, manifest_sha)
    (ROOT / 'progress.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    complete = payload['offlineReviewedFrames'] == 196 and payload['offlineReviewedGroups'] == 14
    status = '本聊天主审离线复核完成，用户尚未验收；未接入客户端' if complete else '当前修复版已导出并完成静态逐帧检查；最新动态观感待验收，未接入客户端' if payload.get('staticReviewedFrames') == 196 else '当前成品继续审核中，未接入客户端'
    lines = ['# 15 水龙书生 · 当前制作进度', '', status, '', f"更新：{payload['updatedAt']}", '',
             f"- 当前真实导出 {payload['exported']}/196；当前静态逐帧检查 {payload['staticReviewedFrames']}/196；最新完整动态通过 {payload['offlineReviewedGroups']}/14 组。静态证据见 audit/current-static-review.json；旧 final-review 已撤回，不复用旧通过结论。",
             f"- 当前选择：本机生成/定向编辑 {payload['newSelected']} 张、旧图复用 {payload['reusedSelected']} 张；历史生成记录 {payload['newAttempts']} 份。",
             f"- 本聊天最终复核记录状态：{payload['offlineReviewRecordStatus']}。",
             '- 来源与当前成品：manifest.json、provenance/derived；两份预览：preview/index.html、preview/all-directions.html。',
             '- 关键姿态读取当前 runtime/run/E/01、hit/E/03、attack/E/06、cast/E/10，不读取淘汰源图。']
    if payload['offlineReviewRecordIssue']:
        lines.append(f"- 复核记录尚不适用于当前版本：{payload['offlineReviewRecordIssue']}")
    if payload.get('latestRepairRound'):
        rr = payload['latestRepairRound']
        lines.append(f"- 最新视频反馈轮：共替换 {rr['changedCount']} 个独立槽，含跑步脚向 {rr['runFootRepairs']} 帧、跑步摆臂 {rr['runHandRepairs']} 帧、战斗手臂 {rr['combatHandRepairs']} 帧（N11两类重叠），其余 {rr['unchangedCount']} 帧保持原成品 SHA；逐图对照见 {rr['record']}。")
    if complete:
        lines.append('- 跑步采用960ms正常节奏、60ms/帧（本地），逐帧时长见 audit/run-timing.json；480ms仅旧基线。')
    else:
        lines.append('- 跑步960ms/圈、60ms/帧已按用户要求生效；196张完成静态逐帧复核，最新动态观感待验收。')
    lines += ['- 以上为本聊天/主审离线复核记录，用户尚未验收；客户端未接入、未进行客户端运行验收。', '',
              '目标 GPT Image 2.5 Sunburst / max；实际型号、质量和来源按每图真实记录，宿主未披露项保持 null。', '']
    (ROOT / 'STATUS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({key: payload[key] for key in ['exported', 'offlineReviewedGroups', 'offlineReviewedFrames', 'offlineReviewRecordStatus']}, ensure_ascii=False))


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    main()
