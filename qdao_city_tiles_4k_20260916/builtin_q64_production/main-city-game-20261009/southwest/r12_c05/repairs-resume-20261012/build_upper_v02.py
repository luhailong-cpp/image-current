from pathlib import Path
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012')
s=(D/'integrate_upper_edge.py').read_text(encoding='utf-8')
for old,new in [
 ('integrated-local-v08','integrated-local-v09'),
 ('poly=[(674,222),(980,3),(980,70),(674,283)]','poly=[(640,237),(1040,0),(1040,65),(640,345)]'),
 ('applied-crop.png','applied-crop-v02.png'),
 ('copy-mask.png','copy-mask-v02.png'),
 ('alpha.png','alpha-v02.png'),
 ('proposal.json','proposal-v02.json'),
 ('-ROI-native-QA.png','-ROI-native-v02-QA.png')]:s=s.replace(old,new)
(D/'integrate_upper_edge_v02.py').write_text(s,encoding='utf-8')
exec(compile(s,str(D/'integrate_upper_edge_v02.py'),'exec'))
