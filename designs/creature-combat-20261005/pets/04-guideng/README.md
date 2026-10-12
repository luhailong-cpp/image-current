# 桂灯童 · 战斗三动作

沿用 Image 原有桂灯童：栗发、金脉叶帽、象牙杏青丝衣。解剖学右手提六角木灯，左手握桂花枝。仅制作原地悬浮战斗，没有移动循环。

- [交互预览](preview/index.html)：六组选择、正常时间、0.25 倍慢放、播放/暂停、逐帧与滑块、深浅棋盘底。可直接打开本地 HTML，不需要安装依赖。
- [当前状态](STATUS.md)、[技术检查](validation.json)、[动作清单](manifest.json)、[SHA-256](SHA256SUMS.txt)。
- [姿态表](POSES.md)、[模型核对](MODEL_CHECK.md)、[接入交接](MERGE_HANDOFF.md)。

|动作|每向帧数|每帧|每向总时长|
|---|---:|---:|---:|
|受击 hit|6|40ms|240ms|
|普攻 attack|12|30ms|360ms|
|施法 cast|16|45ms|720ms|

已完成 68 张 1024×1024 RGBA PNG，路径 `runtime/<action>/<E或W>/<01起帧号>.png`。E 是斜前朝右下，W 是独立绘制的斜后朝左上。全帧及六组正常/慢放已验看，技术检查零错误、零警告；详细证据见 [视觉验看](VISUAL_QA.json)、STATUS 与 validation。

每帧使用内置 image_gen 独立生成/编辑，实际附原有身份 E/W、指定画法图，连续帧另附前帧或同组阶段参考。未采用复制、镜像、插值或全图平移补帧。最终采用同一导出变换：原生 1254 方图整画布等比缩放为 922，置于 1024 透明画布的 [51,51]；没有逐帧按脚对齐，没有新增代码姿态。保留透明 alpha 与自然衣袖/飘带余势；正式执行记录见 EXPORT.json。

逐图来源入口为 manifest 的 `sourceRecord`：E-cast 使用 `records/E-cast/NN.json`，其余五组使用 `records/<方向>-<动作>/NN.generation.json`。提示词在 `prompts/`，记录含原生尺寸/SHA、生成时间、工具返回文本与参考。目标 GPT Image 2.5 Sunburst / max；内置工具没有模型/质量选择器，实际提交和返回未披露字段均为 null，不宣称已显式锁定该 API 型号。

重建预览与校验：使用已安装 Python/Pillow 执行 `tools/build_package.py`。此工具只读正式 PNG，输出清单、SHA、全帧验看图和 HTML，不生成动作或修改人物。运行预览与重建检查不依赖宿主生成缓存；重新执行 `tools/final_export.py` 则需要逐图记录中的原生图。历史提示词/receipt 保留原始证据路径，EXPORT.json 关联导出前后 SHA。跨窗口身份和风格图未更改。

本包仅交付美术与本地预览；客户端资源加载、锚点效果、事件触发与实战表现尚未验证。
