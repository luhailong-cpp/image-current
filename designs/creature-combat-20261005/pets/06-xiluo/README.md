# 汐螺 · 受击、普攻、施法

本包沿用 Image 原有珊瑚杏色蟹灵汐螺：青瓷云纹螺壳、象牙薄绢、桂花铃、红结与玉金关节饰。只有原地战斗动作，没有移动动画。

## 成品与预览

正式素材在 [runtime](runtime/)：E 斜前朝右下，W 独立真斜后朝左上，共 68 张 1024×1024 RGBA PNG。

|动作|E|W|单帧|总时长/方向|事件帧|
|---|---:|---:|---:|---:|---:|
|受击 hit|6|6|40ms|240ms|02 damage|
|普攻 attack|12|12|30ms|360ms|07 attack_hit|
|施法 cast|16|16|45ms|720ms|10 cast_release|

- [六组交互预览](preview.html)：正常、0.25×、暂停、逐帧、深浅底、独立组选择。用用户自己的本地浏览器打开；页面直接引用相对 PNG。
- [独立动画文件目录](preview/)：每组 normal/slow 两个透明 WebP，512×512，仅供播放预览。没有合成新姿态或插值，PNG 是正式交付。
- [全帧清单 manifest](manifest.json)：帧时、事件、pivot、SHA、来源与审阅字段。
- [技术检查](qa/technical-validation.json) · [媒体帧时检查](preview/media-manifest.json) · [视觉检查](qa/visual-review.json)。

## 来源与版本

每帧均由内置 image_gen 独立生成/编辑。原生为 1254×1254，正式为1024×1024；每向跨动作采用相同整画布缩放，E 固定偏移 [0,28]、W [0,-13]，没有逐帧脚底对齐、镜像、复制、平移造帧或插值。左下 pivot [0.5,0.08]、顶部原点锚点 [512,942] 是约定的加载锚点；动作内允许原地反冲、压低和回弹。

目标为本批配置 GPT Image 2.5 / max。内置工具没有 model/quality 选择器且未披露返回版本，因此每图 submittedParameters.model、quality、actualModel、actualQuality 均为 null，不能据提示词或公告宣称实际锁定。

图片到来源的映射：

1. `runtime/<action>/<E|W>/<NN>.png` 对应 `records/<action>/<E|W>/<NN>.json`。
2. 记录中的 prompt 和 evidence.receipt 指向实际提示词及调用返回摘要；定点修订单独保留旧稿文字证据。
3. [generation-audit.json](generation-audit.json) 索引全部成功图与无图失败调用，包含拒稿原生 SHA。
4. [references.json](references.json) 记录旧 E/W 身份与风格图的当前 SHA，未知历史版本不按当前目标回填。
5. 本包加工图清理与外部缓存状态见 [cleanup.json](cleanup.json)。成品 PNG 与当前必需设计/来源文字保留；宿主原生缓存不在本任务唯一可写目录内，未改动且不作为交付或游戏运行依赖。

## 检查范围

已实际逐帧查看身份、E/W方向、双钳连接、六步足支撑与遮挡、薄绢及收势；独立复核报告位于 qa。对发现的普攻闭钳分界、后向回收阶段和施法薄绢边界问题进行定点修订，最终结论以视觉检查记录为准。

内置浏览器拒绝 file 本地页面访问；未绕过安全策略。六组动画媒体已按实际帧时导出并解码检查帧数/时长，但本会话没有完成正常速度和0.25×实时连播的视觉确认。逐帧序列审阅不等同实时动态通过。独立绘制仍有轻微壳体/纹理变化，cast E 收势相对起势壳顶约21px差列入观察记录，不能冒称像素级待机无缝。

未读取或接入客户端，未做游戏内加载、战斗事件或混合动画验收，也未操作 Git。

## 复验

在本目录执行 `python verify_delivery.py --contact-sheets` 重建 manifest/SHA/尺寸/alpha/来源引用检查；执行 `python build_media.py` 由正式PNG重建12个动画预览。两者不生成新动作。源码和历史原生的可用状态分别记录，已按保留规则删除的历史原生不作为游戏运行依赖。

完整交接见 [MERGE_HANDOFF.md](MERGE_HANDOFF.md)；当前完成状态见 [STATUS.md](STATUS.md)。
