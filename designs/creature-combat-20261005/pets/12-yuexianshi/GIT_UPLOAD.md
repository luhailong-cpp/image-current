# Git 上传与本地交付快照

2026-10-08 核对：`yuexianshi-combat-delivery.zip` 为 126,589,065 字节（约 120.72 MiB），超过普通 Git 单文件上传限制。沿用仓库对派生交付 ZIP 的处理方式，根 `.gitignore` 仅精确忽略此文件，并在本地保留它。当前素材、设计与接入文档、打包脚本和逐图来源记录继续纳入 Git，不迁移 LFS。

此 ZIP 是修复前后的旧交付快照，不能作为当前素材已验收的证明，也不能声称由当前目录逐字节重建。当前验收结论以 `README.md`、`VERIFICATION.md` 和现行修复记录为准；本次只处理版本保存与上传，不改变美术验收状态。

逐文件核对 441 个归档条目，413 个与同路径磁盘文件完全一致，28 个与修复中的当前版本不同：

- 13 张旧普攻 PNG（E/01 与 W/01–12）及旧 W 普攻联系表，字节已保存在上传前 HEAD `8de8c7c31b4523ff5cd3b2c76ed99320e3dae6be` 的同路径历史中；当前正式目录保留修复版。
- 13 份旧逐图生成记录，已有逐字节相同的 `records/attack-E/01.pre-guardfix-20261008.generation.json` 和 `records/attack-W/01.pre-guardfix-20261008.generation.json` 至 `12.pre-guardfix-20261008.generation.json`，随当前改动上传。
- 旧 `build_delivery.py` 的全部功能保留于当前升级版。为便于逐字节追溯，将 ZIP 内旧脚本文本另存于 `records/delivery-archive-20261008/build_delivery.py.txt`；当前运行仍使用根目录脚本。

ZIP SHA-256：`e88725c41139f6c1bd288327423a27635773e99ed33ded6ddeee46521b063c01`。

归档旧脚本文本 SHA-256：`f2536f064ea818ff2ea112af30d149b5971501263bbdfc5a41eeedac12be1a6f`。

`package_delivery.py` 用于另行制作当前目录的交付包；本次没有运行它或覆盖现存 ZIP。
