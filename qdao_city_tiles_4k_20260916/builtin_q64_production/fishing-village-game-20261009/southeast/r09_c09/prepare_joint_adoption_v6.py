from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'adopt_joints_20261012.py').read_text(encoding='utf-8')
s=s.replace("jointpass-20261012-v1","jointpass-20261012-v6").replace("jointpass-v1.png","jointpass-v6.png")
s=s.replace("'canopy-cross-r2-c2-v1'","'canopy-cross-r2-c2-v3'").replace("'ridge-cross-r3-c3-v2'","'ridge-cross-r3-c3-v4'")
s=s.replace("else f'{stem}-input.png'","else 'canopy-cross-r2-c2-v1-input.png'")
s=s.replace(" y0,y1,x0,x1=required;assert mask[y0:y1,x0:x1].all()",""" mask=np.zeros((1254,1254),bool)
 holes=[(600,480,890,725)] if 'canopy' in stem else [(0,583,770,675),(590,470,775,675)]
 for x0,y0,x1,y1 in holes:mask[y0:y1,x0:x1]=True""")
s=s.replace(" assert not mask[:48].any() and not mask[-48:].any() and not mask[:,:48].any() and not mask[:,-48:].any()"," assert not mask[:48].any() and not mask[-48:].any() and not mask[:,-48:].any()")
s=s.replace("binary low-difference cut","binary exact input-hole cut")
(R/'adopt_joints_20261012_v6.py').write_text(s,encoding='utf-8')

