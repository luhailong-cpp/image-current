# 玄潮龟来源链收尾记录

2026-10-08。本次仅修复来源文字结构；未生图、改图或修改 runtime sidecar，没有触及 cast W06。根目录最终 manifest、validation、README、STATUS、MERGE_HANDOFF 由主任务更新。

## 已修复

- `provenance/attack/E/01.generation.json` 至 `12.generation.json`、`provenance/attack/W/01.generation.json` 至 `06.generation.json` 共 18 条，改为各自真实原生输出的生成记录。原先顶层误用导出文件路径／SHA／1024 尺寸，同时留下无 generationRecord 的派生层，造成 `missing_source_record_link`。
- 原生路径与 SHA 取自原记录 `derivedFrom`，原生尺寸取自原记录 `native`；逐一核对现存原生文件 SHA、尺寸／格式／RGBA 及真实 receipt 的 output_hint 后修复。没有根据现行配置重填历史实际型号。`actualModel`、`actualQuality`、提交的 model／quality 仍为 null，原配置快照、实际提示词、参考图和回执保持不变。
- 原导出字段完整保留在各记录 `recordNormalization.previousExportFields`，包含原文件路径、SHA、alpha、变换、时长、pivot、event 与单帧审核文字；同时保存修改前 JSON 的 SHA。正式 sidecar 原有的 native generationRecord 指针现可直接终止于真实原生记录，不需改写 sidecar。
- `provenance/cast/E03-rejected-early-effect.generation.json` 的 `evidence.receipt` 修正为实际存在的 `provenance/cast/E03-rejected-early-effect.job.json`。旧指针保存在 `receiptLinkCorrection`，源文件路径与 output_hint 经逐字核对。历史 job 的提示词原路径按历史保留；已归档的实际提示词仍由生成记录顶层 `prompt` 指向。

机器记录见 [provenance-finalize-evidence.json](provenance/provenance-finalize-evidence.json)，实施脚本为 [finalize_provenance.py](tools/finalize_provenance.py)。修复前后 24 张 attack PNG 与 24 个图旁来源记录的 SHA 均完全一致。

## 审计结果

已运行 `tools/build_delivery.py`，默认输出目录为 `preview/audit`。首次调用在覆盖 `preview/contact-sheets/attack-E.jpg` 时遇到 Windows `OSError: [Errno 22] Invalid argument`，未因此改动图片或规避来源校验。随后运行同脚本加 `--no-contact-sheets`，正常退出 0，输出：

- 68／68 正式帧，18 处来源链错误全部消除，错误数 0。
- 无文件 SHA 重复组、无像素 SHA 重复组、无额外 runtime PNG。
- 42 条警告均为 alpha 非零触及画布边缘；这些帧边缘 alpha≥16 的像素数均为 0。此技术阈值统计不能代替主任务的实际边缘、逐帧与连播审核。
- 审计时间为 `2026-10-08T09:22:19.761052+00:00`，结果见 [preview/audit/validation.json](preview/audit/validation.json)。本次审计不声明动画美术或客户端接入通过。主任务后续重画 W06 后须按最终 SHA 重跑审计和刷新联系表。

## 清理候选与保留边界

本次没有删除任何文件，尤其没有删除宿主生成目录中的外部图片。外部原生／拒稿图片是否清理由主任务按项目授权与最终引用完整性决定，本文件只报告。

- 六张 `preview/contact-sheets/*.jpg` 被当前 HTML 引用，继续保留并在最终重画后刷新。
- `preview/qa/cast-W-review-contact.jpg` 是临时审核拼图候选，但现在已被 `cast-W-review.md` 明确引用；旧 `support-provenance-audit.md` 中“未引用”的判断已过时。只有主任务更新审核文档、由最终联系表承接该用途之后，才适合删除这一临时图。
- 来源文字中可见的历史拒稿／候选共 10 条：cast E03 过早法效、attack W11/W12、cast E06 边缘候选、cast W04 两次站直稿、cast W05 站直稿、cast W09 月牙漂浮稿、cast W10 构图漂移稿、hit W04 过伸稿。它们的原生图片位于宿主 generated_images，均不在本子任务写入范围；对应 JSON、receipt、prompt 必须保留。W06 正在主任务定点重画，不作清理判定。
