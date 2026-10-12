from pathlib import Path
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011"
s=(D/"compose-cross-second.py").read_text()
a=s.index(' if attempt.startswith("roof"):');b=s.index(' mi=Image.fromarray(m.astype',a)
new=''' if attempt.startswith("roof"):
  def foreground(a):
   z=a.astype("int16")
   return ((z[:,:,0]>z[:,:,2]+35)&(z[:,:,1]>z[:,:,2]+10))|((z[:,:,0]<115)&(z[:,:,1]<160)&(z[:,:,2]<180))
  m=foreground(old)|foreground(new)
  clip=Image.new("L",(1254,1254));ImageDraw.Draw(clip).polygon([(0,530),(280,575),(520,470),(800,300),(1050,120),(1254,0),(1254,1254),(0,1254)],fill=255);m &= np.array(clip)>0
  mi=Image.fromarray(m.astype("uint8")*255).filter(ImageFilter.MaxFilter(7))
  # Fill fully enclosed highlight holes, leaving exterior background excluded.
  padded=Image.new("L",(1256,1256));padded.paste(mi,(1,1));ImageDraw.floodfill(padded,(0,0),128)
  arr=np.array(padded)[1:-1,1:-1];m=arr!=128
  rule={"type":"union of actual old/new foreground silhouettes, filled enclosed highlights, expanded3px; excludes pavement, bounded2px feather","featherPixels":2}
  note="entire internally consistent generated roof surface reused to avoid a new cut inside teal molding; original exterior pavement preserved; crop perimeter joins still pending"
 else:
  points=[(0,500),(820,0),(1254,0),(1254,1254),(0,1254)]
  mi=Image.new("L",(1254,1254));ImageDraw.Draw(mi).polygon(points,fill=255);m=np.array(mi)>0
  def foreground(a):
   z=a.astype("int16");yy,xx=np.indices(z.shape[:2])
   return (((z[:,:,0]>z[:,:,2]+35)&(z[:,:,1]>z[:,:,2]+10))|((z[:,:,0]<115)&(z[:,:,1]<160)&(z[:,:,2]<180)))&(yy>650)&(xx>430)
  obj=foreground(old)|foreground(new)
  oi=Image.fromarray(obj.astype("uint8")*255).filter(ImageFilter.MaxFilter(9))
  padded=Image.new("L",(1256,1256));padded.paste(oi,(1,1));ImageDraw.floodfill(padded,(0,0),128)
  obj=np.array(padded)[1:-1,1:-1]!=128
  m &= ~obj
  rule={"type":"generated continuous cream/blue paving plane; foreground object mask excluded with4px guard; bounded2px feather","polygon":points,"featherPixels":2}
  note="large three stone border notches corrected and central blue plane unified; crop outer color/line continuation still pending"
'''
s=s[:a]+new+s[b:]
# Blue foreground and roof foreground guards make masks separate; any geometric overlap is foreground guard AA only and should abort.
s=s.replace("integrated-local-v05","integrated-local-v06").replace('applied-crop.png','applied-crop-v02.png').replace('copy-mask.png','copy-mask-v02.png').replace('alpha.png','alpha-v02.png').replace('proposal.json','proposal-v02.json')
(D/"compose-cross-second-wide-native.py").write_text(s)

