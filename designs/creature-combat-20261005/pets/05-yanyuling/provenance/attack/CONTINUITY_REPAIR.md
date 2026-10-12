# E07／E11定点重绘完成记录

日期：2026-10-05（America/New_York）。只替换 `runtime/attack/E/07.png` 和 `11.png` 及其逐图记录，没有改其它runtime帧，没有执行统一锚点变换。

- E07当前为attempt03：真实内置AI单帧重绘，实际附原E身份、原W身份、主要画法图、E06、E08共5图。以E06的双足及翼展为基准保持峰值，头喙略进一步前探。实看新07与06／08并排，旧稿双足偏左及提前收翼现象已消除；两翼、两足、卷轴／砚包侧别保持。右侧羽尖仍较近边界，但原生右边无alpha≥128主体，1024主体范围[11,189,1022,990]，不透明主体未被裁切；统一方向导出时仍需给羽尖留出空间。
- E11当前为attempt02：实际附原E身份、原W身份、主要画法图、E10、E12共5图。实看新11与10／12并排，已是直立、闭喙、收翼状态，没有旧稿的二次低头、张喙及再次前倾。保留细微饰物回摆。

两张均为原生1254×1254透明RGBA，整画布等比导出1024×1024。没有局部拼贴、后期脚位平移、单帧重新对齐、镜像、复制或插值。actualModel／actualQuality以及submitted model／quality均为null，配置目标仍是gpt-image-2.5-sunburst/max。

## 来源及旧稿

E07上个修稿的文字保存为`E/07.attempt02.prompt.txt`、`.receipt.json`、`.generation.json`；11首稿为`E/11.attempt01.*`。未建立拒稿PNG备份。当前新稿对应`E/07.attempt03.*`和`E/11.attempt02.*`，同名当前prompt／receipt索引同步更新。PNG同名generation记录包含全部5张参考的SHA。

本次并排检查图：`continuity-repair-06-08-10-12.png`；对应sources.json保留读取SHA。本子任务目录的旧接触表已从当前帧重建覆盖，避免继续显示被替换旧稿；主线程qa接触表及manifest仍需统一重建。

## 检查

重新运行`validate_assigned.py`：18/18尺寸和alpha通过、18不同SHA、所有prompt／receipt／参考哈希和导出哈希一致。两张修稿逐张及相邻三帧静态检查通过本次指定修正点；完整30ms及0.25慢放连播仍由主线程统一检查，没有宣称客户端接入通过。

当前SHA：
- E07：`ba04309458b36cca38c23f5352ae1e58e9cd5cf9d7ac9b5523f075ae48120a31`
- E11：`a9e57a27856e4421ef0aa5d8b256b9ae29e378c7c02bd14b2616dc55d6007cc7`

