# 04 山岳守卫 · 受击 E/W 完整帧组

2026-10-03 续修：E06 已改用 E_06_finish_attempt04，导出 SHA `e3057b6dd3a28cedc0d2056e3c2c916ee2116e250f7992b672c159f6c59dd786`。以 E05 为编辑目标真实重画收势，恢复头部比例；再局部补实金色杖首背盘。单帧实际查看通过，最新接触表和 40ms/160ms 预览已刷新。此前 E06 attempt01 与本文历史采用表只作旧记录。动态正常/慢速、收势衔接及客户端状态仍待根线程终验；没有把单帧通过计成动态通过。attempt03 单次连接失败的原文保留，随后同入口 attempt04 成功。

**E/W 各6帧，共12/12独立AI姿态已生成并导出。** 全部1024×1024 RGBA；来源均为1254×1254原生单帧，没有镜像、复制、扭曲、插值或小格放大补帧。未接入客户端。

## 查看与技术核验

- 帧与逐图来源：[E](frames/hit/E/) · [W](frames/hit/W/)。
- [正常/慢速/逐帧HTML](provenance/hit/hit_preview.html)，父线程服务地址：http://127.0.0.1:8704/provenance/hit/hit_preview.html。
- 正常每帧40ms，共240ms/段：[E](provenance/hit/hit_E_normal.gif) · [W](provenance/hit/hit_W_normal.gif)。
- 慢速每帧160ms，共960ms/段：[E](provenance/hit/hit_E_slow.gif) · [W](provenance/hit/hit_W_slow.gif)。
- [E逐帧接触表](provenance/hit/hit_E_contact.png) · [W逐帧接触表](provenance/hit/hit_W_contact.png)。
- [技术核验](provenance/hit/hit_technical_validation.json)：12张尺寸/透明/SHA/来源引用、12个唯一SHA、4段GIF的帧数与时长通过。技术通过不代替动态美术验收。

## 美术检查与实际修正

单帧手脚/持物检查已完成：E右杖近侧、左盾远侧；W左盾近侧、右杖远侧。均单眼侧面、两靴可辨，握持和肩肘连接可读；长杖上下端完整，大冠实心金背盘与小挂玉环分开处理。帧序包含初始命中、压缩、后仰峰值、缓冲、恢复和收势。

已实际调用AI修正E03远眼与杖盘、W03衣摆后下杖杆/底尖、W01误画的空心杖盘。接触表发现E04后脚跨得过大；一次局部修正未充分解决，最终以E03为编辑目标续画缓冲，采用E04 attempt03，显著减少支撑脚跳位。

**现场动态终验仍由父线程补核。** 子代理打开独立预览时Cua返回“Browser is not available: iab”，随后浏览器列表为空。未把GIF已编码或接触表当现场播放通过。已请父线程使用根线程可用IAB核对正常/慢速、首尾衔接、收势比例和根锚。虚拟根目标(512,928)仅为布局目标；始终整张画布等比导出，没有逐帧最低脚贴地或包围盒缩放。

原生E03小玉环孔曾采样alpha=1（1/255），背景大量alpha=0。低alpha区可能保留高饱和RGB；灰棋盘合成检查未把黑底view的显示误判为不透明色块，未擅自阈值修改透明。

## 采用版本与来源

| 方向 | 01 | 02 | 03 | 04 | 05 | 06 |
| --- | --- | --- | --- | --- | --- | --- |
| E | attempt02 | attempt02 | attempt05 | attempt03 | attempt01 | E_06_finish_attempt04 |
| W | attempt02 | attempt01 | attempt02 | attempt01 | attempt01 | attempt01 |

真实提示词、参数、回执、失败原文及参考SHA见[provenance/hit](provenance/hit/)和逐帧generation.json。首次以身份画像/对应idle/designs新画；后续本轮候选作编辑目标，同时实传三项原始参考。未用旧run-correction/combat在制图，未取另一电脑未提交内容。

配置目标为GPT Image 2.5 Sunburst / max；内置无model/quality选择器，实际提交两字段为null，实际型号/质量未确认。C2PA泛称gpt-image不确认具体版本。记录时间含UTC或时区偏移，用户时区America/New_York。

## 网络恢复及清理

早先E01/E02网络失败无图；父线程提供同入口真实恢复证据后已恢复制作，两槽重试成功并补齐剩余帧。旧失败记录仍保留，不再代表当前缺口。未用收费API/CLI。

确认当前成品和引用后已删除被替换拒稿与中间导出，保留文字来源/SHA，见[首次清理](provenance/hit/cleanup_after_attempt05.json)及[12帧选择清理](provenance/hit/cleanup_hit_selected12.json)。当前选定帧唯一原生在制来源留至父线程动态终验；无额外图片备份。未操作Git暂存、提交、推送或分支。


2026-10-03 最后技术核验已刷新至当前E06 SHA，12张正式帧和4段预览通过尺寸/透明/哈希/帧数/时长检查。逐帧静态记录见provenance/hit/hit_review_20261003.json；动态仍待主窗口。原生选中来源按父线程要求暂保留至动态终验，89张清理后已仅恢复44张当前选中源（本分工hit12+run32），原生SHA全部核对一致，其余45张拒稿/中间图保持删除；详见provenance/run/W_NW_restore_selected_native_20261003.json。
