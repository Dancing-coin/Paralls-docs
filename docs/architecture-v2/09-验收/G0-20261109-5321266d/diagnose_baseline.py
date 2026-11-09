"""Read-only G0 diagnostic probes. Run with baseline Python; no runtime edits."""
from pathlib import Path
import sys,os,json,subprocess,hashlib,traceback
ROOT=Path('D:/Users/User/Documents/paralls-phase-0-demo')
OUT=Path(__file__).resolve().parent
os.chdir(ROOT/'backend');sys.path[:0]=[str(ROOT/'backend/tests'),str(ROOT/'backend'),str(ROOT)]
results={}
from app.config import Settings
import app.config as config
settings=Settings(dialogue_mode='stub',character_model_provider_kind='local',character_model_endpoint=None,character_model_api_key=None,character_model_model=None,heavenly_graph_path=':memory:')
for field in Settings.model_fields:setattr(config.settings,field,getattr(settings,field))
import test_obj_archive_door_embodied_authority as door
import app.main as main
main.reset_runtime_state();ctx=door._connection()
results['door']={'bind':door._bind_controller(ctx),'observed_at':ctx.observed_at,'interact':door._interact(ctx,producer_ts=110,interaction_type='open')}
code='from scripts.verification.population_benchmark_metrics import current_rss_bytes; print(current_rss_bytes())'
p=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True)
results['rss_subprocess']={'cwd':os.getcwd(),'returncode':p.returncode,'stderr':p.stderr}
code='from test_character_cognition_admission import service,request'
env=dict(os.environ);env['PYTHONPATH']=os.pathsep.join([str(Path('backend').resolve()),str(Path('backend/tests').resolve())])
p=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True)
results['admission_subprocess']={'pythonpath':env['PYTHONPATH'],'returncode':p.returncode,'stderr':p.stderr}
import test_character_runtime_needs_affect_flow as needs
import test_character_memory_consistency_flow as mem
import test_calibration_preclosure as cal
for label,func in [('needs_l2',needs.test_runtime_ingest_character_perceived_event_passes_effective_profile_and_need_tension_state_into_l2),('needs_l3',needs.test_runtime_ingest_character_perceived_event_passes_effective_profile_need_tension_and_dynamic_state_into_l3),('memory',mem.test_actual_interaction_failure_reaches_l3_and_new_evidence_clears_recheck_reason)]:
 trace=[]
 def tracer(frame,event,arg):
  file=frame.f_code.co_filename.replace('\\','/')
  if event=='exception' and ('character_agent' in file or 'test_character_runtime' in file):
   typ,value,_=arg
   if typ not in (StopIteration,GeneratorExit,KeyError): trace.append({'file':file,'line':frame.f_lineno,'type':typ.__name__,'message':str(value)[:1200]})
  if event=='call' and frame.f_code.co_name=='_verification_context': trace.append({'memory':frame.f_locals.get('memory'),'tensions':frame.f_locals.get('unresolved_tensions')})
  return tracer
 sys.settrace(tracer)
 try:func()
 except Exception as e: results[label]={'error':str(e),'trace':trace}
 finally:sys.settrace(None)
provider=cal.preparation.LayaSystemOneProvider(endpoint='http://offline.invalid',option_tokenizer=lambda _:[1],tokenizer_sha256='test:pin',require_option_token_validation=True)
records=json.loads((cal.preparation.INPUTS/'inputs.json').read_text(encoding='utf8'))['records']
cal_trace=[]
def tracer(frame,event,arg):
 if event=='return' and frame.f_code.co_name=='compile':
  cal_trace.append({'candidates':frame.f_locals.get('candidates'),'result':repr(arg)})
 return tracer
sys.settrace(tracer)
try:cal.preparation.prepare_record(records[0],provider)
except Exception as e:results['calibration']={'error':str(e),'trace':cal_trace,'input_candidates':records[0]['candidate_records']}
finally:sys.settrace(None)
import yaml
pins=yaml.safe_load((ROOT/'backend/tests/fixtures/character_evaluation/four_role_preparation/development-policy.yaml').read_text(encoding='utf8'))['source_pins']
results['pins']=[{**p,'actual':hashlib.sha256((ROOT/p['path']).read_bytes()).hexdigest()} for p in pins]
(OUT/'diagnostic-probes-v2.json').write_text(json.dumps(results,ensure_ascii=False,indent=2,default=str),encoding='utf8')
for k,v in results.items():
 print(k,json.dumps(v,ensure_ascii=False,default=str)[:6500])
