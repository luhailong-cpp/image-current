from workflow import *
from PIL import Image
s=read(ROOT/'selection-r11_c12.json')
s['patchVersions'].update({'33':'v01','42':'v01','43':'v01','44':'v02'})
s['missingPatches']=[]
s['status']='complete_core_coverage_pending_seam_review'
write(ROOT/'selection-r11_c12.json',s)

