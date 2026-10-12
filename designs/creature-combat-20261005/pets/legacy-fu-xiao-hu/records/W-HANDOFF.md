# 符小虎 W 子任务交接

本子任务完成真正 W 左上斜背设计参考，以及受击 6 帧、施法 16 帧，共 22 张独立生成的 1024×1024 RGBA PNG。W 普攻 12 帧由根任务负责，本文件不声称其完成或验收。

- 身份/相机参考：`design/W-reference.png`（实际原生 1254×1254，持续引用的设计文件）。
- 正式帧：`runtime/hit/W/01.png` 至 `06.png`（40ms）；`runtime/cast/W/01.png` 至 `16.png`（45ms）。
- 每帧 PNG 旁有 generation.json；实际 prompt、receipt、失败和修正前文字证据在 records/W-*。
- 技术与静态检查：`records/W-QA/technical.json`（统一脚点校准前历史检查）、`records/W-visual-review.json`。当前全帧图见 `preview/hit-W-frames.jpg` 与 `preview/cast-W-frames.jpg`。
- 统一检查页：`preview/index.html`；独立页 `preview/hit-W.html`、`preview/cast-W.html`，含正常速度、0.25 慢速、暂停和逐帧。

全部使用内置 image_gen。目标沿用本批 GPT Image 2.5/max 配置；工具未开放 model/quality 参数，实际型号与质量均记 null/未确认。每张以独立AI调用生成，无复制、镜像、平移补帧或插值。

本子任务导出只有固定整画布 1254→1024 Lanczos 缩放，未逐帧重排锚点。根任务已计划全部 W 统一 y=-4、E 统一 y=-15；应由根任务统一更新 operation、SHA、manifest 和技术报告。W 帧现在可交给根任务处理，本子任务不再改像素。

已实际逐张看全部生成返回图与最终全帧对照。hit03意外漫画标记已AI删除；cast08实体圆盘已AI改成透明能量球；cast10释放光效和尾巴完整；cast11增加了伸爪后的早期回收。技术检查22帧通过尺寸、RGBA、真透明、SHA一致、无重复和无alpha≥128触边。

**动态检查由根任务接续完成。** 本子任务尝试 cua 返回“Browser is not available: iab”且浏览器清单为空，未自行完成连播目视验收。根任务随后报告已通过同窗口 cua 运行统一预览的六组 1×/0.25×；以根任务最终 QA 记录为准。未接入客户端。

素材保留：本宠目录未建立原生中间副本或拒稿图片备份，只有当前W设计参考、最终runtime、QA预览和文字证据。生成工具默认宿主缓存位于本宠目录外，本子任务遵守写入边界未删除它们。


重复QA清理：已确认统一 preview 目录含W两组全帧图、正常/慢速动画与独立HTML，移除 records/W-QA 下重复两张PNG与index.html；保留technical.json并明确它是统一偏移前历史检查。清理记录见 records/W-qa-cleanup.json。
