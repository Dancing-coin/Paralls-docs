"""One authorized image request; save its prompt, result and timing without credentials."""
from pathlib import Path
import json
import subprocess
import sys
import time
from PIL import Image

here = Path(__file__).resolve().parent
art = here.parents[2]
kind = sys.argv[1]
assert kind in {'plan', 'concept'}
out = here / f'{kind}-response.bin'
assert not out.exists(), 'Preserve existing outputs; do not repeat a potentially billable request.'
prompt = (here / f'{kind}-prompt.txt').read_text(encoding='utf-8')
cli = Path('C:/Users/User/.codex/skills/gpt-image-2/gpt_image_2.py')
start = time.monotonic()
result = subprocess.run([sys.executable, str(cli), 'generate', prompt, '--model',
                         'gemini-3-pro-image-preview', '--n', '1', '-o', str(out)],
                        capture_output=True, text=True, encoding='utf-8', errors='replace')
record = {'model': 'gemini-3-pro-image-preview', 'operation': 'generate', 'kind': kind,
          'elapsed_seconds': round(time.monotonic() - start, 2), 'return_code': result.returncode,
          'stdout': result.stdout, 'stderr': result.stderr}
if result.returncode == 0:
    with Image.open(out) as im:
        record.update(actual_format=im.format, dimensions=list(im.size))
        suffix = '.jpg' if im.format == 'JPEG' else '.png'
    destination = here / f'{kind}-generated{suffix}'
    out.rename(destination)
    record['source_output'] = str(destination)
evidence = art / 'evidence/zhaoling-city' / here.name
(evidence / f'generation-{kind}.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(record, ensure_ascii=False, indent=2))
raise SystemExit(result.returncode)
