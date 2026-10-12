"""Fresh, read-only artwork verification; reports only to this resume directory.

Reuses the established native raw/receipt checks without executing or changing
the historical audit's output section. Rebuilds candidate ancestry recursively.
"""
from pathlib import Path
from PIL import Image, ImageChops
from datetime import datetime, timezone
import hashlib
import json
import argparse
import re

BASE = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
HISTORICAL_SCRIPT = BASE / 'extension-20261011' / 'audit-extension-final.py'
RESUME_AUTHORIZATION = Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
FREEZE = BASE / 'migration-freeze-20261011.json'
historical_before = hashlib.sha256(HISTORICAL_SCRIPT.read_bytes()).hexdigest()
freeze_before = hashlib.sha256(FREEZE.read_bytes()).hexdigest()
historical_report = BASE / 'extension-20261011' / 'provenance-audit.json'
historical_report_before = hashlib.sha256(historical_report.read_bytes()).hexdigest()

# The prefix inventories and verifies selected cores, all south raw versions,
# prompts, requests, actual receipts, references, source copies and base images.
# Stop before the historical hard-coded final replay and output writer.
source = HISTORICAL_SCRIPT.read_text(encoding='utf-8-sig')
prefix = source.split('# c10: exact original-size alpha')[0]
prefix = prefix.replace("e=b/'extension-20261011'", "e=b/'resume-20261012'")
exec(compile(prefix, str(HISTORICAL_SCRIPT) + ':reused-read-only-prefix', 'exec'), globals())

check(read(RESUME_AUTHORIZATION).get('newArtworkGenerationAllowed') is True,
      'Resume authorization does not allow artwork production')
check(read(RESUME_AUTHORIZATION).get('historicalFreezeEvidenceMustRemainUnmodified') is True,
      'Resume authorization lacks historical freeze preservation policy')

dependency_checks = []
replay_cache = {}
replay_active = set()
target_derivation_checks = []
prior_report_path = BASE / 'qa' / 'provenance-audit' / 'audit-71-native.json'
prior_summary_path = BASE / 'qa' / 'provenance-audit' / 'summary-current.json'
prior_summary = read(prior_summary_path)
check(prior_summary['status'] == 'PASS_PROVENANCE' and not prior_summary['issues'] and
      prior_summary['rawCounts']['rawGeneratedImageCount'] == 71,
      'Inherited prior 71 native audit did not pass')
for prior_pick in prior_summary['finalCandidatePicks']:
    objecthash(prior_pick['candidate'], 'inherited prior candidate')

# Independently rebuild the resumed edit's cross-tile native target and its
# mechanical transparent knockout. The neighbor halo is context, not scaling.
new_repair_directory = BASE / 'r05_c10' / 'repairs' / 'east-stone-halo-v1'
derivation_path = new_repair_directory / 'target-derivation.json'
if derivation_path.is_file():
    derivation_before = len(issues)
    derivation = read(derivation_path)
    source_images = []
    for target_source in derivation['sources']:
        objecthash(target_source, 'new target source candidate')
        source_images.append(img(target_source['file']))
    check(len(source_images) == 2 and all(im.size == (4096, 4096) for im in source_images),
          'New target requires two full native candidate sources')
    canvas = Image.new('RGB', (8192, 4096))
    for index, source_image in enumerate(source_images):
        canvas.paste(source_image, (4096 * index, 0))
    rebuilt_target = canvas.crop(derivation['tileLocalBox'])
    check(rebuilt_target.size == (1254, 1254), 'New target crop native dimensions invalid')
    check(exact(rebuilt_target, img(new_repair_directory / 'target-native.png')),
          'New repair target is not pixel-exact from its candidate sources')
    rebuilt_inpaint = rebuilt_target.convert('RGBA')
    rebuilt_inpaint.paste((0, 0, 0, 0), tuple(derivation['transparentHoleNativeBox']))
    actual_inpaint = Image.open(new_repair_directory / 'target-inpaint-native.png')
    inpaint_exact = (actual_inpaint.mode == 'RGBA' and
                     actual_inpaint.size == rebuilt_inpaint.size and
                     actual_inpaint.tobytes() == rebuilt_inpaint.tobytes())
    check(inpaint_exact, 'New inpaint reference differs from the mechanical native knockout')
    check(derivation['globalPixelBox'] == [36864 + derivation['tileLocalBox'][0],
          16384 + derivation['tileLocalBox'][1], 36864 + derivation['tileLocalBox'][2],
          16384 + derivation['tileLocalBox'][3]], 'New target global crop coordinates invalid')
    check(derivation['nativePixelsResized'] is False, 'New target resized metadata invalid')
    target_derivation_checks.append({'file': str(derivation_path),
        'sha256': sha(derivation_path), 'dimensions': list(rebuilt_target.size),
        'nativeSourceCropPixelExact': exact(rebuilt_target, img(new_repair_directory / 'target-native.png')),
        'mechanicalInpaintReferencePixelExact': inpaint_exact,
        'checkPassed': len(issues) == derivation_before})

