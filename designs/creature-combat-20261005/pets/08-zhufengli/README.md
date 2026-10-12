# 竹风狸 · 受击 / 普攻 / 施法

2026-10-08 完成素材交付。沿用 Image 原有「竹风狸」，受击、普攻、施法 E/W 六组共 **68 张**，不含移动动画。技术检查通过；全帧及正常速度/0.25 慢放复核完成，视觉结论为 `reviewed-with-notes`，未发现阻断交付的问题。客户端未接入。

## 查看与文件

- [六组预览](preview/index.html)：正常速度、0.25 慢放、暂停、上一/下一帧与滑杆逐帧；各组可单独放大。可直接双击 HTML，无外部网络依赖。
- `preview/*-1x.png` 与 `preview/*-025x.png`：六组正常/慢放 APNG，共12份；`preview/*-contact.jpg` 为六组全帧图，均从正式素材生成，来源见 `preview/sources.json`。
- [姿态与解剖锁定](POSES.md)：方向、四足、唯一卷尾、双玉珠和右前爪攻击约束。
- [正式资源与时序](manifest.json)、[SHA256](SHA256SUMS.txt)、[技术检查](qa/technical.json)。
- 正式 PNG：`runtime/<hit|attack|cast>/<E|W>/01.png` 起编号。逐图来源记录在同目录 `.generation.json`；原始提示词在 `prompts/`，真实工具回执在 `receipts/`。

| 动作 | 每向帧数 | 单帧时间 | 每向时长 |
|---|---:|---:|---:|
| hit 受击 | 6 | 40ms | 240ms |
| attack 普攻 | 12 | 30ms | 360ms |
| cast 施法 | 16 | 45ms | 720ms |

总合同为 E/W 两向 68 张 1024×1024 RGBA PNG。E 为斜前朝右下；W 为独立绘制的斜后朝左上。普攻事件在07，施法事件在09；这些仅为素材建议事件点，不是客户端业务逻辑。

## 来源与模型证据

每帧均使用内置 `image_gen` 独立生成/编辑，实际附原有 E/W 身份图与主要画法图，部分另附同向帧约束连续性。没有复制、镜像、整图平移或插值补帧。代码只用于整画布统一缩放导出、校验和预览拼版。

目标沿用 `gpt-image-2.5-sunburst` / `max`。2026-10-05 查阅 [官方发布页](https://openai.com/index/introducing-chatgpt-images-2-5/) 与 [官方模型页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)，与本次目标一致；公共配置保持只读。宿主工具只开放 prompt、参考图、透明背景，未开放 model/quality 选择器；各图 `submittedParameters.model/quality` 与 `actualModel/actualQuality` 均为 `null`，不能将目标或公告当作实际模型证据。

当前返回的原生图为 1254×1254；正式 1024×1024 是整个原生画布等比 Lanczos 导出。每向、各动作使用相同整画布变换，没有逐帧裁紧或重新对齐脚点。固定元数据 pivot `[0.5,0.08]`（左下原点）/顶部坐标 `[512,942]`，自然重心反冲不被抹平。完整源 SHA、原生尺寸与导出操作保存在逐图记录。

## 验收与接入边界

技术检查通过：68/68、1024×1024 RGBA、无重复文件、SHA与逐图记录相符、无主体触边。低 alpha 的微弱边缘杂点独立记录，不等同于主体被裁。

[视觉复核](qa/visual-review.json)覆盖68帧、六组正常时间与0.25慢放、重点逐帧收势核对；[独立静态复核](qa/final-independent-review.json)另有全帧检查。保留少量独立生图造成的毛丝、叶缘和支撑点细微变化；普攻 E09→10、W07→08 的落爪跨度已重点查看，方向与攻击爪未交换，收势成立。此为素材预览结论，不宣称像素级无抖动或引擎验收通过。

包内旧联系表/局部预览已由统一预览替代；删除清单与历史证据位置映射见 `qa/cleanup.json`。原有跨窗口身份参考及唯一写入目录外的宿主生成缓存未处理。最终播放只依赖本目录成品，逐图来源文字记录完整保留。

未读取、修改或接入客户端/兄弟仓库；未执行 Git 提交、推送或切分支。实际游戏显示、动作触发、排序、命中业务和性能均未测试。交接见 [MERGE_HANDOFF.md](MERGE_HANDOFF.md)。

## 复查

用带 Pillow 与 NumPy 的 Python 执行 `tools/build_delivery.py` 可重建清单、SHA、技术检查、预览数据、APNG及全帧联系表；它不会调用图像模型，也不会创造缺帧。视觉状态仅在正式图 SHA 与已审阅快照一致时沿用；换图后会恢复待复核状态。
