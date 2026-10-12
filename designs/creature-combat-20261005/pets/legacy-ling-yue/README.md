# 灵玥 · 受击、普攻、施法

2026-10-08：本包 **68/68 张独立动作帧制作完成**，技术检查通过，已完成全帧静态复核、六组本地原速/慢速播放取样与首末逐帧检查。交付保留明确的支撑与收势差异；未接入客户端。最新状态见 [STATUS.md](STATUS.md)，复核记录见 [playback-review.md](playback-review.md)，技术结果见 [technical-validation.json](technical-validation.json)。

只延续 Image 原有「灵玥」身份：雪白九尾狐、四条兽肢、金眼、朱砂额纹、金玉项圈及淡紫尾影。E 为朝右下的斜正面；W 为独立绘制、朝左上的真正斜背面。本包只包含以下三种战斗动作，没有走路、跑步或位移循环。

| 动作 | E | W | 每帧 | 每向时长 |
|---|---:|---:|---:|---:|
| 受击 hit | 6 帧 | 6 帧 | 40 ms | 240 ms |
| 普攻 attack | 12 帧 | 12 帧 | 30 ms | 360 ms |
| 施法 cast | 16 帧 | 16 帧 | 45 ms | 720 ms |

正式图片在 `runtime/{hit|attack|cast}/{E|W}/NN.png`，全部为 1024×1024 RGBA PNG，各组从 01 编号。[manifest.json](manifest.json) 按帧列出图片、SHA256、来源记录、帧时长、方向、合同 pivot 和事件字段。`event=null`，没有猜填游戏事件。

## 预览与验收

打开 [preview.html](preview.html)，每组所有图片加载并解码后才可播放。提供 1× 原时间、0.25× 慢放、上一帧/下一帧、逐帧滑条以及透明网格/深色/白色背景。预览使用同一 1024 Canvas 同步绘制真实帧，不对每帧重新找脚点，不插值。加载失败时禁止该组播放并保留错误提示。浏览器负载过高时会变慢；不会主动跳过中间帧赶进度。

技术审计已检查 68 张图片的尺寸、格式、alpha、SHA、精确重复和去透明边后整体平移重复，以及 prompt、receipt 与来源路径。主任务另完成各组全帧静态复核，并实际操作 Canvas 预览的 1×、0.25×、首末步进及恢复后 E 施法 06→07→08 检查。真实播放观察来自截图取样，**不是覆盖每个显示帧的视频记录，也不是客户端验收**。审阅绑定当前 68 张 PNG 与 sidecar SHA，见 [最终审阅绑定](receipts/final-review-frame-binding.json)。旧审阅中的初稿缺陷不自动代表当前像素。

保留的限制：E 普攻部分承重足有约 20–45 px 横向差异，E 施法中段约 10–20 px，W 施法释放阶段约 10–20 px；W 施法尾扇收势与末首头部角度不完全相同。这些均为 1024 画布目测，详细帧号与判断见最终复核。没有使用逐帧平移或插值隐藏差异。

## 坐标和导出

合同 pivot 为 `[0.5, 0.08]`，以左下为原点；顶部整数脚点为 `[512,942]`。E/W 所有正式动作帧都使用固定整画布导出：原生 1254 或 1024 方图统一缩放为 980×980，放在 1024×1024 透明画布的 `[22,0]`。源尺寸及操作在逐图记录中如实保存。该锚点是接入约定，不代表各帧生成像素的支撑足完全重合。

## 模型与逐图来源

全部使用内置 `image_gen`。本批配置目标为 **GPT Image 2.5 / max**（`gpt-image-2.5-sunburst`）；工具未开放 `model`、`quality` 选择器，结果未披露可核实的实际型号/质量，因此每图 `submittedParameters.model/quality`、`actualModel/actualQuality` 均为 **null / 未确认**。配置目标和提示词不是实际版本的确认依据。未使用收费 API/CLI。

每张正式图片旁的 `NN.png.generation.json` 是该图片的直接记录，包含当次配置快照、原生尺寸和 SHA、真实 prompt、参考用途、工具 receipt 及导出操作。[SOURCE_INDEX.md](SOURCE_INDEX.md) 提供 68 张图到记录的索引。`prompts/` 与 `receipts/` 保留重试、拒稿、修正前后的文字来源，不能因清理中间图片而删除。`design/E.png` 与 `design/W.png` 是仍在使用的方向设计。

## 交付边界

未读取或接入客户端、兄弟仓库或其它电脑，没有修改共享配置、旧身份资源或 Git。这里只交付灵玥动作素材及必要检查/接入说明；客户端渲染、事件、资源导入和实机播放均未执行。后续接入说明见 [MERGE_HANDOFF.md](MERGE_HANDOFF.md)。

复核工具和运行命令见 [tools/README.md](tools/README.md)。已按 [cleanup-plan.json](cleanup-plan.json) 清理 10 张旧接触表/WebP；逐图 SHA 与删除结果见 [cleanup-record.json](cleanup-record.json)。未建立图片备份，任务目录外宿主缓存与共享参考未改动。旧审阅中已退役的图片路径由清理记录保留来源说明，当前查看以正式 runtime、根 preview 和 `qa/` 为准。
