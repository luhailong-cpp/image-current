# 灵玥交付检查工具

本工具只读取本任务真实帧与来源文字，写出 manifest、技术报告和离线预览。它不生成、改画、搬动、对齐、裁切、缩放或补出任何图片。预览是检查工具，不是游戏 UI 或客户端接入成果。

## 运行

已核对当前机器内置 Python 3.12.14、Pillow 12.3.0 可用。系统 `python` / `py` 不可用时，用以下 PowerShell 命令；换电脑后按宿主依赖工具返回的 Python 路径更新可执行文件路径。

```powershell
& 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\work\image\designs\creature-combat-20261005\pets\legacy-ling-yue\tools\build_delivery.py'
```

默认写本任务根目录的 `manifest.json`、`technical-validation.json` 和 `preview.html`。帧不齐时也会生成反映实际缺失的预览和报告，退出码 **1**；只有全部 68 帧技术条件满足时退出码 **0**。这两个退出码都不表示美术、解剖、方向、动态或客户端验收通过。其他执行错误为异常失败，不能当成通过。

只读检查追加 `--check-only`。JSON 输出只能写在本任务目录；预览只写任务根 `preview.html`。工具开发时的初始空资产报告已经删除，不作为正式交付；正式报告请在真实帧落盘后运行生成。

## 检查范围

- `runtime/{hit|attack|cast}/{E|W}/NN.png`；每组从 01 起，分别 6 / 12 / 16 帧，共 68 帧。额外 runtime PNG 会报错。
- 每帧实际 PNG 格式、1024×1024、RGBA、透明像素和非空 alpha；边缘接触作为人工裁切检查提示。
- 文件 SHA256、可见像素 SHA256 和去除透明外边后可见内容 SHA256。后两者会消除完全透明像素的隐藏 RGB 差异，并可识别完全相同内容只整体平移的帧。不是近似姿态、插值或独立创作的自动判定器。
- 每帧旁 `NN.png.generation.json` 的必填信息、当前 PNG SHA 和尺寸、时区时间、配置快照、实际参数、型号/质量未知原因，以及实际保留的 prompt / receipt / 参考文件。清单同时计算 sidecar、prompt 和 receipt 的当前 SHA。参考项已写 SHA 时会核对；只读取 Image 仓库内引用，不读取客户端或兄弟目录。
- 所有帧都记录合同 pivot `[0.5,0.08]`（左下原点）及顶部整数锚点 `[512,942]`。脚点整数是约定取整；工具不寻找最低脚，不执行逐帧重定位。两方向各采用固定全画布归一化：原生1254×1254（也接受1024×1024）整体缩放到980×980，放在1024透明画布的 `[22,0]`，不按各帧最低脚点调整。工具核对 sidecar 的 `operation` 是否匹配；`verifiedAgainstNativeSources=false` 表示未重建原生像素来证明导出一致。

manifest 的 `event` 为 `null`，不猜测客户端事件。`visualStatus` 为 `unreviewed_by_tool`，`releaseReady` 固定为 `false`；人工检查结论请保存在独立审阅文件和交付 README 中，避免重跑脚本覆盖结论。

## 逐图生成记录

`file` 可为任务根相对路径、图片旁文件名或 Image 内绝对路径。`width/height` 表示当前 PNG 尺寸，原生输出尺寸另记 `nativeWidth/nativeHeight`。必须保留的字段与项目 `docs/IMAGE_MODEL_POLICY.md` 一致：

