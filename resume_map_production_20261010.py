from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

root = Path('D:/work/image')
base = root / 'qdao_city_tiles_4k_20260916/builtin_q64_production'
resume = base / 'resume-production-20261010'
resume.mkdir(parents=True, exist_ok=True)
prior = base / 'fishing-village-game-20261009/northwest/work-r03_c04/resume-20261010'
now = datetime.now(timezone.utc).isoformat()

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def text_if_missing(p, text):
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')

config_path = root / 'config/image-generation.json'
config = read(config_path if config_path.exists() else prior / 'config/image-generation.json')
assert config['model'] == 'gpt-image-2.5-sunburst' and config['quality'] == 'max'
config['verified_on'] = '2026-10-10'
config['sources']['model'] = 'https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst'
config['sources']['quality'] = 'https://developers.openai.com/api/reference/resources/images/methods/generate'
write(config_path, config)
text_if_missing(root / 'docs/IMAGE_MODEL_POLICY.md', (prior / 'docs/IMAGE_MODEL_POLICY.md').read_text(encoding='utf-8-sig') + '\n## 2026-10-10 恢复制作核对\n\n本文从现有制作区的文字副本恢复。官方模型页与 Images API reference 再次确认配置目标型号及 max 档位；内置工具没有 model/quality 选择器，实际返回字段仍须逐图取证，未知为 null。只使用内置入口，用户未授权付费 API。没有恢复或复制旧图片。\n')

text_if_missing(root / 'README.md', '''# 游戏地图素材\n\n## 给接手的 Codex\n\n2026-10-10 根据当前用户要求与在制记录恢复本交接入口。先读 [已确认风格](designs/README.md)、[统一配置](config/image-generation.json)、[逐图策略](docs/IMAGE_MODEL_POLICY.md)、[UI 视觉](qdao_ui_redesign_v5/UI_SPEC.md)，再读 [当前恢复制作指令](qdao_city_tiles_4k_20260916/builtin_q64_production/resume-production-20261010/README.md)。\n\n当前仅主城、渔村、八仙岛三张日景；各自 production-contract.json 定义固定绘图坐标与分区。主城 16×16 个 4096 图块；渔村和岛各 14×14。世界空间尺寸尚未最终批准，不能把图像分辨率当作容量证明。5000 人静态脚点排布已通过条件试验，入口和运行验收仍未完成。当前允许继续绘图，不再全局暂停。不得回填旧图片的模型字段。\n''')
text_if_missing(root / 'qdao_ui_redesign_v5/UI_SPEC.md', '''# 当前视觉接手说明\n\n本文件于 2026-10-10 依据用户当前明确要求恢复；不声称还原已缺失旧文档的全部章节。\n\n## 2. 统一视觉与控件层级\n\n遵循 designs/README.md 中用户确认的道家 Q 版邮件风格图及三张地图近景参考。圆润饱满、明亮干净、玉绿与暖金点缀。春节、元宵、中秋装饰自然混合；截图中的功能可参考，其他游戏画法不能取代用户已确认风格。地图只做日景，建筑墙、门窗也有春节细节；地面恢复自然灰青石材、不同铺法，不铺红地板。爆竹纸屑、燃放痕迹与墙边烟花少量点缀；树只挨建筑或院墙，无独立街心树、盆栽。每次生图实际附上相应用途的现有成图。地图输出不带 UI、人物、文字标签或水印。\n''')

