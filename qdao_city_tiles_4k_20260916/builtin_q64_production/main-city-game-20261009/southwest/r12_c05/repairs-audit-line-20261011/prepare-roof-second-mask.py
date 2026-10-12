from pathlib import Path
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011"
s=(D/"compose-roof-first.py").read_text().replace("from PIL import Image,ImageFilter","from PIL import Image,ImageFilter,ImageDraw")
start=s.index("def gold(a):");end=s.index("ap=np.rint",start)
s=s[:start]+'''points=[(0,815),(200,745),(560,390),(810,340),(1139,370),(1139,1000),(1030,1254),(0,1254)]
mi=Image.new("L",(1254,1254));ImageDraw.Draw(mi).polygon(points,fill=255);m=np.array(mi)>0
alpha=np.zeros(m.shape,float);er=m.copy()
for k in range(48):
 alpha+=er/48.0
 pad=np.pad(er,1,mode="edge")
 er=pad[:-2,1:-1]&pad[2:,1:-1]&pad[1:-1,:-2]&pad[1:-1,2:]&er
''' +s[end:]
s=s.replace("integrated-local-v01","integrated-local-v02").replace('applied-crop.png','applied-crop-v02.png').replace('copy-mask.png','copy-mask-v02.png').replace('alpha.png','alpha-v02.png').replace('proposal.json','proposal-v02.json')
s=s.replace("union of existing/generated golden rail silhouette, explicitly ROI y>=410 x<1040; 12px dilation, bounded2px feather; excludes far-right tile exterior","explicit polygon around actual gold rail join with48px bounded alpha feather; no color threshold holes; excludes far-right tile exterior")
(D/"compose-roof-second-mask.py").write_text(s)

