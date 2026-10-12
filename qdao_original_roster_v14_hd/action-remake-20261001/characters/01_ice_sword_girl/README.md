# 冰剑少女 · 动作成品

全套196张1024透明PNG已完成：八方向跑步128帧，东西方向受击12帧、普攻24帧、施法32帧。跑步正常速度统一1200ms/圈、16×75ms；脚尖方向及连续承重姿态已逐帧复核。

视频反馈追加修订：东向07/08/15/16、西向13–16重绘前摆小腿与靴子，减少长距离前踢和持续翘尖，补顺落地前的下降；其余188帧保留。逐图修改与来源见 [追加修订记录](review/axis-revision-selection-20261004.json)。

- [下载完整素材包](ice_sword_girl_actions_196.zip)

ZIP 在本机生成并保留，不随 Git 上传；仓库同步全部素材与打包脚本。其他电脑可在本角色目录运行 `python tools/package_actions.py` 重建素材包。

- [全动作当前交互预览](preview/all.html)
- [各动作当前帧与检查状态](manifest.json)
- [当前时长](animation-timing.json)
- [交接/进度/来源](MERGE_HANDOFF.md)
- [最新两帧一位置接地要求](review/paired-position-contact-requirement.json)

使用内置image_gen，实际型号/质量未披露；实际提示词与回执位于sources/及drafts/，各图旁generation记录可追溯。已淘汰图片只保留文字来源与哈希。

此交付为素材及离线预览；客户端尚未接入或验证。candidate/保存选定的最终PNG，交付包使用runtime/目录。
