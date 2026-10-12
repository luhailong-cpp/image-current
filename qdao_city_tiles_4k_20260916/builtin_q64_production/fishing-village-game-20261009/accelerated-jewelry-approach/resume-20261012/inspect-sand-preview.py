from pathlib import Path
from PIL import Image, ImageChops
import json
import numpy as np

base = Path(__file__).resolve().parents[1]
directory = base / 'r05_c11' / 'repairs' / 'sand-halo-v1'
proposal = json.loads((directory / 'proposal.json').read_text(encoding='utf-8-sig'))
rgb = lambda path: Image.open(path).convert('RGB')
mask = Image.open(proposal['mask']['file']).convert('L')
source = rgb(proposal['nativeRepair']['file'])
target = rgb(proposal['target']['file'])
saved = rgb(proposal['localComposite']['file'])
original_local = Image.composite(source, target, mask)
current = rgb(base / 'r05_c11' / 'candidate' / 'r05_c11-4096-candidate-v2.png').crop(proposal['tileTargetBox'])
current_local = Image.composite(source, current, mask)
different = np.any(np.array(saved) != np.array(current_local), axis=2)
alpha = np.array(mask)
print(json.dumps({
    'savedPreviewExactFromOriginalCoreTarget': ImageChops.difference(saved, original_local).getbbox() is None,
    'savedPreviewDiffBoxVersusFinalLocal': ImageChops.difference(saved, current_local).getbbox(),
    'differentPixelCount': int(np.count_nonzero(different)),
    'differentPixelCountWhereMaskZero': int(np.count_nonzero(different & (alpha == 0))),
    'differentPixelCountWhereMaskPositive': int(np.count_nonzero(different & (alpha > 0))),
    'differentPixelCountWhereMask255': int(np.count_nonzero(different & (alpha == 255))),
}))
