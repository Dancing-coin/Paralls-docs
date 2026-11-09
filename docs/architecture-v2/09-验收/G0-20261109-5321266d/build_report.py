"""Build reviewable G0 artifacts from immutable formal captures; never run pytest."""
from pathlib import Path
from collections import Counter
import hashlib, json, re, subprocess, sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ACCEPT = HERE.parent
REPO = Path('D:/Users/User/Documents/paralls-phase-0-demo')
HEAD = '5321266dbd882f45eb6a24dd7b328e9f56746228'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def terminal_counts(directory):
    cases = ET.parse(directory/'junit.xml').getroot().iter('testcase')
    counts = Counter()
    for case in cases:
        skipped = case.find('skipped')
        if case.find('failure') is not None:
            counts['failed'] += 1
        elif case.find('error') is not None:
            counts['error'] += 1
        elif skipped is not None:
            counts['xfailed' if skipped.get('type') == 'pytest.xfail' else 'skipped'] += 1
        else:
            counts['passed'] += 1
    return dict(counts)

def canonical(stack):
    # v2 fixes escaped Windows repr paths; preserve line numbers and semantic values.
    value = stack.replace('\\', '/')
    value = re.sub(r'([A-Za-z]:)/+', r'\1/', value)
    value = re.sub(r'(?<=/)/+', '/', value)
    for path, token in [(str(REPO), '<REPO>'), (sys.prefix, '<PYTHON>'), ('D:/codex-temp/user-temp', '<TEMP>')]:
        value = re.sub(re.escape(path.replace('\\', '/')), token, value, flags=re.I)
    value = re.sub(r'pytest-\d+', 'pytest-N', value)
    value = re.sub(r'0x[0-9a-fA-F]+', '0xADDR', value)
    value = re.sub(r'(cancel scope )[0-9a-fA-F]+', r'\1<SCOPE>', value)
    value = re.sub(r'\b\d{4}-\d{2}-\d{2}[T ][0-9:.]+(?:Z|[+-]\d{2}:\d{2})?', '<TIME>', value)
    return value

# Manually investigated causes, NOT keyword-based heuristic categorization.
RULES = {}
def rule(files, category, reason, evidence, gate='非 G1 共享机制直接阻断；保留失败，后续对应路径单独修复'):
    for file in files.split():
        RULES['tests/test_'+file+'.py'] = dict(category=category, reason=reason, evidence=evidence, gate=gate)

rule('action_window_temporal_owner stormnight_action_loop', '测试过时',
     '0fc54364 明确把每窗口事件从 4 改为 5，增加 terminal_outcome_recorded；这些断言仍要求 head=4 或没有 terminal 事件。重试并未另增一个窗口。',
     ['backend/app/gameplay/p5/investigation_conflict.py:30', 'git:0fc543643367e98237545ffb09370753268badfd', 'backend/tests/test_3d_scripted_mystery_action_replay.py'])
rule('calibration_preclosure', '测试过时',
     '旧离线准备工具的 permission 条件被当前 compiler 判为 unknown，冻结候选为空；Laya 拒绝无候选。调用工具/fixture 未跟随候选冻结契约。',
     ['scripts/verification/prepare_calibration_preclosure.py:105', 'backend/app/character_agent/gateway/laya_provider.py:59', 'diagnostic-probes-v2.json'])
rule('character_agent_runtime', '测试过时',
     '连续性规划发布的语义意图已归一化为 observe_target；旧断言要求 observe。L4 执行映射仍可映射到 action:observe，不能把决策意图和动作名混同。',
     ['backend/app/character_agent/runtime/runtime_loop.py:5697', 'backend/app/character_agent/planning/l3_planner.py:1821', 'diagnostic-probes-v2.json'])
