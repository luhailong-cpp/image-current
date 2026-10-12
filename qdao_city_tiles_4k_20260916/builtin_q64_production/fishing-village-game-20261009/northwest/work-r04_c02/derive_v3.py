from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'apply_repairs_v2.py').read_text(encoding='utf-8')
s=s.replace("base=read(W/'repair-v1/extended.assembly.json')","base=read(W/'repair-v2/extended.assembly.json')").replace("out=W/'repair-v2'","out=W/'repair-v3'")
a=s.index('for name,rect,band in ');e=s.index(':\n p=B/',a)
s=s[:a]+"for name,rect,band in [('r04_c02_paving_joint_v01',[290,300,1030,810],100)]"+s[e:]
(p/'apply_repairs_v3.py').write_text(s,encoding='utf-8')
