# 月弦师 · 受击、攻击、施法

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
