from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
from PIL import Image

ROOT = Path('D:/work/image')
REVIEW = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009'
AUDIT = REVIEW / 'southeast-audit-v01'
BASE = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southeast'
OUT = Path(__file__).resolve().parent

def now():
    return datetime.now(timezone.utc).isoformat()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def save(name, data):
    with (OUT / name).open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

inventory = read(AUDIT / 'inventory.json')
snapshot = read(AUDIT / 'snapshot-inputs.json')
recheck = read(OUT / 'source-recheck.json')
pixel = read(OUT / 'pixel-verification.json')
snapshot_native = {str(Path(x['file'])).lower() for x in snapshot['inputs'] if Path(x['file']).parent == BASE / 'native' and Path(x['file']).suffix.lower() == '.png'}
new_native = []
for p in sorted((BASE / 'native').glob('*.png')):
    if str(p).lower() in snapshot_native:
        continue
    with Image.open(p) as im:
        dimensions, mode = list(im.size), im.mode
    new_native.append({'file': str(p), 'sha256': sha(p), 'dimensions': dimensions, 'mode': mode,
                       'notInOriginalSnapshot': True, 'sourceReconstructionReviewed': False,
                       'formalAccepted': False})

latest_files = [BASE / name for name in ['progress.json', 'progress-r13_c11.json', 'selection-r13_c11.json', 'progress-r14_c11.json', 'progress-r14_c12.json']]
latest = {}
latest_sources = []
for p in latest_files:
    before = sha(p)
    latest[p.name] = read(p)
    after = sha(p)
    latest_sources.append({'file': str(p), 'sha256': after, 'stableDuringRead': before == after})
selection13 = latest['selection-r13_c11.json']['patchVersions']
progress14 = latest['progress-r14_c12.json']
working14 = progress14.get('workingVersions', {})
selected13_files = [BASE / 'native' / f'r13_c11_p{k}_{v}.png' for k, v in sorted(selection13.items())]
working14_files = [BASE / 'native' / f'r14_c12_p{k}_{v}.png' for k, v in sorted(working14.items())]
live = {
    'schemaVersion': 1, 'createdAtUtc': now(), 'zone': 'southeast',
    'baselineInventory': str(AUDIT / 'inventory.json'), 'baselineSnapshot': str(AUDIT / 'snapshot-inputs.json'),
    'snapshotStale': True, 'changedSnapshotSources': recheck['changes'],
    'newNativeImagesNotInSnapshot': new_native,
    'liveMetadataSources': latest_sources,
    'r13_c11': {
        'baselineSelectedCoreCount': 12, 'currentSelectionDeclaredCoreCount': len(selection13),
        'selectedFilesExistCount': sum(p.exists() for p in selected13_files),
        'patchVersions': selection13,
        'missingDeclaredCoreCoordinates': [f'{a}{b}' for a in range(1, 5) for b in range(1, 5) if f'{a}{b}' not in selection13],
        'complete4k': False, 'formalAccepted': False,
        'fourwayBreakpointP14VersionUnchanged': selection13.get('14') == 'v01',
    },
    'r14_c12': {
        'baselineSelectedCoreCount': 14,
        'liveSelectedNativeCoreCountField': progress14.get('selectedNativeCoreCount'),
        'liveWorkingVersionsCount': len(working14),
        'workingFilesExistCount': sum(p.exists() for p in working14_files),
        'workingVersions': working14,
        'liveMissingNativeCoordinatesField': progress14.get('missingNativeCoordinates'),
        'workingVsDeclaredSelectionCountDiscrepancy': len(working14) != progress14.get('selectedNativeCoreCount'),
        'complete4k': False, 'formalAccepted': False,
        'note': 'Working versions contain p33, while selectedNativeCoreCount and missingNativeCoordinates still retain the 14-core baseline. Do not silently promote the working p33 to accepted selection.',
    },
    'currentAdoptedCandidatesCountField': len(latest['progress.json'].get('currentAdoptedCandidates', [])),
    'currentFormalAcceptedCountField': latest['progress.json'].get('formalAcceptedCount'),
    'currentGenerationRule': 'Prefer free/existing builtin GPT Image 2.5; allow builtin 2.0 fallback. Actual undisclosed model remains unknown. No paid route authorized.',
    'legacyMetadataDiscrepancies': [
        {'file': str(BASE / k), 'field': 'newGenerationStatus', 'value': latest[k].get('newGenerationStatus'),
         'interpretation': 'Legacy exact-model hold string conflicts with the current root instruction and newGenerationAllowed=true; it does not establish a project production hold.'}
        for k in ['progress-r13_c11.json', 'progress-r14_c11.json', 'progress-r14_c12.json']
        if latest[k].get('newGenerationStatus') == 'on_hold_exact_model_requirement'
    ],
    'baselineCountsAreNotCurrentReaudit': True,
    'newNativeFullReconstructionAuditPerformed': False,
    'productionModified': False,
}
save('live-delta.json', live)