sand_directory = BASE / 'r05_c11' / 'repairs' / 'sand-halo-v1'
sand_derivation_path = sand_directory / 'target-derivation.json'
if sand_derivation_path.is_file():
    derivation_before = len(issues)
    derivation = read(sand_derivation_path)
    rebuilt_target = Image.new('RGB', tuple(derivation['nativeDimensions']))
    for target_source in derivation['sources']:
        objecthash(target_source, 'sand target source native core')
        core_crop = img(target_source['file']).crop(target_source['nativeCrop'])
        rebuilt_target.paste(core_crop, tuple(target_source['pasteAt'][:2]))
    saved_target = sand_directory / 'target-native.png'
    hashcheck(saved_target, derivation['targetSha256'], 'sand native target')
    target_exact = exact(rebuilt_target, img(saved_target))
    check(target_exact, 'Sand repair target is not exact from its recorded unscaled raw crops')
    rebuilt_inpaint = rebuilt_target.convert('RGBA')
    rebuilt_inpaint.paste((0, 0, 0, 0), tuple(derivation['transparentHoleNativeBox']))
    inpaint_path = sand_directory / 'target-inpaint-native.png'
    hashcheck(inpaint_path, derivation['inpaintSha256'], 'sand inpaint reference')
    actual_inpaint = Image.open(inpaint_path)
    inpaint_exact = (actual_inpaint.mode == 'RGBA' and
                     actual_inpaint.size == rebuilt_inpaint.size and
                     actual_inpaint.tobytes() == rebuilt_inpaint.tobytes())
    check(inpaint_exact, 'Sand inpaint reference differs from recorded mechanical knockout')
    target_derivation_checks.append({'file': str(sand_derivation_path),
        'sha256': sha(sand_derivation_path), 'dimensions': list(rebuilt_target.size),
        'nativeSourceCropPixelExact': target_exact,
        'mechanicalInpaintReferencePixelExact': inpaint_exact,
        'checkPassed': len(issues) == derivation_before})


def original_core_replay(tile):
    result = Image.new('RGB', (4096, 4096))
    for row in range(1, 5):
        for column in range(1, 5):
            selection = read(BASE / tile / 'records' / f'p{row}{column}.selection.json')
            result.paste(img(selection['file']).crop((115, 115, 1139, 1139)),
                         ((column - 1) * 1024, (row - 1) * 1024))
    return result


def replay_proposal(step, replay, label):
    hashcheck(step['proposal'], step['proposalSha256'], label + ' proposal')
    proposal = read(step['proposal'])
    for key in ['outputNative', 'outputCore', 'baseNative', 'restoredGuide',
                'compositeBase', 'repairRaw', 'mask']:
        objecthash(proposal[key], label + ' ' + key)
    reconstructed = img(proposal['baseNative']['file'])
    guide = img(proposal['restoredGuide']['file'])
    reconstructed.paste(guide.crop(proposal['restoredGuide']['crop']),
                        tuple(proposal['restoredGuide']['pasteAt']))
    check(exact(reconstructed, img(proposal['compositeBase']['file'])),
          label + ' composite base replay differs')
    mask = Image.open(proposal['mask']['file']).convert('L')
    repair = img(proposal['repairRaw']['file'])
    check(repair.size == reconstructed.size == mask.size == (1254, 1254),
          label + ' proposal native dimensions invalid')
    reconstructed = Image.composite(repair, reconstructed, mask)
    check(exact(reconstructed, img(proposal['outputNative']['file'])),
          label + ' native proposal replay differs')
    core = reconstructed.crop(proposal['coreCrop'])
    check(core.size == (1024, 1024), label + ' proposal core dimensions invalid')
    check(exact(core, img(step['source'])), label + ' proposal crop replay differs')
    check(exact(core, img(proposal['outputCore']['file'])),
          label + ' saved proposal output core differs')
    replay.paste(core, tuple(proposal['tileDestination']))


