from pathlib import Path
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
src=(z/'r06_c14_extension.py').read_text(encoding='utf-8')
src=src.replace("T='r06_c14';ORIGIN=(53248,20480)","T='r05_c14';ORIGIN=(53248,16384)")
src=src.replace("LEFT=['r06_c13_p14-v1.png','r06_c13_p24-v1.png','r06_c13_p34-v1.png','r06_c13_p44-v1.png']","SOUTH=['r06_c14_p11-v1.png','r06_c14_p12-v1.png','r06_c14_p13-v1.png','r06_c14_p14-v1.png']")
src=src.replace("'tileCoreBox':[53248,20480,57344,24576]","'tileCoreBox':[53248,16384,57344,20480]").replace("box=[1100,420,1254,566]","box=[1100,332,1254,462]").replace("(1232,1168)","(1232,1040)")
a=src.index(" r,c=int(p[-2]),int(p[-1]);left=",src.index("def prep"))
e=src.index(" gp=Z/'guides'",a)
src=src[:a]+""" r,c=int(p[-2]),int(p[-1]);left=Z/'native'/choices.get(f'{T}_p{r}{c-1}',f'{T}_p{r}{c-1}-v1.png') if c>1 else None
 bottom=Z/'native'/(SOUTH[c-1] if r==4 else choices.get(f'{T}_p{r+1}{c}',f'{T}_p{r+1}{c}-v1.png'))
 sources=[]
 for path,side in [(bottom,'bottom'),(left,'left')]:
  if path:
   a=Image.open(path).convert('RGB');assert a.size==(N,N);box=[1024,0,N,N] if side=='left' else [0,0,N,230];at=[0,0] if side=='left' else [0,1024];im.paste(a.crop(box),at);rr=ref(path,'exact_native_'+side+'_230px');rr.update({'cropBox':box,'pasteAt':at});sources.append(rr)
""" +src[e:]
src=src.replace('top owns corner','left owns corner')
p=z/'r05_c14_extension.py';assert not p.exists();p.write_text(src,encoding='utf-8')
print(str(p))

