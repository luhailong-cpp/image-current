from pathlib import Path
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl")
note="NW早期部分调用在宿主会话中断后按本地文件和姿态关联恢复，对应新选帧05/07/08/11；调用与回执的对应关系仍注明推断、未确认，详见provenance/grounding-pairs-E-NW.json及逐图记录。配置目标未冒充实际模型/质量。"
p=R/"tools/build_delivery.py";s=p.read_text(encoding="utf-8")
needle='"另一电脑未提交内容未获取。合并时按完整角色ID和SHA对比；本机没有切分支、暂存、提交、推送或覆盖客户端。"'
assert needle in s
s=s.replace(needle,repr(note)+',"",'+needle)
p.write_text(s,encoding="utf-8")
p=R/"MERGE_HANDOFF.md";s=p.read_text(encoding="utf-8");s=s.replace("另一电脑未提交内容未获取。",note+"\n\n另一电脑未提交内容未获取。")
s=s.replace("|left：","|左脚：").replace("|right：","|右脚：")
p.write_text(s,encoding="utf-8")
p=R/"STATUS.md";s=p.read_text(encoding="utf-8").replace("|left：","|左脚：").replace("|right：","|右脚：");p.write_text(s,encoding="utf-8")

