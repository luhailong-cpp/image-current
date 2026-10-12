from pathlib import Path
R=Path(__file__).resolve().parent
source=(R/'adopt_joints_20261012.py').read_text(encoding='utf-8')
source=source.replace("from PIL import Image","from PIL import Image, ImageFilter")
source=source.replace("jointpass-20261012-v1","jointpass-20261012-v3").replace("jointpass-v1.png","jointpass-v3.png")
source=source.replace("(330,460),(950,1080),(48,145),(1100,1206)","(250,390),(1080,1190),(48,200),(1070,1206)")
source=source.replace("(345,445),(790,890),(48,130),(1020,1140)","(250,390),(1080,1190),(48,200),(1070,1206)")
source=source.replace(" y0,y1,x0,x1=required;assert mask[y0:y1,x0:x1].all()",'''
 y0,y1,x0,x1=required;assert mask[y0:y1,x0:x1].all()
 # Preserve original strong roof contours where the native edit deviated geometrically.
 # The mask copies only whole RGB pixels. No alpha mixing, colour filtering or image blur.
 def gradient(a):
  a=a.astype(np.int16)
  dx=np.max(np.abs(a[:,1:]-a[:,:-1]),axis=2);dy=np.max(np.abs(a[1:]-a[:-1]),axis=2)
  g=np.zeros((1254,1254),np.uint8);g[:,1:]=np.maximum(g[:,1:],dx.astype(np.uint8));g[1:]=np.maximum(g[1:],dy.astype(np.uint8));return g
 originalGradient=gradient(base);newGradient=gradient(joint)
 diffMax=np.abs(base.astype(np.int16)-joint.astype(np.int16)).max(2)
 roof=((base[:,:,2].astype(float)>base[:,:,0]*1.5)&(base[:,:,2]>65))|((joint[:,:,2].astype(float)>joint[:,:,0]*1.5)&(joint[:,:,2]>65))
 safe=(diffMax<50)&(originalGradient<38)&(newGradient<38)
 safe=np.asarray(Image.fromarray(safe.astype(np.uint8)*255).filter(ImageFilter.MinFilter(5)))>0
 roof=np.asarray(Image.fromarray(roof.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(5)))>0
 mask &= (~roof)|safe
''')
source=source.replace("'operation':'unscaled exact native AI pixels through binary low-difference cut; no blending, blur, warp or resampling'","'operation':'unscaled exact native AI pixels through binary material cut with original sharp roof contours retained; no blending, blur, warp or resampling'")
(R/'adopt_joints_20261012_v3.py').write_text(source,encoding='utf-8')