style = base / 'parallel_20261005/daylight-only-20261009/user-references-20261009/mail-daoist-style.jpg'
assert style.is_file(), style
style_hash = hashlib.sha256(style.read_bytes()).hexdigest()
scope = ['main-city-game-20261009', 'fishing-village-game-20261009', 'island-game-20261009']
control = {
 'schemaVersion': 1, 'releasedAtUtc': now,
 'userAuthorization': '那你按我们的需求让他继续做啊',
 'status': 'released_for_art_production_with_local_entrance_review',
 'scope': scope, 'newArtworkGenerationAllowed': True,
 'builtinOnly': True, 'paidApiAllowed': False,
 'preserveArtCoordinatesAndApprovedLayout': True,
 'wholeMapExpansionOrdered': False, 'worldSizeApproved': False,
 'capacity5000Validated': False,
 'staticTrial': {'mainSide': 500, 'villageIslandSide': 433.0127018922193, 'spacing': 2.5, 'selectedFeetPerMap': 5000, 'corridorsReserved': True, 'onlyConditionalStaticGeometry': True},
 'runtimePendingIsNotGlobalArtHold': True,
 'primaryStyleReference': str(style).replace('\\','/'), 'primaryStyleSha256': style_hash,
 'styleResolution': 'Existing user-provided mail UI JPG plus existing approved per-map detail references. Missing prior PNG is not a reason to stop new art; historical source records remain unchanged.',
 'localEntranceReview': {
  'main-city-game-20261009': ['warehouse visible approach', 'manor narrow approach'],
  'fishing-village-game-20261009': ['north gate under-roof visibility', 'cloth shop approach', 'shipyard east and south access'],
  'island-game-20261009': ['east third residence courtyard gap', 'south gate roof occlusion', 'lotus pavilion bridge connections', 'west fourth and east fourth residence approaches']
 },
 'workerInstructions': [
  'Continue within your existing assigned zone; no duplicate zone owners.',
  'Read approved layout, current detail style and adjacent native pixels before generation; actually attach relevant references.',
  'Finish connected native patches, inspect a 2x2 tile neighborhood then continue remaining assigned area; do not stop merely after one candidate.',
  'Review local entrance risks while painting relevant coordinates; preserve buildings and open connected ground, do not enlarge the whole map.',
  'No red paving, no standalone trees or pots, no night scenes, no long north/south exterior extensions.',
  'Preserve all eight immortal residences, village shops and main city functional architecture.',
  'Save native image, dimensions, hashes, prompt, actual references and truthful model/quality evidence for every output.',
  'Formal acceptance still requires native detail and reviewed seams; never mark an enlarged overview as native 4K.',
  'Do not delete unique in-progress artwork before final pixels and references are secured.',
  'Write a resume receipt in your zone; report output counts separately from queued/running status.'
 ]
}
write(resume / 'production-resume.json', control)
text_if_missing(resume / 'README.md', '''# 三张地图继续制作\n\n用户已明确要求“那你按我们的需求让他继续做啊”。主控已依据静态排布试验解除全图绘制暂停，继续现有 12 个分区任务。机器可读指令见 production-resume.json，当前 gate 文件与三份 production-contract.json 同步指向本记录。\n\n主城 16×16，渔村和岛各 14×14，正式图块 4096×4096，保持现有画布坐标与确认布局。每图 5000 个脚点的条件试验已经完成，但世界尺寸、实际角色遮挡、入口与服务器/客户端运行容量尚未验收。运行验证不会阻止所有区域绘制，局部入口问题在对应坐标处理，不因此扩大整张地图。\n\n继续用内置生图。配图采用当前用户的 Q 版道家风格 JPG、对应地图确认总览/近景、已有相邻原生像素。原旧风格 PNG 已缺失，本次只更新未来制作引用，不改历史来源记录。\n\n春节建筑墙门窗、元宵/中秋点缀、自然灰青多样铺地、爆竹碎屑和墙边烟花、仅靠建筑/墙的树、短南北出口、主城功能房屋、渔村商店、八仙八处居所均保留。先完成相邻图块接缝审核，再持续完成所属分区，候选数量与正式验收数量分开报告。\n''')
for name in scope:
    p = base / name / 'production-contract.json'
    contract = read(p)
    old_style = contract.get('primaryStyleReference')
    if old_style != control['primaryStyleReference']:
        contract['previousPrimaryStyleReference'] = old_style
    contract['primaryStyleReference'] = control['primaryStyleReference']
    contract['primaryStyleSha256'] = style_hash
    contract['productionResumeControl'] = str(resume / 'production-resume.json').replace('\\','/')
    contract['productionResumedAtUtc'] = now
    contract['newArtworkGenerationAllowed'] = True
    write(p, contract)

gate_path = base / 'capacity-layout-gate-20261010.json'
gate = read(gate_path)
gate['previousHoldStatus'] = gate['status']
gate['status'] = control['status']
gate['holdGenerationAtNewCoordinates'] = False
gate['newArtworkGenerationAllowed'] = True
gate['releasedAtUtc'] = now
gate['releaseAuthorization'] = control['userAuthorization']
gate['reason'] = 'Root reviewed conditional 5000-foot placement and user explicitly requested continuation. Resume artwork in current coordinates; localized entry review and pending runtime validation do not impose a global art hold.'
gate['productionResumeControl'] = str(resume / 'production-resume.json').replace('\\','/')
gate['latestReview']['productionResumeAuthorized'] = True
gate['latestReview']['runtimeValidationIsGlobalArtBlocker'] = False
write(gate_path, gate)
decision_path = base / 'capacity-layout-validation-20261010/layout-decision-20261010.json'
decision = read(decision_path)
decision['subsequentProductionRelease'] = {'releasedAtUtc':now, 'userAuthorization':control['userAuthorization'], 'control':gate['productionResumeControl'], 'capacity5000Validated':False}
write(decision_path, decision)
print(json.dumps({'status':gate['status'],'configTarget':config['model'],'qualityTarget':config['quality'],'styleSha256':style_hash,'updatedContracts':scope}, ensure_ascii=False))
