"""Bounded additive color candidate; source images/selection/progress are read-only.

Only correction fields are interpolated. No source-image resampling, spatial
registration, image blur, pixel blending, or geometry repair occurs here.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

ZONE = Path(__file__).resolve().parent
TILE = ZONE
SEL = TILE / 'native-selected-before-color.json'
SELECTED = json.loads(SEL.read_text(encoding='utf-8-sig'))
OUT = TILE / 'processed/colorpass'
OUT.mkdir(parents=True, exist_ok=True)
PARAM = dict(corePixels=1024, haloPixels=115, nativePixels=1254,
             correctionLimit=40.0, inwardSupportPixels=384, fieldGridStep=16,
             overlapStatisticHalfWidth=20, profileGaussianSigma=24,
             cornerStatisticHalfWidth=24, cornerEndpointTransition=96,
             incompatibleCornerPolicy='disable corner correction when any RGB spread exceeds 80; do not conceal material/geometry discrepancy',
             harmonicSolver='red-black successive over-relaxation',sorRelaxation=1.8,
             solverTolerance=0.00002,solverMaxIterations=3000,
             coordinateShift=[0, 0], pixelResampling=False, imageBlur=False,
             imagePixelBlending=False, colorSpace='encoded 8-bit RGB additive',
             fieldInterpolation='bilinear, correction field only',
             boundaryExtension='clamp field to core boundary through 115px halo',
             smoothSurfaceSamplingPolicy='Geometry-reviewed inputs; every seam uses smooth same-coordinate pixel samples only; RGB gradient<6 and difference<65, at least8/40 samples per profile row',
             geometrySafety='No color correction used to conceal geometry; all 24 seams and 9 crossings inspected; current sources need color equalization only')
N = 65
COORD = np.arange(N, dtype=np.float32) * 16
NOW = datetime.now(timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def record_path(p):
    return str(p) + ('.generation.json' if p.parent.name == 'native' else '.derivation.json')


def pid(r, c):
    return f'p{r + 1}{c + 1}'


def fimage(path):
    a = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32)
    assert a.shape == (1254, 1254, 3)
    return a


sources = {k: TILE / v for k, v in SELECTED['patches'].items()}
original = {k: fimage(v) for k, v in sources.items()}
edges = {k: {} for k in sources}
seams = []
sampling_evidence = []
for r in range(4):
    for c in range(4):
        a = pid(r, c)
        for dr, dc, axis, sa, sb in [(0, 1, 'horizontal', 'right', 'left'),
                                      (1, 0, 'vertical', 'bottom', 'top')]:
            if r + dr >= 4 or c + dc >= 4:
                continue
            b = pid(r + dr, c + dc)
            aa, bb = original[a], original[b]
            da,db=(aa[:,1119:1159],bb[:,95:135]) if dc else (aa[1119:1159],bb[95:135])
            dif=db-da
            def gradient(x):
                return np.maximum(np.max(np.abs(np.gradient(x,axis=0)),axis=2),np.max(np.abs(np.gradient(x,axis=1)),axis=2))
            mask=(gradient(da)<6)&(gradient(db)<6)&(np.max(np.abs(dif),axis=2)<65)
            # Estimate only reliable same-coordinate smooth surfaces; reject structure and shadow edges.
            dd=dif if dc else np.swapaxes(dif,0,1)
            mm=mask if dc else mask.T
            valid=mm.sum(axis=1)>=8
            rows=np.zeros((1254,3),dtype=np.float32)
            for ii in np.flatnonzero(valid):rows[ii]=np.median(dd[ii][mm[ii]],axis=0)
            kernel=np.exp(-.5*(np.arange(-96,97)/24)**2);kernel/=kernel.sum()
            den=np.convolve(np.pad(valid.astype(np.float32),(96,96),mode='edge'),kernel,mode='valid')
            num=np.stack([np.convolve(np.pad(rows[:,ch]*valid,(96,96),mode='edge'),kernel,mode='valid') for ch in range(3)],axis=1)
            profile=num/np.maximum(den[:,None],1e-8)
            profile[den<.15]=0
            maskpath=OUT/f'{a}-{b}-sampling-mask.npz'
            np.savez_compressed(maskpath,acceptedPixels=mm,acceptedRows=valid,validWeight=den,rawMedianRgb=rows)
            sampling_evidence.append(dict(seam=f'{a}-{b}-{axis}',maskFile=str(maskpath),maskSha256=sha(maskpath),acceptedPixelCount=int(mm.sum()),acceptedRowCount=int(valid.sum()),excluded='RGB gradient>=6 or same-coordinate RGB difference>=65; profiles with effective valid weight<0.15 disabled',sampleWidth=40))
            half = np.clip(profile * .5, -40, 40).astype(np.float32)
            edges[a][sa] = half.copy()
            edges[b][sb] = -half.copy()
            seams.append(dict(id=f'{a}-{b}-{axis}', a=a, b=b, axis=axis))

# A single robust color target for all four images at each crossing.
corners = {k: {} for k in sources}
corner_evidence = []
for r in range(1, 4):
    for c in range(1, 4):
        entries = [(pid(r - 1, c - 1), 'br', 1139, 1139),
                   (pid(r - 1, c), 'bl', 115, 1139),
                   (pid(r, c - 1), 'tr', 1139, 115),
                   (pid(r, c), 'tl', 115, 115)]
        med = np.stack([np.median(original[k][y-24:y+24, x-24:x+24], axis=(0, 1))
                        for k, _, x, y in entries])
        low = (med - 40).max(axis=0)
        high = (med + 40).min(axis=0)
        feasible = low <= high
        mean = med.mean(axis=0)
        target = np.where(feasible, np.maximum(low, np.minimum(high, mean)), (low + high) * .5)
        proposed_corrections = np.clip(target[None] - med, -40, 40).astype(np.float32)
        # A large disagreement can be an incompatible material/geometry halo.
        # Do not force that crossing toward a clipped, artificial common color.
        corrections = proposed_corrections if feasible.all() else np.zeros_like(proposed_corrections)
        for (k, corner, _, _), cor in zip(entries, corrections):
            corners[k][corner] = cor
        corner_evidence.append(dict(row=r, column=c, sources=[x[0] for x in entries],
                                    sourceMedianRgb=med.tolist(), commonTargetRgb=target.tolist(),
                                    commonTargetFeasibleWithinLimit=feasible.tolist(),
                                    proposedAdditiveCorrectionsRgb=proposed_corrections.tolist(),
                                    additiveCorrectionsRgb=corrections.tolist(),
                                    status='shared_target_used' if feasible.all() else 'target_disabled_source_review_required'))


def endpoint_adjust(curve, start, end):
    """Bring each boundary profile to the shared corner target over only 96px."""
    curve = curve.copy()
    y = np.arange(1254, dtype=np.float32)
    if start is not None:
        q = np.clip((y - 115) / 96, 0, 1)
        w = 1 - q*q*(3 - 2*q)
        curve = curve * (1-w[:, None]) + start[None] * w[:, None]
    if end is not None:
        q = np.clip((1139 - y) / 96, 0, 1)
        w = 1 - q*q*(3 - 2*q)
        curve = curve * (1-w[:, None]) + end[None] * w[:, None]
    return np.clip(curve, -40, 40).astype(np.float32)


def harmonic_grid(k):
    """Maximum-principle extension: bounded boundary data, no corner summation."""
    spec = edges[k]
    cr = corners[k]
    mapping = {'left': ('tl', 'bl'), 'right': ('tr', 'br'),
               'top': ('tl', 'tr'), 'bottom': ('bl', 'br')}
    adjusted = {side: endpoint_adjust(v, cr.get(mapping[side][0]), cr.get(mapping[side][1]))
                for side, v in spec.items()}
    values = np.zeros((N, N, 3), dtype=np.float32)
    fixed = np.zeros((N, N), dtype=bool)
    for side, curve in adjusted.items():
        sample = curve[(COORD + 115).astype(int)]
        if side == 'left':
            values[:, 0] = sample; fixed[:, 0] = True
        if side == 'right':
            values[:, -1] = sample; fixed[:, -1] = True
        if side == 'top':
            values[0, :] = sample; fixed[0, :] = True
        if side == 'bottom':
            values[-1, :] = sample; fixed[-1, :] = True
    # Exactly 384px from every applicable seam is the zero correction boundary.
    dist = np.full((N, N), 9999, dtype=np.float32)
    yy, xx = np.meshgrid(COORD, COORD, indexing='ij')
    for side in spec:
        d = {'left': xx, 'right': 1024-xx, 'top': yy, 'bottom': 1024-yy}[side]
        dist = np.minimum(dist, d)
    fixed |= dist >= 384
    unknown = ~fixed
    iy, ix = np.indices((N,N)); masks=[unknown & ((iy+ix)%2==parity) for parity in [0,1]]
    degree=np.full((N,N,1),4,dtype=np.float32)
    degree[0]-=1;degree[-1]-=1;degree[:,0]-=1;degree[:,-1]-=1
    for iteration in range(3000):
        previous=values.copy()
        for mask in masks:
            total=np.zeros_like(values)
            total[1:]+=values[:-1];total[:-1]+=values[1:]
            total[:,1:]+=values[:,:-1];total[:,:-1]+=values[:,1:]
            proposed=total/degree
            values[mask]+=1.8*(proposed[mask]-values[mask])
        if np.max(np.abs(values-previous))<.00002:break
    else:raise RuntimeError('Harmonic field failed to converge')
    assert np.max(np.abs(values)) <= 40.00001
    return values, adjusted, dist


def expand_field(grid):
    # Interpolate ONLY a correction field at original pixel centers.
    q = np.clip((np.arange(1254, dtype=np.float32) - 115 + .5) / 16, 0, N-1)
    lo = np.floor(q).astype(int); hi = np.minimum(lo+1, N-1); w = q-lo
    a = grid[lo[:,None], lo[None,:]] * (1-w[None,:,None]) + grid[lo[:,None], hi[None,:]] * w[None,:,None]
    b = grid[hi[:,None], lo[None,:]] * (1-w[None,:,None]) + grid[hi[:,None], hi[None,:]] * w[None,:,None]
    return (a*(1-w[:,None,None]) + b*w[:,None,None]).astype(np.float32)


def apply_field(source, base, field):
    # The additive color delta is bounded relative to the geometry-reviewed input.
    provisional = source + np.clip(field, -40, 40)
    cumulative = np.clip(provisional-base, -40, 40)
    return np.uint8(np.clip(np.rint(base+cumulative), 0, 255))


def safety_weights(k):
    return np.ones(1254,dtype=np.float32),np.zeros(1254,dtype=np.float32)


def seam_metrics(aa, bb, axis):
    aa=aa.astype(np.float32); bb=bb.astype(np.float32)
    diff = (bb[:,95:135]-aa[:,1119:1159]) if axis == 'horizontal' else (bb[95:135]-aa[1119:1159])
    line = np.median(diff, axis=1 if axis == 'horizontal' else 0)[115:1139]
    segments = np.stack([np.median(line[i:i+64],axis=0) for i in range(0,1024,64)])
    jump = bb[115:1139,115]-aa[115:1139,1138] if axis=='horizontal' else bb[115,115:1139]-aa[1138,115:1139]
    return dict(robustSegmentMeanAbsRgb=float(np.abs(segments).mean()),
                segmentMedianBMinusARgb=segments.tolist(),
                actualAdjacentPixelMeanAbsRgb=float(np.abs(jump).mean()),
                note='Color statistics only; neither value proves geometry or texture acceptance.')


results = {}
output_records = []
for k in sorted(sources):
    source = sources[k]; basepath = source
    base = fimage(basepath)
    grid, curves, dist = harmonic_grid(k)
    wx,py=safety_weights(k)
    fieldpath = OUT / f'{k}-color-field.npz'
    np.savez_compressed(fieldpath, additiveGridRgb=grid, gridCoordinates=COORD,
                        safetyWeightX=wx,safetyProtectionY=py,
                        **{f'boundary_{s}': v for s,v in curves.items()})
    field = expand_field(grid)*(1-py[:,None,None]*(1-wx[None,:,None]))
    result = apply_field(original[k], base, field)
    dest = OUT / f'{k}-colorpass.png'
    Image.fromarray(result).save(dest)
    # Reconstruct from the saved correction grid, not from an in-memory output.
    loaded = np.load(fieldpath)
    savedfield=expand_field(loaded['additiveGridRgb'])*(1-loaded['safetyProtectionY'][:,None,None]*(1-loaded['safetyWeightX'][None,:,None]))
    rebuilt = apply_field(original[k], base, savedfield)
    assert np.array_equal(result, rebuilt)
    delta = result.astype(np.float32)-original[k]
    cumulative = result.astype(np.float32)-base
    assert np.abs(delta).max() <= 40 and np.abs(cumulative).max() <= 40
    record = dict(file=str(dest),sha256=sha(dest),createdAt=NOW,dimensions=[1254,1254],
                  classification='bounded additive color candidate; not formal acceptance',
                  operation='original selected image plus low-frequency harmonic RGB field; integer rounding and gamut clipping only',
                  derivedFrom=[dict(file=str(source),sha256=sha(source),record=record_path(source),role='geometry-reviewed selected input pixels'),
                               dict(file=str(basepath),sha256=sha(basepath),record=record_path(basepath),role='geometry-reviewed source color bound anchor')],
                  correctionEvidence=dict(file=str(fieldpath),sha256=sha(fieldpath),array='additiveGridRgb',
                                          script=str(Path(__file__)),scriptSha256=sha(__file__),
                                          reconstructionPixelsExactlyMatch=True),
                  parameters=PARAM,maximumRequestedChannelCorrection=float(np.abs(field).max()),
                  spatialSafetyMask=dict(xWeightArray='safetyWeightX',yProtectionArray='safetyProtectionY',operation='field *= 1 - yProtection*(1-xWeight); correction field only, no image pixels blended'),
                  maximumActualChannelChangeFromSelected=float(np.abs(delta).max()),
                  maximumColorChangeFromGeometryInput=float(np.abs(cumulative).max()),
                  requestedFieldCoordinateShift=[0,0],actualCoordinateShift=[0,0],
                  resampling=False,imageBlur=False,imagePixelBlending=False,
                  unchangedCoreCenter=np.array_equal(result[499:755,499:755],original[k][499:755,499:755]),
                  formalAccepted=False,externalSeams='unverified')
    write(str(dest)+'.derivation.json',record)
    output_records.append(record)
    results[k] = result


def assemble(images):
    canvas = np.zeros((4096,4096,3),dtype=np.uint8)
    for r in range(4):
        for c in range(4):
            canvas[r*1024:(r+1)*1024,c*1024:(c+1)*1024]=images[pid(r,c)][115:1139,115:1139]
    return Image.fromarray(canvas)


before=assemble(original); after=assemble(results)
candidate=OUT/'r11_c08-colorpass-candidate.png';after.save(candidate)
preview=OUT/'r11_c08-colorpass-QA-preview-1024.png';after.resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
compare=Image.new('RGB',(2048,1024));compare.paste(before.resize((1024,1024),Image.Resampling.LANCZOS),(0,0));compare.paste(Image.open(preview),(1024,0))
comparison=OUT/'before-left-after-right-QA-1024.png';compare.save(comparison)
metrics=[]
for seam in seams:
    a,b,axis=seam['a'],seam['b'],seam['axis']
    entry={**seam,'before':seam_metrics(original[a],original[b],axis),'after':seam_metrics(results[a],results[b],axis)}
    r=int(a[1])-1;c=int(a[2])-1
    box=((c+1)*1024-128,r*1024,(c+1)*1024+128,(r+1)*1024) if axis=='horizontal' else (c*1024,(r+1)*1024-128,(c+1)*1024,(r+1)*1024+128)
    strip=OUT/f'{seam["id"]}-after-100pct.png';after.crop(box).save(strip)
    entry['afterStrip']=str(strip);entry['tileBox']=list(box)
    entry['sha256']=sha(strip);entry['operation']='unscaled crop from colorpass candidate'
    entry['derivedFrom']=dict(file=str(candidate),sha256=sha(candidate))
    write(str(strip)+'.derivation.json',dict(file=str(strip),sha256=sha(strip),tileBox=list(box),operation=entry['operation'],derivedFrom=entry['derivedFrom'],classification='100 percent QA strip only'))
    metrics.append(entry)
crossings=[]
for r in range(1,4):
    for c in range(1,4):
        box=(c*1024-256,r*1024-256,c*1024+256,r*1024+256)
        dest=OUT/f'crossing-r{r}-c{c}-after-100pct.png';after.crop(box).save(dest)
        item=dict(file=str(dest),sha256=sha(dest),tileBox=list(box),operation='unscaled crop from colorpass candidate',derivedFrom=dict(file=str(candidate),sha256=sha(candidate)))
        crossings.append(item);write(str(dest)+'.derivation.json',item)
manifest=dict(schemaVersion=1,createdAt=NOW,status='color_candidate_pending_visual_and_geometry_QA',
              originalSelection=dict(file=str(SEL),sha256=sha(SEL)),tile=SELECTED['tile'],
              patches={k:str((OUT/f'{k}-colorpass.png').relative_to(TILE)) for k in sorted(sources)},
              parameters=PARAM,algorithm='robust paired overlap half-difference; 24px profile smoothing; shared four-source corner target when feasible, otherwise zero corner correction pending source review; bounded harmonic correction-field extension within 384px; no source pixel interpolation',
              candidate=dict(file=str(candidate),sha256=sha(candidate),dimensions=[4096,4096],
                             operation='16 unscaled 1024 cores, no blending',pixelCoverage=16777216),
              qaPreview=str(preview),comparisonPreview=str(comparison),cornerEvidence=corner_evidence,samplingEvidence=sampling_evidence,
              sources=[dict(patch=k,file=str(p),sha256=sha(p),record=record_path(p)) for k,p in sources.items()],
              outputRecords=[dict(file=d['file'],sha256=d['sha256'],record=d['file']+'.derivation.json') for d in output_records],
              seams=metrics,crossings=crossings,visualReview='pending',formalAccepted=False,
              complete4kCount=0,all49TilesComplete=False,externalSeams='unverified',
              capacity5000Validated=False,clientMappingValidated=False)
write(ZONE/'colorpass-selected.json',manifest)
write(OUT/'colorpass-report.json',manifest)
write(str(candidate)+'.derivation.json',dict(file=str(candidate),sha256=sha(candidate),dimensions=[4096,4096],operation='16 unscaled native-resolution core crops [115,115,1139,1139]',derivedFrom=manifest['outputRecords'],formalAccepted=False,externalSeams='unverified'))
for p,operation in [(preview,'4x downsample of colorpass candidate; QA only'),(comparison,'before-left/after-right 4x downsample; QA only')]:
    write(str(p)+'.derivation.json',dict(file=str(p),sha256=sha(p),classification='QA preview only',operation=operation,derivedFrom=[dict(file=str(candidate),sha256=sha(candidate)),dict(file=str(SEL),sha256=sha(SEL))]))
print(json.dumps(dict(candidate=str(candidate),preview=str(comparison),seams=len(metrics),
                     robustBefore=float(np.mean([x['before']['robustSegmentMeanAbsRgb'] for x in metrics])),
                     robustAfter=float(np.mean([x['after']['robustSegmentMeanAbsRgb'] for x in metrics])),
                     maximumActualChannelChange=max(d['maximumActualChannelChangeFromSelected'] for d in output_records),
                     maximumColorChangeFromGeometryInput=max(d['maximumColorChangeFromGeometryInput'] for d in output_records),
                     allFieldsReconstruct=True),indent=2))



