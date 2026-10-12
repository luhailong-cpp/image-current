from workflow import *
from PIL import Image
pairs=[('r11_c12_p33',['r11_c12_p23_v01.png','r11_c12_p32_v01.png','r11_c12_p34_v02.png']),('r11_c12_p42',['r11_c12_p32_v01.png','r11_c12_p41_v02.png'])]
for pid,ns in pairs: context(pid,ns)
s=read(ROOT/'selection-r11_c12.json')
s['patchVersions'].update({'34':'v02','41':'v02'})
s['missingPatches']=['33','42','43','44']
s['status']='production_resumed_12of16'
write(ROOT/'selection-r11_c12.json',s)

