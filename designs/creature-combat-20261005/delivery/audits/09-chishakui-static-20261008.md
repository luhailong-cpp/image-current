# 赤砂魁 cast W07–11 独立静态与来源复核

- 复核者：`/root/audit_pet_batch_a`。
- 实看时间：2026-10-08 11:56 UTC；文件与来源最后复核：2026-10-08 12:05:22 UTC。
- 范围：`pets/09-chishakui/runtime/cast/W/07.png` 至 `11.png`，重点为刚替换的 W08、W09、W10。
- 方法：逐张实际 `view_image` 查看正式 PNG；读取 `POSES.md`、逐图 sidecar 和 `manifest.json`；计算当前 PNG 与原生来源的 SHA-256。未播放动画，未改宠物目录、未生成或加工图片。

## 静态结论

当前 W07 → W08 → W09 → W10 → W11 的支撑脚位置和短腿比例保持稳定。新 W08–10 相对两侧参考帧未再观察到此前明显的支撑脚升降或腿部突然拉长。左右鞋的落地高度连贯，双腿没有新出现的明显断接、额外肢体或左右脚交换。

五帧保持同一后侧朝向，均能辨识两腿、两手与一个背窑。解剖右手持续在画面右侧握短玉锤；左手在画面左侧施法，没有交换持械手。此方向沿用 `POSES.md` 以 E 向身份校正 W 向持锤侧的明确约定。W07/08 掌中蓄云，W09 蓄云增强，W10 左手向左上释放，W11 进入释放后的随动，静态相位关系可以接受。

本次未发现需要再返工的明确解剖问题。结论仅覆盖这五张当前正式图的静态相邻关系，不替代正常速度、慢放或逐帧播放验收，不据此宣布整组六组动画动态通过。

## 当前文件与 SHA-256

五张均为 1024 × 1024 RGBA PNG，alpha 范围 0–255。以下 SHA 与各自 `.png.generation.json` 及 `manifest.json` 中相应条目全部相符。检查时 manifest 的 `createdAt` 为 `2026-10-08T11:49:47.767075+00:00`，三张替换图已经同步，无清单仍指旧稿的情况。

| 正式帧 | 当前 SHA-256 |
| --- | --- |
| cast/W/07.png | `73698e3b1d0579294f35ffd2c20ded1e0cd5ab45b8a63d07668dcdb49d13250a` |
| cast/W/08.png | `ae8ae6ed2cefdd62e1bff16e3fff1c3aa79c70aec6c77bfd062bfb72d02234df` |
| cast/W/09.png | `dce2994b6e030fc925d622e04668d2dfc61cd4d33efb5ebc41ae453bee99073e` |
| cast/W/10.png | `163be4b23354dff86e980d129b7e45d0d79ec4278634e36e4d89c3b5df6c9dab` |
| cast/W/11.png | `35cf7f6eb94e726fb27cc7a18a883933aa67af1182a9ce1d7c121b6dfc8e195e` |

## 三张替换图来源

三张的 prompt、receipt 和 sidecar 所指原生 PNG 检查时均存在；原生 SHA 实算与 sidecar 的 `derivedFrom.sha256` 一致。正式导出记录为原生 1254 × 1254 整画布等比缩放至 1024 × 1024，未记录镜像、裁切或逐帧移位。

| 正式帧 | prompt / receipt（相对宠物目录） | 原生 SHA-256 |
| --- | --- | --- |
| W08 | `prompts/cast-W-08-support-20261008-r2.txt` / `records/cast-W-08-support-20261008-r2.receipt.json` | `4cf12c6b65278b9db7e4d5cf7bb54c7a7bb9f4331520f2910faa98babe2464a4` |
| W09 | `prompts/cast-W-09-support-20261008.txt` / `records/cast-W-09-support-20261008.receipt.json` | `91bfcd77177b4fbce4d70abbf4d9dd41025f5a2f8fa74a710bc0b4fc47b6f3b9` |
| W10 | `prompts/cast-W-10-support-20261008-r2.txt` / `records/cast-W-10-support-20261008-r2.receipt.json` | `d206700d3cade50b4d06ca5b99d2ffa36b1c210818f6427dfb4c477bd30ec3c5` |

逐图记录区分配置目标 Image 2.5 / max 与宿主实际未披露的模型、质量（均为 null），没有把目标冒充实际返回值。三张 `finalVisualReview.fileSha256` 均绑定当前正式 SHA；状态为 `static-reviewed; dynamic-unverified`，与本次检查能力边界一致。本报告不扩大为其余帧或最终全套收尾文件验收。


## 主窗口最终文件绑定：2026-10-08T12:12:40.996588+00:00

68张正式PNG、manifest、逐图来源和records/final-visual-review.json全部SHA匹配，当前回执引用存在，文件集合完整。validation技术通过、issues与sourceIntegrityIssues均为空；README/STATUS/MERGE_HANDOFF和正式预览齐全。三张修订之外的65张沿用已实看且SHA不变的记录。

最终动态状态仍为未验证（dynamicPassed=false）：本地浏览器与播放器限制已由原窗口记录。主窗口不把静态、文件或离线解码验证替代实时连播，也未绕过限制。素材交付完成，客户端未接入。
