"""Write current delivery docs after root approves the actual repaired stills."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
review=json.loads((ROOT/"records/sequence-continuity-review.json").read_text(encoding="utf-8"))
assert review["status"]=="static-repairs-complete-playback-pending"
documents={
"README.md":'''# 月弦师 · 受击、攻击、施法

**三种动作双向共68张1024透明PNG已完成制作与已确认问题修复，静态及技术复核通过；实际连播未验，未接入客户端。** 2026-10-08本轮真实AI修正E攻击01及W受击/攻击全18帧；此前鞋位缺陷报告已由当前像素复核结果替代。

|动作|E帧数|W帧数|每帧|每向总长|
|---|---:|---:|---:|---:|
|受击 hit|6|6|40ms|240ms|
|攻击 attack|12|12|30ms|360ms|
|施法 cast|16|16|45ms|720ms|

[完整交付包](yuexianshi-combat-delivery.zip) · [交互预览](preview.html) · [当前验证结果](VERIFICATION.md)

正式图在`runtime/<hit|attack|cast>/<E|W>/<NN>.png`。预览含六组总览、12个正常/0.25倍APNG及逐帧控件，全部从当前正式PNG生成，无插值补帧。受击保留缩肩护琴、反冲和恢复；攻击保留预备、拨弦、回收；施法保留蓄光、奏弦释放和回位。没有移动序列。

E是真斜前朝右下，W是真斜后朝左上，非镜像。沿用原月弦师栗发长侧辫、靛蓝象牙丝衣、浅蓝纱袖及月牙弦琴，解剖左手托琴、右手拨弦，2手2腿2鞋。修正后的W腿脚采用原角色前后错位的紧凑支撑。

## 文件合同与来源

每张正式图为1024×1024 RGBA；本批生成原生为1254×1254。统一整画布缩至960×960并放入1024画布(32,16)，没有每帧按脚重对齐。顶部坐标锚点[512,942]，左下pivot[0.5,0.08]。本轮编辑输入从旧正式图撤销已知导出边距后缩放回1254，属于坐标归一的参考预处理，不宣称恢复原生像素或产生新动作。

所有新增姿态和修正都使用内置image_gen；提示词在`prompts/`，每帧记录为`records/<action>-<direction>/<NN>.generation.json`。记录区分配置目标gpt-image-2.5-sunburst/max与工具实际证据：内置入口未提供或披露model/quality，因此实际值为null。旧记录与拒稿文字保留，不重标旧图版本。参考图用途、SHA、原始返回信息及统一导出操作均可追溯。

[manifest.json](manifest.json)绑定当前68帧；[SHA256SUMS](SHA256SUMS)保存正式图哈希；[交付编码检查](delivery-verification.json)逐一核对12个APNG共136解码帧的像素、顺序与时长；[本轮静态复核](records/sequence-continuity-review.json)及[脚位/边缘量测](records/guardfix-20261008-measurements.json)记录修复证据。

`build_delivery.py`重建清单与总览，`build_animations.py`封装当前正式帧，`verify_delivery.py`复查像素与编码。清理后的历史原生来源不能再用于确定性重建，预览和清单可由正式PNG重建。

## 验收边界与保留

已确认的明显鞋位问题已经AI修正。独立绘制仍有细微鞋位、腕部、衣发变化；E攻击收势到首帧的右鞋暗色像素中心差约24.5像素，W个别帧也有小幅局部差异，需要正常与慢放确认观感。静态检查、APNG像素相等都不代表实际连播通过。

浏览器安全策略拒绝本地file预览并禁止绕过，原文见[记录](records/cast-E/browser-policy-rejection.json)。本轮未尝试其它入口规避，也未接入客户端。接入约定见[交接说明](MERGE_HANDOFF.md)。

按用户规则只保留正式图、当前预览、设计/接入文件及完整文字来源。首次78张原生/拒稿清理见[cleanup.json](cleanup.json)，本轮新增原生、拒稿和参考中间图清理见[cleanup-guardfix.json](cleanup-guardfix.json)。原身份和主要画法引用继续保留在Image项目原目录，未删除。
''',
"STATUS.md":'''# 制作状态

2026-10-08：月弦师受击、攻击、施法双向共68/68张正式PNG齐全；本轮19帧真实AI修复已选定并落盘。

- 受击：E6/W6，40ms每帧，W全组恢复原有紧凑前后支撑，保留反冲和恢复阶段。
- 攻击：E12/W12，30ms每帧，E01离群鞋位已修，W全组支撑已修且保留拨弦与回收。
- 施法：E16/W16，45ms每帧，沿用已核对的蓄光/释放/回位帧。
- 静态：确认的2项鞋位缺陷已经修复；当前图逐组复核通过，残余小幅轮廓与动作差异见VERIFICATION.md。
- 技术：尺寸、RGBA/透明度、独立像素、缺帧、SHA/逐图来源及预览136解码帧检查见当前JSON。
- 动态：实际连播未验。浏览器file预览遭安全策略拒绝，未绕过；不标动态通过。
- 客户端：未接入、未验证。未读取客户端/兄弟库，未操作Git。
- 保留：最终引用核实后移除原生、拒稿与输入中间PNG，保留正式帧、当前预览和来源文字。

当前状态由records/sequence-continuity-review.json、technical-validation.json和delivery-verification.json共同描述。旧失败报告及旧审核结论仅保留为历史，不能覆盖当前像素。
''',
"MERGE_HANDOFF.md":'''# 月弦师素材交接

交付范围仅Image原月弦师双向受击、攻击、施法共68张PNG；没有移动动作。已确认的鞋位问题已修复，静态/技术检查通过；实际连播和客户端运行仍未验。

正式来源`runtime/<hit|attack|cast>/<E|W>/<NN>.png`。manifest绑定文件SHA、帧序和时长：hit6×40ms，attack12×30ms，cast16×45ms。建议视觉事件点hit03 impact、attack07 release、cast11 release，最终战斗事件需由客户端校准。

PNG RGBA1024方图，pivot[0.5,0.08]，顶部锚点[512,942]。禁止图集自动旋转或按各帧alpha包围盒重新对齐；全部采用相同整画布导出变换。E斜前右下，W斜后左上；左手托琴、右手拨弦。

正常与0.25倍预览在preview.html和preview/*.apng。后续实际播放重点检查E攻击05–08腕部轨迹、末帧→戒备；W受击反冲恢复、攻击脚位小幅变化；施法衰光和回位。完整当前静态证据见VERIFICATION.md，不把编码或文件齐全当实际播放/游戏运行通过。

逐图记录中的实际model/quality仍为工具未披露的null；目标Sunburst/max不能冒充实际型号。原生/拒稿清理后保留SHA、prompt、receipt及输入来源文字，运行和预览仅依赖正式PNG。未自行接入客户端或发布，未读取兄弟仓库，未执行Git写操作。
''',
"VERIFICATION.md":'''# 月弦师当前验证结果 · 2026-10-08

**已确认的图像问题已修复，当前静态与技术检查通过；实际连播仍未验。** 三动作双向68张正式帧齐全，本轮通过真实内置AI编辑更新19张，其余49张复用。

|项目|当前结果|
|---|---|
|受击|E/W各6张；W全组腿脚修正，反冲/护琴/回位保留|
|攻击|E/W各12张；E01及W全组腿脚修正，预备/拨弦/回收保留|
|施法|E/W各16张；蓄光/释放/回位帧齐全|
|方向/持琴/解剖/裁切|逐图及总览静态复核，未见新的明确换手、缺肢、镜头翻转或实体裁边|
|正式图技术检查|1024 RGBA、alpha、唯一像素、SHA及记录对应检查|
|12个APNG|136个解码帧逐一与当前正式帧的512缩放像素比较，核对帧序和时长|
|实际正常/慢速连播|未验；浏览器安全策略拦截，未绕过|
|客户端运行|未接入、未验证|

## 修正证据

E攻击01原右鞋暗色区域质心x771.3，02为690.3，差81.0像素。修正01后为694.3，与02差约3.98像素；与末帧12的669.8仍差约24.51像素，作为实际播放待观察项保留。

W受击/攻击原收势与原戒备鞋位横向相差约145像素。此次将W受击6帧、攻击12帧分别AI局部重绘为原有紧凑前后错位支撑，连同中间过渡帧一起修正。最新各帧位置和图像SHA在[本轮量测](records/guardfix-20261008-measurements.json)，最终鞋位不再保留原宽站离群。攻击12的两个暗鞋区域在固定ROI内连通，质心代表合并区域，不能当单鞋骨骼点比较。

本轮19张选定原生图均检查边缘；W攻击12有6个半透明边缘像素，最高alpha88，已实际查看原生及导出，没有实体轮廓截断。其余选定修复图的原生边缘没有alpha>64像素。

静态残余：W个别帧约10–20导出像素的局部鞋体变化，E攻击腕部05–08的轨迹、衣发与施法衰光节奏仍须正常和慢放观察。独立AI重绘难以保持像素级静止；本次没有用复制、平移、插值或代码粘贴鞋部造帧。受击不是待机循环，首尾本来可不同，检查重点是回到共同戒备的衔接。

## 可追溯检查

- [当前静态审查](records/sequence-continuity-review.json)：19张选定修复图的SHA、已解决问题、残余限制。
- [历史缺陷报告](records/sequence-continuity-review.pre-guardfix-20261008.json)：只作旧像素证据，不是当前结论。
- [技术检查](technical-validation.json)与[APNG像素/帧序/时长检查](delivery-verification.json)。
- [浏览器策略拒绝原文](records/cast-E/browser-policy-rejection.json)。

所有量测在未额外对齐的正式1024RGBA像素上完成。暗鞋像素质心是静态辅助证据，不是骨骼关节，不把自然露鞋底判为异常；文件和静态检查不替代实际连播。
'''}
for name,text in documents.items():(ROOT/name).write_text(text,encoding="utf-8")
print("Current repaired-asset handoff written; actual playback remains unverified.")
