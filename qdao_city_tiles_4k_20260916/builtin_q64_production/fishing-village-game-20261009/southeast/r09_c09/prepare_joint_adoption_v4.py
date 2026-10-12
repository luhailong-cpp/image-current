from pathlib import Path
R=Path(__file__).resolve().parent
source=(R/'adopt_joints_20261012.py').read_text(encoding='utf-8')
source=source.replace('from PIL import Image','from PIL import Image, ImageFilter')
source=source.replace("jointpass-20261012-v1","jointpass-20261012-v4").replace("jointpass-v1.png","jointpass-v4.png")
source=source.replace("(330,460),(950,1080),(48,145),(1100,1206)","(48,400),(1050,1206),(48,250),(1050,1206)")
source=source.replace("(345,445),(790,890),(48,130),(1020,1140)","(48,400),(900,1206),(48,130),(1000,1206)")
source=source.replace("dif=np.abs(base.astype(float)-joint.astype(float)).mean(2)","""dif=np.abs(base.astype(float)-joint.astype(float)).mean(2)
 raw=np.abs(base.astype(np.int16)-joint.astype(np.int16)).max(2).astype(np.uint8)
 spread=np.asarray(Image.fromarray(raw).filter(ImageFilter.MaxFilter(7))).astype(float)
 def grad(a):
  a=a.astype(np.int16);g=np.zeros((1254,1254),float)
  g[:,1:]=np.maximum(g[:,1:],np.abs(a[:,1:]-a[:,:-1]).max(2))
  g[1:]=np.maximum(g[1:],np.abs(a[1:]-a[:-1]).max(2));return g
 edge=np.maximum(grad(base),grad(joint))
 cost=spread**2*(1+edge/8.)
""")
source=source.replace("path(dif[","path(cost[")
(R/'adopt_joints_20261012_v4.py').write_text(source,encoding='utf-8')

