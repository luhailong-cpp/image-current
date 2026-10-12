from pathlib import Path
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011"
s=(D/"compose-roof-protected.py").read_text()
a=s.index("points=[");b=s.index("ap=np.rint",a)
s=s[:a]+'''def warm(a):
 a=a.astype("int16");return (a[:,:,0]>a[:,:,2]+20)&(a[:,:,1]>a[:,:,2]+10)&(a[:,:,0]>80)
m=warm(old)|warm(new)
mi=Image.fromarray(m.astype("uint8")*255).filter(ImageFilter.MaxFilter(7))
m=np.array(mi)>0;m[:420]=False;m[:,920:]=False
mi=Image.fromarray(m.astype("uint8")*255)
er1=np.array(mi.filter(ImageFilter.MinFilter(3)))>0
er2=np.array(Image.fromarray(er1.astype("uint8")*255).filter(ImageFilter.MinFilter(3)))>0
alpha=.25*m+.5*er1+.25*er2
''' +s[b:]
s=s.replace("integrated-local-v03","integrated-local-v04").replace('applied-crop.png','applied-crop-v02.png').replace('copy-mask.png','copy-mask-v02.png').replace('alpha.png','alpha-v02.png').replace('proposal.json','proposal-v02.json')
s=s.replace("explicit polygon around actual gold rail join, bounded2px feather; source crop identical after rebase; excludes far-right tile exterior","union of original and generated warm gold surfaces R>B+20 G>B+10 R>80, expanded3px, clipped y>=420 x<920, bounded2px feather; all other scene pixels retained")
(D/"compose-roof-protected-silhouette.py").write_text(s)

