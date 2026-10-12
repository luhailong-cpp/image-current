"""水龙书生最终交付技术核验与图片保留计划；没有删除功能。

默认只读检查。--write-report 写 audit/final-delivery-check.json/md。
--write-retention-plan 写 audit/retention-plan.json/md，逐图保留当前 SHA。
源 PNG 清理后仍按 runtime + manifest + derived 内嵌生成记录核验；
缺失源图只报告实际状态，不冒充仍可重建，也不改历史记录。
退出码 0=技术检查通过，1=存在错误；不代表视觉/动态/客户端验收通过。
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageSequence
from render_review_board import gif_durations, load_run_timing
from finalize_review import validate_review, OFFLINE, TIMING_SELECTED

ROOT = Path(__file__).resolve().parents[1]
SPECS = {'run': (['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], 16, 60),
         'hit': (['E', 'W'], 6, 40), 'attack': (['E', 'W'], 12, 30),
         'cast': (['E', 'W'], 16, 45)}
IMAGE_SUFFIXES = {'.png', '.apng', '.gif', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def local(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f'路径越出角色目录: {value}')
    return path


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalize(value: str) -> str:
    return value.replace('\\', '/')


def valid_sha(value) -> bool:
    return isinstance(value, str) and re.fullmatch('[0-9a-fA-F]{64}', value) is not None


def prompt_text(value: str) -> str:
    return value.replace('\r\n', '\n').strip()


def image_info(path: Path) -> dict:
    with Image.open(path) as image:
        image.load()
        return {'format': image.format, 'mode': image.mode, 'width': image.width,
                'height': image.height,
                'alphaExtrema': list(image.getchannel('A').getextrema()) if image.mode == 'RGBA' else None}


def expected_slots() -> set[str]:
    return {f'{action}-{direction}-{frame:02d}' for action, (directions, count, _) in SPECS.items()
            for direction in directions for frame in range(1, count + 1)}


def required_preview_images(manifest: dict, default_profile: str) -> set[str]:
    names = {'preview/key-poses-current.png', 'preview/run-all-directions.gif'}
    for group in manifest.get('groups', []):
        prefix = f"preview/{group['action']}-{group['direction']}"
        names.add(prefix + '-contact.png')
        names.add(prefix + '-slow.gif')
        names.add(prefix + (f'-{default_profile}.gif' if group['action'] == 'run' else '-normal.gif'))
    return names


def check_delivery() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    report = {'checkedAt': now, 'character': ROOT.name, 'scope': 'technical_delivery_only',
              'visualApproval': 'not_assessed_by_this_tool', 'dynamicApproval': 'not_assessed_by_this_tool',
              'clientAcceptance': 'not_assessed_by_this_tool', 'issues': [], 'frames': [], 'previews': []}
    counts = Counter()

    def problem(code, detail, severity='error', slot=None):
        report['issues'].append({'severity': severity, 'code': code, 'slot': slot, 'detail': detail})

    def require(condition, code, detail, slot=None):
        if not condition:
            problem(code, detail, slot=slot)
        return condition

    manifest_path = ROOT / 'manifest.json'
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes.decode('utf-8-sig'))
        manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
        report['manifestSha256'] = manifest_sha
        timing = load_run_timing()
        report['timingSha256'] = sha(ROOT / 'audit/run-timing.json')
    except (OSError, ValueError, KeyError) as error:
        problem('manifest_or_timing_unreadable', str(error))
        report['summary'] = {'technicalPass': False, 'errors': 1, 'warnings': 0}
        return report
    frames = manifest.get('frames', [])
    by_slot = {row.get('slot'): row for row in frames}
    require(len(frames) == 196 and set(by_slot) == expected_slots(), 'slot_set_invalid',
            {'count': len(frames), 'missing': sorted(expected_slots() - set(by_slot)),
             'extra': sorted(set(by_slot) - expected_slots())})
    require(manifest.get('expected') == 196 and manifest.get('exported') == 196 and manifest.get('missing') == 0,
            'manifest_not_complete', {key: manifest.get(key) for key in ['expected', 'exported', 'missing']})
    group_ids = [(group.get('action'), group.get('direction')) for group in manifest.get('groups', [])]
    expected_groups = {(action, direction) for action, (directions, _, _) in SPECS.items() for direction in directions}
    require(len(group_ids) == 14 and set(group_ids) == expected_groups, 'group_set_invalid', group_ids)
    for group in manifest.get('groups', []):
        if group.get('action') in SPECS:
            require(group.get('expected') == SPECS[group['action']][1]
                    and group.get('accepted') == group.get('expected') and group.get('missing') == [],
                    'group_incomplete', {'action': group.get('action'), 'direction': group.get('direction')})
    try:
        selection = local(manifest['selection'])
        require(sha(selection) == manifest.get('selectionSha256'), 'selection_changed_since_export', relative(selection))
    except (OSError, KeyError, ValueError) as error:
        problem('selection_text_missing', str(error))
    run_profile = next(p for p in timing['profiles'] if p['id'] == timing['defaultProfile'])
    require(timing.get('clientIntegration') == 'not_integrated', 'timing_client_status_changed', timing.get('clientIntegration'))
    offline_final = manifest.get('animationApproval') == OFFLINE
    require(timing.get('status') == TIMING_SELECTED or 'pending' in timing.get('status', '') or 'candidate' in timing.get('status', ''),
            'timing_status_invalid', timing.get('status'))
    require((timing.get('status') == TIMING_SELECTED) == offline_final,
            'manifest_timing_review_status_mismatch', {'manifest': manifest.get('animationApproval'), 'timing': timing.get('status')})
    if offline_final:
        try:
            final_review_path = ROOT / 'audit/final-review.json'
            validate_review(manifest, read(final_review_path))
            require(sha(final_review_path) == manifest.get('offlineReview', {}).get('sha256'),
                    'final_review_record_sha_mismatch', 'audit/final-review.json')
            require(run_profile.get('status') == TIMING_SELECTED and run_profile.get('cycleMs') == 960,
                    'selected_run_profile_invalid', run_profile)
            require(manifest.get('clientIntegration') == 'not_integrated' and manifest.get('clientRuntimeAcceptance') == 'not_tested',
                    'offline_review_must_not_claim_client', manifest.get('clientIntegration'))
        except (OSError, ValueError, TypeError, KeyError) as error:
            problem('final_lead_offline_review_missing_or_stale', str(error))
        for group in manifest.get('groups', []):
            require(group.get('animationApproval') == OFFLINE, 'offline_group_status_missing', [group.get('action'), group.get('direction')])
            if group.get('action') == 'run':
                require(group.get('frameDurationsMs') == run_profile['frameDurationsMs'] and group.get('cycleMs') == 960
                        and group.get('durationMs') == 60 and group.get('timingStatus') == TIMING_SELECTED
                        and group.get('legacyTiming', {}).get('cycleMs') == 480,
                        'offline_run_group_timing_mismatch', group.get('direction'))
    for row in frames:
        slot = row.get('slot')
        entry = {'slot': slot, 'output': row.get('output'), 'source': row.get('source')}
        initial_errors = len(report['issues'])
        try:
            output = local(row['output'])
            require(relative(output) == f"runtime/{row['action']}/{row['direction']}/{row['frame']:02d}.png",
                    'runtime_path_invalid', row['output'], slot)
            actual_sha = sha(output)
            info = image_info(output)
            entry.update(sha256=actual_sha, geometry=info)
            require(actual_sha == row.get('sha256'), 'runtime_sha_mismatch', row['output'], slot)
            require(info == {'format': 'PNG', 'mode': 'RGBA', 'width': 1024, 'height': 1024, 'alphaExtrema': [0, 255]},
                    'runtime_geometry_invalid', info, slot)
            require(row.get('status') == 'exported', 'runtime_not_marked_exported', row.get('status'), slot)
            derived_path = local(row['derivedRecord'])
            derived = read(derived_path)
            entry['derivedRecord'] = relative(derived_path)
            entry['derivedRecordSha256'] = sha(derived_path)
            require(derived.get('slot') == slot and derived.get('file') == row['output'] and derived.get('sha256') == actual_sha,
                    'derived_output_mismatch', relative(derived_path), slot)
            if offline_final:
                require(row.get('visualApproval') == OFFLINE and row.get('animationApproval') == OFFLINE
                        and derived.get('animationApproval') == OFFLINE
                        and row.get('offlineReview') == manifest.get('offlineReview')
                        and derived.get('offlineReview') == manifest.get('offlineReview'),
                        'offline_frame_review_evidence_mismatch', relative(derived_path), slot)
            origin = derived['derivedFrom']
            require(origin == row.get('derivedFrom'), 'manifest_derived_chain_mismatch', origin, slot)
            require(origin.get('path') == row.get('source') and valid_sha(origin.get('sha256')),
                    'source_chain_invalid', origin, slot)
            original = derived['originalGenerationRecord']
            require(original.get('sha256') == origin.get('sha256'), 'embedded_source_sha_mismatch', origin, slot)
            require(bool(original.get('generatedAt')) and original.get('tool') == 'image_gen.imagegen'
                    and original.get('route') in ('builtin', 'builtin_host_managed'), 'generation_time_or_route_missing', relative(derived_path), slot)
            require(original.get('width', 0) >= 1024 and original.get('height', 0) >= 1024
                    and original.get('format') == 'PNG' and original.get('mode') == 'RGBA',
                    'embedded_native_spec_invalid', {k: original.get(k) for k in ['width', 'height', 'format', 'mode']}, slot)
            generation = local(origin['generationRecord'])
            require(sha(generation) == origin.get('generationRecordSha256'), 'generation_record_sha_changed', relative(generation), slot)
            require(read(generation) == original, 'embedded_original_differs_from_retained_text', relative(generation), slot)
            require('actualModel' in original and 'actualQuality' in original and original['actualModel'] is None
                    and original['actualQuality'] is None and bool(original.get('unverifiedReason')),
                    'actual_model_quality_unconfirmed_record_invalid', relative(generation), slot)
            target = original.get('configSnapshot', {})
            require(target.get('model') == 'gpt-image-2.5-sunburst' and target.get('quality') == 'max',
                    'configured_target_invalid', target, slot)
            submitted = original.get('submittedParameters', {})
            require(bool(submitted.get('prompt')) and submitted.get('model') is None and submitted.get('quality') is None,
                    'submitted_prompt_or_selector_record_invalid', relative(generation), slot)
            refs = original.get('references', [])
            require(bool(refs) and [normalize(ref.get('file', '')) for ref in refs] ==
                    [normalize(path) for path in submitted.get('referenced_image_paths', [])]
                    and all(valid_sha(ref.get('sha256')) for ref in refs),
                    'reference_text_chain_invalid', relative(generation), slot)
            counts['referenceHashesRetained'] += len(refs)
            source = local(origin['path'])
            entry['sourcePresence'] = 'present' if source.is_file() else 'absent_current_file'
            entry['historicalSourceSha256'] = origin['sha256']
            entry['sourceRequiredForRuntimeValidation'] = False
            if source.is_file():
                require(sha(source) == origin['sha256'], 'present_source_sha_mismatch', relative(source), slot)
                counts['sourcePngStillPresent'] += 1
            else:
                counts['sourcePngAbsentHistoricalTextRetained'] += 1
            # Only current bundle-local text files are mandatory. Historical absolute paths remain historical.
            for kind, value in [('prompt', original.get('prompt')), ('receipt', original.get('evidence', {}).get('toolResult'))]:
                require(bool(value), 'historical_text_path_missing', kind, slot)
                if not value:
                    continue
                try:
                    path = local(value)
                except ValueError:
                    counts['historicalExternalTextPathsPreserved'] += 1
                    continue
                require(path.is_file(), 'retained_text_file_missing', relative(path), slot)
                if path.is_file() and kind == 'prompt':
                    require(prompt_text(path.read_text(encoding='utf-8-sig')) == prompt_text(submitted['prompt']),
                            'retained_prompt_mismatch', relative(path), slot)
                if path.is_file() and kind == 'receipt':
                    read(path)
            if derived.get('sourceKind') == 'new':
                request_path = ROOT / 'provenance/requests' / f'{generation.stem}.json'
                request = read(request_path)
                params = request.get('submittedParameters', {})
                compare = lambda values: {k: v for k, v in values.items() if k not in ['model', 'quality'] or v is not None}
                require(compare(params) == compare(submitted), 'retained_request_mismatch', relative(request_path), slot)
            op = derived.get('operation', {})
            require(op.get('outputCanvas') == [1024, 1024] and op.get('scaledWholeCanvas') == [940, 940]
                    and op.get('offset') == [42, 49] and op.get('bboxUsedForTransform') is False
                    and op.get('perFrameGroundAlignment') is False and op.get('poseSynthesis') is False
                    and op.get('coordinateSystem') == manifest.get('coordinateSystem'),
                    'fixed_transform_record_invalid', op, slot)
            if row['action'] != 'run':
                require(row.get('durationMs') == SPECS[row['action']][2], 'combat_duration_changed', row.get('durationMs'), slot)
            elif offline_final:
                require(row.get('durationMs') == run_profile['frameDurationsMs'][row['frame'] - 1]
                        and row.get('timingStatus') == TIMING_SELECTED
                        and derived.get('durationMs') == row.get('durationMs')
                        and derived.get('timingStatus') == TIMING_SELECTED,
                        'offline_run_frame_timing_mismatch', row.get('durationMs'), slot)
            else:
                require(row.get('durationMs') == 60 and row.get('timingStatus') == 'user_requested_not_client',
                        'run_current_timing_mislabeled', row.get('timingStatus'), slot)
        except (OSError, ValueError, TypeError, KeyError) as error:
            problem('frame_chain_unreadable', str(error), slot=slot)
        entry['technicalPass'] = len(report['issues']) == initial_errors
        report['frames'].append(entry)
    outputs = {row.get('output') for row in frames if row.get('output')}
    actual_runtime = {relative(path) for path in (ROOT / 'runtime').rglob('*.png')}
    require(actual_runtime == outputs, 'runtime_file_set_mismatch', {'extra': sorted(actual_runtime - outputs), 'missing': sorted(outputs - actual_runtime)})
    require(len({row.get('sha256') for row in report['frames'] if row.get('sha256')}) == 196,
            'runtime_sha_not_unique_or_missing', '196 个独立成品 SHA 的技术检查；不同 SHA 仍不代表姿态通过。')
    for page_name, manifest_id in [('index.html', 'data'), ('all-directions.html', 'manifest')]:
        try:
            page = (ROOT / 'preview' / page_name).read_text(encoding='utf-8-sig')
            data = re.search(r'<script id="' + manifest_id + r'" type="application/json">([\s\S]*?)</script>', page)
            embedded_timing = re.search(r'<script id="timingData" type="application/json">([\s\S]*?)</script>', page)
            require(bool(data) and json.loads(data.group(1)) == manifest, 'preview_embedded_manifest_stale', page_name)
            require(bool(embedded_timing) and json.loads(embedded_timing.group(1)) == timing, 'preview_embedded_timing_stale', page_name)
            require(not re.search(r'(?:src|href)\s*=\s*["\']https?://', page, re.I), 'preview_external_resource', page_name)
        except (OSError, ValueError) as error:
            problem('preview_page_unreadable', {'file': page_name, 'error': str(error)})
    for group in manifest.get('groups', []):
        prefix = f"{group['action']}-{group['direction']}"
        try:
            rows = sorted([r for r in frames if r['action'] == group['action'] and r['direction'] == group['direction']], key=lambda r: r['frame'])
            record_path = ROOT / 'preview' / f'{prefix}.preview.json'
            record = read(record_path)
            if offline_final:
                require(record.get('animationApproval') == OFFLINE, 'preview_offline_review_status_stale', relative(record_path))
            require(record.get('derivedFrom') == [{'file': r['output'], 'sha256': r['sha256']} for r in rows],
                    'preview_source_list_stale', relative(record_path))
            require(record.get('manifest', {}).get('sha256') == manifest_sha, 'preview_manifest_snapshot_stale', relative(record_path))
            contact = ROOT / 'preview' / f'{prefix}-contact.png'
            image_info(contact)
            variants = {row['file']: row for row in record.get('animations', [])}
            base = run_profile['frameDurationsMs'] if group['action'] == 'run' else [r['durationMs'] for r in rows]
            for suffix, multiplier in [(timing['defaultProfile'] if group['action'] == 'run' else 'normal', 1), ('slow', 4)]:
                file = f'preview/{prefix}-{suffix}.gif'
                variant = variants[file]
                gif = local(file)
                require(sha(gif) == variant.get('sha256'), 'preview_gif_sha_mismatch', file)
                requested = [value * multiplier for value in base]
                with Image.open(gif) as image:
                    actual = [frame.info['duration'] for frame in ImageSequence.Iterator(image)]
                require(variant.get('originalFrameDurationsMs') == base and variant.get('requestedFrameDurationsMs') == requested
                        and variant.get('gifActualFrameDurationsMs') == actual
                        and actual == gif_durations(requested, legacy_combat=group['action'] != 'run')
                        and len(actual) == group['expected'] and sum(actual) == sum(requested),
                        'preview_gif_timing_mismatch', file)
                report['previews'].append({'file': file, 'sha256': sha(gif), 'frameDurationsMs': actual, 'cycleMs': sum(actual)})
        except (OSError, ValueError, KeyError, TypeError) as error:
            problem('preview_group_unreadable_or_not_rebuilt', {'group': prefix, 'error': str(error)})
    key_record = ROOT / 'preview/key-poses-current.png.generation.json'
    try:
        image_info(ROOT / 'preview/key-poses-current.png')
        selected_source_shas = {row.get('derivedFrom', {}).get('sha256') for row in frames} | {row.get('sha256') for row in frames}
        key = read(key_record)
        if key.get('manifest'):
            require(key['manifest'].get('sha256') == manifest_sha, 'key_pose_manifest_snapshot_stale', relative(key_record))
        if key.get('sha256'):
            require(key['sha256'] == sha(ROOT / 'preview/key-poses-current.png'), 'key_pose_image_sha_mismatch', relative(key_record))
        if offline_final:
            require(key.get('animationApproval') == OFFLINE, 'key_pose_offline_review_status_stale', relative(key_record))
        require(all(row.get('sha256') in selected_source_shas for row in key.get('derivedFrom', []))
                and bool(key.get('derivedFrom')), 'key_pose_preview_uses_unselected_source', relative(key_record))
    except (OSError, ValueError) as error:
        problem('key_pose_preview_unreadable', str(error))
    try:
        overview = ROOT / 'preview/run-all-directions.gif'
        overview_record = read(ROOT / 'preview/run-all-directions.gif.provenance.json')
        expected_run = [{'slot': row['slot'], 'file': row['output'], 'sha256': row['sha256']}
                        for number in range(1, 17) for direction in SPECS['run'][0]
                        for row in [by_slot[f'run-{direction}-{number:02d}']]]
        with Image.open(overview) as image:
            actual_durations = [frame.info['duration'] for frame in ImageSequence.Iterator(image)]
        require(overview_record.get('sha256') == sha(overview)
                and overview_record.get('manifestSha256') == manifest_sha
                and overview_record.get('derivedFrom') == expected_run
                and overview_record.get('sourceFrameDurationsMs') == run_profile['frameDurationsMs']
                and overview_record.get('gifActualFrameDurationsMs') == actual_durations
                and actual_durations == gif_durations(run_profile['frameDurationsMs'])
                and len(actual_durations) == 16 and sum(actual_durations) == 960,
                'run_overview_stale_or_invalid', 'preview/run-all-directions.gif')
    except (OSError, ValueError, KeyError, TypeError) as error:
        problem('run_overview_unreadable', str(error))
    require(sha(manifest_path) == manifest_sha, 'manifest_changed_during_check', '重新运行核验以取得稳定快照。')
    errors = sum(issue['severity'] == 'error' for issue in report['issues'])
    report['summary'] = {'technicalPass': errors == 0, 'errors': errors,
                         'warnings': len(report['issues']) - errors, 'expectedRuntimeFrames': 196,
                         'checkedRuntimeFrames': len(report['frames']),
                         'framesWithoutTechnicalErrors': sum(row['technicalPass'] for row in report['frames']),
                         **dict(counts)}
    report['sourceAbsenceMeaning'] = '源 PNG 缺失时，只验证保留文字记录和现有成品；不宣称源图仍存在，不从成品还原原生图，不等同可重跑原生导出。'
    return report


def retention_plan(check: dict) -> dict:
    manifest = read(ROOT / 'manifest.json')
    timing = load_run_timing()
    retained_previews = required_preview_images(manifest, timing['defaultProfile'])
    runtime = {row['output'] for row in manifest['frames'] if row.get('output')}
    selected = {row.get('source'): row.get('slot') for row in manifest['frames']}
    planned_images = []
    previous_path = ROOT / 'audit/retention-plan.json'
    previous = read(previous_path) if previous_path.exists() else {}
    old_entries = {entry['file']: entry for entry in previous.get('images', [])}
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        file = relative(path)
        entry = {'file': file, 'sha256': sha(path), 'bytes': path.stat().st_size,
                 'presentAtPlanTime': True, 'selectedSlot': selected.get(file),
                 'observedAt': check['checkedAt']}
        if file in runtime:
            entry.update(decision='keep_final_runtime', reason='最终 1024 游戏 PNG；以当前 manifest 校验。')
        elif file in retained_previews:
            entry.update(decision='keep_current_delivery_preview', reason='当前交付 contact、主候选/慢速 GIF 或关键姿态图；最终构建后核实来源刷新。')
        elif file.startswith('runtime/'):
            entry.update(decision='hold_unexpected_runtime', reason='不在当前 manifest，必须先确认，不自动删除。')
        elif file.startswith('sources/'):
            generation = ROOT / 'provenance/generation' / f'{path.stem}.json'
            if file.startswith('sources/reused/'):
                generation = ROOT / 'provenance/reused/run-E-09-original-record.json'
            entry.update(decision='delete_after_final_verification', reason='原生/重试源图；即使旧记录引用此路径也不永久保留像素。当前 SHA 与生成文字保留。')
            if generation.is_file():
                original = read(generation)
                entry['retainedGenerationText'] = {'file': relative(generation), 'sha256': sha(generation),
                    'sourceSha256': original.get('sha256'), 'generatedAt': original.get('generatedAt'),
                    'configuredTarget': original.get('configSnapshot'),
                    'actualModel': original.get('actualModel'), 'actualQuality': original.get('actualQuality'),
                    'unverifiedReason': original.get('unverifiedReason'), 'prompt': original.get('prompt'),
                    'references': original.get('references'), 'evidence': original.get('evidence')}
                if original.get('sha256') != entry['sha256']:
                    entry.update(decision='hold_source_provenance_gap', reason='当前源 SHA 与记录不符；先补真实来源文字，禁止改历史 SHA 掩盖。')
                elif file in selected and manifest.get('animationApproval') != OFFLINE:
                    entry.update(decision='keep_current_design_input', reason='当前入选原生设计，最新动态复核尚未完成；保留用于当前修订，不是图片备份。')
            else:
                entry.update(decision='hold_source_provenance_gap', reason='未按已知命名找到生成文字，需人工定位或补当前真实核验说明。')
        else:
            entry.update(decision='delete_after_final_verification', reason='历史诊断图、退稿比较图、旧预览或非必要中间图。保留其当前 SHA 和文字记录。')
        planned_images.append(entry)
    # Replanning after deletion must not discard historical hashes or pretend missing files remain.
    for file, old in old_entries.items():
        if not (ROOT / file).is_file():
            entry = dict(old)
            entry['presentAtPlanTime'] = False
            entry['lastObservedAbsentAt'] = check['checkedAt']
            entry['absenceNote'] = '当前缺失；本工具没有执行删除，也不推断删除者或时间。'
            planned_images.append(entry)
    present = [entry for entry in planned_images if entry['presentAtPlanTime']]
    missing_required = sorted((runtime | retained_previews) - {entry['file'] for entry in present})
    return {'schemaVersion': 1, 'character': ROOT.name, 'plannedAt': check['checkedAt'],
            'status': 'plan_only_no_deletion_performed', 'workspaceBoundary': ROOT.as_posix(),
            'manifestSha256': sha(ROOT / 'manifest.json'), 'timingSha256': sha(ROOT / 'audit/run-timing.json'),
            'policy': '依据用户 AGENTS.md 2026-09-23：最终成品与当前引用核实后只保留最终游戏图片、必要设计与接入文件；删除原图/回退/拒稿/中间图，保留逐图来源文字。',
            'prerequisites': ['root 已完成当前选帧和实际静态审阅；动态未完成时保留当前入选原生设计，不宣称最终动态验收通过。',
                              '只从当前 runtime 刷新预览；不要全量重建已清理的旧 sources。',
                              '运行 final_delivery_check.py --write-report --write-retention-plan，技术错误清零，所有必要图片存在。',
                              '删除前重新核实计划中每条路径仍在角色目录内、SHA 未改变；实际删除由 root 负责。',
                              '删除后再次运行核验；历史原图路径允许缺失，但 runtime/当前预览/来源文字必须完整。'],
            'currentTechnicalCheckPassed': check['summary']['technicalPass'],
            'deletionAuthorizedByThisTool': False,
            'keepTextAndImplementation': ['manifest.json', 'sources-index.json', 'audit/run-timing.json',
                'provenance/**/*.json', 'provenance/prompts/*.txt', 'prompts/*.txt', 'audit/*.json', 'audit/*.md',
                'review/**/*.json', 'review/**/*.md', 'preview/*.json', 'tools/*.py',
                'README.md', 'TASK.md', 'STATUS.md', 'MERGE_HANDOFF.md', 'progress.json'],
            'keepLiveHtml': ['preview/index.html', 'preview/all-directions.html'],
            'historicalHtmlPolicy': 'audit/review 中历史 HTML 仅作文字诊断历史，不是交付入口；不因它们引用旧图片而保留全部旧图。可随无必要中间文件一并由 root 清理。',
            'outsideWorkspacePolicy': '本计划不处理其他角色、旧批次、共享风格/身份图或宿主 generated_images。',
            'missingRequiredImages': missing_required,
            'summary': {'presentImageCount': len(present), 'historicalAbsentCount': len(planned_images) - len(present),
                        'byDecision': dict(Counter(entry['decision'] for entry in present)),
                        'candidateDeleteBytes': sum(entry['bytes'] for entry in present if entry['decision'] == 'delete_after_final_verification')},
            'images': sorted(planned_images, key=lambda entry: entry['file'])}


def write_json(path: Path, value: dict):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write-report', action='store_true')
    parser.add_argument('--write-retention-plan', action='store_true')
    args = parser.parse_args()
    report = check_delivery()
    if args.write_report:
        write_json(ROOT / 'audit/final-delivery-check.json', report)
        lines = ['# 最终交付技术核验', '', f"时间（UTC）：{report['checkedAt']}", '',
                 json.dumps(report['summary'], ensure_ascii=False), '',
                 '本检查不代表美术、动态或客户端验收。源图已清理时按保留文字与当前成品核验，不冒充原图仍在。', '']
        lines += [f"- {issue['slot'] or '全局'} [{issue['severity']}] {issue['code']}：{json.dumps(issue['detail'], ensure_ascii=False)}" for issue in report['issues']]
        (ROOT / 'audit/final-delivery-check.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if args.write_retention_plan:
        plan = retention_plan(report)
        write_json(ROOT / 'audit/retention-plan.json', plan)
        lines = ['# 水龙书生图片保留与清理计划', '', '仅准备清单，本工具没有删除功能，本次未删除图片。', '',
                 f"计划时间（UTC）：{plan['plannedAt']}", f"当前交付技术检查通过：{plan['currentTechnicalCheckPassed']}", '',
                 '## 执行前置条件', ''] + [f'- {item}' for item in plan['prerequisites']]
        lines += ['', '## 当前数量', '', json.dumps(plan['summary'], ensure_ascii=False), '',
                  '196 张 runtime 保留；每组最新 contact、跑步主选 uniform960/slow、战斗 normal/slow、当前关键姿态图保留。HTML固定960ms/圈，保留正常、慢速和逐帧检查。', '',
                  '当前入选且仍在使用的原生设计在最新动态复核完成前保留；淘汰 sources 及历史 audit/review 诊断图列为删除候选。JSON 内逐图保存当前 SHA、原生成记录路径及模型/质量/参考文字。', '',
                  '历史来源文字不改写成“文件仍在”。清理源图后不能再运行依赖原生输入的 build_delivery；成品检查用 final_delivery_check，HTML/GIF可从 runtime 重建。', '',
                  '仅处理本角色目录，不处理宿主缓存、共享参考或其他角色。保留全部逐图 JSON、提示词、清理文字、交接文档与必要脚本。', '',
                  '## 缺少的必要图片', '']
        lines += [f'- {file}' for file in plan['missingRequiredImages']] or ['- 无']
        lines += ['', '## 暂缓处理项', '']
        holds = [entry for entry in plan['images'] if entry['decision'].startswith('hold_') and entry['presentAtPlanTime']]
        lines += [f"- {entry['file']}：{entry['reason']}" for entry in holds] or ['- 无']
        lines += ['', '完整逐图路径、SHA、字节数和决定见 retention-plan.json。', '']
        (ROOT / 'audit/retention-plan.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2))
    return 0 if report['summary']['technicalPass'] else 1


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())
