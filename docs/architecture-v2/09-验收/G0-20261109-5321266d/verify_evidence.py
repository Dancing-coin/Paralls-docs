"""Check G0 evidence consistency without running tests or changing the code repo."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from build_report import HEAD, HERE, REPO, canonical, terminal_counts


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = read(HERE/'run1/test-files.json')
    assert manifest['head'] == HEAD
    frozen = {f['path']: f['sha256'] for f in manifest['files']}
    actual = {p.relative_to(REPO/'backend').as_posix(): sha(p)
              for p in (REPO/'backend/tests').rglob('test_*.py')}
    assert actual == frozen, 'Test inventory/content changed'
    results = []
    for name in ['run1-full', 'run2-full']:
        folder = HERE/name
        data = read(folder/'results.json')
        env = read(folder/'environment.json')
        nodes = read(folder/'collected-nodeids.json')
        assert data['head'] == env['head'] == env['head_after'] == HEAD
        assert not env['git_status_before'] and not env['git_status_after']
        assert env['source_unchanged']
        assert all(sha(REPO/p) == digest for p, digest in env['source_hashes'].items())
        assert env['manifest_sha256'] == sha(HERE/'run1/test-files.json')
        assert data['collected_count'] == len(nodes) == len(data['tests']) == len(set(nodes))
        assert sum(data['counts'].values()) == len(nodes)
        assert sum(terminal_counts(folder).values()) == len(nodes)
        assert not data['collection_errors']
        captured = [json.loads(line) for line in (folder/'failures.jsonl').read_text(encoding='utf-8').splitlines()]
        assert captured == data['failures']
        results.append(data)
    snapshot = read(HERE.parent/'failures_baseline_5321266d.json')
    assert len(snapshot['failures']) == results[0]['counts']['failed']
    assert sum(snapshot['category_counts'].values()) == len(snapshot['failures'])
    assert snapshot['unknown_count'] == 0
    for classified, raw in zip(snapshot['failures'], results[0]['failures'], strict=True):
        assert classified['test_name'] == raw['test_name']
        assert classified['stack'] == raw['stack'] and classified['evidence'] and classified['reason']
        assert classified['stack_hash'] == hashlib.sha256(canonical(raw['stack']).encode()).hexdigest()
    outcomes = {t['test_name']: t['outcome'] for t in results[0]['tests']}
    for path in HERE.glob('G1-*-regression.json'):
        data = read(path)
        assert data['head'] == HEAD
        assert data['node_count'] == len(data['nodeids'])
        assert all(outcomes[n] == data['baseline_outcomes'][n] for n in data['nodeids'])
    broken = []
    reports = [*HERE.parent.glob('G0-*.md'), HERE.parent/'baseline_failures_classification.md']
    for path in reports:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            target = re.sub(r':\d+$', '', target.split('#', 1)[0])
            if not (path.parent/target).exists():
                broken.append((str(path), target))
    assert not broken, broken
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=REPO, text=True) == ''
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip() == HEAD
    print(json.dumps({'evidence_consistent': True, 'test_files': len(frozen),
                      'round_counts': [r['counts'] for r in results],
                      'classified_failures': len(snapshot['failures']), 'broken_links': broken},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
