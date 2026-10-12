# r09_c11 完整候选

已完成 16 片原生内容覆盖并原尺寸拼接为 4096×4096。当前是可审阅候选，**正式验收 0，内部接缝已完成候选级目检**。

- [4096 候选](tiles/r09_c11.candidate.png)
- [选图与逐像素贡献表](selected-native-r09_c11.json)
- [候选来源记录](tiles/r09_c11.candidate.png.generation.json)
- [质量检查及剩余复核项](qa/r09_c11-quality-review.json)
- [来源审计](qa/r09_c11-source-audit.json)
- [独立进度](progress-r09_c11.json)

全部 28 次生成/编辑的输出实测为 1254×1254；16 片各裁出本地 [115,115,1139,1139) 的 1024 核心，按 4×4 原尺寸硬切拼接。候选像素与这些来源核心逐一完全一致，无放大、无羽化。全图范围 [40960,32768,45056,36864)。候选 SHA256：`1030a336d737f3859fd3c4a517a95b358a483fe129cc14427f3c27bb87687621`。

原有 p23→p24 檐梁、墙梁与红窗错位，以及 p43→p44 台阶错位，分别以 p23_v03、p43_v03 原生片重绘修正。四个跨缝修复稿及二值硬切试接均未采用，p43_v02 因改变木架且新增装饰而拒用。24 条内部硬接与 9 个交会点已目检；局部金属和石材色调、编钟细节及木架支撑与布局图的贴合度仍需主任务复核。

右侧 4 条跨块接缝已对 r09_c12 原生片做候选级目检。上、左、下外部边尚未通过邻块验收。客户端映射、导航和承载测试未在此任务验证。

使用宿主内置 image_gen。配置目标为同批次的 gpt-image-2.5-sunburst / max，但工具未开放这些选择器，也未返回可核实型号/质量；实际提交及实际返回字段均为 null。每次完整提示词、输入角色与哈希、真实工具参数/回执均保存在 prompts、receipts 及逐图记录中。原始输入仍为当前候选和后续修图依赖，尚未进行成品清理。

## 逐图记录

| 图片 | 用途 | 来源记录 | 实际型号 / 质量 |
|---|---|---|---|
| `r09_c11_p11_v01.png` | 候选采用 | [记录](native/r09_c11_p11_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p12_v01.png` | 未采用 | [记录](native/r09_c11_p12_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p12_v02.png` | 候选采用 | [记录](native/r09_c11_p12_v02.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p13_v01.png` | 未采用 | [记录](native/r09_c11_p13_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p13_v02.png` | 候选采用 | [记录](native/r09_c11_p13_v02.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p14_v01.png` | 候选采用 | [记录](native/r09_c11_p14_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p21_v01.png` | 未采用 | [记录](native/r09_c11_p21_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p21_v02.png` | 候选采用 | [记录](native/r09_c11_p21_v02.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p22_v01.png` | 候选采用 | [记录](native/r09_c11_p22_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p23_v01.png` | 未采用 | [记录](native/r09_c11_p23_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p23_v02.png` | 未采用 | [记录](native/r09_c11_p23_v02.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p23_v03.png` | 候选采用 | [记录](native/r09_c11_p23_v03.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p24_v01.png` | 候选采用 | [记录](native/r09_c11_p24_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p31_v01.png` | 候选采用 | [记录](native/r09_c11_p31_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p32_v01.png` | 候选采用 | [记录](native/r09_c11_p32_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p33_v01.png` | 候选采用 | [记录](native/r09_c11_p33_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p34_v01.png` | 未采用 | [记录](native/r09_c11_p34_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p34_v02.png` | 候选采用 | [记录](native/r09_c11_p34_v02.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p41_v01.png` | 候选采用 | [记录](native/r09_c11_p41_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p42_v01.png` | 候选采用 | [记录](native/r09_c11_p42_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p43_v01.png` | 未采用 | [记录](native/r09_c11_p43_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p43_v02.png` | 未采用 | [记录](native/r09_c11_p43_v02.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p43_v03.png` | 候选采用 | [记录](native/r09_c11_p43_v03.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_p44_v01.png` | 候选采用 | [记录](native/r09_c11_p44_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_seam-p23-p24_v01.png` | 未采用 | [记录](native/r09_c11_seam-p23-p24_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_seam-p23-p24_v02.png` | 未采用 | [记录](native/r09_c11_seam-p23-p24_v02.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_seam-p43-p44_v01.png` | 未采用 | [记录](native/r09_c11_seam-p43-p44_v01.png.generation.json) | 未确认 / 未确认 |
| `r09_c11_seam-p43-p44_v02.png` | 未采用 | [记录](native/r09_c11_seam-p43-p44_v02.png.generation.json) | 未确认 / 未确认 |

## 可复现工具

`r09_c11_request.py` 修正共享提示词中的右邻方向说明。`r09_c11_assemble.py` 机械拼接原生核心并生成接缝/交会检查。`r09_c11_seam.py` 准备真实跨缝编辑输入和接收原生输出；`r09_c11_preview_repair.py` 检查硬回填，不修画像素。所有调用须设置 `ISLAND_PROGRESS_FILE=progress-r09_c11.json`，避免写主进度。
