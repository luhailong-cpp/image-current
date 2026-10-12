from pathlib import Path
import sys, json, shutil
from PIL import Image
T = Path(__file__).resolve().parent
sys.path.insert(0, str(T.parent))
import tile_native_workflow as w
import review_external_seams as ex

SPECS = {
    'G1-eaststairs-v1-20261012': ([38400,45400,39654,46654], 'Use case: precise-object-edit. Repair ONLY the inconsistent right endpoints of this stone staircase in Image1. Native square 1254 by 1254 pixels, original crop and exact scale. The three broad tall pale stone risers on the left must continue coherently to a proper right stone side cheek next to the existing square stone wall and wooden post. The straight vertical splice at x627 currently joins these broad risers to an incompatible set of tiny steps. Replace that incompatible endpoint geometry with one continuous three-step staircase and its physically correct side cheek. Preserve every left-edge tread and riser endpoint, the upper landing, the outer square stone wall, the entire wooden post at the right, turquoise water, and every deck plank entering the image edges. Keep the repair local to x420..1010: join each large tread and riser naturally to the right side support; remove the small duplicate stair fragments. No straight rectangular cut line. Image2 is authoritative full-map layout A only; Image3 daylight materials B; Image4 primary rounded Q Chinese Daoist painterly style C. Clean bright daylight, pale gray/cyan stone with low contrast joints and fine honey-gold wood grain. Preserve all other geometry and materials. No added objects, people, text, UI, labels, border or watermark.'),
    'G2-railing-v1-20261012': ([37440,47898,38694,49152], 'Use case: precise-object-edit. Repair ONLY the left endings of the two honey-gold foreground railing beams in Image1, native square 1254 by 1254 pixels with original crop and exact scale. Both beams currently stop on an artificial straight vertical line near x563 against the rounded foreground rocks. Give each beam physically correct natural occlusion behind the existing mossy rock silhouette. Round and continue the rock contour where it overlaps each beam so no beam has a visible cut vertical edge; the two beams continue behind those rocks and remain connected to the existing square upright at the right. Preserve all upper deck planks, the capped round dock support, right square post, beam thickness and angle, right beam sockets, bright turquoise water and every silhouette touching an image edge. Local change around x470..750 and y600..1254 only; no new support or extra beam. Image2 authoritative full-map layout A only; Image3 sunny materials B; Image4 primary rounded Q Chinese Daoist painterly style C. Bright daylight, detailed fine wood grain and softly beveled painterly rocks. No added objects, people, text, UI, labels, border or watermark.')
}

def prepare(stem):
    box, prompt = SPECS[stem]
    out, pieces, missing = ex.Sources().extract(box)
    assert not missing
    input_path = T/'repairs'/(stem+'-input.png')
    assert not input_path.exists()
    out.save(input_path)
    w.write(input_path.with_suffix('.png.derivation.json'), dict(file=str(input_path), sha256=w.sha(input_path), globalBox=box, sources=pieces, operation='exact current selected native core inspection crop', resamplingApplied=False, dimensions=[1254,1254]))
    refs = [str(input_path)] + [r['path'] for r in w.approved_refs()]
    req = dict(prompt=prompt, referenced_image_paths=refs, transparent_background=False, submittedParameters=dict(model=None,quality=None), referenceRoles={'1':'edit target; exact current native core geometry','2':'layout reference A only','3':'daylight material style B','4':'primary painterly style C'}, coordinate=dict(globalBox=box, nativeDimensions=[1254,1254]))
    (T/'repairs'/(stem+'.prompt.txt')).write_text(prompt,encoding='utf-8')
    w.write(T/'repairs'/(stem+'.request.json'),req)
    print(json.dumps(req))

def ingest(stem, source):
    p = T/'repairs'/(stem+'.png')
    assert not p.exists()
    source=Path(source)
    raw=T/'raw-sources'/(stem+'-source.png')
    shutil.copy2(source,raw)
    shutil.copy2(source,p)
    assert Image.open(p).size == (1254,1254)
    reqp=T/'repairs'/(stem+'.request.json'); req=w.read(reqp)
    promptp=T/'repairs'/(stem+'.prompt.txt'); receiptp=T/'repairs'/(stem+'.receipt.json')
    receipt=dict(receivedAt=w.now(),sourcePath=str(source),rawSourceCopy=str(raw),rawSourceSha256=w.sha(raw),route='builtin',tool='image_gen__imagegen',actualModel=None,actualQuality=None,result='generated image returned')
    w.write(receiptp,receipt)
    refs=[dict(path=r,sha256=w.sha(r),role=req['referenceRoles'][str(i)]) for i,r in enumerate(req['referenced_image_paths'],1)]
    record=dict(file=str(p),sha256=w.sha(p),ingestedAt=w.now(),generatedAt=receipt['receivedAt'],generatedAtBasis='tool response received time',nativeDimensions=[1254,1254],width=1254,height=1254,format='PNG',tool='image_gen__imagegen',route='builtin',configSnapshot=w.read(w.CONFIG_PATH),submittedParameters=dict(model=None,quality=None),actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin; no model/quality selector or returned model/quality metadata',prompt=str(promptp),promptSha256=w.sha(promptp),references=refs,evidence=dict(request=str(reqp),requestSha256=w.sha(reqp),receipt=str(receiptp),receiptSha256=w.sha(receiptp),sourcePath=str(source),rawSourceCopy=str(raw),rawSourceCopySha256=w.sha(raw)),coordinate=req['coordinate'],upsamplingApplied=False,status='candidate_pending_geometry_and_seam_review')
    w.write(p.with_suffix('.png.generation.json'),record)
    print(json.dumps(dict(file=str(p),sha256=w.sha(p),nativeDimensions=[1254,1254])))

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare(sys.argv[2])
    elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