visual = {
    'schemaVersion': 1, 'createdAtUtc': now(), 'zone': 'southeast',
    'reviewer': '/root',
    'reviewRecordSource': 'Parent task handoff: root actually viewed both groups at 100 percent, all 16 shared seam crops and the four-tile cross per group, plus all three breakpoint images.',
    'finalizerPersonallyRepeatedVisualViews': False,
    'imageIdentityConfirmedBy': str(OUT / 'pixel-verification.json'),
    'groups': [
        {'groupId': 'g01-r09-r10-c12-c13', 'cropCoverage': '16 shared seam crops plus four-tile junction',
         'geometryStatus': 'local_pass', 'visualFinding': 'Stair floor, wooden rail, wall lines and four-tile intersection are locally continuous.',
         'formalAccepted': False, 'wholeMapAccepted': False},
        {'groupId': 'g02-r11-r12-c11-c12', 'cropCoverage': '16 shared seam crops plus four-tile junction',
         'geometryStatus': 'local_pass', 'materialStatus': 'pending',
         'visualFinding': 'Shared-line geometry is continuous. Wooden column material and hard framing remain locally pending; earlier material evidence is not closed by this check.',
         'formalAccepted': False, 'wholeMapAccepted': False},
    ],
    'breakpoints': [
        {'id': 'fourway-shared-column-current-selection', 'geometryStatus': 'local_pass', 'materialStatus': 'pending',
         'visualFinding': 'Column outline is continuous. Column and water-color material remain pending. r13_c11 was 12-core in the reviewed snapshot and is now declared 14-core; it remains incomplete and cannot receive full acceptance.',
         'p14VersionStillMatchesCurrentSelection': selection13.get('14') == 'v01', 'formalAccepted': False},
        {'id': 'r12_c13-floor-groove-x1024-y2167', 'status': 'repair_required',
         'tileLocalCoordinate': [1024, 2167], 'visualFinding': 'Small floor-groove mismatch remains in unadopted candidate-sol-20261012-v02; original pixels preserved.', 'formalAccepted': False},
        {'id': 'r12_c13-low-sail-batten-x3072-y3730', 'status': 'repair_required',
         'tileLocalCoordinate': [3072, 3730], 'visualFinding': 'Small low sail-batten mismatch remains in unadopted candidate-sol-20261012-v02; original pixels preserved.', 'formalAccepted': False},
    ],
    'r12_c12CandidateIdentity': {'adoptedVersion': 'candidate-sol-20261012-v01', 'v02ProposalAdopted': False},
    'formalAccepted': False,
}
save('visual-review.json', visual)

