from PIL import Image
from production import W,write
a=Image.open(W/'joint-v3/joint.context.png').crop((14900-12173,7320-3981,16154-12173,8574-3981));p=Image.open(W/'native/r02_c04_r03_c04_fence_post_whole_bridge_v01.png');a.paste(p.crop((0,0,909,1121)),(345,133));q=W/'guides/rail-post-full-anchor-v01.target.png';a.save(q);write(str(q)+'.derivation.json',{'guideOnly':True,'globalNativeBox':[14900,7320,16154,8574],'baseAssembly':str(W/'joint-v3/joint.assembly.json'),'overlayNative':'r02_c04_r03_c04_fence_post_whole_bridge_v01.png','sourceBox':[0,0,909,1121],'destination':[345,133]})

