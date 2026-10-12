"""Column 02 local orchestration; no AI calls and no final pixel modification."""
import sys
sys.dont_write_bytecode = True
import argparse, json, hashlib, datetime
from pathlib import Path
from types import SimpleNamespace
import batch_pipeline as pipe

B = Path(__file__).resolve().parents[1]
def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2))
def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest='cmd', required=True)
    q = s.add_parser('prepare')
    q.add_argument('--tile', choices=['r01_c02','r02_c02'], required=True)
    q.add_argument('--row', type=int, required=True)
    q.add_argument('--col', type=int, required=True)
    q.add_argument('--attempt', type=int, default=1)
    q.add_argument('--content', required=True)
    q.add_argument('--guide-only', action='store_true')
    for side in ('south','west','east','north'):
        q.add_argument('--'+side)
        q.add_argument('--'+side+'-record')
    q = s.add_parser('review')
    q.add_argument('--stem', required=True)
    q.add_argument('--decision', choices=['continue','hold','reject'], required=True)
    q.add_argument('--note', required=True)
    q.add_argument('--issue', action='append', default=[])
    a = p.parse_args()
    if a.cmd == 'review':
        assert a.stem.startswith(('r01_c02_','r02_c02_'))
        image = B/'native'/f'{a.stem}.png'
        generation = image.with_suffix('.png.generation.json')
        from PIL import Image
        with Image.open(image) as im:
            dimensions=list(im.size)
        assert dimensions==[1254,1254]
        review={'schemaVersion':1,'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'stem':a.stem,'raw':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
                'generationRecord':str(generation),'actualSize':dimensions,
                'inspection':'Native 1254 original visually inspected; layout and provided neighbor overlaps checked.',
                'decision':a.decision,'selectedForContinuedProduction':a.decision=='continue',
                'note':a.note,'openIssues':a.issue,'internalFullTileQA':'pending','externalAcceptance':'pending','formalAccepted':False}
        path=B/'qa'/f'{a.stem}.quick-review-v01.json'
        save(path,review)
        print(json.dumps({'review':str(path),'decision':a.decision}))
        return
    stem=f'{a.tile}_s{a.row:02d}_{a.col:02d}_a{a.attempt:02d}'
    sides=[side for side in ('south','west','east','north') if getattr(a,side)]
    prompt=(f'Use case: sketch-to-render. Generate ONE native opaque 1254x1254 PNG game-map patch {stem}. '
            'Central core is [115,115,1139,1139]. IMAGE 1 is the sole target composition/camera guide; '
            'its blurred pixels require genuine finely painted native detail at exactly the same positions and scale. '
            'Never copy another reference scene as the target composition.\n'
            f'EXACT LOCAL CONTENT: {a.content}\n'
            f'The sharp 230px edge strips on these sides of IMAGE 1 are fixed existing overlaps: {", ".join(sides)}. '
            'Keep all those strips in their exact canvas coordinates and match every shape, color, object edge and material through the joint. '
            'Continue the same geometry into the newly rendered center. IMAGE 2 is the full-size adjacent contact, '
            'with original 1254px panels in the supplied neighbor order. Each adjacent patch center is 1024px away, '
            'so only its corresponding 230px edge overlaps this target. Do not transplant its entire scene.\n'
            'Same refined rounded Daoist Q hand-painted style as the already finished neighbor: bright daylight, '
            'soft brushwork, clean detailed edges, consistent lighting and object scale, natural pale grey/blue-grey stones, '
            'blue/jade materials only where already in this exact guide, yellow/white flowers and green leaves as shown. '
            'STRICT: no unrequested building, gate, furniture, props, characters, animals, UI, text, frame, grid, watermark, '
            'new landmass, new tree, invented courtyard or scene redesign. Do not add the map whole or change camera scale. '
            'Do not introduce blurry bands, pasted low-resolution pixels, repeated strips, or canvas padding. '
            'Only restore detailed art within the supplied exact local geometry. Output exactly1254x1254.')
    if a.guide_only:
        prompt=prompt.replace('IMAGE 2 is the full-size adjacent contact, with original 1254px panels in the supplied neighbor order. Each adjacent patch center is 1024px away, so only its corresponding 230px edge overlaps this target. Do not transplant its entire scene.', 'There is only ONE image reference. Its sharp edge strips carry all native style and seam evidence. Preserve those strips and render the blurry interior into fully detailed matching art.')
    promptpath=B/'prompts'/f'{stem}.custom.txt'
    promptpath.parent.mkdir(parents=True,exist_ok=True)
    with promptpath.open('x',encoding='utf-8') as f:f.write(prompt)
    args=SimpleNamespace(tile=a.tile,subrow=a.row,subcol=a.col,attempt=a.attempt,
        prompt_file=str(promptpath),no_neighbor_contact=a.guide_only,geometry_references_only=True)
    for side in ('south','west','east','north'):
        setattr(args,side,getattr(a,side));setattr(args,side+'_record',getattr(a,side+'_record'))
    result=pipe.prepare(args)
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
