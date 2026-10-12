from pathlib import Path
import json
R=Path(__file__).resolve().parent
p=R/'prompts/r12_c13_p41_v03.prompt.txt'
p.write_text('''Use case: precise-object-edit. Edit image 1 at exactly its existing 1254-square crop, camera, scale and daylight painting style. Preserve the whole dock floor and beams, turquoise water, boat contour, gunwale, supports and every boundary overlap at their current coordinates.
There is ONE local defect: the low cross-bench inside the boat has an artificial vertical splice around x1024, y860..1010. Join this into a single real straight solid wood bench. Continue its golden top-face upper and lower edges across that location without a rectangular step, align the brown front face and continuous shadow, and keep the diagonal shadow of the boat gunwale consistent on that bench. Restore only this small bench area and its immediately adjacent shadow. The bench is straight; no break, seam, notch, extra joint, or internal crop boundary at x1024. The rightmost 115 pixels are exact accepted neighboring boat pixels and must stay fixed. Do not move any other objects or redraw the entire floor. References 2, 3 and 4 specify layout, material and painting style only. One complete opaque square, no panels, text, UI or people.''',encoding='utf-8')
print(json.dumps({'prompt':p.as_posix()}))