def replay_candidate(path):
    path = Path(path)
    key = norm(path)
    if key in replay_cache:
        return replay_cache[key].copy()
    if key in replay_active:
        raise ValueError('Candidate ancestry cycle: ' + str(path))
    replay_active.add(key)
    before = len(issues)
    manifest_path = path.with_suffix('.manifest.json')
    if not manifest_path.is_file():
        missing.append(str(manifest_path))
        issue('Missing candidate manifest: ' + str(manifest_path))
        replay_active.remove(key)
        return img(path)
    manifest = read(manifest_path)
    hashcheck(path, manifest['sha256'], 'candidate')
    with Image.open(path) as candidate:
        dimensions = list(candidate.size)
    check(dimensions == manifest.get('dimensions') == [4096, 4096],
          'Candidate dimensions invalid: ' + str(path))
    tile = path.parent.parent.name
    steps_checked = []

    if path.name.endswith('-candidate-v1.png'):
        replay = original_core_replay(tile)
        operation = '16 original unscaled 1024 core crops'
        check(exact(replay, img(path)), 'Base core replay differs: ' + str(path))
    elif 'steps' in manifest:
        base_path = Path(manifest.get('base', manifest.get('baseCandidate', '')))
        base_hash = manifest.get('baseSha256', manifest.get('baseCandidateSha256'))
        hashcheck(base_path, base_hash, 'recursive candidate base')
        if 'baseManifest' in manifest:
            hashcheck(manifest['baseManifest'], manifest['baseManifestSha256'],
                      'recursive base manifest')
        replay = replay_candidate(base_path)
        check(manifest.get('nativePixelsResized') is False,
              'Candidate native resize metadata invalid: ' + str(manifest_path))
        check(manifest.get('overviewPixelsUsedInFinal') is False,
              'Candidate overview pixels metadata invalid: ' + str(manifest_path))
        check(manifest.get('actualModel') is None and manifest.get('actualQuality') is None,
              'Candidate model/quality metadata must remain unknown: ' + str(manifest_path))
        for index, step in enumerate(manifest['steps'], 1):
            step_before = len(issues)
            step_extra = {}
            label = tile + ' ' + step.get('name', f'step-{index}')
            hashcheck(step['source'], step['sourceSha256'], label + ' source')
            if 'proposal' in step and 'mask' not in step:
                replay_proposal(step, replay, label)
            else:
                if 'proposal' in step and 'proposalSha256' in step:
                    hashcheck(step['proposal'], step['proposalSha256'], label + ' proposal')
                if 'generationRecord' in step:
                    hashcheck(step['generationRecord'], step['generationRecordSha256'],
                              label + ' generation record')
                    generation = read(step['generationRecord'])
                    check(norm(generation['file']) == norm(step['source']) and
                          generation['sha256'] == step['sourceSha256'],
                          label + ' source differs from actual generation record')
                hashcheck(step['mask'], step['maskSha256'], label + ' mask')
                box = step['tileBox']
                mask = Image.open(step['mask']).convert('L')
                source_image = img(step['source'])
                check(source_image.size == mask.size ==
                      (box[2] - box[0], box[3] - box[1]) == (1254, 1254),
                      label + ' native dimensions invalid')
                local = Image.composite(source_image, replay.crop(box), mask)
                if step.get('name') == 'sand-halo-v1' and 'proposal' in step:
                    proposal = read(step['proposal'])
                    for proposal_key in ['nativeRepair', 'mask', 'target', 'localComposite']:
                        objecthash(proposal[proposal_key], label + ' saved ' + proposal_key)
                    preview = img(proposal['localComposite']['file'])
                    preview_replay = Image.composite(source_image, img(proposal['target']['file']), mask)
                    check(exact(preview, preview_replay), label + ' saved local preview replay differs')
                    preview_difference = np.any(np.array(preview) != np.array(local), axis=2)
                    alpha = np.array(mask)
                    contributing_exact = not np.any(preview_difference & (alpha > 0))
                    check(contributing_exact, label + ' preview pixels differ within the contribution mask')
                    outside_difference_count = int(np.count_nonzero(preview_difference & (alpha == 0)))
                    step_extra = {'savedLocalPreviewReplayExact': exact(preview, preview_replay),
                                  'previewContributingPixelsMatchFinal': contributing_exact,
                                  'previewContextDifferencesOutsideMask': outside_difference_count}
                    if outside_difference_count:
                        notes.append('Historical sand proposal preview uses original-core context outside '
                                     'the applied mask. All preview pixels under positive alpha match the '
                                     'final v2-based composition; final v3 independently replays exactly.')
                replay.paste(local, (box[0], box[1]))
            steps_checked.append({'name': step.get('name', 'p11-north-net-v2'),
                                  'source': step['source'], 'mask': step.get('mask'),
                                  'checkPassed': len(issues) == step_before, **step_extra})
        operation = 'recursive base replay then ordered native mask steps'
    elif 'repairRecord' in manifest:
        # Historical c10 v2 predates the common ordered-step manifest schema.
        base_path = Path(manifest['baseCandidate'])
        hashcheck(base_path, manifest['baseCandidateSha256'], 'c10 v2 base')
        replay = replay_candidate(base_path)
        generation_path = Path(manifest['repairRecord'])
        generation = read(generation_path)
        objecthash(generation['reference'], 'c10 v2 exact target')
        objecthash(generation['mask'], 'c10 v2 alpha mask')
        hashcheck(generation['file'], generation['sha256'], 'c10 v2 raw repair')
        box = generation['targetTileBox']
        target = img(generation['reference']['file'])
        check(exact(target, replay.crop(box)), 'c10 v2 target differs from candidate crop')
        repair = img(generation['file'])
        mask = Image.open(generation['mask']['file']).convert('L')
        check(target.size == repair.size == mask.size == (1254, 1254),
              'c10 v2 repair native dimensions invalid')
        local = Image.composite(repair, target, mask)
        check(exact(local, img(generation_path.parent / 'after-local-composite-native.png')),
              'c10 v2 saved local composite replay differs')
        replay.paste(local, (box[0], box[1]))
        application = read(generation_path.parent / 'repair-application.json')
        hashcheck(path, application['candidateSha256'], 'c10 v2 repair application')
        steps_checked.append({'name': generation_path.parent.name,
                              'source': generation['file'], 'mask': generation['mask']['file'],
                              'checkPassed': len(issues) == before})
        operation = 'recursive base replay then original-size native alpha composite'
    else:
        issue('Unsupported candidate replay manifest: ' + str(manifest_path))
        replay = img(path)
        operation = 'unsupported'

    matched = exact(replay, img(path))
    check(matched, 'Full candidate native replay differs: ' + str(path))
    result = {'tile': tile, 'candidate': str(path), 'sha256': sha(path),
              'manifest': str(manifest_path), 'manifestSha256': sha(manifest_path),
              'dimensions': dimensions, 'repairSteps': len(steps_checked),
              'steps': steps_checked, 'operation': operation,
              'fullNativePixelReplayExact': matched, 'checkPassed': len(issues) == before}
    dependency_checks.append(result)
    replay_cache[key] = replay.copy()
    replay_active.remove(key)
    return replay


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate', action='append', default=[], metavar='TILE=VERSION',
                    help='Explicit current version; otherwise use highest fully saved PNG/manifest pair.')
