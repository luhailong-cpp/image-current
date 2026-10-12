"""当前 runtime 的接触表和 GIF；逐帧候选时序与 GIF 量化均留证。"""
from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont, ImageSequence
from render_review_board import frame_durations, gif_durations, load_run_timing, offline_reviewed

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest_path = ROOT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    timing = load_run_timing()
    fully_reviewed = offline_reviewed(manifest, timing)
    static_reviewed = bool(manifest.get('staticReview')) and all(r.get('visualApproval') == 'static_sequence_reviewed' for r in manifest['frames'])
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 19)
    names = {'run': '跑步', 'hit': '受击', 'attack': '普攻', 'cast': '施法'}
    (ROOT / 'preview').mkdir(parents=True, exist_ok=True)
    for group in manifest['groups']:
        action, direction = group['action'], group['direction']
        rows = sorted([r for r in manifest['frames'] if r['action'] == action and r['direction'] == direction and r['output']], key=lambda r: r['frame'])
        if not rows:
            continue
        thumbs = []
        for row in rows:
            path = ROOT / row['output']
            if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError(f"runtime 与清单 SHA 不一致: {row['output']}")
            canvas = Image.new('RGB', (384, 430), '#e5e5df')
            ImageDraw.Draw(canvas).text((12, 10), f'{names[action]} {direction} · {row["frame"]:02d}', font=font, fill='#173d49')
            with Image.open(path) as original:
                if original.size != (1024, 1024) or original.mode != 'RGBA':
                    raise ValueError(f"预览要求 1024 RGBA 成品: {row['output']}")
                image = original.resize((384, 384), Image.Resampling.LANCZOS)
                canvas.paste(image, (0, 39), image)
                image.close()
            thumbs.append(canvas)
        cols = min(4, len(thumbs))
        sheet = Image.new('RGB', (384 * cols, ((len(thumbs) + cols - 1) // cols) * 430), '#e5e5df')
        for i, image in enumerate(thumbs):
            sheet.paste(image, ((i % cols) * 384, (i // cols) * 430))
        prefix = f'{action}-{direction}'
        contact = ROOT / 'preview' / f'{prefix}-contact.png'
        sheet.save(contact)
        sheet.close()
        outputs, animations = [contact.relative_to(ROOT).as_posix()], []
        if len(rows) == group['expected']:
            if action == 'run':
                variants = [(p['id'], p['id'], 1,
                             '960ms 正常节奏（姿态待复核）' if p['status'] == 'offline_selected_not_client' and not fully_reviewed else p['label'],
                             'candidate_pending_root_final_review' if p['status'] == 'offline_selected_not_client' and not fully_reviewed else p['status'])
                            for p in timing['profiles']]
                default_profile = next(profile for profile in timing['profiles'] if profile['id'] == timing['defaultProfile'])
                slow_label = default_profile['label'] if fully_reviewed or static_reviewed else '960ms 正常节奏（姿态待复核）'
                variants.append(('slow', timing['defaultProfile'], 4, slow_label + ' · 0.25×',
                                 timing['status'] if fully_reviewed or static_reviewed else 'candidate_pending_root_final_review'))
            else:
                status = 'offline_reviewed_not_client' if fully_reviewed else 'planned'
                variants = [('normal', None, 1, '原战斗方案 · 1×', status), ('slow', None, 4, '原战斗方案 · 0.25×', status)]
            for suffix, profile, multiplier, label, status in variants:
                original_ms = frame_durations(group, rows, timing, profile)
                requested_ms = [value * multiplier for value in original_ms]
                encoded_ms = gif_durations(requested_ms, legacy_combat=action != 'run')
                output = ROOT / 'preview' / f'{prefix}-{suffix}.gif'
                thumbs[0].save(output, save_all=True, append_images=thumbs[1:], duration=encoded_ms, loop=0, disposal=2, optimize=False)
                with Image.open(output) as saved:
                    actual_ms = [frame.info['duration'] for frame in ImageSequence.Iterator(saved)]
                if actual_ms != encoded_ms:
                    raise ValueError(f'GIF 实际时长与量化不符: {output.name}')
                outputs.append(output.relative_to(ROOT).as_posix())
                animations.append({'file': outputs[-1], 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                                   'label': label, 'profile': profile, 'timingStatus': status,
                                   'playbackSpeed': 1 / multiplier, 'originalFrameDurationsMs': original_ms,
                                   'requestedFrameDurationsMs': requested_ms, 'gifActualFrameDurationsMs': actual_ms,
                                   'originalCycleMs': sum(original_ms), 'requestedCycleMs': sum(requested_ms),
                                   'gifActualCycleMs': sum(actual_ms), 'frameCount': len(actual_ms),
                                   'quantization': ('Cumulative boundaries rounded half-up to GIF centiseconds; no inserted, duplicated or interpolated frames.' if action == 'run'
                                                    else 'Original combat cumulative boundary quantization retained (Python round, ties to even); no frame timing plan changed.')})
        record = {'outputs': outputs, 'animations': animations,
                  'operation': 'preview thumbnails and GIF on neutral backdrop; no pose synthesis or per-frame anchoring',
                  'manifest': {'file': 'manifest.json', 'sha256': manifest_sha},
                  'expectedFrames': group['expected'], 'actualFrames': len(rows),
                  'previewTiming': ({'file': 'audit/run-timing.json', 'sha256': hashlib.sha256((ROOT / 'audit/run-timing.json').read_bytes()).hexdigest(),
                                     'defaultProfile': timing['defaultProfile'], 'status': timing['status'],
                                     'legacyBaselineCycleMs': 480, 'clientIntegration': 'not_integrated'} if action == 'run'
                                    else {'status': 'offline_reviewed_not_client' if fully_reviewed else 'planned', 'frameDurationsMs': frame_durations(group, rows, timing), 'unchangedCombatTiming': True}),
                  'animationApproval': 'offline_reviewed' if fully_reviewed else ('pending_final_dynamic_review' if static_reviewed else 'pending_visual_dynamic_review'),
                  'staticReview': manifest.get('staticReview') if static_reviewed else None,
                  'offlineReview': manifest.get('offlineReview') if fully_reviewed else None,
                  'clientIntegration': 'not_integrated', 'clientRuntimeAcceptance': 'not_tested',
                  'userAcceptance': 'not_reviewed_by_user',
                  'derivedFrom': [{'file': row['output'], 'sha256': row['sha256']} for row in rows]}
        (ROOT / 'preview' / f'{prefix}.preview.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for thumb in thumbs:
            thumb.close()
        print(prefix, len(rows), len(outputs))


if __name__ == '__main__':
    main()
