from pathlib import Path
from PIL import Image
import pipeline as p
tile=p.ROOT/'r04_c04';raw=tile/'rejected/s04_01-v1.png';receipt=p.read(tile/'receipts/s04_01.tool-result.json');args=p.read(tile/'receipts/s04_01.parameters.json')
host=Path(receipt['output_hint'].split(' as ',1)[1].split(' by default',1)[0]);im=Image.open(raw)
record={'schemaVersion':1,'file':str(raw),'sha256':p.sha(raw),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'hostOutputPath':str(host),'hostBytesMatch':p.sha(host)==p.sha(raw) if host.exists() else None,'resizedAfterGeneration':False,'finalArtUpscaled':False,'submittedParameters':args,'rawToolReceipt':str(tile/'receipts/s04_01.tool-result.json'),'references':[p.reference(f,'actual submitted reference') for f in args['referenced_image_paths']],'review':receipt['review'],'selected':False,'formalAccepted':False}
p.put_json(Path(str(raw)+'.generation.json'),record)
print({'file':str(raw),'sha256':record['sha256'],'pixels':im.size,'hostBytesMatch':record['hostBytesMatch']})