rule('character_agent_runtime_persistence_wiring p2dr_authored_bakery_authority_reclosure', '环境差异',
     '测试用仓库根相对路径；正式入口 cwd=backend，故 backend/app/main.py 变成 backend/backend/app/main.py，或 assets/characters/profiles 解析为空。真实根文件存在。',
     ['backend/tests/test_character_agent_runtime_persistence_wiring.py', 'backend/tests/test_p2dr_authored_bakery_authority_reclosure.py'])
rule('character_cognition_admission siming_admission population_transport_metrics', '环境差异',
     '子进程 PYTHONPATH 未包含正确根/测试路径。backend cwd 下再次 resolve backend 导致嵌套路径，或子进程无法导入 scripts.verification。失败在 import 阶段，未验证硬退出恢复。',
     ['backend/tests/test_character_cognition_admission.py:165', 'backend/tests/test_siming_admission.py:194', 'diagnostic-probes-v2.json', 'run1-full.log'])
rule('character_development_runner character_evaluation_preparation', '测试过时',
     '冻结评测策略的 source_pins 与当前受跟踪角色源不一致。char_a 预期 8e8f3292519a7879f2f16eca2d64be7b90467010dc7641689a8e6b9821879463，实际/git blob 均 9c41753ac79644e8a4a81779b2ff7a9e49f04e28439e5489c052b7fef166ef88；不是 CRLF 漂移。source_changed 拒绝是当前保护行为。不得自动刷新语料哈希。',
     ['scripts/verification/prepare_character_evaluation.py:25', 'backend/tests/fixtures/character_evaluation/four_role_preparation/development-policy.yaml:127', 'diagnostic-probes-v2.json'])
rule('character_development_v4_runner', '测试过时',
     '旧 v4 准备工具传 cognition_policy={}，当前 CognitionPolicy 有九个必填字段；在模型调用之前校验失败，18 项不是 18 个独立网络故障。',
     ['scripts/verification/run_character_development_v4.py:107', 'backend/app/character_agent/gateway/model_gateway.py:62', 'diagnostic-probes-v2.json'])
rule('character_memory_consistency_flow', '已知缺陷',
     '新知识 valid_at=4 已存在，却被 recall 的 480-token/4条预算裁掉（435 tokens，2 event+1 observation，0 knowledge，truncated=true）。L3 用裁剪后的 recall.memory 生成 verification context，看不到比失败 tension 更晚的证据，旧 recheck_reason 未清除。',
     ['backend/tests/test_character_memory_consistency_flow.py:255', 'backend/app/character_agent/planning/l3_planner.py:731', 'diagnostic-additional.json'],
     'B2：影响角色记忆投影/决策输入；G1 前须独立修复或以明确迁移边界实证排除该投影路径，不可默认豁免')
rule('character_mind_frame_consumers', '测试过时',
     '旧 planner fixture 缺少当前必须绑定的 turn context；在 l3 prepare 的边界保护处拒绝。',
     ['backend/tests/test_character_mind_frame_consumers.py', 'backend/app/character_agent/planning/l3_planner.py:651'])
rule('character_mind_frame_models', '测试过时',
     'fixture 同时有 actor/turn 不匹配，当前先拒绝 actor mismatch；旧测试只接受 turn 字样。错误仍被拒绝，断言对校验顺序过度绑定。',
     ['backend/tests/test_character_mind_frame_models.py:209', 'backend/app/character_agent/models/mind_frame.py:228'])
rule('character_runtime_needs_affect_flow', '测试过时',
     '三个旧 stub 分别不接受 model_dump(mode=json)、prepare_perceived_event(capability_envelope=...)、prepare_intent_plan(capability_envelope=...)。运行时捕获后走 fallback，旧记录变量为空；不能用 stub 失败证明真实 provider 行为。',
     ['backend/tests/test_character_runtime_needs_affect_flow.py', 'diagnostic-probes-v2.json'])
rule('character_turn_embodied_episode economy_random_command_application obj_archive_door_embodied_authority obj_archive_door_embodied_websocket', '环境差异',
     'fixture 的可信启动凭证 issued_at=100/expires_at=200；连接入口用当前墙钟 observed_at，故 trusted_local_launch_expired，继而 controller_binding_required/command 拒绝。不是对象动作提交自身的失败。',
     ['backend/app/main.py:3483', 'backend/tests/test_obj_archive_door_embodied_authority.py', 'diagnostic-probes-v2.json'])
