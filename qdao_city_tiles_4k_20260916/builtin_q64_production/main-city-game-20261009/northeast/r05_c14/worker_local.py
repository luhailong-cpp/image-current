from pathlib import Path
import importlib.util, sys

TILE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('production', TILE.parent/'production.py')
production = importlib.util.module_from_spec(spec)
spec.loader.exec_module(production)
production.TILE = TILE
production.update = lambda *args, **kwargs: None

if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'context':
        production.context(sys.argv[2])
    elif command == 'ingest':
        production.ingest(sys.argv[2], sys.argv[3])
    else:
        raise ValueError('Only tile-local context/ingest supported')
