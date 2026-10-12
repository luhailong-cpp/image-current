# Git 同步说明

2026-10-08 已删除重复的 `17-spirit-scribe-actions.zip`，其 586 个条目删除前与已落盘文件逐项 SHA-256 一致。Git 保留完整的展开交付文件，克隆仓库后可直接使用；交付入口见 [DELIVERY.md](DELIVERY.md)，原打包哈希继续保存在 `package.json`。

如需重新生成 ZIP，在本角色目录使用 Python 3 运行 `python tools/package_delivery.py`；该现有脚本会生成本地 ZIP 并更新 `package.json` 中的打包记录。
