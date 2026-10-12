# city-tower-north 原生像素工具

仅适用 `r03_c13,r03_c14,r04_c13,r04_c14`。无图像生成、AI 编辑、Git、共享 progress 更新。准备期间仅执行 `coords`、`--help` 和隔离的 `selfcheck`；真实登记、选择和装配由 root 在 owner ack 核实后使用。

从仓库任意路径运行：

```powershell
$python = 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$tool = 'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel-production-20261013\city-tower-north\tools\native_batch.py'
& $python -B $tool coords --tile r03_c13 --patch p11
& $python -B $tool register --spec 'D:\path\actual-return-spec.json'
& $python -B $tool assemble --selection 'D:\path\selection-v001.json'
& $python -B $tool guide --tile r04_c13 --patch p41 --selection 'D:\path\selection-v001.json' --include-south-current
& $python -B $tool selfcheck
```

脚本按自身位置推导仓库根；换盘后调整命令中的路径即可。默认创建时间戳和随机后缀的新版本。所有真实输出限制在本批 `versions/<version>/`；`--version` 可指定同一原生批次版本，已存在的文件永不覆盖。装配和 guide 的同名输出目录也拒绝覆盖。原始文件全部保留。拒绝大小非 **1254×1254** 的源文件，拒绝透明地表、非 PNG、非 RGB/RGBA；不自动裁切或缩放。记录内置入口 `image_gen.imagegen`，`actualModel=null`、`actualQuality=null`，未知实际型号不会标为 2.5。

实际工具回执先另存 JSON，原样保存提交 prompt，实际附图填写 references；如保存了实际 request，可一并提供并核实 prompt 和附图完全一致。登记 spec 为 JSON，相对路径以 spec 所在目录解释：

```json
{
  "tile": "r04_c13",
  "patch": "p41",
  "sourceOutputPath": "D:/actual/imagegen/returned.png",
  "prompt": "D:/this-batch/prompts/p41-v001.txt",
  "receipt": "D:/this-batch/receipts/p41-v001.json",
  "request": "D:/this-batch/requests/p41-v001.json",
  "references": [
    {"file": "D:/actual/reference.png", "role": "actual attached layout/style/continuity reference"}
  ]
}
```

`request` 可省略，其余字段必需。登记先核实所有输入，再将返回文件按字节复制到 `versions/<version>/<tile>/native/<patch>.png`，附 `.generation.json`。输出含源与 native SHA-256、实际尺寸、世界坐标、prompt、回执、附图及原始请求证据。不会修改源图。

root 手工选定后另存不可变的 selection JSON。每个 entry 的三个值直接取 `register` 输出；selection 路径可置于本批自己的版本目录。相对 record 路径以 selection 所在目录解释：

```json
{
  "schemaVersion": 1,
  "selectionVersion": "r04_c13-choice-v001",
  "tile": "r04_c13",
  "patches": {
    "p41": {
      "record": "D:/this-batch/versions/native-v001/r04_c13/native/p41.png.generation.json",
      "sha256": "SHA256_FROM_REGISTER",
      "recordSha256": "RECORD_SHA256_FROM_REGISTER"
    }
  }
}
```

装配重新核实记录、原生图、来源、prompt、回执及附图的哈希。宿主临时返回路径若已自然失效，以登记时按字节保存的 native 与记录的源 hash 核实；不会恢复原路径。16 块生成 **4096×4096 candidate** 和 **4326×4326 context**；不足 16 块仅允许完整矩形，如 p21+p22 生成 2048×1024 partial 与 2278×1254 context；不填空、不补底、不把 partial 冒充完整图。不规则或有洞 selection 会拒绝。

core 用 `[115,115,1139,1139)` 逐像素裁切。context 内部所有像素归对应 core，外圈 115 halo 仅由矩形边界 patch 提供，分区不重叠、不融合。每条内部接缝分为 1024 长度的 **100% 无缩放片**；完整 4×4 图有 24 片（竖12、横12）。预览独立命名 `DERIVATIVE-preview`，图内也标记派生与未验收；只有预览可缩小。机械完整不等于视觉验收。

guide 允许 `--selection` 重复指定本批多个 tile 的已选原生源，`--include-south-current` 使用东北区当前索引中南邻 `r05_c13/r05_c14` 的哈希锁定候选图。宏观布局经 BICUBIC 放大，仅作 GUIDE；`--layout` 仅支持内容与合同 `layoutSha256` 一致的迁移副本。所有与目标 context 相交的已知 **native core 边界像素** 按世界坐标原位无缩放覆盖并逐区验证像素哈希。已知 core 为权威；native 外圈 halo 不作为锁定区域，以免不同源 halo 互相覆盖。metadata 列出每个源图、hash、world box、source crop、paste、像素 hash。guide 不含新生图，不计原生数量，不参与最终装配。不重复提供同一 tile/core 的多个 selection；重叠权威区域会拒绝。

自测只在 `tools/selfcheck/run-.../` 写合成色彩图和诊断结果，明确标记非美术资产。保留自测文件作为验证证据。默认不生成 `__pycache__`，使用 `python -B`。
