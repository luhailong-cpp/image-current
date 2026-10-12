# 东北区制作断点：首块未通过原生接缝与布局验收

本区 **49 块任务未完成**。实际完成 36 次内置 AI 原生出图，均为 1254×1254；16 个原生核心覆盖并输出 1 张 4096×4096 候选。`usableNativeCount=0`、`complete4kCount=0`、`formalAcceptedCount=0`；其余 48 块尚未生成。

当前 [4K 候选](tiles/r06_c12.candidate.png) SHA256 为 `997d0f2d213d60610c5e92f3314da18efbc93131419ea7dd2167c6c69207ae56`。16 核心只做原生整数裁切与不透明拼接，未放大、描画或羽化。最新两次失败修复均未进入 selection。

## 实际阻断与复现证据

1. **四片交点木构不连续。** 当前 [交点](qa/r06_c12/junction_r2_c2.native-1to1.png) 的横木梁有高度阶差。额外一次内置 AI 四片联合重绘消除了中心错误，却在回贴右外边新增横梁断头：[原生失败图](qa/junction-r2c2-outer-right.png)，局部 x128、约 y730–900。修复没有同时满足中心与外边约束，因此拒用。[完整检查](qa/junction-r2c2-check.json)。
2. **右侧小鱼摊偏离布局。** 额外一次内置 AI 联修 p34/p44，实际附上精准坐标 guide、既有鱼体和三张必备参考。鱼鳞改善，但前柱仍偏右约 160–180 原生像素、柱脚偏高约 260–350 像素，下方回贴边又有材质跳变，故拒用。[视觉复核](qa/p34-p44-repair-visual-review.json)；[调用与回贴记录](qa/p34-p44-repair-check.json)。位置数值是对低分辨率布局 guide 的目视估计。
3. **其他未通过项。** p23、p24 的片内重绘边有竖直木纹/色调变化；多片石地出现规律菱形纹、偏暖强亮缝。[上半检查](qa/r06_c12/upper-core-review.json)、[下半检查](qa/r06_c12/lower-core-review.json)、[材质观察](qa/root-material-observations.json)。

前面三个联合桥接确有局部改善，不能据此把完整候选记为通过。以上是实际图片验收失败；工具调用成功，不将它描述为权限缺失或工具不可用。

## 核验范围

- 24 条内部边界、9 个四片交点和 16 个完整核心已按原尺寸检查。当前 [清单](qa/r06_c12/manifest.json) 与三份视觉 review 对应上述候选哈希。
- 前 34 次生成及当前 4K 的 [来源审计](records/provenance-final-candidate-audit.json)：16 核心像素与选源一致，26 个来源节点、929 条哈希链接通过。后两次拒用修复的 [补充审计](records/final-repair-provenance-audit.json) 无哈希错误。派生、别名、layout-only guide 不计新原生出图。
- 实际型号/质量均未披露，记录为 null；配置目标 `gpt-image-2.5-sunburst / max` 不是实际返回证据。全程内置路径，无付费 API。
- 外侧相邻 4K 与跨区边界、客户端映射、导航和 5000 人容量未验证。未写共享契约、全局配置、客户端或其他区。

## 接续位置

先解决中央四片木构的中心与四周共同连续性，再修正小鱼摊占地和石板材质，同时复核 p23/p24 插入边。新方案必须检查完整原生外接边，不能只检查修好的中央区域。新候选需要更新明确 selection、来源链和受影响 QA，通过后再按 [49 块计划](records/zone-tile-plan.json) 扩展。

本批次没有可用于游戏的正式成品。当前文件保留为未完成在制与接续证据；成品通过且当前引用完整后，再按项目规则删除拒稿、原图和加工中间图，保留逐图文字记录。不得将当前候选接入正式资源索引。


2026-10-10 resumed production update: versioned candidate r06_c12.candidate-v2.png integrates new native beam, stall and quay repairs. Root inspected all 24 seams, 9 junctions and 16 complete cores. Previous beam and stall footprint blockers are locally resolved; p43/p44 wood-versus-yellow-stone mismatch now requires northrepair44, in progress. East/south/SE native extension continues. Historical failures above describe prior candidates; none establishes current formal acceptance. Runtime/client/capacity work is outside the current request. Four tiles r03_c10,c11 and r04_c10,c11 are exclusively handed off to accelerated-jewelry-approach; owned target is45.
