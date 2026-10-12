"""只应用已存在的本聊天主审离线复核记录；绝不创建通过记录。

python tools/finalize_review.py          # 只读预检
python tools/finalize_review.py --write  # 验证通过后更新清单/派生状态/时序/两份 HTML

audit/final-review.json 要求 reviewer、reviewedAt，frames 为完整196条
{slot, sourceSha256}，或 slots 为 {slot: sourceSha256} 映射；
groups 必须完整14条 {action, direction, offlineApproved: true, notes}。
这只是本地审核，不产生客户端验收。PNG、原生生成记录、选表均不改变。
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from render_review_board import load_run_timing, render_review_board
from build_delivery import render_main_preview

ROOT = Path(__file__).resolve().parents[1]
SPECS = {'run': (['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], 16),
         'hit': (['E', 'W'], 6), 'attack': (['E', 'W'], 12), 'cast': (['E', 'W'], 16)}
OFFLINE = 'offline_reviewed'
TIMING_SELECTED = 'offline_selected_not_client'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(value: str) -> Path:
    path = Path(value)
    path = (path if path.is_absolute() else ROOT / path).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f'路径越出角色目录: {value}')
    return path


def validate_review(manifest: dict, review: dict) -> dict:
    """纯校验：不能以缺省值、非布尔 true 或部分审核推导整组通过。"""
    expected_slots = {f'{action}-{direction}-{number:02d}' for action, (directions, count) in SPECS.items()
                      for direction in directions for number in range(1, count + 1)}
    expected_groups = {(action, direction) for action, (directions, _) in SPECS.items() for direction in directions}
    frames = manifest.get('frames', [])
    by_slot = {frame.get('slot'): frame for frame in frames}
    if len(frames) != 196 or set(by_slot) != expected_slots:
        raise ValueError('当前 manifest 不是完整且唯一的196槽')
    if manifest.get('exported') != 196 or any(frame.get('status') != 'exported' or not frame.get('output') for frame in frames):
        raise ValueError('196槽必须已经真实导出，不能将候选或空槽直接标为通过')
    if review.get('character', manifest.get('character')) != manifest.get('character'):
        raise ValueError('主审复核记录角色与当前 manifest 不符')
    if review.get('supersededAt') or review.get('status') == 'superseded_by_user_feedback':
        raise ValueError('该复核已被用户新反馈撤回，不得重新应用')
    if not review.get('reviewer') or not review.get('reviewedAt'):
        raise ValueError('主审复核记录必须注明 reviewer 和 reviewedAt')
    stamp = datetime.fromisoformat(review['reviewedAt'].replace('Z', '+00:00'))
    if stamp.tzinfo is None:
        raise ValueError('reviewedAt 必须含时区')
    if 'frames' in review and 'slots' in review:
        raise ValueError('主审复核记录只用 frames 或 slots 一种映射，避免两份结论冲突')
    if isinstance(review.get('slots'), dict):
        reviewed_sources = review['slots']
    elif isinstance(review.get('frames'), list):
        reviewed_sources = {}
        for row in review['frames']:
            slot = row.get('slot')
            if slot in reviewed_sources:
                raise ValueError(f'主审离线复核重复槽位: {slot}')
            if 'sourceSha256' in row and 'sourceSha' in row and row['sourceSha256'] != row['sourceSha']:
                raise ValueError(f'主审离线复核来源 SHA 冲突: {slot}')
            reviewed_sources[slot] = row.get('sourceSha256', row.get('sourceSha'))
    else:
        raise ValueError('缺少完整196槽的 frames/sourceSha256 或 slots 映射')
    if set(reviewed_sources) != expected_slots:
        raise ValueError('主审离线复核必须覆盖且只覆盖当前196槽')
    for slot, source_sha in reviewed_sources.items():
        if not isinstance(source_sha, str) or not re.fullmatch('[0-9a-f]{64}', source_sha):
            raise ValueError(f'主审复核来源 SHA 不合法: {slot}')
        if source_sha != by_slot[slot].get('derivedFrom', {}).get('sha256'):
            raise ValueError(f'主审离线复核已过期，来源已变化: {slot}')
    groups = review.get('groups', [])
    if not isinstance(groups, list) or len(groups) != 14:
        raise ValueError('主审离线复核必须逐组覆盖14组')
    reviewed_groups = {}
    for group in groups:
        key = (group.get('action'), group.get('direction'))
        if key in reviewed_groups or key not in expected_groups:
            raise ValueError(f'主审离线复核重复或非法动作组: {key}')
        if group.get('offlineApproved') is not True:
            raise ValueError(f'主审离线复核尚未明确通过: {key}')
        reviewed_groups[key] = group
    if set(reviewed_groups) != expected_groups:
        raise ValueError('主审离线复核动作组不完整')
    manifest_groups = {(group.get('action'), group.get('direction')): group for group in manifest.get('groups', [])}
    if len(manifest.get('groups', [])) != 14 or set(manifest_groups) != expected_groups:
        raise ValueError('manifest 动作组不完整')
    return {'sources': reviewed_sources, 'groups': reviewed_groups,
            'reviewer': review['reviewer'], 'reviewedAt': review['reviewedAt']}


def apply_review(manifest: dict, timing: dict, review: dict, derived_records: dict,
                 review_sha256: str, finalized_at: str) -> tuple[dict, dict, dict]:
    """生成待写内容，函数自身不写文件，便于验证过期/缺失审核的拒绝行为。"""
    validated = validate_review(manifest, review)
    manifest, timing, derived_records = deepcopy(manifest), deepcopy(timing), deepcopy(derived_records)
    profile = next(profile for profile in timing['profiles'] if profile['id'] == timing['defaultProfile'])
    durations = profile['frameDurationsMs']
    if timing['defaultProfile'] != 'uniform960' or durations != [60] * 16 or sum(durations) != 960:
        raise ValueError('当前时序不等于用户指定960ms/圈、均匀60ms逐帧节奏，需主审另行明确')
    evidence = {'record': 'audit/final-review.json', 'sha256': review_sha256,
                'reviewer': validated['reviewer'], 'reviewedAt': validated['reviewedAt'],
                'scope': 'offline_static_and_dynamic_not_client',
                'reviewAuthority': 'current_chat_lead_offline_review',
                'userAcceptance': 'not_reviewed_by_user'}
    legacy = {'frameDurationsMs': [30] * 16, 'cycleMs': 480,
              'status': 'legacy_baseline_not_approved_normal'}
    for row in manifest['frames']:
        derived = derived_records[row['slot']]
        if derived.get('derivedFrom') != row.get('derivedFrom') or derived.get('sha256') != row.get('sha256'):
            raise ValueError(f"派生记录与当前清单不符: {row['slot']}")
        if derived.get('originalGenerationRecord', {}).get('sha256') != validated['sources'][row['slot']]:
            raise ValueError(f"内嵌原始记录来源不符: {row['slot']}")
        row.update(visualApproval=OFFLINE, animationApproval=OFFLINE, offlineReview=evidence)
        derived.update(animationApproval=OFFLINE, offlineReview=evidence,
                       clientIntegration='not_integrated', clientRuntimeAcceptance='not_tested',
                       userAcceptance='not_reviewed_by_user')
        if row['action'] == 'run':
            row.update(durationMs=durations[row['frame'] - 1], timingStatus=TIMING_SELECTED,
                       legacyDurationMs=30, legacyTimingStatus=legacy['status'])
            derived.update(durationMs=row['durationMs'], timingStatus=TIMING_SELECTED,
                           legacyDurationMs=30, legacyTimingStatus=legacy['status'])
    for group in manifest['groups']:
        human = validated['groups'][(group['action'], group['direction'])]
        group.update(animationApproval=OFFLINE, offlineReview={**evidence, 'notes': human.get('notes')})
        if group['action'] == 'run':
            group.update(durationMs=60, frameDurationsMs=list(durations), cycleMs=960,
                         timingStatus=TIMING_SELECTED, legacyTiming=legacy)
    manifest.update(animationApproval=OFFLINE, offlineReview=evidence,
                    reviewFinalizedAt=finalized_at, clientIntegration='not_integrated', clientRuntimeAcceptance='not_tested',
                    userAcceptance='not_reviewed_by_user',
                    sourceRetention={'sourcePixelsGuaranteedPresent': False,
                                     'historicalFields': ['frames[].source', 'inventory[].source', 'derivedFrom', 'originalGenerationRecord'],
                                     'executionRecord': 'audit/retention-executed.json',
                                     'note': 'source、inventory及逐图来源中的路径记录原生成历史，不承诺源像素留存；最终清理执行与留存情况以 audit/retention-executed.json 为准。本收尾脚本不删除图片。'},
                    runTiming={'file': 'audit/run-timing.json', 'defaultProfile': timing['defaultProfile'],
                               'status': TIMING_SELECTED, 'cycleMs': 960, 'legacyCycleMs': 480},
                    note='196帧与14动作组已由所引主审复核记录完成本地静态及动态审核；这是本聊天主审离线复核结论，用户尚未验收；未接入或验收客户端。')
    timing.update(status=TIMING_SELECTED, selectedAt=validated['reviewedAt'], selectionEvidence=evidence,
                  clientIntegration='not_integrated', clientRuntimeAcceptance='not_tested',
                  userAcceptance='not_reviewed_by_user',
                  note='用户指定960ms/圈，每帧60ms，旧快速档移出正式预览；未入客户端。')
    profile.update(status=TIMING_SELECTED, label='960ms 正常跑步 · 每帧60ms')
    return manifest, timing, derived_records


def encode(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def prepare() -> tuple[dict, dict, dict, dict]:
    snapshots = {}

    def take(path: Path):
        data = path.read_bytes()
        snapshots[path] = sha(data)
        return json.loads(data.decode('utf-8-sig'))

    manifest = take(ROOT / 'manifest.json')
    timing = take(ROOT / 'audit/run-timing.json')
    review_path = ROOT / 'audit/final-review.json'
    if not review_path.is_file():
        raise ValueError('尚无 audit/final-review.json 主审离线复核通过记录；不会生成或补写通过结论')
    review = take(review_path)
    validate_review(manifest, review)
    selection = safe_path(manifest['selection'])
    if sha(selection.read_bytes()) != manifest.get('selectionSha256'):
        raise ValueError('选表已变化，必须先重建当前清单再最终审核')
    snapshots[selection] = sha(selection.read_bytes())
    derived_records = {}
    for row in manifest['frames']:
        output_path = safe_path(row['output'])
        if sha(output_path.read_bytes()) != row['sha256']:
            raise ValueError(f"成品 SHA 不符: {row['slot']}")
        snapshots[output_path] = row['sha256']
        derived_records[row['slot']] = take(safe_path(row['derivedRecord']))
        generation_path = safe_path(row['derivedFrom']['generationRecord'])
        original = take(generation_path)
        if snapshots[generation_path] != row['derivedFrom']['generationRecordSha256']:
            raise ValueError(f"原生成文字已变化，需先刷新派生记录: {row['slot']}")
        if derived_records[row['slot']].get('originalGenerationRecord') != original:
            raise ValueError(f"内嵌原记录已过期: {row['slot']}")
    now = datetime.now(timezone.utc).isoformat()
    final_manifest, final_timing, final_derived = apply_review(
        manifest, timing, review, derived_records, snapshots[review_path], now)
    return final_manifest, final_timing, final_derived, snapshots


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write', action='store_true', help='严格审核预检通过后才写本地审核状态；不改任何 PNG')
    args = parser.parse_args()
    manifest, timing, derived, snapshots = prepare()
    if args.write:
        outputs = {safe_path(row['derivedRecord']): encode(derived[row['slot']]) for row in manifest['frames']}
        outputs[ROOT / 'manifest.json'] = encode(manifest)
        outputs[ROOT / 'audit/run-timing.json'] = encode(timing)
        outputs[ROOT / 'preview/index.html'] = render_main_preview(manifest, timing).encode('utf-8')
        outputs[ROOT / 'preview/all-directions.html'] = render_review_board(manifest, timing).encode('utf-8')
        if any(sha(path.read_bytes()) != old_sha for path, old_sha in snapshots.items()):
            raise ValueError('预检期间输入发生变化，拒绝写入；请重新核对当前审核记录')
        # All gate checks finish before the first write. No PNG is among these outputs.
        for path, data in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({'written': args.write, 'frames': 196, 'groups': 14,
                      'approval': OFFLINE, 'runCycleMs': 960, 'clientIntegration': 'not_integrated'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f'finalize_review: {error}', file=sys.stderr)
        raise SystemExit(2)
