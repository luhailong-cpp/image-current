# 符小虎交接

仅此目录为本窗口写入范围，未操作Git索引、分支、提交或推送。未读取客户端、兄弟仓库或其他电脑内容。原身份来自 Image 的 `qdao_chibi_pets_v1/02_fu_xiao_hu-transparent_1254.png`；主画法参考为 `designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png`，二者只读且实际附图生成。

## 接收内容

- `runtime/`：已完成E/W各hit6、attack12、cast16，共68张1024RGBA。
- `manifest.json`：逐帧文件、SHA、像素SHA、尺寸、40/30/45ms时长、锚点、事件建议、来源索引；实际数量与完成状态以此和STATUS为准。
- `preview/`：六组总览、独立HTML、正常及0.25慢放WebP、逐帧总览图。
- `design/`与`POSES.md`：当前有效E/W方向身份和解剖规则；W是真斜后，不能以E镜像替换。
- `records/`：每次调用的prompt/request、receipt、当次目标配置、实际型号与质量未确认证据、原生与派生SHA、拒稿文字历史、修图与清理记录。
- `tools/`：只基于现有实图导出/审计/生成预览，不用代码绘制或补动作。

## 接入约定

E朝右下斜前、W朝左上斜后；两向都是原宠坐姿，屁股和后足支撑，普攻持续解剖右前爪。每组编号01起；attack07为建议击点、cast10为建议释放点，这只是美术事件建议，须由客户端战斗逻辑确认。整图透明1024，顶部逻辑脚点[512,942]，pivot[0.5,0.08]。原生1254经整画布缩放并按方向固定偏移，源/导出坐标不可混用。

## 验收与边界

请读 `validation.json`、`records/source-audit.json`、`records/visual-review.json` 和 `STATUS.md`。技术及来源检查通过；最终68帧已做全帧查看、六组正常/0.25慢放、逐帧与收势检查，视觉结论绑定最终SHA。校准证据在`records/final-direction-calibration.json`，12个动画预览的帧数和时长检查在`records/preview-audit.json`。未接入客户端、未验真实游戏缩放/混合/受击事件/技能同步，不宣称客户端通过。

模型目标沿用用户Image2.5/max；宿主内置工具没有model/quality选择器，实际字段null。配置目标、公告和提示词不能证明API分支被显式锁定。未运行收费API/CLI。

只保留正式游戏帧、当前方向设计、必要预览和文字证据。旧原宠/风格参考供其他窗口共用，未删除。宿主generated_images缓存不在唯一授权写目录内，不作为游戏加载依赖。仓库内拒稿和原生在制副本在核实正式资产与当前引用后清理，不另建图片备份。
