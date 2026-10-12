"""Read-only audit of this character's committed predecessor assets."""
from collections import defaultdict
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parents[2]
RUN = BASE / 'run-correction-20260930/characters' / ROOT.name
COMBAT = BASE / 'combat-20260929/characters' / ROOT.name
REVIEW = ROOT / 'review'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def describe(path):
    with Image.open(path) as image:
        image.load()
        rgba = image.convert('RGBA')
        return {'path': path.as_posix(), 'sha256': digest(path), 'size': list(image.size),
                'mode': image.mode, 'format': image.format,
                'alpha_range': list(rgba.getchannel('A').getextrema()),
                'pixel_sha256': sha256(str(image.size).encode() + rgba.tobytes()).hexdigest()}


def combat_path(value):
    value = value.replace('\\', '/')
    if '/characters/' in value:
        value = 'characters/' + value.split('/characters/', 1)[1]
    return (BASE / 'combat-20260929' / value) if value.startswith('characters/') else COMBAT / value


def provenance(path, batch):
    candidates = [Path(str(path) + '.generation.json')]
    if batch == COMBAT:
        candidates.append(COMBAT / 'provenance/receipts' / (path.stem + '.json'))
    records = []
    for record_path in candidates:
        if not record_path.is_file():
            continue
        record = read(record_path)
        records.append({'path': record_path.as_posix(), 'sha256': digest(record_path),
                        'png_sha_matches': record.get('sha256') == digest(path),
                        'content': record})
    tool_path = COMBAT / 'provenance/receipts' / (path.stem + '-tool.json')
    tool = ({'path': tool_path.as_posix(), 'sha256': digest(tool_path), 'content': read(tool_path)}
            if batch == COMBAT and tool_path.is_file() else None)
    return {'full_records': records, 'tool_receipt': tool,
            'status': ('full_record_sha_verified' if all(r['png_sha_matches'] for r in records)
                       else 'sha_mismatch') if records else 'tool_receipt_only' if tool else 'missing',
            'actual_model_quality': 'unconfirmed'}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    run_review = read(RUN / 'review.json')
    decisions = {r['file']: r for r in run_review['attempts']}
    run_native, combat_native, exports, selections = [], [], [], []
    for path in sorted((RUN / 'generation').rglob('*.png')):
        item = describe(path)
        item.update(slot=f'run/{path.parent.name}/{path.stem.split("-")[0]}.png',
                    provenance=provenance(path, RUN),
                    prior_review=decisions.get(path.relative_to(RUN).as_posix()))
        run_native.append(item)
    for path in sorted((COMBAT / 'staging').glob('*.png')):
        match = re.fullmatch(r'(hit|attack|cast)-([EW])-(\d+)-v(\d+)', path.stem)
        if match:
            action, direction, number, version = match.groups()
            item = describe(path)
            item.update(filename_slot=f'{action}/{direction}/{number}.png', version=int(version),
                        provenance=provenance(path, COMBAT))
            combat_native.append(item)
    selected_sources = {}
    for path in [COMBAT / 'hit-E-selection.json', COMBAT / 'hit-W-selection.json',
                 COMBAT / 'staging/attack-E-selection.json']:
        data = read(path)
        selected = []
        for frame in data['frames']:
            source = combat_path(frame['file'])
            record_path = combat_path(frame['generationRecord'])
            key = f"{data['action']}/{data['direction']}/{frame['frame']:02}.png"
            selected_sources[key] = source.as_posix()
            selected.append({'slot': key, 'source_path': source.as_posix(), 'sha256': digest(source),
                             'source_record': record_path.as_posix(), 'record_exists': record_path.is_file(),
                             'expected_source_sha': frame.get('sha256'), 'original_selection': frame})
        selections.append({'path': path.as_posix(), 'sha256': digest(path),
                           'status': data.get('status'), 'frames': selected})
    slots = []
    for action, directions, count in [('run', ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], 16),
                                     ('hit', ['E', 'W'], 6), ('attack', ['E', 'W'], 12),
                                     ('cast', ['E', 'W'], 16)]:
        for direction in directions:
            for index in range(1, count + 1):
                key = f'{action}/{direction}/{index:02}.png'
                if action == 'run':
                    candidates = [r for r in run_native if r['slot'] == key]
                elif key in selected_sources:
                    candidates = [r for r in combat_native if r['path'] == selected_sources[key]]
                else:
                    candidates = [r for r in combat_native if r['filename_slot'] == key]
                nonrejected = [r for r in candidates if r.get('prior_review', {}).get('result') != 'rejected']
                slots.append({'slot': key, 'candidate_paths': [r['path'] for r in candidates],
                              'has_native_candidate': bool(candidates),
                              'selected_source': selected_sources.get(key),
                              'status': 'missing' if not candidates else 'prior_rejected_only'
                              if action == 'run' and not nonrejected else 'selected_pending_review'
                              if key in selected_sources else 'pending_selection_or_review'})
    path = RUN / 'candidate/walk/E/01.png'
    record_path = Path(str(path) + '.generation.json')
    derived = read(record_path)
    item = describe(path)
    item.update(slot='run/E/01.png', kind='candidate_not_visual_approved', derivation=derived,
                record_path=record_path.as_posix(),
                source_path=(RUN / 'generation/E/01-v4.png').as_posix(),
                source_sha_matches=digest(RUN / 'generation/E/01-v4.png') == derived['derivedFrom']['sha256'],
                output_sha_matches=item['sha256'] == derived['sha256'])
    exports.append(item)
    technical_path = COMBAT / 'export-preview-20260930-v1/technical-report.json'
    technical = read(technical_path)
    for derived in technical['frames']:
        action, direction, number = Path(derived['file']).parts[-3:]
        path = COMBAT / 'export-preview-20260930-v1/characters' / action / direction / number
        source = combat_path(derived['derivedFrom']['file'])
        record_path = combat_path(derived['derivedFrom']['generationRecord'])
        item = describe(path)
        item.update(slot=f'{action}/{direction}/{number}', kind='technical_preview_not_runtime',
                    source_path=source.as_posix(), source_sha_matches=digest(source) == derived['derivedFrom']['sha256'],
                    source_record=record_path.as_posix(),
                    source_record_sha_matches=digest(record_path) == derived['derivedFrom']['generationRecordSha256'],
                    output_sha_matches=item['sha256'] == derived['sha256'], derivation=derived)
        exports.append(item)
    study_path = BASE / 'run-correction-20260930/00-reference-run-E/run-keys-v1.png'
    study = describe(study_path)
    study.update(kind='2x2_pose_study_sheet', native_cell_size=[627, 627], formal_native_eligible=False,
                 generation_record=read(Path(str(study_path) + '.generation.json')))
    contacts = [describe(p) for p in sorted((COMBAT / 'export-preview-20260930-v1').glob('contact-*.png'))]
    contacts += [describe(p) for p in sorted((RUN / 'preview').glob('*.jpg'))]
    groups = []
    for group in dict.fromkeys('/'.join(r['slot'].split('/')[:2]) for r in slots):
        matching = [r for r in slots if r['slot'].startswith(group + '/')]
        groups.append({'group': group, 'required': len(matching),
                       'native_covered_slots': sum(r['has_native_candidate'] for r in matching),
                       'missing_slots': [r['slot'] for r in matching if r['status'] == 'missing'],
                       'rejected_only_slots': [r['slot'] for r in matching if r['status'] == 'prior_rejected_only'],
                       'selected_slots': sum(bool(r['selected_source']) for r in matching),
                       'exported_1024_count': sum(r['slot'].startswith(group + '/') for r in exports)})
    native = run_native + combat_native
    tool_only = [r['path'] for r in native if r['provenance']['status'] == 'tool_receipt_only']
    sha_problems = [r['path'] for r in native if r['provenance']['status'] == 'sha_mismatch']
    full_records = [r for r in native if r['provenance']['full_records']]
    pixels = defaultdict(list)
    for item in native:
        pixels[item['pixel_sha256']].append(item['path'])
    duplicates = [paths for paths in pixels.values() if len(paths) > 1]
    summary = {
        'required': 196, 'run_native_attempts': len(run_native), 'combat_native_attempts': len(combat_native),
        'run_native_slots_including_rejected': 2, 'run_nonrejected_candidate_slots': 1,
        'run_slots_without_any_native_attempt': 126, 'run_slots_without_nonrejected_candidate': 127,
        'combat_native_slots': 55, 'combat_missing_slots': 13, 'combat_selected_slots': 24,
        'run_1024_candidate_exports': 1, 'combat_1024_technical_previews': 24,
        'combat_runtime_pngs': len(list((COMBAT / 'runtime').rglob('*.png'))),
        'total_native_slots_including_rejected': 57, 'slots_without_any_native_attempt': 139,
        'nonrejected_candidate_slot_upper_bound': 56, 'slots_without_nonrejected_candidate': 140,
        'full_generation_record_count': len(full_records), 'tool_receipt_only_count': len(tool_only),
        'sha_mismatch_count': len(sha_problems), 'native_duplicate_pixel_groups': len(duplicates),
        'all_native_files_1254_rgba': all(r['size'] == [1254, 1254] and r['mode'] == 'RGBA' for r in native),
        'export_source_and_output_sha_checks_passed': all(r['source_sha_matches'] and r['output_sha_matches']
                                                       and r.get('source_record_sha_matches', True) for r in exports),
        'actual_model_quality_confirmed_count': 0, 'visual_review_performed': False,
        'client_integration_or_runtime_test_performed': False,
    }
    evidence = [RUN / 'review.json', RUN / 'STATUS.md', RUN / 'HANDOFF.md', RUN / 'candidate-inventory.json',
                technical_path, BASE / 'combat-20260929/handoffs-20260930/00_reference_topright_boy.md',
                BASE / 'combat-20260929/handoffs-20260930/recovered-cast-W-15-tool-result.json']
    report = {'schema_version': 1, 'character': ROOT.name,
              'audited_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
              'scope': '只读旧稿，实测PNG尺寸和SHA；不复制、修改或删除图片，不执行美术验收或客户端操作。',
              'summary': summary, 'groups': groups, 'slots': slots,
              'run_native_attempts': run_native, 'combat_native_attempts': combat_native,
              'existing_1024_exports': exports, 'selections': selections, 'research_sheet': study,
              'contact_images': contacts, 'provenance_gaps': tool_only, 'sha_problems': sha_problems,
              'duplicate_native_pixel_groups': duplicates,
              'supporting_evidence': [{'path': p.as_posix(), 'sha256': digest(p)} for p in evidence]}
    REVIEW.mkdir(exist_ok=True)
    (REVIEW / 'prior_inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    markdown = ['# 00 金发带道童：旧动作库存与高清来源审计', '',
                f"核对时间：{report['audited_at']}（America/New_York）。只读旧稿，未复制、修改或删除 PNG；没有新增美术验收或客户端验证结论。", '',
                '已有 **71 张原生1254×1254 RGBA独立单帧尝试**：跑步4张、战斗67张。按槽位去重为 **57/196**，其中跑步E09只有明确拒稿；非拒稿候选覆盖上限 **56/196**。这些是可继续审核的制作库存，不表示已经通过。', '',
                '| 动作/方向 | 目标 | 原生覆盖槽 | 无原生尝试帧号 | 既有选表槽 | 1024技术导出 |',
                '|---|---:|---:|---|---:|---:|']
    for group in groups:
        missing = ', '.join(Path(s).stem for s in group['missing_slots']) or '无'
        markdown.append(f"| {group['group']} | {group['required']} | {group['native_covered_slots']} | {missing} | {group['selected_slots']} | {group['exported_1024_count']} |")
    markdown += ['', '## 高清单帧与正式导出', '',
                 '- 战斗55/68槽已有1254原生独立单帧；准确缺口是 W普攻01–12、W施法16，共13槽。已有24槽选序，其余施法候选须选图和完整序列验收。',
                 '- 跑步E01-v4是唯一非拒稿候选；E01-v1多余手部、E01-v3双臂链条不合理、E09-v1葫芦穗颜色和头部比例错误，旧review明确拒收。其余126槽没有单帧尝试，连同E09修正，共127槽缺非拒稿候选。',
                 '- 实际1024导出共25张：跑步E01候选1张、战斗技术预览24张。全部来源和导出SHA已重新核验，源图均1254；尚非本批美术通过或正式交付。combat/runtime实际0张。', '',
                 '## 小格研究与预览', '',
                 f'- 四关键姿势母表：[run-keys-v1.png]({study_path.as_posix()})，整图1254×1254，2×2每格 **627×627**；不能放大计为1024原生单帧。',
                 '- 战斗三张联系表分别780×520、780×520、1040×780 RGB，跑步E-contact.jpg也是派生联系表；它们不计动作槽。',
                 '- 更早v13 E/W idle仅512，只用于身份和朝向参考；这不影响已有1254独立生成稿的原生尺寸资格。', '',
                 '## 模型与逐图来源', '',
                 f'- 71张原生单帧中，**{len(full_records)}张有完整逐图JSON**，SHA全部吻合；**{len(tool_only)}张只有成功工具回执**。未发现原生稿RGBA像素完全重复。',
                 '- 完整记录目标为gpt-image-2.5-sunburst/max，实际提交model/quality为null，实际返回型号/质量也为null；配置目标不等于实际确认。12份tool-only回执同样没有披露实际模型与质量。',
                 '- 缺完整逐图记录的是cast-W-01-v1至09-v1及11-v1、12-v1、13-v1。实图和成功回执存在，应补来源记录，不应因缺记录重新生成；无证据参数保持null。',
                 '- cast/W15已由旧completed工具结果恢复，当前SHA与恢复记录一致，不是缺图。',
                 '- 旧记录中D:/luyuan/wuxingqitan/image为历史路径，本报告使用本机D:/work/image核对；旧来源记录不改写。', '',
                 '## 选序和需要继续复核的部分', '',
                 '- hit/E：01-v1 → 03-v3 → 02-v1 → 04-v1 → 05-v1 → 06-v1。',
                 '- hit/W：03-v1 → 02-v1 → 03-v2 → 04-v1 → 05-v1 → 06-v1。第1槽有既有选图，不应按文件名缺01误报。',
                 '- attack/E：04-v2、07-v2，其余v1。施法不可按最高版本号自动选定。',
                 '- 旧handoff提示hit/E末帧变高、hit/W峰值顺序和回弹偏急、attack/E09→10→11头高跳动风险，需当前正常速度动态复核。',
                 '- 跑步STATUS中0候选已落后于review.json及实际1张导出；战斗旧technical-report的file字段写runtime路径，而实际文件只在export-preview中。',
                 '- 本报告不把文件数、分辨率、SHA不同或旧静态选表当作美术通过；未运行客户端。', '',
                 '逐PNG实际路径、SHA、原生尺寸、原始来源记录、196槽状态、选择映射和证据SHA见 [prior_inventory.json](prior_inventory.json)。', '']
    (REVIEW / 'prior_inventory.md').write_text('\n'.join(markdown), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