summary = {
    'schemaVersion': 1, 'createdAtUtc': now(), 'zone': 'southeast', 'taskStatus': 'audit_finalized_with_live_source_delta',
    'baselineSnapshotCounts': {**inventory['counts'], 'selectedTotalCores': inventory['counts']['fullCoverage'] * 16 + inventory['counts']['selectedPartialCores'], 'historicalNativeArchive': 444},
    'snapshotStale': recheck['snapshotStale'], 'snapshotInputCount': recheck['inputCount'],
    'snapshotHashMatchedCount': recheck['hashMatchedCount'], 'changedSnapshotSourceCount': recheck['changedOrUnreadableCount'],
    'unchangedExistingPngCount': sum(1 for x in recheck['inputs'] if Path(x['file']).suffix.lower() == '.png' and x['hashMatches']),
    'newNativeImagesNotInSnapshotCount': len(new_native),
    'mechanicalChecksPassed': pixel['allMechanicalChecksPassed'], 'groupSourceStale': {x['groupId']: x['sourceStale'] for x in pixel['groups']},
    'quadrantsChecked': pixel['quadrantsChecked'], 'fullTilePixelsCompared': pixel['fullTilePixelsCompared'],
    'nativeCropsChecked': pixel['nativeCropsChecked'], 'correctedContactPanelsChecked': pixel['correctedContactPanelsChecked'],
    'breakpointImagesChecked': pixel['breakpointImagesChecked'],
    'formalAcceptedCount': 0, 'finalMapComplete': False,
    'generationPerformed': False, 'aiEditPerformed': False, 'newOutputImagesCreated': False,
    'historicalActualModel': 'not returned / unconfirmed',
    'sharedGitTouched': False, 'productionModified': False,
    'reports': {name: str(OUT / name) for name in ['source-recheck.json', 'pixel-verification.json', 'live-delta.json', 'visual-review.json', 'review.md']},
    'interpretation': 'The original inventory is an auditable historical snapshot, not a current complete-map verdict. Its PNGs and inspected group evidence remain exact; live metadata and additional native files require separate continuation audit before promoting current coverage.',
}
save('summary.json', summary)

