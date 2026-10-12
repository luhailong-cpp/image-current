import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path('D:/work/image')
OUT=Path(__file__).resolve().parent
old=json.loads((OUT/'roster.json').read_text(encoding='utf-8-sig'))
now=datetime.now(timezone.utc).isoformat()
excluded=[e for e in old['entries'] if e['type']=='monster']
if excluded:
    (OUT/'scope-correction.json').write_text(json.dumps({'correctedAtUTC':now,'userInstruction':'只要Image目录下原本已有的怪物和宠物，不要客户端来源','excludedClientMonsters':excluded,'formerThreadsState':'6客户端怪物窗口已归档；发送停止指令返回archived，未恢复。','doNotCountNewImportsAsOriginalImageAssets':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
entries=[e for e in old['entries'] if e['type']=='pet' and not e['slug'].startswith('legacy-')]
extra=json.loads((ROOT/'designs/pets-original-20260924/asset-config.json').read_text(encoding='utf-8-sig'))
for p in extra['pets']:
    if p['slug'] not in ['11-xiajiaolu','13-yalingtong'] or any(e['slug']==p['slug'] for e in entries):
        continue
    entries.append({'type':'pet','slug':p['slug'],'name':p['name'],'kind':p['kind'],'identity':p['identitySummary'],'anatomy':('无翼四足斑点鹿，两枝淡紫杏晶角、鹿蹄和短尾；保持原有装饰。' if p['slug']=='11-xiajiaolu' else '人形仙童，两臂两腿；两只种铃悠悠球各由一手持线，实际查看E/W并锁定左右归属。'),'avoidIdentity':p['avoidReferenceIdentity'],'references':[str(ROOT/'designs/pets-original-20260924/source'/f"{p['slug']}-{d}.png") for d in ['E','W']],'currentCombatFrames':0,'inclusionReason':'本次Image内全部原有不重复形象；旧任务未选入14截图包不代表身份拒用。'})
legacy=[
 ('legacy-hu-tuan-tuan','葫团团','四足白毛葫芦灵狐，单条青绿尾尖，金色发带和太极葫芦，前爪抱葫芦','qdao_chibi_pets_v1/01_hu_tuan_tuan-transparent_1254.png'),
 ('legacy-fu-xiao-hu','符小虎','杏金虎纹虎崽，额前符箓、太极铃、四肢；保持当前实际姿态和尾形','qdao_chibi_pets_v1/02_fu_xiao_hu-transparent_1254.png'),
 ('legacy-yun-jiu-jiu','云啾啾','白羽红冠幼鹤，青绿翼尖，两翼两足、祥云脚垫','qdao_chibi_pets_v1/03_yun_jiu_jiu-transparent_1254.png'),
 ('legacy-ling-yue','灵玥','雪白九尾灵狐，金眼、朱砂额纹、金玉项圈、淡紫尾影；四肢与九个真实尾尖','qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png')
]
for slug,name,identity,path in legacy:
    entries.append({'type':'pet','slug':slug,'name':name,'identity':identity,'anatomy':identity,'references':[str(ROOT/path)],'currentCombatFrames':0,'needsTrueBackReference':True,'inclusionReason':'Image原有独立宠物，当前属性头像仍引用，和14宠身份不重复。'})
style=str(ROOT/'designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png')
for e in entries:
    for reference in e['references']:
        p=Path(reference).resolve()
        if not p.is_relative_to(ROOT.resolve()) or not p.is_file():
            raise ValueError(f'Nonexistent or non-Image reference: {reference}')
    folder=OUT/'pets'/e['slug']
    folder.mkdir(parents=True,exist_ok=True)
    e.update(output=str(folder),task=str(folder/'TASK.md'),title=f"Image宠物·{e['name']}｜受击普攻施法",styleReferences=[style])
    refs='\n'.join('- '+r for r in e['references'])
    task=f'''# Image原有形象：{e['name']} · 三种战斗动作

用户最新明确范围是D:/work/image原本已有的怪物和宠物。你只制作本只原有形象，不从客户端、兄弟仓库、另一电脑、外部游戏或本轮新导入参考选新对象。不替换/重新设计现有身份；补受击、普攻、施法，不做跑步/走路/移动循环。

唯一写入目录：{folder}。其它Image内窗口目录、旧静态包和公共文件只读；禁止读取客户端及兄弟仓库。不提交/推送/切分支/修改Git索引。本轮公共规范：{OUT/'COMBAT_SPEC.md'}；先读根AGENTS、designs/README、README接手说明、config/image-generation.json、docs/IMAGE_MODEL_POLICY.md，使用imagegen技能和内置image_gen。

原有身份：{e['identity']}。
解剖和持物：{e.get('anatomy','先实际看静态图，锁定手、脚、尾和持物的解剖归属。')}
禁止身份漂移：{e.get('avoidIdentity','保持当前实际脸型、毛色、材质、配饰、物种和尾数。')}。

实际view_image查看并在生图中附以下身份参考，注明用途：
{refs}

主要画法/材质成图也要实际查看并附图：{style}。{'当前只有单向静态；请保留原形象补真正斜后W身份设计作为动作参考，不水平镜像。' if e.get('needsTrueBackReference') else '当前真实E/W原生图均已有，直接沿用，不用未采用/重复旧包覆盖。'}

E为敌方斜前朝右下；W为真正我方斜后朝左上，要有后脑/背部/后足或鞋跟，独立绘制。每向hit6帧×40ms、attack12帧×30ms、cast16帧×45ms，共68张1024×1024透明PNG。此为新动作制作合同。支撑和重心按真实物种，人形腿掌避免外翻，四足/鸟翼/蟹钳等不能套成人形，也不能缺肢、多肢或突然换手。自然原地反冲、蓄力、抬肢及回弹可保留，不生成位移序列。

先写本只POSES.md锁定解剖左右与姿态阶段，随即开始真实内置AI单帧生成/编辑，持续完成六组全部68帧，不停在计划或来源盘点，不再问是否开始。正确已有成果复用，错帧定点修；不复制、整图平移、镜像或插值补帧。逐图保存模型目标/实际提交/真实返回证据、时间、SHA、prompt和参考；没有model/quality选择器则实际未知为null，目标沿用用户GPT Image2.5/max，不转付费API/CLI。

成品落本目录，提供manifest/SHA/alpha尺寸与缺帧检查、README/STATUS/MERGE_HANDOFF、正常时间/0.25慢放/逐帧预览。实际看全帧与六组连播，检查方向、手爪/足/翼/尾/道具连续性与收势，不把文件齐全说成动态或游戏接入通过；未接入客户端如实记录。根素材保留规则在最终引用完整后执行；跨窗口旧身份参考不要删除。
'''
    (folder/'TASK.md').write_text(task,encoding='utf-8')
assert len(entries)==20, len(entries)
out={**old,'updatedAtUTC':now,'scope':'Image原本已有不重复生物形象；只hit/attack/cast；绝不从客户端导入新对象。','plannedCoreCount':20,'plannedMonsterCount':0,'plannedPetCount':20,'entries':entries,'optionalLegacyPets':[],'legacyPetScope':'按本次Image原有每只范围，纳入4独立宠物与2未选中旧截图包的原创身份。','monsterInventory':'Image本来未找到独立怪物/Boss素材包；已向用户请求具体子目录/名称，不猜造新名单。','excludedSource':'所有6种客户端来源怪物与本轮新导入参考均排除。'}
(OUT/'roster.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'imageOnlyCount':len(entries),'names':[e['name'] for e in entries],'referencesOutsideImage':0},ensure_ascii=False))
