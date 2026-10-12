"""Account for one retired historical style reference; never substitute pixels."""
from datetime import datetime
import hashlib
import json
from pathlib import Path

ZONE = Path(__file__).resolve().parent
OLD_PATH = Path('D:/work/image/designs/mail-ui-v1/01-mail-event.png').resolve()
OLD_SHA = '3cf0b7d7b3bae337d51e947719588419a01ae21bdce9bccedd6258ce1feef0a2'


def file_record(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def reference(value, base, generation=None):
    if not isinstance(value, dict) or not isinstance(value.get('path'), str):
        raise ValueError('Reference must include path and sha256.')
    path = Path(value['path'])
    path = (path if path.is_absolute() else base / path).resolve()
    expected = value.get('sha256')
    identity = {'path': str(path), 'sha256': expected}
    if path.is_file():
        if file_record(path) != identity:
            raise ValueError(f'Reference hash mismatch: {path}')
        return identity, {'reference': identity, 'available': True}
    if path != OLD_PATH or expected != OLD_SHA or generation is None:
        raise ValueError(f'Missing required reference: {path}')
    contract_path = ZONE.parent / 'production-contract.json'
    contract = json.loads(contract_path.read_text(encoding='utf-8-sig'))
    resume_path = Path(contract['productionResumeControl']).resolve()
    resume = json.loads(resume_path.read_text(encoding='utf-8-sig'))
    if Path(contract.get('previousPrimaryStyleReference', '')).resolve() != OLD_PATH or resume.get('newArtworkGenerationAllowed') is not True:
        raise ValueError('No explicit production evidence for retired style reference.')
    generated = datetime.fromisoformat(generation['generatedAt'].replace('Z', '+00:00'))
    released = datetime.fromisoformat(resume['releasedAtUtc'].replace('Z', '+00:00'))
    if generated >= released:
        raise ValueError('New generation cannot use the retired missing style reference.')
    replacement_path = Path(contract['primaryStyleReference']).resolve()
    replacement = file_record(replacement_path)
    if replacement['sha256'] != contract['primaryStyleSha256'] or replacement['sha256'] != resume['primaryStyleSha256']:
        raise ValueError('Current authorized style reference differs from release evidence.')
    return identity, {'reference': identity, 'available': False, 'status': 'retiredHistoricalReferenceUnavailable',
                      'contract': file_record(contract_path), 'resumeControl': file_record(resume_path),
                      'currentReferenceForFutureOnly': replacement,
                      'historicalReferenceReplaced': False, 'historicalBytesReverified': False}


def evidence(generation, base):
    refs = generation.get('references')
    if not isinstance(refs, list) or not refs:
        raise ValueError('Generation must declare its actual reference list.')
    details = [reference(item, base, generation)[1] for item in refs]
    return {'fullReferenceAvailability': all(item['available'] for item in details), 'references': details,
            'missingReferenceDoesNotImplyMissingNativePixels': True}
