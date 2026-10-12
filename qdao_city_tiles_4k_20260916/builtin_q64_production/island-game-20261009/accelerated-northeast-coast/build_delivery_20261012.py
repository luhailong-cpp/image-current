"""Build a new compact delivery only after final QA and integrity audit pass.

Usage: python -B build_delivery_20261012.py --integrity-report <JSON inside B>
       --r01-c14-final-review <JSON inside B>

This script does not generate artwork, change production state, upload, or use Git.
Existing source files remain untouched. The output directory must not exist.
"""
from pathlib import Path, PurePosixPath, PureWindowsPath
from datetime import datetime, timezone
from PIL import Image
import argparse
import hashlib
import io
import json
import re
import zipfile

B = Path(__file__).resolve().parent
OUT = B / 'delivery-20261012'
ORDER = ['r02_c13', 'r02_c14', 'r01_c13', 'r01_c14']
WORLD = {
    'r01_c13': [49152, 0, 53248, 4096],
    'r01_c14': [53248, 0, 57344, 4096],
    'r02_c13': [49152, 4096, 53248, 8192],
    'r02_c14': [53248, 4096, 57344, 8192],
}
PREVIEW_AT = {'r01_c13': (0, 0), 'r01_c14': (1024, 0),
              'r02_c13': (0, 1024), 'r02_c14': (1024, 1024)}
CROP = [115, 115, 1139, 1139]
ARCHIVE_NAME = 'northeast-coast-4tiles-4096.zip'
ABS_PATH_PATTERN = re.compile(r'(?:[A-Za-z]:[/\\]|file://|(?<!:)\\\\[^\\\s]+\\)')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()