```json
{
  "file": "runtime/hit/E/01.png",
  "sha256": "真实当前PNG的SHA256",
  "generatedAt": "2026-10-05T12:00:00-04:00",
  "width": 1024,
  "height": 1024,
  "format": "PNG",
  "tool": "image_gen.imagegen",
  "route": "builtin",
  "configSnapshot": {
    "model": "复制当次目标配置",
    "quality": "复制当次目标配置",
    "builtin_product": "复制当次目标配置",
    "verified_on": "复制当次目标配置",
    "sources": {"release": "复制当次依据", "model": "复制当次依据"}
  },
  "submittedParameters": {"model": null, "quality": null},
  "actualModel": null,
  "actualQuality": null,
  "unverifiedReason": "宿主管理，工具未披露型号和质量参数/无可核实返回元数据",
  "evidence": {"receipt": "source/hit-E-01.receipt.json"},
  "prompt": "source/hit-E-01.prompt.txt",
  "operation": {"type": "sourceNormalizedTo980Square", "sourceSize": [1254,1254], "resize": [980,980], "offset": [22,0], "canvas": [1024,1024], "perFrameAlignment": false, "resample": "LANCZOS"},
  "derivedFrom": {"path": "source/hit-E-01.png", "sha256": "真实原生PNG的SHA256", "generationRecord": "source/hit-E-01.png.generation.json"},
  "references": [
    {"path": "D:/work/image/qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png", "purpose": "原有灵玥身份"},
    {"path": "D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png", "purpose": "确认画法和材质"}
  ]
}
```

以上仅是结构示例，不能拿示例时间或占位值建立真实来源记录。`operation.sourceSize` 必须按当次原生图片填写1254或1024，不能照抄。receipt 必须保留实际工具原始输出，prompt 必须是实际调用文本；如有结果 ID、原生尺寸、输出 SHA、C2PA 等，应同时原样留存。`evidence` 支持路径字符串、列表或嵌套对象，路径采用 `.json/.txt/.log/.receipt` 文件。脚本验证文件存在，不能替人判定记录内容为真实证据。若记录了非空 actualModel/actualQuality，会提醒人工核对对应 receipt 字段。

派生输出必须另记 `derivedFrom`（对象或对象列表，字段 `path/sha256/generationRecord`）和 `operation`，关联原生图片 SHA 与原始生成记录。项目允许清理的原图删除后，在对应 `derivedFrom` 条目另记 `removed: true` 与 `cleanupRecord` 文本路径，保留来源文字及清理记录，不因删除图片而删除 receipt。仍在磁盘的源图会核对 SHA；已删除的图片不能再做像素复验。此工具不会清理任何素材。

## 预览检查

直接打开任务根 `preview.html`，不需服务端或联网。六组按 40 / 30 / 45 ms 原时长播放，提供全局和每组 1×、0.25×、播放/暂停、上一帧/下一帧、逐帧滑条、透明棋盘/深色/白色背景、合同锚点开关。初始暂停；每组所有真实 PNG 加载并 `decode()` 成功才解锁该组播放，六组全部成功才解锁全部播放。缺图或加载/解码错误显示明确提示，不跳帧掩盖缺失。图片 URL 带当前文件 SHA，修图后刷新不会复用旧版缓存。

预览用一个固定 1024×1024 Canvas 同步清除并绘制完整当前帧，不通过隐藏/显示 img 切换，避免未完成解码时闪空白。每次屏幕刷新最多前进一帧，负载过高时会变慢，不主动跳过中间帧赶进度。连续性检查需要正常速度与慢速，逐帧解剖则用滑条和下一帧。当前文件更新后需重新运行脚本并刷新预览。页内显示技术错误、检查时间，以及美术/动态/客户端未由工具验收的状态。

`tools/prepare_handoff.py` 只写 68 张图的 SOURCE_INDEX 和清理候选计划。它核对当前 PNG SHA 与 manifest/sidecar 一致，只在 `receipts/` 选择旧接触表/预览图；不删除图片、不修改生成记录，不读取客户端或兄弟目录。最终清理必须再次核实整个计划的绝对路径、SHA、正式帧未变和引用关系；保留实际清理记录。

本次清理已完成，`cleanup-plan.json` 与 `cleanup-record.json` 是执行证据，不要重跑 prepare_handoff 覆盖已执行计划。`tools/verify_handoff.py` 核对最终审阅绑定的 68 张 PNG 和 68 份 sidecar SHA、核心文档链接以及清理记录/磁盘状态，写 `delivery-validation.json`；通过也仅代表本地素材交付和证据一致，不代表客户端接入。
