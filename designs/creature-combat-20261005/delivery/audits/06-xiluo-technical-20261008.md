# 汐螺 · 独立技术及来源核对

检查时间：2026-10-08T11:41:52.919512+00:00（2026-10-08 07:41 EDT）。本次只读宠物目录，只写本报告；未查看图片、未播放、生图或修改正式素材。视觉判断由另一独立审查任务负责。

## 结论

**当前68张正式PNG及12个动画预览没有技术阻塞。** manifest、正式PNG、当前逐图来源与媒体来源SHA全部一致；README、STATUS、MERGE_HANDOFF均已存在并与实际合同一致。另有一处旧W09拒稿文字记录的历史receipt链接待整理，详细路径见下文，未影响当前成品或当前来源链。

| 动作 | E实数 | W实数 | 单帧 | 每方向总时长 |
|---|---:|---:|---:|---:|
| hit | 6 | 6 | 40ms | 240ms |
| attack | 12 | 12 | 30ms | 360ms |
| cast | 16 | 16 | 45ms | 720ms |

- 实际runtime文件集合与manifest精确对应68张，缺帧0，额外正式图0。
- 68张均1024×1024 RGBA，alpha极值0–255；每张文件SHA与解码像素SHA均匹配manifest，未发现文件或像素完全重复。
- 每张对应当前records记录的正式图SHA一致；manifest绑定的generationRecord、prompt、receipt文件均存在，三个文字文件的SHA逐项匹配。
- 当前记录的prompt、evidence.receipt与manifest链接一致。
- 六组帧数、逐帧40/30/45ms、事件02/07/10、pivot[0.5,0.08]、锚点[512,942]与三份交付文档一致。
- README正确指向 `qa/technical-validation.json`，不是根目录validation.json；该技术报告为passed、0 errors。不将不存在的根目录同名文件误报为缺文档。

## 动画媒体

12个WebP均实际解码检查，未执行视觉播放。每个媒体文件SHA、帧数、512×512预览尺寸、逐帧时长、总时长及全部sourceFiles/sourceSha256与当前正式PNG一致。正常速度为40/30/45ms；0.25×预览分别160/120/180ms，无媒体仍引用旧W09图的现象。

| 文件 | 帧数 | 每帧 | 总时长 | 结果 |
|---|---:|---:|---:|---|
| preview/hit-E-normal.webp | 6 | 40ms | 240ms | 通过 |
| preview/hit-E-slow.webp | 6 | 160ms | 960ms | 通过 |
| preview/hit-W-normal.webp | 6 | 40ms | 240ms | 通过 |
| preview/hit-W-slow.webp | 6 | 160ms | 960ms | 通过 |
| preview/attack-E-normal.webp | 12 | 30ms | 360ms | 通过 |
| preview/attack-E-slow.webp | 12 | 120ms | 1440ms | 通过 |
| preview/attack-W-normal.webp | 12 | 30ms | 360ms | 通过 |
| preview/attack-W-slow.webp | 12 | 120ms | 1440ms | 通过 |
| preview/cast-E-normal.webp | 16 | 45ms | 720ms | 通过 |
| preview/cast-E-slow.webp | 16 | 180ms | 2880ms | 通过 |
| preview/cast-W-normal.webp | 16 | 45ms | 720ms | 通过 |
| preview/cast-W-slow.webp | 16 | 180ms | 2880ms | 通过 |

## W09新旧SHA与唯一历史链接备注

当前正式 `runtime/attack/W/09.png` 的SHA为：

`fa20e9c0d26f1cfaacda1e0fa9c761251c74a044e07d154669428a386d0e2f28`

它与当前 `records/attack/W/09.json`、manifest、视觉记录的correctedCurrentFiles和两个attack-W媒体来源索引一致。旧拒稿SHA没有继续冒充当前图。

旧导出SHA：

`f961d148a6aceffc4a46a2c39b408ed4d31e140cf5f95cb752d6b386840f5409`

