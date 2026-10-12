from pathlib import Path
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011"
s=(D/"compose-roof-second-mask.py").read_text()
s=s.replace('f=D/"roof-horizontal-join-v01"','f=D/"roof-horizontal-protected-v02"')
s=s.replace('Image.open(f/"input.png")','Image.open(q["referenced_image_paths"][0])')
a=s.index("points=[");b=s.index("ap=np.rint",a)
s=s[:a]+'''points=[(0,860),(300,700),(580,425),(805,415),(900,630),(900,840),(0,1220)]
mi=Image.new("L",(1254,1254));ImageDraw.Draw(mi).polygon(points,fill=255);m=np.array(mi)>0
er1=np.array(mi.filter(ImageFilter.MinFilter(3)))>0
er2=np.array(Image.fromarray(er1.astype("uint8")*255).filter(ImageFilter.MinFilter(3)))>0
alpha=.25*m+.5*er1+.25*er2
''' +s[b:]
s=s.replace('src=Path(q["sourceContext"]["file"]);assert sha(src)==q["sourceContext"]["sha256"]','targetA=json.loads((B/"pipeline/output/14e348439418c1f6/assembly.json").read_text());src=Path(targetA["contextOutput"]["file"]);assert sha(src)==targetA["contextOutput"]["sha256"]')
s=s.replace("integrated-local-v02","integrated-local-v03").replace("applied-crop-v02.png","applied-crop.png").replace("copy-mask-v02.png","copy-mask.png").replace("alpha-v02.png","alpha.png").replace("proposal-v02.json","proposal.json")
s=s.replace('"input":q["sourceContext"]','"input":targetA["contextOutput"],"originalRequestContext":q["sourceContext"],"originalCropIdenticalAfterRebase":True')
s=s.replace('"sourceAssembly":q["sourceAssembly"]','"sourceAssembly":str(B/"pipeline/output/14e348439418c1f6/assembly.json")')
s=s.replace("explicit polygon around actual gold rail join with48px bounded alpha feather; no color threshold holes; excludes far-right tile exterior","explicit polygon around actual gold rail join, bounded2px feather; source crop identical after rebase; excludes far-right tile exterior")
(D/"compose-roof-protected.py").write_text(s)

