from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'adopt_joints_20261012.py').read_text(encoding='utf-8')
s=s.replace("jointpass-20261012-v1","jointpass-20261012-v5").replace("jointpass-v1.png","jointpass-v5.png")
s=s.replace("('canopy-cross-r2-c2-v1',(1421,1421),(330,460),(950,1080),(48,145),(1100,1206),(510,700,600,960))","('canopy-cross-r2-c2-v2',(1421,1421),(460,500),(660,715),(545,610),(860,930),(510,644,627,795))")
s=s.replace("('ridge-cross-r3-c3-v2',(2445,2445),(345,445),(790,890),(48,130),(1020,1140),(600,665,130,700))","('ridge-cross-r3-c3-v3',(2445,2445),(415,465),(655,690),(540,605),(770,825),(475,635,627,740))")
s=s.replace("else f'{stem}-input.png'","else 'canopy-cross-r2-c2-v1-input.png'")
(R/'adopt_joints_20261012_v5.py').write_text(s,encoding='utf-8')