rule('economy_random_replay_participant', '测试过时',
     '重开 fixture 构造 PresenceAuthority(store) 未注入 sources；当前历史重验 spawn 要求 sources，原始 helper 却有 sources。回放参与者装配不完整。',
     ['backend/tests/test_economy_random_replay_participant.py:332', 'backend/app/population_continuity/presence_runtime.py:169'])
rule('economy_temporal_replay_application', '测试过时',
     'checkpoint 带 social 状态，重开 replay_scoped_tail 仅传 inventory；当前回放拒绝 replay_social_participant_missing。旧恢复 fixture 不完整，不能静默忽略 social。',
     ['backend/tests/test_economy_temporal_replay_application.py:102', 'backend/app/world_runtime/replay_participants.py:1865'])
rule('esm_physical_channel_runtime interaction_orchestration_runtime_service', '测试过时',
     '旧 fixture 的 obj_box 未注册到当前 ESM 语义 authority；先 unsupported_object，再 semantic_authority_required，未进入断言所期待的旧物理交互路径。',
     ['backend/tests/test_esm_physical_channel_runtime.py', 'backend/tests/test_interaction_orchestration_runtime_service.py', 'diagnostic-probes.json'])
rule('gameplay_event_store_json_cache', '测试过时',
     '损坏 JSON 与关闭 snapshot 仍 fail-closed，实际错误分别 json_codec_invalid / snapshot_closed；旧 regex 要求 row_invalid。不是成功读出坏行。',
     ['backend/app/gameplay/event_store.py:58', 'backend/app/gameplay/event_store.py:944'])
rule('infra_package_declared_negotiated_exchange', '已知缺陷',
     '测试向已提交 receipt 插入 missing:event 后精确重试仍 committed=true。Economy duplicate 仅校验 digest 并 get_by_idempotency 后直接返回，未验证事件引用。旧缺陷文档“已修复”不能覆盖本 HEAD 实测。',
     ['backend/tests/test_infra_package_declared_negotiated_exchange.py:343', 'backend/app/gameplay/economy_runtime.py:1269', '../05-基线缺陷-幂等回放未校验.md'],
     'B1：直接影响幂等收据/事件引用；按规格明确阻塞 G1，须独立缺陷轨道修复并重新建立基线')
rule('inventory_cadence_revocation_commit', '测试过时',
     'fixture read_set.temporal_pins={}，授权结算窗口当前要求 timeline_id。三项均先 settlement_window_invalid，append/撤权/race hook 尚未到达；需补齐时间上下文再验证原断言。',
     ['backend/app/population_continuity/inventory_owner_adapter.py:53', 'backend/app/population_continuity/inventory_owner_adapter.py:117', 'diagnostic-probes.json'])
rule('mind_frame_turn_boundary', '测试过时',
     '测试要求 legacy 消费，但 gateway 当前强制 frame_digest 与 turn_id；旧 payload 在绑定边界被拒绝。',
     ['backend/tests/test_mind_frame_turn_boundary.py', 'backend/app/character_agent/gateway/model_gateway.py:55'])
rule('population_long_session_recovery', '已知缺陷',
     'f1e18067 有意把源码指纹改为手工 kernel_version=v1+函数形状。functools.wraps 的实现变化不改 digest；相同 code 重新 FunctionType 丢 return annotation 却改 digest。已定位契约分歧：当前算法不等于测试要求的自动实现变更检测；不能未经决策称测试过时或承诺回放等价。',
     ['backend/app/population_continuity/recovery.py:20', 'backend/tests/test_population_long_session_recovery.py:140', 'git:f1e18067'],
     'B4：恢复身份/投影兼容性契约分歧；G1 前独立决定语义版本责任并实证排除或修复，不把手工签名当自动行为等价证明')
