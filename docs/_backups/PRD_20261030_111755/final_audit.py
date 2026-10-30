from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
D = ROOT / 'docs'

def owners(p):
    return [m.group(1).strip() for m in re.finditer(r'^\|\s*\d{2}\s*\|([^|]+)\|', p.read_text(encoding='utf-8-sig'), re.M)]

registry = D / 'architecture/03-Owner领域/01-Owner注册表.md'
matrix = D / 'architecture/05-运行时接入/01-UE本地提交与Paralls同步.md'
roots = ['PRD', 'architecture', 'production', 'validation', 'templates/PRD', 'archive/PRD', 'art_resources/standards', 'art_resources/requirements/召陵县']
missing, command, receipt, full = [], [], [], []
for p in D.rglob('*.md'):
    if '_backups' in p.parts:
        continue
    t = p.read_text(encoding='utf-8-sig')
    if len(owners(p)) == 23:
        full.append(p.relative_to(ROOT).as_posix())
    for block in re.findall(r'(?ms)^```[^\n]*\n(.*?)^```', t):
        if all(x in block for x in ['command_version', 'expected_revisions', 'principal_ref', 'expires_at']):
            command.append(p.relative_to(ROOT).as_posix())
        if all(x in block for x in ['committed_events', 'result_status', 'owner_kind', 'recovery_action']):
            receipt.append(p.relative_to(ROOT).as_posix())
for folder in roots:
    for p in (D / folder).rglob('*.md'):
        t = p.read_text(encoding='utf-8-sig')
        if not all(x in t[:1200] for x in ['版本', '评审状态', '实现状态']):
            missing.append(p.relative_to(ROOT).as_posix())
audit = {
    'owner_registry_count': len(owners(registry)),
    'ue_cadence_count': len(owners(matrix)),
    'owner_names_order_identical': owners(registry) == owners(matrix),
    'full_23_owner_tables': full,
    'command_envelope_schema_locations': command,
    'receipt_schema_locations': receipt,
    'directory_md_counts': {folder: len(list((D / folder).rglob('*.md'))) for folder in roots},
    'metadata_needing_review': missing,
}
(B / 'FINAL_AUDIT.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps(audit, ensure_ascii=False, indent=2))
assert len(owners(registry)) == len(owners(matrix)) == 23
assert owners(registry) == owners(matrix)
assert len(full) == 2 and len(command) == len(receipt) == 1
assert not missing
