import hashlib
raise RuntimeError('本脚本已被用户Image-only范围纠正停用；请用prepare_image_only_batch.py，不再导入客户端素材。')
import io
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path('D:/work/image')
OUT = Path(__file__).resolve().parent
CLIENT = Path('D:/work/mmorpg-client')
PETS = ROOT / 'designs/pets-xianling-20260924'
CONFIG = json.loads((ROOT / 'config/image-generation.json').read_text(encoding='utf-8-sig'))
NOW = datetime.now(timezone.utc).isoformat()
def git_bytes(spec):
    return subprocess.check_output(['git', '-C', str(CLIENT), 'show', spec])
commit = subprocess.check_output(['git', '-C', str(CLIENT), 'rev-parse', 'HEAD'], text=True).strip()
monsters = [(1, '01-wild-wolf', '野狼'), (2, '02-mountain-imp', '山鬼'), (3, '03-three-tail-fox', '狐妖'), (4, '04-stone-spirit', '石灵'), (5, '05-snake-demon', '蛇妖'), (6, '06-bandit', '山贼')]
entries = []
style = str(ROOT / 'designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png')
creature_style = str(PETS / 'source/03-shuangtuan-E.png')
for mid, slug, name in monsters:
    base = f'Assets/Resources/Battle/Monsters/{mid}'
    meta = json.loads(git_bytes(f'{commit}:{base}/meta.json'))
    refs = OUT / 'references/monsters' / slug
    refs.mkdir(parents=True, exist_ok=True)
    path = refs / 'legacy-idle-E-01.png'
    strip_bytes = git_bytes(f'{commit}:{base}/idle_E_strip.png')
    image = Image.open(io.BytesIO(strip_bytes))
    image.crop((0, 0, 256, 256)).save(path)
    provenance = {'createdAtUTC':NOW, 'operation':'exact first-cell crop; no resizing or AI generation', 'sourceRepository':str(CLIENT), 'sourceCommit':commit, 'sourceGitPath':f'{base}/idle_E_strip.png', 'sourceSha256':hashlib.sha256(strip_bytes).hexdigest(), 'output':str(path), 'outputSha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'sourceWidth':image.width, 'sourceHeight':image.height, 'width':256, 'height':256, 'actualModel':None, 'actualQuality':None, 'note':'本机已提交Git对象；历史程序绘制的身份参考，不能当作高清成图或另一电脑未提交素材。'}
    (refs / 'reference-provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (refs / 'legacy-meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    entries.append({'type':'monster', 'slug':slug, 'name':name, 'clientMonsterId':mid, 'identity':meta['note'], 'references':[str(path)], 'styleReferences':[style, creature_style], 'legacyContract':{'direction':['E'], 'cell':256, 'framesPerAction':8, 'actions':['idle','attack','hit'], 'castExists':False}, 'currentCombatFrames':0})
pet_config = json.loads((PETS / 'asset-config.json').read_text(encoding='utf-8-sig'))
anatomy = {
 '01-zhuling':'两翼两足、短尾；不能变长尾凤凰。',
 '02-jiangling':'右手三铃折扇，左手空手。',
 '03-shuangtuan':'四足、圆耳、貂脸，浅玉宽卷尾；不是尖耳狐。',
 '04-guideng':'右手六角木灯，左手桂花枝。',
 '05-yanyuling':'两翼两足猫头鹰，砚包与卷轴侧别需实看E/W锁定。',
 '15-landuoxian':'无翼；右手三玉铎框架，左手玉槌。',
 '06-xiluo':'六条步足、两只前钳，不得减少或增加步足。',
 '07-cangzhanglin':'无翼四足，两弯角、分趾蹄、云尾。',
 '08-zhufengli':'四足，竹叶披肩不能变翼，卷曲环尾。',
 '09-chishakui':'短玉锤持手和窑炉背包归属先实际看E/W锁定。',
 '10-xuanchaogui':'四足、龟壳、短尾；背上浅水盂与桂枝固定。',
 '12-yuexianshi':'左手托月牙弦琴，右手拨弦。',
 '16-luhualing':'无翼；左手紫釉露壶，右手露珠枝。',
 '14-feierling':'两狐耳、单条黑尖红尾；木狐面具持手须实看E/W锁定。'
}
for pet in pet_config['pets']:
    slug = pet['slug']
    references = [str(PETS/'source'/f'{slug}-{d}.png') for d in ['E','W']]
    for path in references:
        if not Path(path).is_file():
            raise FileNotFoundError(path)
    entries.append({'type':'pet', 'slug':slug, 'name':pet['name'], 'kind':pet['kind'], 'identity':pet['identitySummary'], 'anatomy':anatomy[slug], 'avoidIdentity':pet['avoidReferenceIdentity'], 'references':references, 'idleReferences':[str(PETS/'runtime'/slug/f'idle_{d}.png') for d in ['E','W']], 'styleReferences':[style], 'identityConfig':str(PETS/'asset-config.json'), 'currentCombatFrames':0})
for item in entries:
    folder = OUT / ('monsters' if item['type']=='monster' else 'pets') / item['slug']
    folder.mkdir(parents=True, exist_ok=True)
    item.update(output=str(folder), task=str(folder/'TASK.md'), title=f"{'怪物' if item['type']=='monster' else '宠物'}·{item['name']}｜受击普攻施法")
    identity_refs = '\n'.join(f'- {p}' for p in item['references'])
    extra = ('怪物旧资源只有E、8帧256格、无施法；旧清单记录仅作身份和历史合同证据。先制作本批高清E/W静态身份参考，再连续做三动作。不得把历史程序图放大当成新成品。' if item['type']=='monster' else '沿用当前仙气提升版E/W真实原生身份；勿用旧未采用pets包或外部游戏截图覆盖。当前只有静态，无可复用三动作。')
    task = f'''# {item['name']} · 受击、普攻、施法

用户2026-10-05明确要求每只怪物/宠物独立一个窗口制作三种战斗动作，不制作移动动作。你的唯一写入范围：`{folder}`。公共名单、公共规范、来源参考和其它角色目录只读；不改客户端、Git索引或分支，不提交/推送/重置。

先读 `{OUT/'COMBAT_SPEC.md'}`、根AGENTS.md、designs/README.md、README接手说明及所指交接/美术定调、config/image-generation.json、docs/IMAGE_MODEL_POLICY.md，使用imagegen技能。不要停在计划、仅盘点或写交接，开始内置生图并持续完成本只三动作。

身份：{item['identity']}。
解剖与持物：{item.get('anatomy','按真实身份图锁定手足/尾/角数量；蛇按腹面盘身、石灵按底部承重，不套人形腿。')}。
避免：{item.get('avoidIdentity','不要改成其他怪物身份或加新武器。')}。

实际打开以下身份图；工具调用中实际附图、注明身份参考用途：
{identity_refs}

实际打开并附主要画法/材质参考 `{style}`；独立生物可补 `{creature_style}` 作为画法完成度参考，不能复制貂的身体或饰物。{extra}

三动作均制作E敌方斜前朝右下、W我方真正斜后朝左上；背向须真实后脑/背部/后足或鞋跟，独立绘制，不水平镜像冒充。每向受击6帧、普攻12帧、施法16帧，共68张1024×1024透明PNG。此为本轮沿用人物战斗数量的新制作合同，不能称为旧怪物8帧合同。时长受击40ms/帧、普攻30ms/帧、施法45ms/帧；动作正常/0.25慢放及逐帧预览齐备。没有跑步、走路、移动循环、位移序列任务。

所有技术/美术验收、逐图来源记录与不复制移图补帧要求见公共规范。使用GPT Image 2.5/max配置目标，内置优先，不启用单独计费API/CLI。工具若无模型/质量参数，实际记录null及原因，不能把提示词算显式选择参数。把每张选中最终图落本目录；不要只留在用户generated_images路径。

先观察静态身份，写本只 `POSES.md` 明确解剖左右持物、姿态阶段和首尾衔接，再按单帧独立姿态执行真实AI生成/编辑；正确已有图复用，错帧定点改。手/爪/翅连接、道具握持、四足/六步足数量、尾数、支撑接触必须在全序列一致。膝—踝—足掌沿本物种正常运动平面，避免外翻；允许自然屈伸，不把腿锁死或把所有物种做成人形。原地小幅重心、反冲、蓄力和回弹合法，不能复制图并平移充当动作。

完成本只68图、清单/逐图生成来源索引、README/STATUS/MERGE_HANDOFF、离线预览（正常/慢放/逐帧）、尺寸alpha及SHA检查；实际看所有帧、全部六组动态与邻接、手足放大。记录未在游戏客户端接入验收的范围，不把文件存在或消息发送当作成品通过。无需再问是否开始，继续完成。
'''
    (folder/'TASK.md').write_text(task, encoding='utf-8')
roster={'schemaVersion':1, 'createdAtUTC':NOW, 'dateLocal':'2026-10-05', 'timezone':'America/New_York', 'projectId':'c1032ce0-cb68-4fe1-89ec-49647b88f6cf', 'scope':'Individual monster/pet chats; hit, attack, cast only; no movement animation.', 'plannedCoreCount':len(entries), 'plannedMonsterCount':6, 'plannedPetCount':14, 'framesPerCreature':68, 'directions':['E','W'], 'modelConfigSnapshot':CONFIG, 'actualModel':None, 'actualQuality':None, 'entries':entries, 'optionalLegacyPets':['灵玥','葫团团','符小虎','云啾啾'], 'legacyPetScope':'optional clarification pending; does not block current 14 pets and 6 monsters'}
(OUT/'roster.json').write_text(json.dumps(roster,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'monsters':6,'pets':14,'tasks':len(entries),'plannedFrames':len(entries)*68,'roster':str(OUT/'roster.json')},ensure_ascii=False))