rule('runtime_asgi', '测试过时',
     'fixture 把所有 exclude 字段赋为 controlled-test-value 字符串；新增 physics_contact_authority_secrets 是 dict[str,str]。父模型未赋值校验，子进程 Settings.model_validate_json 在启动前 dict_type 失败。',
     ['backend/tests/test_runtime_asgi.py:225', 'backend/app/services/runtime_process.py:585', 'diagnostic-additional.json', 'run1-full.log:11329'])
rule('siming_heavenly_godot_static', '环境差异',
     '测试按 repo cwd 打开 scripts/object/InteractiveObject.gd、scripts/autoload/BackendBridge.gd 和 scenes/integration 下资源；正式 backend cwd 不能定位，根目录真实文件存在。仅静态读取，没有 Godot/UE 运行验收。',
     ['backend/tests/test_siming_heavenly_godot_static.py', 'run1-full.log'])
rule('siming_llm_tls_context', '环境差异',
     '本机 httpx=0.27.2，CI constraints=0.28.1。旧版 create_ssl_context 走 SSLConfig/ssl.SSLContext，不走测试 monkeypatch 的 ssl.create_default_context，contexts/ca_options 始终为空；不存在 CA 文件的环境行为也不同。版本/观测点不兼容，不推断 TLS 不安全。',
     ['backend/ci-constraints.txt', 'backend/tests/test_siming_llm_tls_context.py:27', 'backend/app/services/siming_llm_provider.py:263', 'diagnostic-additional.json', 'C:/Anaconda3/Lib/site-packages/httpx/_config.py:51'])

def classify(failure):
    name = failure['test_name']
    file = name.split('::')[0]
    if file == 'tests/test_ws_protocol.py':
        if 'test_worktable_finish_use' in name:
            return dict(category='已知缺陷', reason='main 旧 worktable finish-use 路径先输出结果/修改 occupancy 再直接调用 ESM commit_interaction_state；当前持久化 ESM 明确禁止该直接 setter，抛 esm_object_durable_settlement_required。接入路径与持久化权威不一致。', evidence=['backend/app/main.py:6330', 'backend/app/main.py:6362', 'backend/app/services/esm_service.py:1224', 'backend/tests/test_ws_protocol.py:1433'], gate='B3：对象提交/投影接入缺陷；G1 前独立修复或以边界实证排除，不可只改异常断言')
        return dict(category='测试过时', reason='旧 approach action_request_bundle 请求已被 social_spatial_owner 明确拒绝；只返回 accepted=false/legacy_social_spatial_source_unavailable 的 ack。测试仍固定接收 13 条消息而超时，未发生调度轮执行。', evidence=['backend/app/main.py:5680', 'backend/tests/test_ws_protocol.py:1701', 'diagnostic-additional.json:ws_direct'], gate='非 G1 共享机制直接阻断；更新请求契约后再验调度轨迹')
    if file not in RULES:
        raise ValueError('Uninvestigated node: '+name)
    return RULES[file]

