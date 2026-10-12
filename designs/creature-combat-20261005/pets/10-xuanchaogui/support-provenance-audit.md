# 玄潮龟来源与清理辅助审计

审计快照：2026-10-05 16:45 EDT（20:45 UTC）。仅只读检查本角色目录；本轮唯一写入为本文件。未改图片、生成记录、README 或其它交付文件。共享身份／画法参考与宿主生成目录均在本次审计范围外，仅核对记录中的路径、用途与已保存哈希，不重新读取或清理外部图片。

## 结论与仍在制作的部分

当前正式 PNG 为 65／68：hit E/W 各 6，attack E 9、W 12，cast E/W 各 16。attack E10–12 尚未落盘，属于正在补制的暂缺，不能据此判定来源记录损坏。审计期间 E09 刚落盘；所有数量均为此时快照。

已存在的正式帧均能找到对应来源文字记录，已核对运行图 SHA 与记录一致。具有 sidecar 的 50 张，当前本目录 prompt、原生生成记录、receipt 链可解析；已记录的本目录参考图哈希未发现变化。其余普攻 15 张的专用 provenance 记录存在，但与当前交付检查器约定不一致，见下项。

## 需要根任务收尾的具体项

1. **普攻 sidecar／索引缺口**：`runtime/attack/E/01.png`–`09.png`、`runtime/attack/W/01.png`–`06.png` 尚无图旁 `.generation.json`。真实独立记录分别在 `provenance/attack/E/01.generation.json`–`09.generation.json`、`provenance/attack/W/01.generation.json`–`06.generation.json`，包含正式文件 SHA、原生尺寸和源 SHA、实际提示词路径、参考数组、内嵌工具 output_hint、时间和模型目标／实际未知值。并非没有生成证据。
2. **检查器只发现部分结构**：`tools/build_delivery.py:190` 仅搜索名为 `generation.json` 的中央记录，不扫描上述 `NN.generation.json`，所以旧快照 `preview/audit/validation.json` 把早期 14 张报为 missing_generation_record。这些专用记录又将生成证据与导出信息合在一条中，`derivedFrom` 无 `generationRecord` 链、receipt 放在顶层而非 `evidence`；仅复制文件名仍会触发严格检查器的链路要求。请由该动作的负责人按既有真实证据补齐适配或统一索引，勿编造模型返回值、原生元数据或替换历史输入。
3. **历史拒稿的一个悬空链接**：`provenance/cast/E03-rejected-early-effect.generation.json` 的 `evidence.receipt` 仍写 `provenance/cast/E03.job.json`，该路径已不存在；实际保留的历史文件是 `provenance/cast/E03-rejected-early-effect.job.json`。这不影响当前正式 E03，其 sidecar 指向新的 `provenance/cast/E/03.generation.json` 与 `03.receipt.json`。建议仅修正历史指针，保留拒稿文字证据。
4. **最终交付尚属待收尾**：根目录 `manifest.json`、`validation.json`、`README.md`、`STATUS.md`、`MERGE_HANDOFF.md` 在快照时尚未出现；现有 `preview/audit/*` 是 64 帧阶段的暂态文件。待补制结束再重建最终清单、SHA、预览与验收状态。部分旧记录的单帧审核措辞仍为 pending，最终应以根实际逐帧／连播结果统一说明，不能仅依据文件数改成通过。

## 旧 cast E01／E02 追溯核对

| 正式帧入口 | 实际提示词 | 原生生成记录 | 工具回执 |
|---|---|---|---|
| `runtime/cast/E/01.png.generation.json` | `prompts/cast/E01.txt`（1936 字符） | `provenance/cast/E01.generation.json` | `provenance/cast/E01.job.json` |
| `runtime/cast/E/02.png.generation.json` | `prompts/cast/E02.txt`（2120 字符） | `provenance/cast/E02.generation.json` | `provenance/cast/E02.job.json` |

两条链中的本目录文件均存在。E01 的 3 项输入为原有 E／W 身份与主要画法图；E02 有相同 3 项输入及 E01 原生图，共 4 项。生成记录保存参考用途与 SHA、submittedParameters 的真实参考路径、output_hint 原文；sidecar 保存 1254→1024 整画布导出操作和源 SHA。配置目标为 GPT Image 2.5/max，实际 model／quality 为 null，有宿主管理未披露说明。**可以从正式 sidecar 完整查到现有 prompt／reference／receipt 文字证据，无需把 E01/E02 改成新式目录才能追溯。** 宿主原生图片是否仍在不属本次越界核查范围。

## 图片保留／清理建议

- 本目录目前只有 65 张 runtime PNG 与 7 张预览 JPG；没有 source 原图、回退图或文件名含 rejected/candidate 的图片副本。拒稿图片路径只在来源文字中指向宿主默认目录，不能据本次审计越界删除。
- 六张 `preview/contact-sheets/<action>-<direction>.jpg` 被 `preview/index.html` 实际引用，是正式检查辅助，保留并在最终帧补齐后重建。尤其 attack-E 联系表当前不能代表 12 帧齐全。
- 唯一可考虑的冗余图片候选为 `preview/qa/cast-W-review-contact.jpg`。当前 HTML、MD、工具代码未引用它；`preview/qa/cast-W-reviewed-files.json` 另保留被审帧 SHA。根确认正式 cast-W 联系表及最终文字审核已充分承接后，可删除这张临时审核拼图；若仍作为本轮审核证据正在使用，暂留到最终验收。
- 所有失败、拒稿的 prompt／receipt／generation 文字记录继续保留；不要以文件名带 rejected 为由删除这些 JSON/TXT。
- 现有检查器的 alpha 边缘提示不能直接当作主体裁切，也不适合通过逐帧贴底或改坐标消除。应以实际可见边缘与连播核实，再决定是否修图。本审计不新增视觉通过结论，不代表客户端接入通过。

