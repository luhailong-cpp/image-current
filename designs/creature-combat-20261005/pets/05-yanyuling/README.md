# 砚羽灵 · 受击、普攻、施法

2026-10-05。沿用 Image 原有暮紫猫头鹰身份，保持两翼两鸟足、右侧卷轴、左侧砚包及玉金／象牙饰物。E为斜前朝右下，W为独立绘制的真正斜后朝左上。本包不含移动动作。

## 查看

- [互动预览](preview.html)：六组同步或顺序连播，正常速度、0.25倍慢放、逐帧、浅米白／深蓝／棋盘背景。
- [正式帧与逐图索引](manifest.json)：68张1024×1024透明RGBA PNG，含帧序、时长、pivot、视觉事件、SHA与来源记录路径。
- [独立动画预览](previews/manifest.json)：每组正常／慢放APNG各一份，共12份；预览512方，正式帧保持1024方。
- [技术验收](qa/technical-validation.json) · [视觉与连播验收](qa/visual-review-final.json)。
- [完成状态](STATUS.md) · [68帧SHA清单](CHECKSUMS.sha256) · [接手说明](MERGE_HANDOFF.md)。

|动作|每向帧数|每帧时间|单向全长|E／W路径|
|---|---:|---:|---:|---|
|受击 hit|6|40ms|240ms|runtime/hit/E、runtime/hit/W|
|普攻 attack|12|30ms|360ms|runtime/attack/E、runtime/attack/W|
|施法 cast|16|45ms|720ms|runtime/cast/E、runtime/cast/W|

## 画布与接入

帧名均从01.png开始。左上画布脚点约定为[512,942]，左下pivot为[0.5,0.08]。以两足落点投影中点人工确定每方向基准，再对该方向三个动作执行同一个固定导出：1024工作画布整幅等比至840，E偏移[24,130]，W偏移[114,151]。详见[导出登记](export-registration.json)。基准来自像素目测，具有约±15工作像素的估计误差；没有逐帧依最低脚对齐，原地反冲、压身与回弹保留。

每张动作姿态均由一次独立内置AI生成或定点重绘得到，没有镜像、复制、全图平移或插值补动作。整幅缩放与固定定位仅用于导出。原生生成尺寸为1254×1254，正式输出1024×1024，不冒称原生1024或通过放大提升模型画质。

事件字段是美术阶段建议：hit第3帧、attack第7帧、cast第9／10帧及各末帧；尚未接到游戏逻辑。**本包未读取或修改客户端，游戏接入未验证。**

## 模型与来源

使用内置 `image_gen.imagegen`。本批配置目标为GPT Image2.5 Sunburst／max；实际工具无model／quality选择器，也未返回可核实版本，逐图submittedParameters.model／quality和actualModel／actualQuality均为null。详情见[官方核对与限制](MODEL_VERIFICATION.md)。

manifest每帧的`sourceRecord`指向该图的`.generation.json`；记录包含当次配置快照、实际prompt、receipt、参考图及历史SHA、原生尺寸与导出链。cast记录在`provenance/cast/<E|W>/`，hit及attack记录在正式PNG旁。`provenance`也保留重试、拒稿和连接失败的文字记录。

历史输入在后续统一导出后SHA变化时，仍保留生成当时的SHA，并用`historicalRevision`和`export-registration.json`核对前后版本，未将当前像素冒充旧输入。旧身份图和公共风格图保持只读。

## 维护

只更新检查与预览：先运行`tools/build_delivery.py --strict`，再运行`tools/build_apng.py`。这两个入口不创作或补齐动作。`register_export.py`只允许首次统一导出，防止重复缩放；重新生图需按登记中的同方向固定变换接续。

项目内仅保留正式帧、当前预览及设计／接入所需文本和脚本；拒稿、旧接触表与加工中间图按[清理记录](cleanup.json)处理，逐图模型、prompt、receipt和SHA记录保留。
