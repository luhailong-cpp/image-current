# 主城东南分区制作

本窗口仅负责本目录，范围为行9–16、列9–16，共64块。权威像素坐标来自上一级 production-contract.json。首块 r13_c13 核心为 [49152,49152,53248,53248)。

## 当前断点

- 2026-10-10 已接收容量/布局门控：暂停新增生图与坐标扩展，当前无在途生图。见 [capacity-gate-ack.json](capacity-gate-ack.json)。只有主线程完成布局/尺度核对并解除门控后续产。
- 本轮只读重建已验证16个当前原生源及7次修补可精确还原当前4K与上下文；现有像素未修改。见 [capacity-gate-provenance-review.json](capacity-gate-provenance-review.json)。历史主风格参考 `D:/work/image/designs/mail-ui-v1/01-mail-event.png` 已不在原路径，不能把已存哈希当作参考仍在场的证明；旧记录保持原样。
- 道路/建筑风险清单见 [capacity-gate-review.json](capacity-gate-review.json)：桌架支撑、客栈外摆、伞柱与东侧长凳、中央铺地连通、左下植被及裁图外建筑占地均需与统一角色占位/碰撞规则核对，不从图像推断容量。[参考可用性记录](capacity-gate-reference-availability.json) 记录了相关JPG，但其尺寸和哈希均不同，未替换历史参考。
- 首块16个原生坐标片已齐，并完成7次原生局部重绘；每次真实返回均测得1254×1254。
- 已落盘1张4096×4096检查稿，块内视觉检查通过，正式验收0块。其余63块尚未开始。
- 当前检查稿：[r13_c13-4k-candidate-repaired.png](r13_c13/candidate/r13_c13-4k-candidate-repaired.png)。
- 缩小预览：[overview-repaired-preview-only.png](r13_c13/review/overview-repaired-preview-only.png)。预览不可替代4K资源。
- 精确数量、当前文件哈希及下一步读取 [progress.json](progress.json)。历史生成数量包含拒稿和替代稿，不代表完成图块数量。

## 原生与证据

4×4原生片各1254×1254，核心1024、四边上下文115，相邻重叠230。装配上下文4326×4326后，裁切核心 [115,115,4211,4211) 得4096×4096。候选像素没有放大布局总览、重采样或整体模糊。最小误差拼接仅用于边缘选取，不能替代结构重绘。

原候选已完成6条完整接缝、9个交汇及4边检查。发现伞骨双重结构、下方硬水平断线、左下边带断头，以及脱离木构的独立枝叶。已用7张新的1254原生编辑输出局部修补，最后一次利用4326上下文跨过正式右边界重绘，再裁回4096。最新逐处视觉结论见 [qa-report.json](r13_c13/review/current/qa-report.json)，报告必须匹配当前候选SHA。外接缝需与相邻图块合验，不能提前标记正式通过。

- [active-native-map.json](r13_c13/active-native-map.json)：16个逻辑片与当前版本。
- [assembly-manifest.json](r13_c13/candidate/assembly-manifest.json)：初始无放大装配配方、源图哈希、实际提示词和参考证据快照。
- [composition-history.json](r13_c13/repairs/composition-history.json)：前六次原生修补的坐标、遮罩、输入与输出哈希。
- [context-composition.json](r13_c13/repairs/context-composition.json)：第七次跨右边界的上下文修补；最新上下文为 [r13_c13-context-4326-repaired.png](r13_c13/candidate/r13_c13-context-4326-repaired.png)，外侧接缝待相邻块合验。
- [replay-verification.json](r13_c13/candidate/replay-verification.json)：从初始候选按全部七次原生修补顺序重放，逐步及最终PNG哈希完全一致。
- native/ 与 repairs/ 中逐图 .generation.json、request、prompt、receipt 记录每次实际请求与返回。工具未披露实际型号/质量，actualModel 与 actualQuality 保持 null；配置目标不当作实际锁定的证据。
- layout-only/ 只用于布局引导，不能作为交付像素；每次生成实际附上契约中的三张风格/布局参考。
- [model-verification.json](model-verification.json)：本批配置快照和官方核对来源。

## 接续与保留

读取当前视觉QA报告后，先修复未通过的位置，再用最新原生边缘扩展相邻块。不可重新运行 prepare.py，它会初始化进度。assemble_candidate.py --check 只检查16个源；--assemble 会重建初始候选，不含后续七次修补。verify_repaired.py 验证全部七次修补重放，不代表视觉验收。

当前4096块内检查通过。外围上下文在本块坐标约 x=4155–4211 仍有旧伞骨/伞沿残留，位于正式块之外；扩展 r13_c14 时须一并处理，不能将这段外侧上下文直接锁成正确硬锚点。正式验收仍需与相邻图块合验。

已删除本目录内4张未被当前源引用的明确拒稿PNG，逐图文字证据保留，见 [cleanup-record.json](cleanup-record.json)。当前在制片、实际被引用的来源及重建输入暂留，待成品正式核实且引用完整后清理。没有删除其他分区或宿主生成目录中的文件。

世界尺寸、5000人容量与客户端映射均未验证；本目录仅交付美术候选及来源记录，不作运行时接入承诺。
