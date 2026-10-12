# 云啾啾素材接入交接

本只目录：`designs/creature-combat-20261005/pets/legacy-yun-jiu-jiu`。正式资源读取manifest列出的68张runtime PNG；不按source目录扫描生成游戏动画。原静态身份未被替换，W为新绘的真实斜背设计。

方向：E斜正面朝右下，W斜背朝左上。所有图1024×1024、直通RGBA；pivot左下[0.5,0.08]、顶左像素[512,942]，同方向全部动作使用相同源坐标和导出变换。云垫随帧保留，不另加第二个云垫。

|动画|帧数/向|帧间隔|建议事件|
|---|---:|---:|---|
|hit|6|40ms|第2帧hit_contact|
|attack|12|30ms|第7帧attack_strike|
|cast|16|45ms|第11帧cast_release|

以上事件只是美术阶段标记；实际伤害/技能结算由客户端或服务端战斗逻辑决定。三动作按一次性播放后返回既定待机处理，本包没有走路、跑步或新的待机循环。

技术结果见validation.json；逐帧与正常/慢放浏览器检查见qa/final-review.json。普攻仍有轻微云垫起伏及峰值透视变化，需在实际显示尺寸和战斗场景中复核；本包不代替客户端验收。浏览器支持全部或单组预览，30ms显示节奏受屏幕刷新率影响。

逐图生成与编辑证据保存在records；runtime旁的generation.json关联原生SHA、生成记录和统一导出操作。model/quality实际未知，禁止按配置目标重标成已确认Sunburst/max。原生候选已按项目保留规则清理，历史路径见sourceRetention/referenceRetentionAudit；2张方向设计与既有Image身份/风格参考继续保留。

本次没有Git提交、推送或分支变更。合并者只接收本只目录；本任务没有读取客户端、兄弟仓库或其它电脑素材。后续核验命令和脚本在tools/README.md，常规复核用verify。
