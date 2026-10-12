from native_work import *
import numpy as np
for v in [2,3,4]:
 a=np.array(Image.open(ZONE/'qa'/f'r04_c12_cross_01_02_jar_paint_repair_v{v}.top-100pct.png')).astype(float)
 print(v,float(np.abs(a[100,400:]-a[99,400:]).mean()),float(np.abs(a[90:110,400:][1:]-a[90:110,400:][:-1]).mean()))

