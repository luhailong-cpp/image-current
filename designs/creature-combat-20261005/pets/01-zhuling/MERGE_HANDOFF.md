# 烛翎接入交接

68/68帧资源与本目录资料已完成。当前SHA绑定的静态检视、浏览器正常/慢放画面抽查及逐帧操作记录见STATUS.md与qa/visual-review.json。客户端未读取、未接入、未运行；不能把本地HTML播放与PNG检查称为游戏接入通过。

以manifest.json为资源真值，使用`runtime/<action>/<direction>/<NN>.png`。E为斜前朝右下，W为独立AI绘制的真斜后朝左上，禁止运行时把E镜像作为W。透明PNG为1024×1024 RGBA，颜色与alpha未经额外抠图。

使用manifest每帧durationMs：hit40、attack30、cast45。普攻07为impact、施法10为release，事件建议由播放帧驱动；当前未绑技能伤害、弹道或音效。施法烛光已经画入帧，可直接播放，不能宣称有可分离特效层。

底部虚拟悬浮锚点top-left pixel [512,942]；bottom-left normalized pivot [0.5,0.08]。全套统一原画全画布缩820，再透明留边(102,102)，保持重心/饰物自然运动。不要再逐帧按最低爪或bbox对齐；推荐保持一致Pixels Per Unit和同方向跨动作锚点。

验收入口：preview/index.html 可本地打开正常/慢放/逐帧，qa/为全帧检视；validation.json只证明文件技术检查。接入方仍需实际验证引擎的颜色空间、alpha混合、过滤方式、排序、世界尺寸、动作事件和战斗节奏。

构建/复核：使用带Pillow的Python运行 `build_delivery.py`，读取已保存runtime及文字来源记录即可重建manifest/SHA/预览/检查图，不调用生图。生图不能依靠脚本确定性重现。原生图清理情况见cleanup.json；原生已清理时不能重新执行导出脚本复原像素，只使用最终PNG与SHA。
