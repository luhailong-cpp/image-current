"""Private adapter for retained west_sol bridge provenance; never alters source records."""
import assemble_native_candidate as a
from pathlib import Path
from PIL import Image
original=a.normalize_record
def normalize(record):
 d=original(record)
 if 'base' in d and 'nativeGeneratedSource' in d and 'operation' in d:
  base=d['base'];source=d['nativeGeneratedSource'];d['derivedFrom']=[base,source]
  for p in [base,source]:
   assert a.sha_file(p['path'])==p['sha256'],('Parent hash mismatch',p['path'])
  b=Image.open(base['path']).convert('RGB');s=Image.open(source['path']).convert('RGB');out=Image.open(d['file']).convert('RGB')
  crop=s.crop(d['sourceCropBox']);box=d['targetContributionBox'];assert crop.size==(box[2]-box[0],box[3]-box[1])
  b.paste(crop,tuple(box[:2]));assert b.tobytes()==out.tobytes(),('Bridge crop/paste pixel proof failed',d['file'])
 return d
a.normalize_record=normalize
if __name__=='__main__':a.main()
