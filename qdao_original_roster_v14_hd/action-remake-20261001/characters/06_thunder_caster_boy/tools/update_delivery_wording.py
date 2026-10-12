"""Retired one-shot migration; retained below only as historical text."""
raise SystemExit('该旧迁移已退役；请运行build_delivery.py，正常跑步1200ms/75ms。')
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'tools/build_delivery.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace('先复核已有E/S完整方向的承重、蹬地、短暂腾空，再推广其余方向；720仅试播，不等于最终采用','八方向逐组复核承重、蹬地、短暂腾空与肩肘反向摆臂；720仅试播，不等于最终采用')
s=s.replace('当前为制作中候选帧包，尚未完成完整196帧/动态验收。不得整包覆盖另一电脑资源。','当前为制作中候选帧包。生成/导出数量见下表，完整美术动态与客户端验收另行记录；合并时逐文件比较另一电脑资源。')
s=s.replace('E/S完整帧组仍为候选。','所有八方向帧组仍按各自复核状态交接。')
s=s.replace('先修已有完整方向，再继续缺失方向。','逐方向相位、手脚修正与未解决项见review中的对应记录。')
s=s.replace('完整序列才生成WebP连播，缺槽为空。','完整序列才生成WebP连播，缺槽为空。脚向/握持逐动作复核见review，自动播放证据不等于美术通过。')
p.write_text(s,encoding='utf-8')
print('delivery wording refreshed')
