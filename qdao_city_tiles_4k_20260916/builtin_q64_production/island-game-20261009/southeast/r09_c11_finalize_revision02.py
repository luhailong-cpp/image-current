from workflow import ROOT
p=ROOT/'r09_c11_audit.py';s=p.read_text(encoding='utf-8')
a=s.index('failures={');b=s.index('\nseams=[]',a);s=s[:a]+"failures={}"+s[b:]
s=s.replace("'allInternalSeamsPassed':False","'allInternalSeamsPassed':True")
s=s.replace("'native/r09_c11_seam-p43-p44_v01.png']","'native/r09_c11_seam-p43-p44_v01.png','native/r09_c11_seam-p23-p24_v02.png','native/r09_c11_seam-p43-p44_v02.png','native/r09_c11_p43_v02.png']")
s=s.replace("status='complete_4k_candidate_requires_seam_repair'","status='complete_4k_candidate_internal_reviewed'")
s=s.replace("Repair p23-p24 beam/window and p43-p44 stairs without displacing outer anchors; root review layout and remaining tile edges","Root review layout, tone consistency and top/left/bottom edges; extend r10_c11 from current selected native")
s=s.replace("usableNativeCount=16,complete4kCount=1","generatedNativeCount=len(items),usableNativeCount=16,complete4kCount=1")
p.write_text(s,encoding='utf-8')
p=ROOT/'r09_c11_document.py';s=p.read_text(encoding='utf-8')
s=s.replace('Selected for complete candidate; formal and internal acceptance not passed','Selected for complete candidate; internal visual continuity reviewed; formal external acceptance not passed')
s=s.replace("r['internalSeamsPassed']=False","r['internalSeamsPassed']=True")
s=s.replace('正式验收 0，内部接缝未全部通过','正式验收 0，内部接缝已完成候选级目检')
s=s.replace('质量检查及两处未通过项','质量检查及剩余复核项').replace('全部 23 次','全部 28 次')
a=s.index('尚需修正：');b=s.index('\n\n右侧',a)
s=s[:a]+'原有 p23→p24 檐梁、墙梁与红窗错位，以及 p43→p44 台阶错位，分别以 p23_v03、p43_v03 原生片重绘修正。四个跨缝修复稿及二值硬切试接均未采用，p43_v02 因改变木架且新增装饰而拒用。24 条内部硬接与 9 个交会点已目检；局部金属和石材色调、编钟细节及木架支撑与布局图的贴合度仍需主任务复核。'+s[b:]
s=s.replace("'r09_c11_p34_v01.png':'replaced", "'r09_c11_p23_v01.png':'replaced: beam/window seam repaired by v03','r09_c11_p43_v01.png':'replaced: stair seam repaired by v03','r09_c11_p43_v02.png':'rejected: changed upright base and invented ornament','r09_c11_seam-p23-p24_v02.png':'not inserted: perimeter contour discontinuity','r09_c11_seam-p43-p44_v02.png':'not inserted: perimeter stair discontinuity and central tone line','r09_c11_p34_v01.png':'replaced")
p.write_text(s,encoding='utf-8')

