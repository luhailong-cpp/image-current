import json
from pathlib import Path
R=Path(__file__).resolve().parent
sel=json.loads((R/'selected-patches-core-refresh-v1.json').read_text())
sel.update(status='native_geometry_reviewed_before_color',internalReady=False,internalGeometryReady=True,formalAccepted=False)
snapshot=R/'native-selected-before-color-20261012-v2.json'
assert not snapshot.exists();snapshot.write_text(json.dumps(sel,indent=2),encoding='utf-8')
s=(R.parent/'r12_c09/color_match_tile.py').read_text(encoding='utf-8-sig')
s=s.replace("'native-selected-before-color.json'","'native-selected-before-color-20261012-v2.json'")
s=s.replace("'processed/colorpass'","'processed/colorpass-20261012-v1'")
s=s.replace("'colorpass-selected.json'","'colorpass-selected-20261012-v1.json'")
s=s.replace('r12_c09-colorpass-candidate.png','r09_c09-colorpass-candidate-4096.png').replace('r12_c09-colorpass-QA-preview-1024.png','r09_c09-colorpass-QA-preview-1024.png')
s=s.replace('correctionLimit=40.0','correctionLimit=24.0').replace('RGB spread exceeds 80','RGB spread exceeds 48')
s=s.replace('-40, 40','-24, 24').replace('(med - 40)','(med - 24)').replace('(med + 40)','(med + 24)')
s=s.replace('<= 40.00001','<= 24.00001').replace('<= 40 and','<= 24 and').replace('<= 40\n','<= 24\n')
s=s.replace("OUT.mkdir(parents=True, exist_ok=True)","assert not OUT.exists(), 'Use a fresh versioned output directory'\nOUT.mkdir(parents=True, exist_ok=False)")
s=s.replace("def safety_weights(k):\n    return np.ones(1254,dtype=np.float32),np.zeros(1254,dtype=np.float32)","""def safety_weights(k):
    # Preserve all original pixels in the available south 256px QA strip.
    # Fade ONLY the correction field toward zero; never blur or mix image pixels.
    if k[1]=='4':
        y=np.arange(1254,dtype=np.float32)
        q=np.clip((y-499)/(883-499),0,1)
        protection=q*q*(3-2*q)
        return np.zeros(1254,dtype=np.float32),protection
    return np.ones(1254,dtype=np.float32),np.zeros(1254,dtype=np.float32)""")
s=s.replace("unchangedCoreCenter=np.array_equal","availableSouth256PixelsPreserved=(np.array_equal(result[883:],original[k][883:]) if k[1]=='4' else None),\n                  actualModel=None,actualQuality=None,\n                  unchangedCoreCenter=np.array_equal")
assert '-40, 40' not in s and 'med - 40' not in s
(R/'color_match_tile_20261012_v1.py').write_text(s,encoding='utf-8')
print(json.dumps({'selectionSnapshot':str(snapshot),'script':str(R/'color_match_tile_20261012_v1.py')}))