def main():
    one = read(HERE/'run1-full/results.json')
    env = read(HERE/'run1-full/environment.json')
    nodes = read(HERE/'run1-full/collected-nodeids.json')
    failures = []
    for index, f in enumerate(one['failures'], 1):
        c = classify(f)
        failures.append({**f, **c, 'id':f'F{index:03d}', 'raw_capture_stack_hash':f['stack_hash'],
                         'stack_hash':sha(canonical(f['stack']).encode()), 'canonicalization':'g0-stack-v2',
                         'canonical_stack':canonical(f['stack']), 'raw_ref':f'G0-20261109-5321266d/run1-full/results.json#/failures/{index-1}'})
    counts = dict(Counter(f['category'] for f in failures))
    terminal = terminal_counts(HERE/'run1-full')
    assert sum(terminal.values()) == one['collected_count'] == len(nodes)
    assert len(failures) == one['counts']['failed']
    snapshot = dict(schema_version=2, head=HEAD, collected_count=one['collected_count'],
                    counts=one['counts'], terminal_counts=terminal,
                    category_counts=counts, unknown_count=counts.get('未知根因', 0), failures=failures,
                    environment_ref='G0-20261109-5321266d/run1-full/environment.json',
                    scope='all backend/tests test_*.py; broader than historical 15-domain/624-file baseline',
                    historical_failed_count=201, historical_count_is_current=False)
    write(ACCEPT/'failures_baseline_5321266d.json', snapshot)

    comparison = {'status':'pending_run2','canonicalizer':'g0-stack-v2', 'allowed_normalization':['absolute roots including escaped Windows repr', 'pytest temporary counters', 'memory addresses', 'asyncio cancel-scope runtime identifiers', 'ISO timestamps'], 'not_normalized':['line numbers','semantic values','UUIDs','digests','assertion results','test order']}
    if (HERE/'run2-full/results.json').exists():
        two = read(HERE/'run2-full/results.json')
        e2 = read(HERE/'run2-full/environment.json')
        a = {t['test_name']:t for t in one['tests']}
        b = {t['test_name']:t for t in two['tests']}
        f2 = {f['test_name']:f for f in two['failures']}
        differences = []
        for f in failures:
            other = f2.get(f['test_name'])
            if other and f['canonical_stack'] != canonical(other['stack']):
                differences.append({'test_name':f['test_name'], 'run1':f['canonical_stack'], 'run2':canonical(other['stack'])})
        comparison.update(status='compared', collection_order_equal=nodes==read(HERE/'run2-full/collected-nodeids.json'),
            failure_order_equal=[f['test_name'] for f in one['failures']]==[f['test_name'] for f in two['failures']],
            state_changes=[{'node':n,'run1':a.get(n),'run2':b.get(n)} for n in sorted(a.keys()|b.keys()) if a.get(n)!=b.get(n)],
            type_phase_changes=[f['test_name'] for f in failures if f['test_name'] in f2 and (f['error_type'],f['phase'])!=(f2[f['test_name']]['error_type'],f2[f['test_name']]['phase'])],
            stack_differences=differences, counts_run1=one['counts'], counts_run2=two['counts'],
            terminal_counts_run1=terminal, terminal_counts_run2=terminal_counts(HERE/'run2-full'),
            started_run1=one['started'], finished_run1=one['finished'],
            started_run2=two['started'], finished_run2=two['finished'],
            head_equal=env['head']==e2['head']==HEAD,
            source_equal=env['source_hashes']==e2['source_hashes'], packages_equal=env['packages_sha256']==e2['packages_sha256'],
            manifest_equal=env['manifest_sha256']==e2['manifest_sha256'], source_unchanged=[env.get('source_unchanged'),e2.get('source_unchanged')],
            git_status_after=[env.get('git_status_after'), e2.get('git_status_after')],
            exit_codes=[one['exit_code'], two['exit_code']],
            collection_errors=[one['collection_errors'], two['collection_errors']])
    write(HERE/'reproducibility-comparison.json', comparison)

    domains = {
      'ownership':r'test_ownership.*\.py',
      'modifier':r'test_(modifier|effective_stats|resource_modifier).*\.py',
      'equipment':r'test_(equipment|resource_modifier|command_service).*\.py',
      'inventory':r'test_inventory.*\.py',
      'shared-replay':r'test_(gameplay_event_store|gameplay_event_replay|gameplay_shared_replay|world_replay|economy.*replay|infra_package_declared_negotiated_exchange|population_long_session_recovery).*\.py',
    }
    manifests = {}
    for domain, pattern in domains.items():
        selected = [n for n in nodes if re.fullmatch(pattern,n.split('::')[0].split('/')[-1])]
        if not selected: raise ValueError('Empty regression domain '+domain)
        files = sorted({n.split('::')[0] for n in selected})
        manifest = dict(head=HEAD, domain=domain, file_count=len(files), node_count=len(selected), files=files, nodeids=selected,
                        baseline_outcomes={n:next(t['outcome'] for t in one['tests'] if t['test_name']==n) for n in selected})
        write(HERE/f'G1-{domain}-regression.json', manifest)
        (HERE/f'G1-{domain}-nodeids.txt').write_text('\n'.join(selected)+'\n',encoding='utf-8')
        manifests[domain] = {'files':len(files),'nodes':len(selected),'failed':sum(n in {f['test_name'] for f in failures} for n in selected)}
    write(HERE/'G1-regression-index.json', manifests)

    lines = ['# G0 当前失败根因分类', '', f'- 日期：2026-11-09；代码 HEAD：`{HEAD}`。',
             '- 当前基线 **108 失败 / 33 文件**；历史 201 不适用于更新后的代码与扩大后的测试集合。',
             '- 四类按实际堆栈、测试输入与源码分类；环境项仍计失败。未知根因为 0 不代表产品契约已获批准。',
             '- 每项完整错误类型、阶段、原始/规范化堆栈、SHA-256、源码帧与理由见 [机器快照](failures_baseline_5321266d.json)。', '',
             '| 类别 | 数量 |', '|---|---:|']
    lines += [f'| {cat} | {counts.get(cat,0)} |' for cat in ['环境差异','已知缺陷','测试过时','未知根因']]
    lines += ['', '## 阻塞决定', '',
      '**G0 未通过，G1 未放行。** B1 是规格明确要求先修复的幂等缺陷。B2/B3/B4 涉及投影、提交接入或恢复身份；须在独立缺陷/契约轨道处理并重新验证，或提供经审查的精确迁移边界排除证据。当前没有这种排除证据。不得在结构重构里顺手改变语义。',
      '', '“测试过时”包含旧工具调用和冻结 fixture 漂移，不意味着删除失败测试；应更新契约输入并确认原保护仍成立。环境项只允许作为带说明的对照噪声，不能从总数消失。', '', '## 逐项记录', '']
    for f in failures:
        lines += [f"### {f['id']} · {f['category']}", '', f"`{f['test_name']}`", '',
                  f"- 错误：`{f['error_type']}`；阶段：`{f['phase']}`。", f"- 根因：{f['reason']}",
                  '- 证据：'+ '；'.join('`'+s+'`' for s in f['evidence'])+'。', f"- 阶段门：{f['gate']}。",'']
    (ACCEPT/'baseline_failures_classification.md').write_text('\n'.join(lines),encoding='utf-8')

    gameplay = sorted((REPO/'backend/app/gameplay').rglob('*.py'))
    line_count = sum(len(p.read_bytes().splitlines()) for p in gameplay)
    envmd = f'''# G0 基线环境记录

- 日期：2026-11-09；执行者：Codex。基线取证完成状态以复现比较为准；G0/G1 放行状态见检查清单。

## 代码与范围

- 原路径 `D:\\Paralls-phase0-1` 不存在；实际仓库 `{REPO}`。
- 按用户“拉取远端更新”要求，从 `d77d9db6` fast-forward 19 个提交到 `{HEAD}`；没有合并提交或 runtime 修改。
- 提交：`{env['commit']}`。历史 `c5f249bd` 是祖先；历史 201 失败不能推断为当前数量。
- 当前 gameplay：{len(gameplay)} 个 Python 文件，{line_count} 物理行（bytes.splitlines）。
- 正式范围：冻结 `backend/tests/` 全部 1025 个 `test_*.py`，实际收集 9899 节点；不是旧 15 域/624 文件集合，也不覆盖根目录 scripts 的独立测试/Harness/Godot/UE 验收。
- 示例 `backend/app/gameplay/tests/` 不存在。真实入口是 backend cwd 的 `tests`。

## 环境身份

- OS：`{env['os']}`；Python：`{env['python']}`；解释器：`{env['executable']}`。
- pytest 8.3.4；本机 Python 3.13.5 与 CI 3.12.14 不同；已安装 httpx 0.27.2 与 CI constraints 0.28.1 不同。本轮未安装/升级依赖。
- 根与 backend 均无 requirements.txt。pyproject SHA-256：`{env['dependency_files']['pyproject.toml']}`。
- ci-constraints SHA-256：`{env['dependency_files']['ci-constraints.txt']}`。
- 已安装全部 distributions 的版本与 SHA：`{env['packages_sha256']}`，见 [环境快照](G0-20261109-5321266d/run1-full/environment.json)。这是可比环境记录，不是可移植容器或锁定镜像。
- 测试文件内容哈希清单：[test-files.json](G0-20261109-5321266d/run1/test-files.json)；后端 app 源文件哈希在每轮 environment.json，含运行前后 Git/HEAD 检查。
- 释放内存后继续；正式测试串行执行。没有启动 UE、导入、美术构建或显存操作。最终资源观测见 final-verification.json。

## 命令与结果

在文档仓库执行以下命令；runner 将 cwd 切换为 backend，给当前进程 sys.path 前置 backend 和 repo。子进程不继承这种 sys.path 注入，这正是数个已保留环境失败的根因。

```powershell
python "docs/architecture-v2/09-验收/G0-20261109-5321266d/run_baseline.py" --repo "D:/Users/User/Documents/paralls-phase-0-demo" --output "<新的绝对证据目录>" --manifest "<绝对路径>/G0-20261109-5321266d/run1/test-files.json"
```

底层 pytest：`pytest tests -v --tb=short -p no:cacheprovider --junitxml=<output>/junit.xml`。新 output 必须不存在；原捕获不可覆盖。

- 第一轮：本地 14:19:17–14:43:19；pytest 1436.03 秒。**9787 passed、108 failed、2 skipped、2 xfailed，总计 9899**；收集错误 0；退出码 1。
- runner 统一 outcome 将 xfailed 归入 skipped，故 results.json 是 skipped=4；细分以终端与 JUnit 为准，不是计数冲突。
- 第二轮：14:43:40–15:10:20；两轮均为 9787 passed、108 failed、2 skipped、2 xfailed，9899 节点。收集顺序、失败顺序、失败 outcome、错误类型/阶段一致；源、依赖与清单哈希一致；无收集错误、代码变更或状态漂移。精确差异见[复现比较](G0-20261109-5321266d/reproducibility-comparison.json)。
- [第一轮日志](G0-20261109-5321266d/run1-full.log)、[结果](G0-20261109-5321266d/run1-full/results.json)、[第二轮日志](G0-20261109-5321266d/run2-full.log)。早期 run1/ 是中断的收集/试运行，smoke/ 是小样本，均不计正式结果。

## 比较规则

build_report.py 的 `g0-stack-v2` 规范化绝对路径（含 repr 双反斜线）、pytest 临时计数器、内存地址、asyncio 明确格式 `Cancelled by cancel scope <hex>` 中的运行时对象 ID、ISO 时间。第二轮唯一原始堆栈差异是 anyio `_backends/_asyncio.py` 生成的该 ID（见本机 anyio 源 575 行）；规范化后为零堆栈差异。保留错误类型、阶段、行号、语义值、UUID、摘要与断言差异。原始捕获哈希仍在 raw_capture_stack_hash；两轮使用同一规则比较，原始证据不覆盖。

相同失败节点/顺序和类型只是第一层；堆栈语义差异必须逐项说明，不能用宽泛正则删掉。当前比较状态：`{comparison['status']}`。技术负责人审批和独立缺陷修复尚未完成。
'''
    (ACCEPT/'G0-baseline-environment-2026-11-09.md').write_text(envmd,encoding='utf-8')
    print(json.dumps({'category_counts':counts,'comparison':{k:v for k,v in comparison.items() if k not in ['stack_differences','state_changes']},'stack_difference_count':len(comparison.get('stack_differences',[])),'regression_sets':manifests},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
