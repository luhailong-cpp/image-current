# cast E 子任务交接

已完成 runtime/cast/E/01.png 至 16.png，共 16 张独立内置 AI 生成，均为 1024×1024 RGBA，每帧 45 ms。本组写入仅限 runtime/cast/E 和 provenance/cast/E。

- 每一帧均实际查看返回图；04 提前达到展翼峰值、08 缩放变化、09 身体左移、11 过早折翼、16 最低爪尖触边均进行了定点 AI 重绘。
- 所有帧保持暮紫猫头鹰 E 斜前朝右下、两翼两足、屏左卷轴和屏右砚包；未做人形手脚、移动循环或镜像补帧。
- 原生图均 1254×1254；仅整画布等比导出 1024，未逐帧按脚点对齐。最后各方向统一取景由主线程处理。
- 16 张 PNG / 16 个不同 SHA；尺寸、RGBA、非空透明通道、输出与来源记录 SHA 检查通过。alpha>=32 的主体没有接触画布边界，详见 CHECKS.json。
- 逐图 *.prompt.txt、*.receipt.json、*.generation.json 包含实际输入路径/SHA、原生尺寸/SHA、输出 SHA、时间和配置快照。目标 gpt-image-2.5-sunburst/max；实际 model/quality 与实际提交选择器均为 null，宿主工具未披露，不能冒称已锁定目标参数。
- 04/08/09/11/16 的拒稿图片已在替代图检查后删除；文字记录与 SHA 保留。16-rejected.png 曾用于定点修爪输入，其历史引用已显式标记 retained=false。
- 后续参考帧 01.png（11/12 另引用 10.png）记录的是生成时像素 SHA。主线程若执行方向统一变换，请保留这是历史输入的说明，更新当前正式产物 SHA，不重写历史来源证据。
- 本子任务已逐图验看；最终正常/慢放/逐帧六组连播由主线程统一复验。未接入客户端，不能称游戏验证通过。

文件清单：

- runtime/cast/E/01.png → provenance/cast/E/01.generation.json
- runtime/cast/E/02.png → provenance/cast/E/02.generation.json
- runtime/cast/E/03.png → provenance/cast/E/03.generation.json
- runtime/cast/E/04.png → provenance/cast/E/04.generation.json
- runtime/cast/E/05.png → provenance/cast/E/05.generation.json
- runtime/cast/E/06.png → provenance/cast/E/06.generation.json
- runtime/cast/E/07.png → provenance/cast/E/07.generation.json
- runtime/cast/E/08.png → provenance/cast/E/08.generation.json
- runtime/cast/E/09.png → provenance/cast/E/09.generation.json
- runtime/cast/E/10.png → provenance/cast/E/10.generation.json
- runtime/cast/E/11.png → provenance/cast/E/11.generation.json
- runtime/cast/E/12.png → provenance/cast/E/12.generation.json
- runtime/cast/E/13.png → provenance/cast/E/13.generation.json
- runtime/cast/E/14.png → provenance/cast/E/14.generation.json
- runtime/cast/E/15.png → provenance/cast/E/15.generation.json
- runtime/cast/E/16.png → provenance/cast/E/16.generation.json

