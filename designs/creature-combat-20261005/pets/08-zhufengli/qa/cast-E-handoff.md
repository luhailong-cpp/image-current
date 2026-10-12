# cast E 交接

16 张独立内置 image_gen 单帧已落盘 runtime/cast/E/01.png 至 16.png，每帧45ms，共720ms；未做移动、镜像、复制、整图平移或帧间插值。导出只作原生整画布缩为1024×1024 RGBA。全部16张尺寸/alpha通过，SHA各不相同。

已实际查看每次生成图及最终4×4导出全帧接触表 qa/cast-E-contact.png。方向保持E斜前，四足与单尾双玉珠未改变，披肩保持叶片衣饰。01–04下沉、05–08聚气、09–11释放、12–16回收。09与10初版风叶在右缘被截，已AI定点缩小并保留拒稿文字证据，最终风叶完整入画。所有帧实体alpha≥128边界均不触画边；个别图最外缘有1–2/255的极低alpha像素，详见qa/cast-E-checks.json。

逐图prompts、真实request、receipts与.generation.json齐全。顶层file/sha256/generatedAt/prompt/evidence.receipt/configSnapshot/submittedParameters齐备；configured为gpt-image-2.5-sunburst/max，submitted模型质量与actualModel/actualQuality均null。

09/10编辑输入引用了当时的旧runtime路径；已用reference.atSubmissionSHA256和historicReceipt锁定历史输入SHA，不能用当前同路径成品SHA回填。旧版图未另存备份，仅保留文字记录。内置工具产生的宿主原生PNG路径与SHA列于receipts，可在根代理完成全部引用与交付检查后按素材保留规则清理；跨窗口身份/画法参考不可删。

正常/0.25慢放连播由根代理汇总六组预览后实际检查，本子任务报告如实为pending parent preview；静态全帧检查不冒充动态验收。未接入客户端。
