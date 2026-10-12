from pathlib import Path
B=Path(__file__).resolve().parents[1]
p=B/'tools/select_run_e.py';s=p.read_text(encoding='utf-8').replace("15:'run-E-15-v3'","15:'run-E-15-v5'")
s=s.replace("8:'右靴预触地高度修正，保留小间距。'","8:'按实图改记右足跟初触，已达到接触高度，不能继续算腾空。'")
s=s.replace("10:'原10扇轴与拳分離定点修v3，手指实握枢轴。'","10:'v3修复握轴，v4回收右扇至腰边过渡，避免前后摆跳变；保留右支撑。'")
s=s.replace("15:'原15前靴过低，v3曲膝修到离地；与14腾空高度相近，下降连续性需组审。'","15:'v5前靴高度1140，介于14峰值1124与16预触地1171；修复悬停，右扇前摆连续。'")
s=s.replace("9:'right_contact',12:","8:'right_heel_initial_contact',9:'right_contact',12:")
p.write_text(s,encoding='utf-8')
p=B/'tools/review_run_e_grounding.py';s=p.read_text(encoding='utf-8')
s=s.replace('左后掌待推蹬修正','左后掌推蹬（v3）').replace('高位换鞋角/下降不足','第二下降（v5）')
s=s.replace('720均匀为比较中点；承重分配只作实验，在E04接地、E10摆臂和E15下降修好后重评，不能用时长掩盖姿态。','E04脚尖/摆臂、E10回摆和E15下降已针对性修正；更新快照后复核640/720/800与承重720，正式节奏未定。')
p.write_text(s,encoding='utf-8')
p=B/'tools/render_run_e_grounding.py';s=p.read_text(encoding='utf-8')
start=s.index("data['browser']=");end=s.index("\np.write_text",start)
s=s[:start]+"data['browser']={'status':'pending_updated_snapshot_review','html':'audit/run-E-grounding.html','notClaimed':'未接入客户端，更新后的整组仍待主审'}"+s[end:]
p.write_text(s,encoding='utf-8')
p=B/'audit/run-E-grounding.html';s=p.read_text(encoding='utf-8').replace('其余新修图未自动混入本比较。','已按最新选表更新E04v3、E10v4、E15v5；来源逐帧可核。')
p.write_text(s,encoding='utf-8')
print('Updated E selections and grounding diagnostics.')
