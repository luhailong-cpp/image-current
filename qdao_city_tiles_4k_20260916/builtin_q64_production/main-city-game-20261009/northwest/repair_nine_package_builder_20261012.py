from pathlib import Path
Z=Path(__file__).resolve().parent
source=Z/'package_nine_tiles_20261012.py';target=Z/'package_nine_tiles_20261012_v2.py'
assert not target.exists()
code=source.read_text(encoding='utf-8')
code=code.replace(chr(92)*2+'n',chr(92)+'n')
code=code.replace('OUTPUT = ZONE / "verified-nine-tiles-20261012"','OUTPUT = ZONE / "verified-nine-tiles-20261012-v2"')
old='destination / "actual-west-boundary/'
new='ZONE / "verified-nine-tiles-20261012/9195bae2e10f72ba/actual-west-boundary/'
code=code.replace(old,new)
needle='    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "'+chr(92)+'n", encoding="utf-8")'
assert needle in code
code=code.replace(needle,needle+'\n    require(json.loads(path.read_text(encoding="utf-8")) == value, "Written JSON failed strict round-trip validation")')
needle='            verified.append({**item, "archiveSha256": actual, "originalFileByteIdentity": True})'
assert needle in code
code=code.replace(needle,'            if item["zipEntry"].lower().endswith(".json"):\n                json.loads(archive.read(item["zipEntry"]).decode("utf-8-sig"))\n'+needle)
code=code.replace('"allOriginalFilesByteIdentityVerified": True, "verifiedEntries": len(files),','"allOriginalFilesByteIdentityVerified": True, "allArchivedJsonStrictlyParsed": True, "verifiedEntries": len(files),')
code=code.replace('"zipCRCVerified": True, "existingEightDeliveryPreserved": True,','"zipCRCVerified": True, "allArchivedJsonStrictlyParsed": True, "existingEightDeliveryPreserved": True,')
target.write_text(code,encoding='utf-8')
print(target)
