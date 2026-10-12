# 砚羽灵 · 素材接手

本只唯一工作目录：`D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling`。

正式入口为`manifest.json`和`runtime/`，预览入口为`preview.html`。两方向各34帧，共68张1024透明RGBA；hit6×40ms、attack12×30ms、cast16×45ms。E斜前右下，W真斜后左上，不含移动动画。

以`README.md`、`POSES.md`、`export-registration.json`、`qa/visual-review-final.json`和`qa/technical-validation.json`理解最终状态。`provenance`中的早期局部HANDOFF、检查和STATIC_REVIEW具有历史时间，最终连续性修正由总验收覆盖；其prompt、生成时间、原生SHA和实际模型未知证据仍有效，不回填旧记录。

接入时使用左下pivot[0.5,0.08]，目标画内脚点[512,942]。每方向固定导出已经应用，不再逐帧对齐。事件仅为视觉建议，伤害／技能结算时机必须由客户端任务确认。

没有读取客户端、兄弟仓库或另一台电脑；没有修改公共配置、公共身份／风格图，没有Git提交、推送或切分支。游戏引擎、实际战斗、资源加载与排序均未验证。

所有新图采用内置image_gen；GPT Image2.5／max为用户目标，实际model／quality未披露，逐图均为null。不可把文件完整、预览可播放或目标型号当作游戏接入或显式模型参数已验证。