旧原生SHA：

`ab8bfcc12dadaa6df198666bb696cc119b38952317f0fcf385cb5d0361459844`

旧原生来源文件名为 `exec-8c2c8f05-d517-4e8e-8e4b-db8261b898cb.png`；generation-audit将对应旧回执标为rejected_or_superseded，旧回执的output_hint也明确指向此文件。当前新稿原生来源则是 `exec-3ea85148-f638-4bd9-a7f2-8c038ed19598.png`，原生SHA为 `287416c55c89c522c19b20c3285ff520381980f9ed1125719666b8449ba425ae`，两条证据可区分。

**需整理的历史文字链接仅此一处：**

- 文件：`D:/work/image/designs/creature-combat-20261005/pets/06-xiluo/records/attack/W/09-rejected-first.json`
- 字段：`evidence.receipt`
- 当前值：`receipts/attack/W/09.json`
- 应指向已存在的旧回执：`receipts/attack/W/09-rejected-first.json`
- 正确旧回执绝对路径：`D:/work/image/designs/creature-combat-20261005/pets/06-xiluo/receipts/attack/W/09-rejected-first.json`
- 正确旧回执文件SHA：`e695c1626fe5f8b64a5e85376ecea2c001a3a8ba665ec1298eab554733e62fd7`

这是旧记录在回执另存后留下的路径关联，不需要改写旧图SHA、时间、旧实际prompt或新稿任何像素。本任务未修改该字段，交由统筹任务只修历史链接。

## 模型证据与验收界限

68张当前逐图记录均明确使用 `image_gen.imagegen` / `builtin`；configSnapshot目标为 `gpt-image-2.5-sunburst` / `max`。68条记录的submittedParameters.model、submittedParameters.quality、actualModel及actualQuality全部明确为null，并有未披露原因。未发现把目标当作实际确认版本或转为API/CLI的记录。

当前README、STATUS、MERGE_HANDOFF和qa/visual-review均诚实说明实时正常/0.25×视觉连播未确认（原窗口记录为本地file访问限制）；技术媒体解码并未冒称动态视觉通过。本次不进行播放、不改变该状态；若统筹另完成实际播放，需独立记录。

qa/technical-validation保留三条alpha>16触边警告，分别cast/W08、W09、W12；没有技术error。本任务按分工不查看图，不据该警告单独断言主体裁切或需要重画。其它视觉观察以独立视觉审查及原窗口记录为准。客户端未接入。

## 记录快照

| 文件 | SHA256 |
|---|---|
| manifest.json | `794ab6856f396ed93812fcc44562f5c5d0b766d1bcedc67850736a8fa87fdb05` |
| qa/technical-validation.json | `b968832cd37296a60a3deab164e50217702ddfc769f794f5e1fd778d7c445bf5` |
| qa/visual-review.json | `2e3da53c61db6b0d019e7b1cacbed84c1ee6a0149bf26527840a1d6eadcb2073` |
| preview/media-manifest.json | `b4193562729bf25e3c9581a75edfb57f707f3ea8bbfb4919e6fe11691d39790a` |

结论只绑定此次文件快照；后续修改图像、来源记录或媒体需重新检查受影响条目。



## 主窗口修正历史文字链接：2026-10-08T12:04:44.808137+00:00

已将records/attack/W/09-rejected-first.json的evidence.receipt从当前采用稿09.json纠正为已保留的09-rejected-first.json。旧回执SHA确认是e695c1626fe5f8b64a5e85376ecea2c001a3a8ba665ec1298eab554733e62fd7；记录附带更正时间、旧值、新值与理由，没有改写原始生成时间、参数或原生SHA。正式W09图及当前来源未变，PNG SHA仍为fa20e9c0d26f1cfaacda1e0fa9c761251c74a044e07d154669428a386d0e2f28。本项历史链接问题已解决。
