# 玄潮龟 · 受击、攻击、施法成品

原有玄潮龟形象的六组战斗动作，共 **68 张 1024×1024 RGBA 透明 PNG**，正式帧已全部落盘。E 为斜前朝右下，W 为独立绘制的真实斜后朝左上。W 不是 E 的镜像。未制作移动循环，未接入客户端。

[打开动作预览](preview/index.html)；支持正常速度、0.25 倍慢放、暂停逐帧、循环与棋盘／白／深色背景。预览直接读取正式 PNG，无补帧或插值。

| 动作 | 正式目录 | 每方向帧数 | 每帧时长 | 单次时长 | 事件 |
| --- | --- | ---: | ---: | ---: | --- |
| 受击 hit | `runtime/hit/E`、`runtime/hit/W` | 6 | 40 ms | 240 ms | 无 |
| 攻击 attack | `runtime/attack/E`、`runtime/attack/W` | 12 | 30 ms | 360 ms | 第 7 帧 `impact` |
| 施法 cast | `runtime/cast/E`、`runtime/cast/W` | 16 | 45 ms | 720 ms | 第 10 帧 `release` |

帧文件按 `01.png` 起顺序编号；表中事件帧号为 **1 起始**。各帧统一使用左下原点 pivot `[0.5, 0.08]`，对应左上原点像素锚点 `[512, 942]`（取整）。导出使用统一整画布缩放，不按单帧轮廓贴底或移动角色。

角色保持黑青灵龟、珠白青瓷浅水盂背甲、暖金雕边、一枚月牙玉石、桂枝及朱结玉珠短穗。四足承重，遮挡足按原视角自然隐藏；固定饰物的解剖侧归属见 [POSES.md](POSES.md)。每张姿态均为内置工具真实 AI 单帧生成／编辑，没有以复制、镜像、整图平移或插值补齐帧数。

## 验收与文件

- [manifest.json](manifest.json)：正式文件清单、时序、事件、锚点、SHA 与来源链接。
- [validation.json](validation.json)：缺帧、尺寸、RGBA／alpha、SHA、重复帧与来源链的机器检查。
- [SHA256SUMS.txt](SHA256SUMS.txt)：68 张正式 PNG 的文件校验值。
- [visual-review.json](visual-review.json)：绑定最终帧 SHA 的人工逐帧与连播验收；最终美术及动态结论以此文件为准。
- [STATUS.md](STATUS.md)：本次完成范围与已修正问题。
- [MERGE_HANDOFF.md](MERGE_HANDOFF.md)：接入参数及交接边界。

最终技术检查为 68／68 帧、0 错误；42 条边缘警告均为 alpha 不高于 6／255 的微弱散点，未发现可见主体裁切。已复核全部帧，运行六组正常／0.25 倍播放并抽样观察，关键衔接另行暂停逐帧检查。视觉与动态结论为通过并保留上述备注；具体方法及最终 SHA 见 `visual-review.json`。已有阶段性审核文档保留工作证据，不覆盖最终结论。

## 生成证据

本批使用宿主内置 `image_gen`，配置目标为 **ChatGPT Images 2.5 / `gpt-image-2.5-sunburst` / `max`**。工具未提供型号、质量选择器或实际返回值，因此实际提交与返回的 model／quality 均记录为 `null`，不能将配置目标冒称实际确认版本。

每帧的 `runtime/.../NN.png.generation.json` 连接 `provenance` 中的原生来源、时间、SHA、调用回执及实际参考；准确提示词位于 `prompts`。旧稿的文字来源记录保留，不作为正式游戏图片。跨目录原生身份与主要画法参考仍属于原项目设计，不属于本目录清理范围。

如需复核，可在本目录使用含 Pillow 的 Python 运行 `tools/build_delivery.py --output-dir .`；该命令重建技术清单和预览联系表，不生成姿态。只有全部正式 PNG 的 SHA 与 `visual-review.json` 完全一致且技术检查无错误时，才沿用本次人工结论；图片变化会恢复待复核状态。工具说明见 [tools/README.md](tools/README.md)。
