"""Native-scale additional seam target, with a truthful shifted world box."""
from pathlib import Path
from PIL import Image
import importlib.util
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v2',HERE.parent/'production_v2.py')
v2=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
west=HERE.parent/'r07_c05/candidate/r07_c05-candidate-hard-1672ae5e4698.png'
own=HERE/'candidate/r07_c06-candidate-hard-2e59491c741a.png'
w=Image.open(west).convert('RGB')
c=Image.open(own).convert('RGB')
target=Image.new('RGB',(1254,1254))
target.paste(w.crop((3469,1974,4096,3228)),(0,0))
target.paste(c.crop((0,1974,627,3228)),(627,0))
selection=v2.read(HERE.parent/'r07_c05/selection.json')
west_current=[]
for row in range(1,5):
    pid=f's{row:02}_04'
    path=v2.selected_path(HERE.parent/'r07_c05',pid,selection)
    proof=v2.validate_native(path,HERE.parent/'r07_c05',pid)
    native=Image.open(path).convert('RGB').crop((115,115,1139,1139))
    assert native.tobytes()==w.crop((3072,(row-1)*1024,4096,row*1024)).tobytes()
    west_current.append(proof)
out=HERE/'layout-only/west-seam-r3-fix01.actual-1254.png'
v2.save_png(out,target)
record=dict(id='west-seam-r3-fix01',purpose='Supplemental seam-native edit target, not one of the 16 planned patch frames',
            guide=str(out),sha256=v2.sha(out),size=[1254,1254],worldBox=[19853,26550,21107,27804],
            boundaryPixelX=627,worldBoundaryX=20480,
            pixelSources=[dict(file=str(west),sha256=v2.sha(west),sourceBox=[3469,1974,4096,3228],targetBox=[0,0,627,1254]),
                          dict(file=str(own),sha256=v2.sha(own),sourceBox=[0,1974,627,3228],targetBox=[627,0,1254,1254])],
            currentWestEdgeNativeProof=west_current,westEdgeMatchesCurrentSelection=True,
            sourceResampled=False,sourceUpscaled=False,warped=False,blended=False,recolored=False,
            intendedLocalEditBox=[600,500,840,740],formalAccepted=False)
v2.write_json(out.with_suffix('.png.derivation.json'),record)
print(json.dumps(dict(guide=str(out),sha256=v2.sha(out),worldBox=record['worldBox'],currentWestEdgeMatches=True)))