def sha_file(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def path_in_b(value):
    path = Path(value)
    if not path.is_absolute():
        path = B / path
    path = path.resolve(strict=True)
    require(path.is_relative_to(B.resolve()), f'Input is outside production root: {path.name}')
    require(path.is_file(), f'Input is not a file: {path.name}')
    return path

def relative(path):
    return path.resolve().relative_to(B.resolve()).as_posix()

def safe_member(name):
    p = PurePosixPath(name)
    require(name and not p.is_absolute() and '..' not in p.parts and '\\' not in name
            and ':' not in name and all(part not in ('', '.') for part in p.parts),
            f'Unsafe archive entry: {name}')
    return name

INPUT_HASHES = {}

def capture(value):
    path = path_in_b(value)
    digest = sha_file(path)
    previous = INPUT_HASHES.setdefault(path, digest)
    require(previous == digest, f'Input changed during validation: {relative(path)}')
    return path, digest

def load(value):
    path, digest = capture(value)
    return json.loads(path.read_text(encoding='utf-8-sig')), path, digest

def portable(value, key=None):
    """Normalize archival JSON copies; never modify historical JSON source bytes."""
    if isinstance(value, dict):
        result = {}
        for child_key, child_value in value.items():
            if child_key in ('output_hint', 'image_url', 'imageData', 'imageBase64'):
                result[child_key + 'OmittedForPortableArchive'] = True
                continue
            result[child_key] = portable(child_value, child_key)
        return result
    if isinstance(value, list):
        return [portable(item, key) for item in value]
    if not isinstance(value, str):
        return value
    if ABS_PATH_PATTERN.search(value):
        windows_path = PureWindowsPath(value)
        if windows_path.is_absolute() and '\n' not in value and '\r' not in value:
            candidate = Path(value).resolve()
            if candidate.is_relative_to(B.resolve()):
                return candidate.relative_to(B.resolve()).as_posix()
            return {'externalPathOmitted': True, 'basename': windows_path.name,
                    'includedInPackage': False, 'originalPathUtf8Sha256': sha_bytes(value.encode('utf-8'))}
        return {'absolutePathTextOmitted': True,
                'originalTextUtf8Sha256': sha_bytes(value.encode('utf-8'))}
    if value.startswith('/') and not value.startswith('//'):
        return {'externalPathOmitted': True, 'basename': PurePosixPath(value).name,
                'includedInPackage': False, 'originalPathUtf8Sha256': sha_bytes(value.encode('utf-8'))}
    return value

def json_bytes(value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    require(not ABS_PATH_PATTERN.search(data.decode('utf-8')), 'Absolute path survived JSON normalization')
    return data

ENTRIES = {}
ENTRY_METADATA = {}

def add_original(value, role):
    path, digest = capture(value)
    name = safe_member(relative(path))
    if name in ENTRIES:
        require(ENTRY_METADATA[name]['sha256'] == digest, f'Duplicate archive entry conflict: {name}')
        return name
    ENTRIES[name] = path
    ENTRY_METADATA[name] = {'file': name, 'sha256': digest, 'bytes': path.stat().st_size,
                            'role': role, 'transformation': 'original_bytes'}
    return name

def add_record(value, role):
    record, path, original_digest = load(value)
    name = safe_member(relative(path))
    data = json_bytes(portable(record))
    digest = sha_bytes(data)
    if name in ENTRIES:
        require(ENTRY_METADATA[name]['sha256'] == digest, f'Duplicate normalized entry conflict: {name}')
        return name
    ENTRIES[name] = data
    ENTRY_METADATA[name] = {'file': name, 'sha256': digest, 'bytes': len(data), 'role': role,
                            'transformation': 'portable_json_path_normalization',
                            'originalFileSha256': original_digest}
    return name

def selected_qa_sources(report):
    values = report.get('sources')
    if not values and report.get('sourceManifest'):
        values = load(report['sourceManifest'])[0]['sources']
    require(isinstance(values, list), 'Final QA report lacks selected source manifest')
    return {Path(item['file']).stem: item for item in values}

def archive_qa_source_manifests(report):
    """Include JSON source lists referenced by final QA, without their raster files."""
    found = set()
    def visit(value):
        if isinstance(value, dict):
            for key,item in value.items():
                if key == 'sourceManifest' and isinstance(item,str) and item:
                    path = path_in_b(item)
                    require(path.suffix.lower() == '.json', 'QA sourceManifest must be a JSON inside B')
                    found.add(path)
                else:
                    visit(item)
        elif isinstance(value,list):
            for item in value:
                visit(item)
    visit(report)
    result = []
    for path in sorted(found):
        entry = add_record(path, 'final QA selected source manifest')
        result.append({'file':entry,'originalSha256':ENTRY_METADATA[entry]['originalFileSha256'],
                       'archivedSha256':ENTRY_METADATA[entry]['sha256']})
    return result

def validate_nested_source_hashes(value, selected_hashes):
    if isinstance(value, dict):
        for label in ('a','b'):
            if isinstance(value.get(label), str) and isinstance(value.get(label+'Sha256'),str):
                ident = Path(value[label]).stem
                if re.fullmatch(r'(?:'+'|'.join(ORDER)+r')_p\d+_\d+(?:_v\d+)?',ident):
                    require(ident in selected_hashes and value[label+'Sha256'] == selected_hashes[ident],
                            f'QA uses stale paired source hash: {ident}')
        if isinstance(value.get('file'), str) and isinstance(value.get('sha256'), str):
            ident = Path(value['file']).stem
            if re.fullmatch(r'(?:'+'|'.join(ORDER)+r')_p\d+_\d+(?:_v\d+)?',ident):
                require(ident in selected_hashes and value['sha256'] == selected_hashes[ident],
                        f'QA uses stale source hash: {ident}')
        for item in value.values():
            validate_nested_source_hashes(item, selected_hashes)
    elif isinstance(value, list):
        for item in value:
            validate_nested_source_hashes(item, selected_hashes)

def require_passed_items(items, count, label):
    require(isinstance(items,list) and len(items) == count, f'{label}: incomplete evidence items')
    for item in items:
        require(str(item.get('status','')).startswith('passed'), f'{label}: an evidence item has not passed')
        evidence_path = item.get('evidence',item.get('file'))
        require(isinstance(evidence_path,str), f'{label}: evidence path missing')
        _, digest = capture(evidence_path)
        if item.get('evidenceSha256'):
            require(digest == item['evidenceSha256'], f'{label}: evidence raster hash changed')

def expected_geometry(ident):
    m = re.fullmatch(r'r(\d+)_c(\d+)_p(\d+)_(\d+)(?:_v\d+)?', ident)
    require(m is not None, f'Invalid selected core ID: {ident}')
    tr, tc, pr, pc = map(int, m.groups())
    require((tr, tc) in ((1,13),(1,14),(2,13),(2,14)) and 1 <= pr <= 4 and 1 <= pc <= 4,
            f'Unexpected coordinate: {ident}')
    x, y = (tc-1)*4096+(pc-1)*1024, (tr-1)*4096+(pr-1)*1024
    return {'id': ident, 'coreWorldBox': [x,y,x+1024,y+1024],
            'nativeWorldBox': [x-115,y-115,x+1139,y+1139], 'coreCrop': CROP}, [(pc-1)*1024,(pr-1)*1024]

def verify_integrity_report(report, candidate_info, selected_hashes, final_qa_path):
    summary = report.get('summary', {})
    require(summary.get('candidateTilesAudited') == 4 and summary.get('nativeCoresAudited') == 64
            and summary.get('allAuditedCandidatesPassed') is True and summary.get('failureCount') == 0,
            'Integrity report must certify four candidates and 64 selected cores with zero failures')
    require(summary.get('productionAll4Complete') is True and not report.get('problems'),
            'Integrity report does not certify completed four-tile production')
    require(report.get('selectionSnapshot', {}).get('changedDuringAudit') is False,
            'Integrity audit observed changing current-selection')
    audited = {item['tileId']: item for item in report.get('tiles', [])}
    require(set(audited) == set(ORDER), 'Integrity report tile set differs from assignment')
    audited_ids = set()
    for tile in ORDER:
        item = audited[tile]
        require(item.get('passed') is True and all(item.get('checks', {}).values()),
                f'Integrity tile checks failed: {tile}')
        require(item.get('sha256') == candidate_info[tile]['sha256']
                and item.get('selectedCores') == candidate_info[tile]['selectedCores'],
                f'Integrity candidate or selected grid is stale: {tile}')
        require(len(item.get('coreChecks', [])) == 16, f'Integrity source checks are incomplete: {tile}')
        for core in item['coreChecks']:
            require(core.get('passed') is True and all(core.get('checks', {}).values())
                    and core.get('sha256') == selected_hashes.get(core['id']),
                    f'Integrity core check is stale or failed: {core["id"]}')
            audited_ids.add(core['id'])
        qa_path = path_in_b(item['qaReport'])
        require(sha_file(qa_path) == item['qaReportSha256'], f'Integrity QA report changed: {tile}')
        if tile == 'r01_c14':
            require(qa_path == final_qa_path, 'Integrity audit must use the supplied final r01_c14 QA report')
    require(audited_ids == set(selected_hashes), 'Integrity report does not cover exactly the 64 selected IDs')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrity-report', required=True, help='Four-candidate/64-core integrity audit JSON inside B.')
    parser.add_argument('--r01-c14-final-review', required=True, help='Authoritative final r01_c14 QA JSON inside B.')
    args = parser.parse_args()
    require(not OUT.exists(), 'delivery-20261012 already exists; no files may be overwritten')
    integrity, integrity_path, integrity_hash = load(args.integrity_report)
    c14_qa, c14_qa_path, _ = load(args.r01_c14_final_review)
    qa_paths = {
        'r02_c13': path_in_b('qa/audit-final-r02-c13/final-review.json'),
        'r02_c14': path_in_b('qa/audit-resume-20261012/r02_c14-final-review.json'),
        'r01_c13': path_in_b('qa/audit-final-20261012/r01_c13-current-final-review.json'),
        'r01_c14': c14_qa_path,
    }
    qa_reports = {tile: load(path)[0] for tile, path in qa_paths.items()}
    require(len({path for path in qa_paths.values()}) == 4, 'Four distinct final QA reports are required')
    selection, selection_path, selection_hash = load('current-selection-20261012.json')
    candidates = {item['tileId']: item for item in selection.get('candidates', [])}
    require(len(selection.get('candidates', [])) == 4 and set(candidates) == set(ORDER),
            'Current selection must contain exactly four candidate tiles')
    require(selection.get('formalAcceptedCount') == 0, 'Formal acceptance must remain zero')
    require(set(selection.get('native', {})) == set(ORDER), 'Native selection tile set must match assignment')
    preview = Image.new('RGB', (2048,2048))
    tiles = []
    selected_hashes = {}
    candidate_info = {}
    for tile in ORDER:
        selected = candidates[tile]
        candidate_path, candidate_hash = capture(selected['file'])
        require(candidate_path == path_in_b(f'candidates/{tile}.4096-candidate.png'),
                f'Unexpected candidate path for {tile}')
        assembly, assembly_path, assembly_hash = load(candidate_path.with_suffix('.png.assembly.json'))
        require(assembly.get('tileId') == tile and candidate_hash == selected.get('sha256') == assembly.get('sha256'),
                f'Candidate hashes disagree: {tile}')
        require(selected.get('dimensions') == assembly.get('dimensions') == [4096,4096],
                f'Candidate dimensions disagree: {tile}')
        require(assembly.get('formalAccepted') is False and selected.get('formalAccepted') is False
                and assembly.get('resizedFinalPixels') is False, f'Candidate flags invalid: {tile}')
        grid = assembly.get('selectedCores')
        require(grid == selected.get('selectedCores') and len(grid) == 4 and all(len(row) == 4 for row in grid),
                f'Selected grid must match current selection: {tile}')
        flattened = [ident for row in grid for ident in row]
        require(len(set(flattened)) == 16 and len(assembly.get('sources', [])) == 16,
                f'Candidate must have 16 unique selected cores: {tile}')
        native_index = {item['id']: item for item in selection['native'][tile]}
        require(len(selection['native'][tile]) == 16 and set(native_index) == set(flattened),
                f'Native selection differs from candidate: {tile}')
        qa = qa_reports[tile]
        require(qa.get('formalAccepted') is False and not qa.get('blockingIssues'),
                f'Final QA has blocking issues or formal acceptance: {tile}')
        qa_sources = selected_qa_sources(qa)
        require(set(qa_sources) == set(flattened), f'Final QA selected sources differ: {tile}')
        qs = qa.get('summary', {})
        internal_count = qs.get('internalSeamsPassed', qa.get('internalSeamsReviewed'))
        crossing_count = qs.get('internalCrossingsPassed', qa.get('nativeCrossJunctionsReviewed'))
        require(internal_count == 24 and crossing_count == 9, f'Final QA must pass 24 joins and 9 crossings: {tile}')
        require(qs.get('internalSeamsTotal',24) == 24 and qs.get('internalCrossingsTotal',9) == 9
                and not qs.get('blockingIssues'), f'Final QA totals or summary blocking state differ: {tile}')
        internal_items = qa.get('internalSeams')
        if internal_items is None:
            internal_items = [item for item in qa.get('seams',[]) if item.get('scope') == 'internal']
        crossing_items = qa.get('internalCrossings',qa.get('crossings',qa.get('crosses')))
        require_passed_items(internal_items,24,f'{tile} internal joins')
        require_passed_items(crossing_items,9,f'{tile} internal crossings')
        if qa.get('candidate'):
            require(qa['candidate'].get('sha256') == candidate_hash
                    and qa['candidate'].get('selectedCores', qa.get('selectedCores')) == grid, f'QA candidate snapshot differs: {tile}')
        if 'selectedCores' in qa:
            require(qa['selectedCores'] == grid, f'Final QA grid differs: {tile}')
        with Image.open(candidate_path) as opened:
            require(opened.size == (4096,4096) and opened.mode == 'RGB', f'Unexpected candidate image format: {tile}')
            candidate = opened.copy()
        rebuilt = Image.new('RGB', (4096,4096))
        sources = []
        for source in assembly['sources']:
            native_path, native_hash = capture(source['file'])
            ident = native_path.stem
            require(ident in native_index and ident not in selected_hashes and ident.startswith(tile+'_p'),
                    f'Unexpected or duplicate native source: {ident}')
            record, record_path, record_hash = load(source['generationRecord'])
            geo, paste = expected_geometry(ident)
            require(record_path == native_path.with_suffix('.png.generation.json') and
                    native_hash == source.get('sha256') == record.get('sha256') == native_index[ident].get('sha256')
                    == qa_sources[ident].get('sha256'), f'Selected source hashes disagree: {ident}')
            require(all(record.get(k) == v for k,v in geo.items()) and source.get('sourceCrop') == CROP
                    and source.get('pasteAt') == paste and grid[paste[1]//1024][paste[0]//1024] == ident,
                    f'Exact core geometry differs: {ident}')
            require(record.get('resizedAfterGeneration') is False and record.get('route') == 'builtin'
                    and record.get('tool') == 'image_gen.imagegen' and record.get('actualModel') == 'unknown'
                    and record.get('actualQuality') == 'unknown', f'Native provenance flags differ: {ident}')
            with Image.open(native_path) as opened:
                require(opened.size == (1254,1254) and opened.mode == record.get('mode'),
                        f'Native decode dimensions/mode differ: {ident}')
                native = opened.convert('RGB')
            require(source.get('nativeSize') == record.get('size') == [record.get('nativeWidth'),record.get('nativeHeight')]
                    == native_index[ident].get('dimensions') == [1254,1254], f'Native dimension records differ: {ident}')
            core = native.crop(tuple(CROP))
            require(core.size == (1024,1024), f'Core is not 1024 square: {ident}')
            target = candidate.crop((paste[0],paste[1],paste[0]+1024,paste[1]+1024))
            require(target.tobytes() == core.tobytes(), f'Candidate core pixels differ from exact native crop: {ident}')
            rebuilt.paste(core, tuple(paste))
            prompt_path, prompt_hash = capture(record['prompt'])
            require(prompt_hash == record.get('promptSha256'), f'Prompt hash differs: {ident}')
            receipt, receipt_path, receipt_hash = load(record['receipt'])
            require(receipt.get('actualModel', 'unknown') == 'unknown' and receipt.get('actualQuality', 'unknown') == 'unknown',
                    f'Receipt actual model/quality unexpectedly differs: {ident}')
            generation_entry = add_record(record_path, 'selected native generation provenance')
            prompt_entry = add_original(prompt_path, 'exact submitted prompt')
            require(not ABS_PATH_PATTERN.search(prompt_path.read_text(encoding='utf-8-sig')),
                    f'Prompt contains an absolute path; compact archive requires portable text: {ident}')
            receipt_entry = add_record(receipt_path, 'built-in tool receipt provenance')
            selected_hashes[ident] = native_hash
            sources.append({'id': ident, 'file': relative(native_path), 'sha256': native_hash,
                'dimensions': [1254,1254], 'includedInArchive': False, 'retainedAtProductionRoot': True,
                'generationRecord': generation_entry, 'generationRecordOriginalSha256': record_hash,
                'generationRecordArchivedSha256': ENTRY_METADATA[generation_entry]['sha256'],
                'sourceCrop': CROP, 'pasteAt': paste, 'coreRgbPixelSha256': sha_bytes(core.tobytes()),
                'prompt': prompt_entry, 'promptSha256': prompt_hash, 'receipt': receipt_entry,
                'receiptOriginalSha256': receipt_hash, 'receiptArchivedSha256': ENTRY_METADATA[receipt_entry]['sha256'],
                'actualModel': 'unknown', 'actualQuality': 'unknown', 'resizedAfterGeneration': False})
        require(set(source['id'] for source in sources) == set(flattened)
                and candidate.tobytes() == rebuilt.tobytes(), f'Full candidate reconstruction differs: {tile}')
        preview.paste(candidate.resize((1024,1024), Image.Resampling.LANCZOS), PREVIEW_AT[tile])
        png_entry = add_original(candidate_path, 'final 4096 candidate artwork')
        assembly_entry = add_record(assembly_path, 'exact unscaled assembly provenance')
        qa_entry = add_record(qa_paths[tile], 'latest authoritative final tile QA report')
        qa_source_manifests = archive_qa_source_manifests(qa)
        candidate_info[tile] = {'sha256':candidate_hash, 'selectedCores':grid}
        tiles.append({'tileId':tile, 'file':png_entry, 'sha256':candidate_hash,
            'fileBytes':candidate_path.stat().st_size,'dimensions':[4096,4096],'mode':'RGB','tileWorldBox':WORLD[tile],
            'assemblyRecord':assembly_entry,'assemblyRecordOriginalSha256':assembly_hash,
            'assemblyRecordArchivedSha256':ENTRY_METADATA[assembly_entry]['sha256'],
            'method':'4x4 exact unscaled 1024 cores cropped from measured 1254 native inputs',
            'nativeInputDimensions':[1254,1254],'coreDimensions':[1024,1024],
            'selectedCores':grid,'sources':sources,'resizedFinalPixels':False,
            'candidateRgbPixelSha256':sha_bytes(candidate.tobytes()),
            'qaReport':qa_entry,'qaReportOriginalSha256':INPUT_HASHES[qa_paths[tile]],
            'qaReportArchivedSha256':ENTRY_METADATA[qa_entry]['sha256'],
            'qaSourceManifests':qa_source_manifests,
            'qaStatus':qa.get('status'),'formalAccepted':False})
    require(len(tiles) == 4 and len(selected_hashes) == 64, 'Expected four candidates and 64 unique sources')
    for tile, qa in qa_reports.items():
        for key in ('seams','internalSeams','crosses','crossings','internalCrossings','externalSeams',
                    'southExternalSeams','westExternalSeams','regionCenterCrossing'):
            validate_nested_source_hashes(qa.get(key, []), selected_hashes)
    c14_summary = c14_qa.get('summary', {})
    require(c14_summary.get('southExternalSegmentsPassed') == 4
            and c14_summary.get('westExternalSegmentsPassed') == 4,
            'Final r01_c14 QA must pass all four south and all four west region joins')
    require(qa_reports['r01_c13'].get('summary', {}).get('southExternalSegmentsPassed') == 4
            and qa_reports['r02_c14'].get('summary', {}).get('westExternalSegmentsPassed') == 4,
            'Existing QA must pass the other two four-segment region borders')
    center = c14_qa.get('regionCenterCrossing', {})
    require(str(center.get('status', '')).startswith('passed') and center.get('worldCoordinate') == [53248,4096],
            'Final QA must certify the 2x2 region center crossing')
    require(re.fullmatch(r'[0-9a-f]{64}',str(center.get('evidenceSha256',''))) is not None,
            'Final region center QA must record its evidence raster hash')
    require(capture(center['evidence'])[1] == center['evidenceSha256'], 'Final region center evidence hash changed')
    center_sources = center.get('sources', [])
    expected_center = {'r01_c13_p04_04','r01_c14_p04_01','r02_c13_p01_04','r02_c14_p01_01'}
    require(len(center_sources) == 4 and
            {re.sub(r'_v\d+$','',s.get('id',Path(s['file']).stem)) for s in center_sources} == expected_center,
            'Region center QA must reference its four expected current source corners')
    for source in center_sources:
        ident = source.get('id', Path(source['file']).stem)
        require(source.get('sha256') == selected_hashes.get(ident), f'Region center QA source is stale: {ident}')
    verify_integrity_report(integrity, candidate_info, selected_hashes, c14_qa_path)
    integrity_entry = add_record(integrity_path, 'final four-candidate integrity audit')
    preview_buffer = io.BytesIO()
    preview.save(preview_buffer, format='PNG')
    preview_data = preview_buffer.getvalue()
    preview_name = 'region.preview-only2048.png'
    ENTRIES[preview_name] = preview_data
    ENTRY_METADATA[preview_name] = {'file':preview_name,'sha256':sha_bytes(preview_data),'bytes':len(preview_data),
        'role':'QA preview only; not final artwork','transformation':'each 4096 tile resized to 1024 using Lanczos; 2x2 preview'}
    manifest = {
        'schemaVersion':1, 'createdAtUtc':datetime.now(timezone.utc).isoformat(),
        'productionRoot':'.','assignment':ORDER,'regionWorldBox':[49152,0,57344,8192],
        'candidateTileCount':4,'coveredCoreCount':64,'remainingCoreCount':0,'remainingCoordinates':[],
        'productionComplete':True,'regionalQaComplete':True,'formalAcceptedCount':0,'formalAccepted':False,
        'status':'completed_region_candidates_pending_formal_external_acceptance',
        'builtinOnly':True,'paidApiAllowed':False,'actualImageModel':'unknown','actualImageQuality':'unknown',
        'native4kGeneration':False,
        'resolutionClaim':'4096x4096 candidate tiles assembled from sixteen exact unscaled 1024 cores cropped from measured 1254x1254 native inputs',
        'tiles':tiles,
        'regionSeamQa':{
            'r01_c13_south__r02_c13_north':{'status':'passed_current_selected_hashes','segments':4,'report':relative(qa_paths['r01_c13'])},
            'r02_c13_east__r02_c14_west':{'status':'passed_current_selected_hashes','segments':4,'report':relative(qa_paths['r02_c14'])},
            'r01_c14_south__r02_c14_north':{'status':'passed_current_selected_hashes','segments':4,'report':relative(c14_qa_path)},
            'r01_c13_east__r01_c14_west':{'status':'passed_current_selected_hashes','segments':4,'report':relative(c14_qa_path)},
            'regionCenterCrossing':{'status':'passed_current_selected_hashes','worldCoordinate':[53248,4096],'report':relative(c14_qa_path)},
            'historicalPendingFlagsSupersededByNewerEvidence':True},
        'pendingExternalEdges':[{'tileId':'r01_c13','side':'west','adjacentTile':'r01_c12','status':'neighbor_unavailable_not_reviewed'},
            {'tileId':'r02_c13','side':'west','adjacentTile':'r02_c12','status':'neighbor_unavailable_not_reviewed'}],
        'outerMapBoundaries':{'north':['r01_c13','r01_c14'],'east':['r01_c14','r02_c14'],
            'status':'outer_map_extent_no_adjacent_external_tile'},
        'availableExternalSouthQa':{'r02_c13':{'status':'passed_available_native_south_neighbor','segments':4,'report':relative(qa_paths['r02_c13'])},
            'r02_c14':{'status':'passed_available_native_south_neighbor','segments':4,'report':relative(qa_paths['r02_c14'])}},
        'integrityAudit':{'file':integrity_entry,'originalSha256':integrity_hash,
            'archivedSha256':ENTRY_METADATA[integrity_entry]['sha256'],'candidateTilesPassed':4,'nativeCoresPassed':64},
        'currentSelectionSnapshot':{'file':relative(selection_path),'originalSha256':selection_hash,
            'updatedAtUtc':selection.get('updatedAtUtc'),'includedInArchive':False,'selectedValuesFullyCapturedInManifest':True},
        'packageScope':'Four 4096 candidate PNGs plus assembly, selected generation/prompt/receipt provenance, four final QA reports and their B-internal sourceManifest JSONs, final integrity audit, manifest/checksums and a clearly marked preview. Native images, guides and QA raster evidence remain at the production root and are not included.',
        'recordPortability':{'jsonRecordsAreNormalizedCopies':True,'originalRecordsRemainUnchanged':True,
            'internalAbsolutePathsConvertedToProductionRootRelative':True,'externalPathsOmittedWithBasenameAndPathTextHash':True,
            'originalAndArchivedJsonSha256RecordedSeparately':True,'absoluteArchiveEntryPathsAllowed':False},
        'archive':{'file':ARCHIVE_NAME,'entryPaths':'production-root-relative','zipSha256InCompanionFile':ARCHIVE_NAME+'.sha256',
            'checksumFile':'SHA256SUMS.txt','manifestSelfHashExcludedFromManifestIncludedInChecksumFile':True},
        'preview':{'file':preview_name,'dimensions':[2048,2048],'resized':True,'isFinalArtwork':False,
            'sourceRegionDimensions':[8192,8192], 'tilePositions':{k:list(v) for k,v in PREVIEW_AT.items()},
            'sha256':sha_bytes(preview_data)},
        'uploadState':{'status':'not_performed_by_this_script','responsible':'other window'},
        'gitState':{'status':'not_performed_by_this_script','responsible':'other window'},
        'productionStateFilesModified':False,
        'packageEntries':[ENTRY_METADATA[name] for name in sorted(ENTRY_METADATA)],
    }
    manifest_data = json_bytes(manifest)
    ENTRIES['manifest.json'] = manifest_data
    ENTRY_METADATA['manifest.json'] = {'file':'manifest.json','sha256':sha_bytes(manifest_data),'bytes':len(manifest_data)}
    checksum_data = ''.join(f"{ENTRY_METADATA[name]['sha256']}  {name}\n" for name in sorted(ENTRY_METADATA)).encode('utf-8')
    ENTRIES['SHA256SUMS.txt'] = checksum_data
    # Complete every assertion and check for active writes before making outputs.
    for path, digest in INPUT_HASHES.items():
        require(sha_file(path) == digest, f'Input changed before packaging: {relative(path)}')
    for name in ENTRIES:
        safe_member(name)
    require(not any(name.endswith('.png') and name.startswith(('native/','guides/','qa/')) for name in ENTRIES),
            'Compact archive must not include native/guide/QA raster images')
    OUT.mkdir(exist_ok=False)
    for name, data in [('manifest.json',manifest_data),('SHA256SUMS.txt',checksum_data),(preview_name,preview_data)]:
        with (OUT/name).open('xb') as handle:
            handle.write(data)
    archive_path = OUT/ARCHIVE_NAME
    with zipfile.ZipFile(archive_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as archive:
        for name in sorted(ENTRIES):
            payload = ENTRIES[name]
            if isinstance(payload, Path):
                archive.write(payload, arcname=name)
            else:
                archive.writestr(name,payload)
    with zipfile.ZipFile(archive_path,'r') as archive:
        require(set(archive.namelist()) == set(ENTRIES) and len(archive.namelist()) == len(ENTRIES),
                'Final ZIP entries differ or duplicate')
        require(archive.testzip() is None, 'Final ZIP CRC validation failed')
        for name, meta in ENTRY_METADATA.items():
            require(sha_bytes(archive.read(name)) == meta['sha256'], f'Final ZIP entry hash differs: {name}')
        require(archive.read('SHA256SUMS.txt') == checksum_data, 'ZIP checksum file differs')
    for path,digest in INPUT_HASHES.items():
        require(sha_file(path) == digest, f'Input changed while packaging: {relative(path)}')
    archive_hash = sha_file(archive_path)
    with (OUT/(ARCHIVE_NAME+'.sha256')).open('xb') as handle:
        handle.write(f'{archive_hash}  {ARCHIVE_NAME}\n'.encode('utf-8'))
    print(json.dumps({'deliveryDirectory':OUT.as_posix(),'manifest':(OUT/'manifest.json').as_posix(),
        'archive':archive_path.as_posix(),'archiveSha256':archive_hash,'archiveBytes':archive_path.stat().st_size,
        'archiveEntries':len(ENTRIES),'candidateTileCount':4,'selectedCoreCount':64,
        'productionComplete':True,'formalAccepted':False,'uploadedByThisScript':False},ensure_ascii=False))

if __name__ == '__main__':
    main()