arguments = parser.parse_args()
requested_versions = {}
for candidate_argument in arguments.candidate:
    candidate_tile, candidate_version = candidate_argument.split('=', 1)
    if candidate_tile not in ['r05_c10', 'r05_c11']:
        parser.error('Candidate tile must be r05_c10 or r05_c11')
    requested_versions[candidate_tile] = int(candidate_version)
final_paths = []
current_selections = []
for tile in ['r05_c10', 'r05_c11']:
    if tile in requested_versions:
        version = requested_versions[tile]
    else:
        available_versions = []
        for saved_candidate in (BASE / tile / 'candidate').glob(f'{tile}-4096-candidate-v*.png'):
            match = re.fullmatch(re.escape(tile) + r'-4096-candidate-v(\d+)\.png', saved_candidate.name)
            if match and saved_candidate.with_suffix('.manifest.json').is_file():
                available_versions.append(int(match.group(1)))
        version = max(available_versions, default=3)
    candidate_path = BASE / tile / 'candidate' / f'{tile}-4096-candidate-v{version}.png'
    final_paths.append(candidate_path)
    current_selections.append({'tile': tile, 'version': version,
                               'candidate': str(candidate_path),
                               'selectionBasis': 'explicit_version' if tile in requested_versions
                               else 'highest_fully_saved_candidate_and_manifest_pair'})
