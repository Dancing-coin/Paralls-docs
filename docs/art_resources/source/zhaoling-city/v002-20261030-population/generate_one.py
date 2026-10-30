"""One authorized edit sample; never retry an uncertain image request automatically."""
from pathlib import Path
import json
import subprocess
import sys
import time
from PIL import Image

here=Path(__file__).resolve().parent
art=here.parents[2]
evidence=art/'evidence/zhaoling-city'/here.name
record_path=evidence/'generation-plan.json'
assert not record_path.exists(), 'Request already attempted; preserve billing uncertainty and outputs.'
prompt=(here/'plan-prompt.txt').read_text(encoding='utf-8')
out=here/'plan-response.bin'
model='gemini-3-pro-image-preview'
record={'model':model,'operation':'edit','n':1,'status':'started','automatic_retry':False}
record_path.write_text(json.dumps(record,indent=2),encoding='utf-8')
start=time.monotonic()
try:
    result=subprocess.run([sys.executable,'C:/Users/User/.codex/skills/gpt-image-2/gpt_image_2.py',
        'edit',str(here/'layout-reference.png'),prompt,'--model',model,'--n','1','-o',str(out)],
        capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=150)
    record.update(elapsed_seconds=round(time.monotonic()-start,2),return_code=result.returncode,
                  stdout=result.stdout,stderr=result.stderr,status='success' if result.returncode==0 else 'failed')
    if result.returncode==0:
        with Image.open(out) as im:
            im.load()
            record.update(actual_format=im.format,dimensions=list(im.size))
            suffix='.jpg' if im.format=='JPEG' else '.png'
            dest=here/f'plan-generated{suffix}'
            out.rename(dest)
            stage=art/'staging/zhaoling-city'/here.name
            im.convert('RGB').save(stage/'zhaoling-illustrated-plan.png')
            preview=im.convert('RGB');preview.thumbnail((2000,2000))
            preview.save(stage/'zhaoling-illustrated-plan-preview.jpg',quality=94)
        record['source_output']=str(dest)
except subprocess.TimeoutExpired:
    record.update(status='timeout_completion_and_billing_uncertain',elapsed_seconds=round(time.monotonic()-start,2))
except Exception as error:
    record.update(status='failed',error_type=type(error).__name__,error=str(error))
record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
raise SystemExit(0 if record['status']=='success' else 1)
