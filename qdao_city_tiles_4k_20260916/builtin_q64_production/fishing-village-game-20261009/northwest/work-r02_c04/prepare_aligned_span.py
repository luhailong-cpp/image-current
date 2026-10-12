from PIL import Image
from production import W,write
a=Image.open(W/'native/r02_c04_rail_span_right_v02.png').convert('RGB');p=Image.open(W/'native/r02_c04_r03_c04_fence_post_whole_bridge_v01.png').convert('RGB');a.paste(p.crop((0,0,682,941)),(572,313));o=W/'guides/rail-span-right-v03.target.png';a.save(o)
write(str(o)+'.derivation.json',{'guideOnly':True,'globalNativeBox':[14673,7140,15927,8394],'layers':[{'native':'r02_c04_rail_span_right_v02.png','globalBox':[14673,7140,15927,8394]},{'native':'r02_c04_r03_c04_fence_post_whole_bridge_v01.png','sourceBox':[0,0,682,941],'destination':[572,313]}],'reason':'exact full right post and incoming beam heights anchored to native whole post; repair between this and complete left post'})

