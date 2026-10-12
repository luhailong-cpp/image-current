# 葫团团检查工具

`build_preview.py` 只读正式帧和来源记录，不生成、补帧、复制、位移或插值动画。联系表只作固定完整画布缩放。工具依据 TASK、COMBAT_SPEC、POSES 的六组合同：hit 6×40ms，attack 12×30ms，cast 16×45ms，两向共 68 张。

在 PowerShell 执行（不要求当前目录）：

```powershell
$petPython = 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$petCheck = 'D:\work\image\designs\creature-combat-20261005\pets\legacy-hu-tuan-tuan\tools\build_preview.py'
& $petPython $petCheck --check-only
& $petPython $petCheck
```

第一条命令完全不写文件；第二条生成 `preview/index.html`、六张 `contact-动作-方向.png` 及其派生记录、`checksums.sha256`、`manifest-candidate.json`。缺帧时仍生成可检查的预览，缺失格明确标注 MISSING，不补画。存在任何技术错误时退出码为 1；全部通过为 0。主任务负责人可显式指定 `--manifest-out manifest.json` 写根 manifest，否则只出 preview 内候选。

浏览器打开 `preview/index.html` 即可，无需服务端或联网。六组可独立或一起播放，支持正常时长、0.25 慢放和按钮/滑块逐帧。浏览器后台时自动暂停；超出计时容差时提示延迟。真实画面审核仍须实际观看每帧、正常及慢速六组并记录，技术检查不会替代审核。

逐图来源记录优先名称为 `01.png.generation.json`，也兼容 `01.generation.json`，两种同时存在视为歧义。原生生成记录检查政策要求的字段、时区、配置快照、SHA、输入引用、未知模型说明。裁切缩放派生记录使用 `derivedFrom`（对象或数组，必须有 `file/path`、`sha256`、`generationRecord`）及 `operation`；递归检查原始文字记录。已经按保留规则删掉的源图片，在 `derivedFrom` 对象中注明 `deleted: true`，保留 SHA 和原生成记录，工具会提示而不当作缺图错误。有效参考必须在 D:/work/image 内；工具不会读取兄弟仓库、客户端或其他电脑。

预览中所有图共用正式1024画布及 [512,942] 标记，未进行逐帧包围盒定位；可切换棋盘格、深色和浅色背景检查透明边缘。技术检查不会自行得出视觉结论：只有 `records/final-visual-review.json` 中68张SHA与当前正式图全部匹配时，manifest和命令输出才导入其真实逐帧／播放检查范围；缺失或不匹配时保持 `pending-human-review`。`clientIntegration` 仍为 `not-performed`。
