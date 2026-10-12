# 八仙岛已有素材独立收尾报告

本批已完成已有素材的来源核对、去重清单、原像素局部拼接及未验收接缝检查。全图196坐标的冻结基线为54张完整覆盖候选，其中53张位于当前采用清单，另1张r12_c13为完整待修未采用候选；10坐标部分覆盖，132坐标无选用核心。完整覆盖未等同画面通过，正式验收仍为0。

953个1024核心已有选择来源，3136个目标核心中缺2183个。加速区r01 r02 c13 c14只记一次，东北主区目标为45，加速区为4；四象限合计196。详细196行见[覆盖清单](coverage-inventory-v01.json)，逐坐标缺块见[缺块清单](missing-tiles-v01.json)。

生产在检查期间继续。冻结基线后的东南r13_c11选择已从12增至14核心；r14_c12另有p33和p43原生图落盘，但工作与选用字段未同步，未擅自提高整块完成数。东南5个元数据JSON变化，旧全区快照标过期；755张旧PNG未变，两组拼接直接来源仍有效。东北海岸选择文件亦变化，根审计标记其选择元数据过期；已有成图像素保持对应hash。后续版本必须按[来源变化记录](southeast-finalize-v01/live-delta.json)重新选择和验边。

跨区已实查西北r07_c03与西南r08_c03的4096共享边，4个1024段轮廓和石缝连续。右上r07_c04仍缺，四交叉点不能验收。东北海岸与主区两条南北接边8张旧裁片与当前像素完全相等，可复用。主地图中线其余边与中央四交叉仍缺邻图，列表见[跨区边界](cross-zone-edges-v01.json)。

需修位置已写入[接缝待修清单](seam-repair-queue-v01.json)：西北红墙脚线、雕座、花叶和屋瓦断口；西南竹院石缝、金木框保留带和矮墙高度；东北海水x53248约y7900至8050直线材质带、r03_c10石面直带；东南r12_c13木地板x1024 y2167及帆桁x3072 y3730小错接。材质待核与邻图缺失分别保留，不用模糊、程序补画或插值掩盖。

以下局部图保持8192乘8192原像素，均由四张4096成图机械拼接。只作为列明版本的局部交付，外围和全图验收状态见各区域报告：

- [西北 r04 r05 c03 c04](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/northwest-audit-v01/middle_r04-r05_c03-c04_native8192_internal-pass_perimeter-pending_v01.png)：共享内边通过 外围待验。
- [西南 r10 r11 c03 c04](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/southwest-audit-v01/native-assemblies/current-r10-r11-c03-c04-native-8192-v01.png)：最新来源局部拼接 以区域报告限制为准。
- [东北 r03 r04 c11 c12](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/root-audit-v01/g03-main-r03-r04-c11-c12/native-hard-join-8192.png)：本批共享边和交叉点通过 外围待验。
- [东北 r04 r05 c13 c14](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/root-audit-v01/g04-main-r04-r05-c13-c14/native-hard-join-8192.png)：本批共享边和交叉点通过 外围待验。
- [东南 r09 r10 c12 c13](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/southeast-audit-v01/g01-r09-r10-c12-c13/native-hard-assembly-8192x8192-v01.png)：共享边局部通过 外围待验。

[全部局部图hash清单](local-deliverables-v01.json)记录原像素来源。预览文件均标明缩略用途，不能替代4K图块。

本批来源审计由[西北](northwest-audit-v01/review.md)、[西南](southwest-audit-v01/review.md)、[东北及跨区](root-audit-v01/review.md)、[东南收尾](southeast-finalize-v01/review.md)给出尺寸、hash、像素回放和检查证据。未修改原制作目录、progress、共享索引、AGENTS或Git，未删除或恢复素材。新规则为免费现有入口2.5优先、不可用允许内置2.0，本独立检查未调用生图，已有图实际型号仍按原回执记录。
