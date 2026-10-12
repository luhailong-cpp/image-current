本批机械生产工具，不调用生图 API。仅写本批目录，所有文件必须使用新版本；不使用 latest/glob 自动选片。启动 Python 必须带 `-B`，工具也关闭 bytecode，避免共享 `__pycache__`。

PowerShell 环境变量示例：

```powershell
$taskPython = 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$taskTool = 'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel-production-20261013\island-west-residences\tools\batch_pipeline.py'
```

准备一个实际坐标（将南邻路径替换为 anchors 中对应的修订来源；**不是**可直接复制运行的占位原画）：

```powershell
& $taskPython -B $taskTool prepare --tile r02_c02 --subrow 4 --subcol 1 --attempt 1 --south '实际1254南邻PNG绝对路径' --south-record '实际同版本坐标证据JSON绝对路径'
```

可加 `--north/--south/--west/--east` 和各自 `--SIDE-record`。`--left/right` 使用 `--west/east`。相邻图必须实测1254×1254 PNG，坐标为目标1254 globalBox沿所指方向移动1024像素；不接受任意裁图冒充相邻坐标。自动查找对应 `image.png.derivation.json`、`image.derivation.json`、`../guides/STEM.input.json`。坐标证据顶层 `globalBox`、`globalNativeBox` 或 `geometry.globalNativeBox`。

生成准备文件：`guides/STEM.input.json`、`guides/STEM.references.json`、`guides/STEM.layout-with-native.png`、`prompts/STEM.txt`，有邻图时再保存原尺寸横向contact。最多5张提交参考：guide、合同地图近景、根邮件、根组队、邻图contact。邻图230px重叠原尺寸贴入guide；corner按north/south/west/east后写者保留，只记录机制，不宣称视觉通过。概览仅为布局guide，边缘采用重复填充，无黑色占位，禁止作为正式像素。可用 `--prompt-file` 复制实际自定义提示词；准备后不要改已存prompt或参考，否则ingest拒收。`--no-neighbor-contact` 可只提交4张，但guide仍保留精确邻边。

当前授权由根 AGENTS 与 split 的 `allocated_root_reserved` 决定，核实六块、指定 worker 与本批输出目录。不再要求历史 owner 回执，`ownerAcknowledged=false` 如实保留。准备文件不构成生图调用。只读授权检查：

```powershell
& $taskPython -B $taskTool gate
```

实际生图前保存独立的新调用前记录，检查本坐标已有原图、当前原区选源/在途状态、输入与合同哈希；结果须 `ready=true`。旧 split 哈希变化单列授权更新，不算图片漂移。当前来源总索引若只改了其他坐标，仍须相关锚点的选源路径/哈希完全相同才能复用。真实冲突只暂停相应坐标，非冲突片继续。

```powershell
& $taskPython -B $taskTool precall --stem r02_c02_s04_01_a02 --retry-reason 'a01 courtyard hallucination; raw preserved and rejected by visual QA'
```

`--retry-reason` 仅在本批该坐标已有其他原图时必需；同一 attempt 已有图时禁止再生成。调用前记录写入 `precall/STEM.UTC.json`。不扫描历史版本，不推断最大 attempt 为选源。

对已看过根风格且相邻原图足以延续画法的局部地图，可用 `prepare --geometry-references-only --prompt-file '实际定制提示词路径'`，只提交 guide 与可选 adjacent contact，不提交地图近景/邮件/组队风格图，避免风格参考中无关建筑污染局部布局。此模式必须提供与实际引用数量对应的定制提示词。原图/旧提示词不改写，返修使用新 attempt。

实际生图使用 `.input.json` 中 `prompt.path` 内容及 `imageGenReferencedImagePaths`，`transparent_background=false`。生图调用不在本工具中。保存实际未改工具结果JSON（保留完整返回内容，不用手填“成功”代替），然后入库：

```powershell
& $taskPython -B $taskTool ingest --stem r02_c02_s04_01_a01 --raw '实际工具原图绝对路径' --tool-result '实际工具返回JSON绝对路径'
```

可用 `--generated-at` 记录真实生成 UTC 时间；不提供则保持 null，不用入库时间代替。`--precall-record '实际ready记录路径'` 将同 attempt 的调用前证据钉入 generation/receipt。入库重新检查当前正式划拨和 prepared 输入/合同 hash；字节复制真实图到 `native/STEM.png`，保存 `.png.generation.json`、实际 tool JSON 副本与明确标注为 mechanical wrapper 的 receipt。不修改/放大真实输出；若实际尺寸、格式或 alpha 不合格，保留 raw 并标 `nativeGeometryEligible=false`，不得装配。参考或邻边证据 hash 变化时仍保留真实 raw，标 `requiresReferenceRecheck=true` 并列差异，装配器拒绝此状态。不从目标偏好回填实际型号，仅采集返回中明确的 actualModel/actual_model 等字段及 JSON 路径；未返回则 null/“未返回”。

拼接必须提供batch-local版本化selection JSON，显式4×4、每个path和generationRecord正确对应同坐标，可用sha256钉住原图。以下是**schema示例片段，不能直接装配**；实际patchMatrix必须4行×4列全部真实图，不能省略或补占位：

```json
{
  "schemaVersion": 1,
  "tileId": "r02_c02",
  "nativePixels": 1254,
  "corePixels": 1024,
  "haloPixels": 115,
  "patchMatrix": [
    [
      {"path": "../native/r02_c02_s01_01_a01.png", "generationRecord": "../native/r02_c02_s01_01_a01.png.generation.json", "sha256": "填写实测64位sha256"}
    ]
  ]
}
```

```powershell
& $taskPython -B $taskTool assemble --manifest 'batch内实际4x4版本化selection.json绝对路径' --output 'tiles/r02_c02_candidate-v1_4096.png'
```

机械装配沿用已审原脚本：230px重叠中的最小误差binary源选择，原像素不变形、不调色、不羽化；保存4096候选、每像素source_id的NPZ、来源hash/贡献、33个100%接缝/交汇裁片及单独标注preview。自动数值来源通过不等于视觉或全图验收。root须继续100%视觉检查、邻边复核和独立acceptance记录。原区/shared progress/selection保持只读。
