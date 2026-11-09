"""Additional read-only probes; not a replacement for either formal baseline."""
from pathlib import Path
import json, os, sys, traceback
ROOT = Path('D:/Users/User/Documents/paralls-phase-0-demo')
OUT = Path(__file__).resolve().parent
os.chdir(ROOT/'backend')
sys.path[:0] = [str(ROOT/'backend/tests'), str(ROOT/'backend'), str(ROOT)]
from app.config import Settings
import app.config as config
settings = Settings(dialogue_mode='stub', character_model_provider_kind='local',
    character_model_endpoint=None, character_model_api_key=None,
    character_model_model=None, heavenly_graph_path=':memory:')
for field in Settings.model_fields:
    setattr(config.settings, field, getattr(settings, field))
results = {}
import test_character_memory_consistency_flow as mem
trace = []
def tracer(frame, event, arg):
    path = frame.f_code.co_filename.replace('\\', '/')
    if path.endswith('/memory_recall.py') and frame.f_code.co_name == 'select' and event == 'return':
        trace.append({'input': frame.f_locals.get('memory'),
            'normalized': frame.f_locals.get('normalized'), 'policy': frame.f_locals.get('cognition_policy'),
            'candidates': frame.f_locals.get('candidates'), 'result': arg})
    return tracer
sys.settrace(tracer)
try:
    mem.test_actual_interaction_failure_reaches_l3_and_new_evidence_clears_recheck_reason()
except Exception:
    results['memory'] = {'trace': trace, 'exception': traceback.format_exc()}
finally:
    sys.settrace(None)
import test_ws_protocol as ws
import app.main as main
ws._reset_runtime_state_with_local_character_model()
payload = main.Envelope(message_type='character_agent_execution', payload={
    'actor_id': 'char_b', 'action_request_bundle': {'requested_actions': [{
        'request_type': 'approach', 'actor_id': 'char_b', 'target_actor_id': 'char_a'}]}})
try:
    messages = main._handle_envelope(payload)
    results['ws_direct'] = {'count':len(messages), 'messages': messages}
except Exception:
    results['ws_direct'] = {'exception': traceback.format_exc()}
import inspect, httpx
results['httpx'] = {'version': httpx.__version__, 'factory': inspect.getsource(httpx.create_ssl_context)}
from app.character_agent.gateway.model_gateway import CharacterModelGateway
from app.character_agent.models.mind_frame import CharacterMindFrame
from app.config import Settings
field = Settings.model_fields['physics_contact_authority_secrets']
results['asgi_field'] = {'annotation':str(field.annotation), 'exclude': field.exclude}
def encode(obj):
    if hasattr(obj, 'model_dump'): return obj.model_dump(mode='json')
    if hasattr(obj, '__dict__'): return obj.__dict__
    return str(obj)
(OUT/'diagnostic-additional.json').write_text(json.dumps(results, ensure_ascii=False, indent=2, default=encode), encoding='utf-8')
print(json.dumps({k: ({'count':v['count'], 'types':[m.get('message_type') for m in v['messages']]} if k=='ws_direct' and 'count' in v else str(v)[-1800:]) for k,v in results.items()}, ensure_ascii=False,default=encode))
