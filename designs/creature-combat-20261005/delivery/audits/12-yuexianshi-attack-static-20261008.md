# 月弦师攻击修正帧独立静态点检

- 复核者：`/root/audit_pet_batch_a`。
- 实看及核对时间：2026-10-08 12:07–12:08 UTC；最后文件快照 `2026-10-08T12:08:35.391768+00:00`。
- 范围仅为正式 `attack/E/01 → 02`、`attack/W/11 → 12 → 01` 五张图，以及这些图对应的逐图来源记录和 manifest 条目。
- 方法：实际逐张 `view_image` 查看正式 PNG，读取 `POSES.md` 约定，计算当前文件 SHA-256。未检查其他帧，未播放、生成或修改宠物目录。

## 静态观察

E01 → E02：两只鞋及露出的踝部保持相近支撑位置，未再观察到首帧相对次帧的大幅脚位错开。脚踝到鞋面的连接自然，未见额外脚、断踝或新出现的明显外翻。左手持续从下方托住同一把月牙琴，右手由弦面附近转为预备拨弦姿势；琴体没有脱手或换手。当前来源记录称原 81 px 差已减到 3.98 px，本次独立结论依据实际静态图对照，未重新测算该数值。

W11 → W12 → W01：三个后视姿态的双鞋均为紧凑前后错落，鞋底朝向与露出的踝部连续，未再见收势帧突然换成宽开脚位、再跳回首帧的明显差别。头、背、琴及持琴位置接近；右手在弦边收回戒备，左手始终托琴。W12 左侧纱带环形与两侧帧不同，属于衣袖余摆，在本次静态对照中没有构成明确解剖错误或必须重画的证据。

五张均可辨识两手、两鞋，未发现多余肢体或持琴手交换。W 向露鞋底符合 `POSES.md` 指定的后侧透视，不能单凭露鞋底认定外翻。大腿和大部分小腿被裙摆遮挡，本次只能确认可见踝足及整体姿态没有明确错接，不能声称完整隐藏腿骨已获验证。

**本次未发现明确需要重画的新错误；所查静态相邻关系可接受。** 此结论不代表实际正常速度、慢放或逐帧播放通过，也不代表整组及全角色最终验收。

## 当前 PNG、逐图记录与 manifest

五张正式图均存在，为 1024 × 1024 RGBA PNG，alpha 范围 0–255。该角色将逐图 sidecar 保存在 `records/attack-E/NN.generation.json` 或 `records/attack-W/NN.generation.json`，并非 PNG 同目录；这五份均存在，记录 SHA 全部与当前 PNG 一致。

| 正式帧 | 当前 PNG SHA-256（逐图记录一致） | manifest 是否一致 |
| --- | --- | --- |
| attack/E/01.png | `15069725e57c876838aa41dfbe19a65d53fb740a1df695f2abab5c34d0ab535c` | 否，仍为旧稿 |
| attack/E/02.png | `62440d4888aa66db6780de0a92cb6753562964d715008f91838f91213c49c7fe` | 是 |
| attack/W/11.png | `57493d6a2a1bbc5d91007404f5f7ef45ea712431f777726358c8df8732113b13` | 否，仍为旧稿 |
| attack/W/12.png | `c60bff6ef53d3cb8502766064e3c2a28bde441c1ca6dd06ef676095971a0edf4` | 否，仍为旧稿 |
| attack/W/01.png | `887b7f11a3eb2a9214f3f7c3a1729d7361c54f9157f934544ba7feb792ff1e22` | 否，仍为旧稿 |

快照时 `manifest.json.generatedAt` 为 `2026-10-08T09:18:30.136724+00:00`。其中四份旧 SHA 分别为：

- E01：`91dbff56147165ac9f61fbfaeccf18fc3a4b9e846be0f60df706a2c9cef9b91f`。
- W11：`db22f48e37b8a6da311294c3a4726df8b4a3c83bb094172a39c49ae7aefbfaea`。
- W12：`6e42a4de2dc961171ec992dd7eaf127f497714901d8b6fa43214728e71014364`。
- W01：`7826c594caf6881c2186ccdf95c616b12193d03d5736909d1547daf7dbc534e5`。

因此当前状态为：修正图与逐图来源已经落盘并匹配，总清单仍待原窗口重建；不能提前宣称五张正式文件与总清单全部同步。未代改清单，也未把旧 manifest 的旧稿审查标记当作当前图片艺术缺陷。

## 来源记录

五份 sidecar 指向的 prompt 与 receipt 均存在。E01、W11、W12、W01 的当前原生 PNG 也存在，实算 SHA 与各 sidecar `derivedFrom.sha256` 相符。E02 原生图已按其 `sourceRetention.state=deleted-after-final-export-verification` 清理，文字证据、prompt、receipt 和正式 PNG 均保留；这是已记录的素材保留策略，不属于缺失正式帧。

| 帧 | 当前 prompt / receipt（相对宠物目录） |
| --- | --- |
| E01 | `prompts/attack-E/01.guardfix-20261008.txt` / `records/attack-E/01.guardfix-20261008.receipt.json` |
| E02 | `prompts/attack-E/02.txt` / `records/attack-E/02.receipt.json` |
| W11 | `prompts/attack-W/11.guardfix-20261008-cropped.txt` / `records/attack-W/11.guardfix-20261008-cropped.receipt.json` |
| W12 | `prompts/attack-W/12.guardfix-20261008-cropped.txt` / `records/attack-W/12.guardfix-20261008-cropped.receipt.json` |
| W01 | `prompts/attack-W/01.guardfix-20261008-retry1.txt` / `records/attack-W/01.guardfix-20261008-retry1.receipt.json` |

五张导出均记录同一整画布变换：原生 1254 × 1254 缩至 960 × 960，再置入 1024 × 1024 的 `[32,16]` 偏移，`perFrameAlignment=false`。实际模型与质量继续记录为宿主未披露的 null；本报告没有将配置目标当作实际确认结果。

## 主窗口最终补充

补充时间：2026-10-08T13:07:13.863745+00:00。月弦师当前68帧、来源、清单及交付包已完成独立绑定核验；本报告早期的清单待刷新事项已结清。详见[最终交付核验](12-yuexianshi-final-binding-20261008.md)。W受击01采用获批r4，实际连播仍未验证，客户端未接入。
