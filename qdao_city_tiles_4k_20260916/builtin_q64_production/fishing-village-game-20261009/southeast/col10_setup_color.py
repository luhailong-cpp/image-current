from pathlib import Path
Z=Path(__file__).resolve().parent
source=Z/'r12_c09/color_match_tile.py';dest=Z/'r11_c10/color_match_tile.py'
code=source.read_text(encoding='utf-8-sig').replace('r12_c09','r11_c10')
code=code.replace("geometrySafety='No color correction used to conceal geometry; all 24 seams and 9 crossings inspected; current sources need color equalization only'","geometrySafety='Candidate after geometry joint fixes; color field does not alter geometry; final 24-seam/9-crossing and external review required'")
dest.write_text(code,encoding='utf-8')
import shutil
sp=Z/'r11_c10/native-selected-before-color.json'
assert not sp.exists()
shutil.copy2(Z/'r11_c10/selected-patches.json',sp)

