from native_work import *

ident = 'r03_c12_cross_03_03_bottle_paint_repair'
source = ZONE / 'tiles/r03_c12.png'
expected = 'd9f3eb6247a0d903b7a3ef59c875ce4ec28dd7c60aa56f1d4d9c9f361169473a'
assert sha(source) == expected, 'Current tile changed; re-inspect before preparing.'
guide = ZONE / 'guides' / f'{ident}.png'
prompt = ZONE / 'prompts' / f'{ident}.prompt.txt'
assert not guide.exists() and not prompt.exists(), 'Preserve prior preparation.'
native_local = [2445, 2445, 3699, 3699]
core_local = [2560, 2560, 3584, 3584]
im = Image.open(source).convert('RGB')
im.crop(tuple(native_local)).save(guide)
native_world = [47501, 10637, 48755, 11891]
core_world = [47616, 10752, 48640, 11776]
derivation = {
    'operation': 'exact1254 crop from current native4096 tile; no resampling, painting, or feathering',
    'sources': [{'file': source.as_posix(), 'sha256': expected, 'sourceCrop': native_local}],
    'nativeWorldBox': native_world,
    'coreWorldBox': core_world,
    'coreCrop': [115, 115, 1139, 1139],
    'tileLocalPaste': core_local[:2],
    'finalArt': False,
}
write(guide.with_suffix('.png.derivation.json'), derivation)
write(ZONE / 'prompts' / f'{ident}.inputs.json', [{
    'file': guide.as_posix(),
    'sha256': sha(guide),
    'role': 'only edit target; current native color and geometry authority for minimal glaze color repair',
    'derivationRecord': guide.with_suffix('.png.derivation.json').as_posix(),
}])
prompt.write_text(
    'Edit this image very minimally. Remove only the artificial rectangular color seams on the tall brown ceramic bottle: '
    'the horizontal seam at y627 and the vertical seam at x627 through the bottle belly. '
    'Make the glaze shading cross these seams smoothly, using the original adjacent colors. '
    'Keep the outer115-pixel border and all unchanged stone paving exactly as in the input. '
    'Keep the original colors at the future central1024 crop perimeter x115, x1139, y115, y1139 so the repaired area attaches invisibly. '
    'Do not change the bottle silhouette, highlight placement, texture scale, paving joints, foreground jar mouth, framing or dimensions. '
    'Do not globally brighten, darken or recolor. Output the same1254x1254 image. '
    'The only visible change should be removal of the artificial rectangular paste boundaries on the brown bottle surface.\n',
    encoding='utf-8',
)
for side, box in {
    'top': [2560, 2432, 3584, 2688],
    'bottom': [2560, 3456, 3584, 3712],
    'left': [2432, 2560, 2688, 3584],
    'right': [3456, 2560, 3712, 3584],
}.items():
    im.crop(tuple(box)).save(ZONE / 'qa' / f'{ident}.before-{side}-100pct.png')
write(ZONE / 'qa' / f'{ident}.preparation.json', {
    'id': ident,
    'preparedAtUtc': now(),
    'status': 'local_preparation_only_not_generated_not_merged',
    'imagegenCalled': False,
    'sourceFile': source.as_posix(),
    'sourceSha256': expected,
    'guide': guide.as_posix(),
    'guideSha256': sha(guide),
    'prompt': prompt.as_posix(),
    'promptSha256': sha(prompt),
    'inputs': (ZONE / 'prompts' / f'{ident}.inputs.json').as_posix(),
    'nativeWorldBox': native_world,
    'coreWorldBox': core_world,
    'coreCrop': [115, 115, 1139, 1139],
    'tileLocalPaste': core_local[:2],
    'locatedDefects': [
        {'type': 'horizontal glaze color step', 'tileLocalY': 3072, 'guideY': 627, 'visual': 'clear band across the bottle belly'},
        {'type': 'vertical glaze color step', 'tileLocalX': 3072, 'guideX': 627, 'visual': 'visible cross junction in the bottle belly'},
    ],
    'fitAssessment': 'One1024 core contains the horizontal band and central cross junction across the full bottle width. It does not contain the entire bottle height; inspect the top attachment and continuation of the vertical color seam before claiming the whole bottle passed. A second native repair may be required if the vertical band remains outside this core.',
    'preserve': ['outer115-pixel halo', 'all four central1024 attachment edges', 'stone paving and its joint positions', 'bottle contour, highlight placement and glaze texture scale', 'foreground jar mouth and its elliptical rim', 'current tile outer boundary'],
    'mandatoryReview': ['same1254 native dimensions', 'minimal geometry and color change', 'four overlay perimeter100pct crops', 'cross-junction and horizontal band', 'full-height bottle context to check residual vertical seam', 'exact source hash before merge'],
    'mergeAuthorizedByThisRecord': False,
    'tileSelectionProgressChanged': False,
    'actualModel': None,
    'actualQuality': None,
    'submittedParameters': {'model': None, 'quality': None},
})
print(guide.as_posix())