for candidate_path in final_paths:
    if not candidate_path.is_file():
        missing.append(str(candidate_path))
        issue('Missing current candidate: ' + str(candidate_path))
        continue
    try:
        replay_candidate(candidate_path)
    except Exception as exc:
        issue('Candidate replay exception ' + str(candidate_path) + ': ' + repr(exc))

replays = [next(entry for entry in dependency_checks
                if norm(entry['candidate']) == norm(candidate_path))
           for candidate_path in final_paths
           if any(norm(entry['candidate']) == norm(candidate_path) for entry in dependency_checks)]
check(len(replays) == 2, 'Latest final candidate checks must include both south candidates')
check(len(cores) == 32, 'Selected core total is not 32')

receipt_census = []
for tile in ['r05_c10', 'r05_c11']:
    receipt_census.extend((BASE / tile / 'records').glob('*.receipt.json'))
    receipt_census.extend((BASE / tile / 'repairs').rglob('*receipt.json'))
recorded_receipts = {norm(entry['receiptFile']) for entry in raw if 'receiptFile' in entry}
for receipt_path in receipt_census:
    if norm(receipt_path) not in recorded_receipts:
        issue('Receipt not represented by raw inventory: ' + str(receipt_path))

check(sha(HISTORICAL_SCRIPT) == historical_before, 'Historical audit script changed during audit')
check(sha(historical_report) == historical_report_before, 'Historical audit report changed during audit')
check(sha(FREEZE) == freeze_before, 'Historical migration freeze changed during audit')
raw_core_count = sum(entry['kind'] == 'core' for entry in raw)
repair_count = sum(entry['kind'] == 'repair' for entry in raw)
report = {
    'schemaVersion': 2,
    'auditedAt': datetime.now(timezone.utc).isoformat(),
    'status': 'PASS' if not issues and not missing else 'ISSUES',
    'selectedCoreCount': len(cores), 'requiredCoreCount': 32,
    'newRawCount': len(raw), 'newCoreRawCount': raw_core_count,
    'newRepairRawCount': repair_count, 'priorRawCount': 71,
    'totalRawCount': 71 + len(raw),
    'selectedCores': cores, 'rawGenerations': raw,
    'candidateChecks': candidates, 'finalCandidateChecks': replays,
    'currentCandidateSelections': current_selections,
    'recursiveCandidateDependencyChecks': dependency_checks,
    'resumedTargetDerivationChecks': target_derivation_checks,
    'issues': issues, 'missing': missing, 'notes': notes,
    'actualModel': None, 'actualQuality': None, 'formalAcceptedCount': 0,
    'receiptInventoryCount': len(receipt_census),
    'receiptInventoryMatchedToRaw': len(receipt_census) == len(recorded_receipts) == len(raw),
    'uniqueNewRawShaCount': len({entry['sha256'] for entry in raw}),
    'newRawCountSinceResume': len(raw) - 45,
    'inheritedPriorAudit': {'file': str(prior_report_path), 'sha256': sha(prior_report_path),
                           'status': prior_summary['status'], 'rawCount': 71,
                           'summary': str(prior_summary_path), 'summarySha256': sha(prior_summary_path)},
    'resumeAuthorization': {'file': str(RESUME_AUTHORIZATION), 'sha256': sha(RESUME_AUTHORIZATION)},
    'historicalBaselinePreserved': {
        'freeze': {'file': str(FREEZE), 'sha256': freeze_before},
        'auditScript': {'file': str(HISTORICAL_SCRIPT), 'sha256': historical_before},
        'auditReport': {'file': str(historical_report), 'sha256': historical_report_before}},
    'scope': 'Fresh verification of all 32 selected south cores and every south raw core/repair version, including rejected versions. Real prompts/requests/receipts, reference hashes, native dimensions, and explicit unknown model/quality metadata are checked. Each current candidate is independently rebuilt recursively from original selected 1024 core crops and all native repair steps. Current versions can be explicitly selected; otherwise the highest fully saved PNG/manifest pair is audited. Prior 71 raw outputs passed in historical audits and are carried forward. Visual seam QA is separate.'
}
(OUT / 'provenance-audit.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: report[key] for key in ['status', 'selectedCoreCount', 'newRawCount',
      'newCoreRawCount', 'newRepairRawCount', 'totalRawCount', 'issues', 'missing', 'notes']}))