new_lines = '\n'.join(f"- `{Path(x['file']).name}`：{x['dimensions'][0]}×{x['dimensions'][1]}；SHA-256 `{x['sha256']}`。" for x in new_native) or '- 未发现新增 native PNG。'
changed_lines = '\n'.join(f"- `{Path(x['file']).name}`：`{x['expectedSha256']}` → `{x['actualSha256']}`。" for x in recheck['changes'])
text = f'''# 八仙岛东南区独立审计收尾

本次只读复核现有素材；输出只写本收尾目录。没有生图、AI 编辑、重绘、缩放、覆盖或删除原图，没有操作共享 Git，也没有重跑 444 张 native 的来源重建审计。

原快照 810 个输入中 805 个 SHA-256 一致，5 个 JSON 已随生产续作发生变化，故 `snapshotStale=true`。755 张既有 PNG 全部未变。两组硬拼的直接来源仍未变，分别 `sourceStale=false`，其局部检查证据可继续追溯到相同原像素；原库存计数须称为快照基线。

## 机械复核

两张 8192×8192 硬拼的 8 个 4096×4096 区域，逐块 raw pixel SHA-256 与对应输入完全一致，共比较 134,217,728 像素。34 张原比例接缝／四块交点裁片、8 张纠正后的 v02 接触板及 3 张断点图同样逐像素一致。验证没有模式转换、缩放、混合或补绘。

原 v01 接触板每组 4 张已有索引错误排除记录；保留文件，使用 v02。1024 预览仅为缩小预览，不能作为原生 4K 或 8192 验收依据。

## 视觉复核结果

本节来自主审 `/root` 的实际 100% 查看记录；收尾窗口没有将机械 hash 检查冒充再次视觉查看。对应图像身份由本次 SHA 与像素验证确认。

- g01（r09–r10、c12–c13）：16 段共享接缝和四块交点均已查看；楼梯地铺、木栏、墙线及交叉点局部几何连续。
- g02（r11–r12、c11–c12）：16 段共享接缝和四块交点均已查看；共享线几何连续。木柱材质和硬框局部仍待核，不据此闭合旧材质问题。
- r12–r13、c11–c12 共享柱交点：柱轮廓局部连续，柱材质及水色仍待核。审图快照 r13_c11 为 12 core，最新 selection 已为 14 core，仍缺 43、44，不能完整验收。断点使用的 p14-v01 身份未变，没有擅自采用 shared-lower 提案。
- r12_c13 的未采用 v02 仍须修复：tile-local `(1024,2167)` 地槽线及 `(3072,3730)` 低位帆横杆存在小错接。原像素保留。
- r12_c12 当前采用版本仍是 sol-v01；sol-v02 是未采用提案，不能替代本次组图输入。

正式验收数仍为 **0**；上述结论只覆盖已明确查看的局部接缝与断点，不等同整屏、全区或全图通过。

## 快照库存基线

范围 r08–r14、c08–c14，共 49 块。快照已有 15 块完整覆盖，其中 14 块采用并记录内部通过，r12_c13 为 1 块完整但未采用／待修候选；3 块部分覆盖共 27 core，合计 267 core。缺完整块 34，其中空块 31。历史 native 档案 444 张包含拒绝版本，不能换算为选用覆盖。

r10_c12 虽记录 externalPassed，但引用的旧外检 manifest 在快照中不存在；保留此证据缺口。r13_c12 已有 actual_north_pass 记录，库存 pending 文句“north 正单独检查”滞后。旧 remainingAssigned4kCount=37 及历史候选列表也不是当前 15 块基线的可靠计数。

## 生产续作变化

以下既有快照来源 SHA 已变：

{changed_lines}

相对快照发现 {len(new_native)} 张新增 native 原图，仅记录文件、尺寸和 SHA，没有做新来源重建、选用或验收：

{new_lines}

r13_c11 当前 selection 声明 {len(selection13)} core，新增 p41、p42；仍缺 p43、p44。r14_c12 的 workingVersions 为 {len(working14)} 项并已包含 p33，但 selectedNativeCoreCount 仍为 {progress14.get('selectedNativeCoreCount')}、missingNativeCoordinates 仍列 33/43，存在工作版本与选用字段不同步；本审计不默默把 p33 升为已选用。旧 267 core 只能作为快照计数，不据这些新增文件重算完整当前验收总数。

部分进度 JSON 仍残留 `newGenerationStatus=on_hold_exact_model_requirement`，而其新规则已写 `newGenerationAllowed=true`；这些旧状态字符串不构成全项目停工依据。根 AGENTS 当前规则为免费／现有内置 2.5 优先，不可用允许内置 2.0 继续。历史工具未返回实际型号，不能标为已确认 2.5。本检查窗口按分工零生图／AI 编辑。

## 交付记录

- `source-recheck.json`：810 输入复 hash，含全部输入与 5 个变化。
- `pixel-verification.json`：8 整块 raw pixel SHA、34 裁片、8 纠正接触板、3 断点的逐像素证据。
- `live-delta.json`：续作来源变化、当前部分选择声明及旧字段冲突。
- `visual-review.json`：主审实际查看结果、材质待核及两处返修坐标。
- `summary.json`：用于主对话汇总的机械计数和验收界限。

所有路径以仓库相对结构为制作依据；本目录绝对路径仅用于当前电脑点击与核验。没有提交或 push 声明。
'''
with (OUT / 'review.md').open('x', encoding='utf-8') as f:
    f.write(text)
print(json.dumps({'summary': str(OUT / 'summary.json'), 'newNativeCount': len(new_native),
                  'newNativeNames': [Path(x['file']).name for x in new_native],
                  'r13_c11Selected': len(selection13), 'r14_c12Working': len(working14),
                  'r14_c12DeclaredSelected': progress14.get('selectedNativeCoreCount'),
                  'snapshotStale': True}, ensure_ascii=False), flush=True)
