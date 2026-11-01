#!/usr/bin/env python3
"""Private, file-backed GitHub double for executing the real workflow shell steps."""
import json
import os
from pathlib import Path
import subprocess
import sys

state_path = Path(os.environ['MOCK_GH_STATE'])
state = json.loads(state_path.read_text())
args = sys.argv[1:]
assert args[0] == 'api', args
method = args[args.index('--method') + 1] if '--method' in args else 'GET'
route = next(arg for arg in args[1:] if arg.startswith('repos/'))
state.setdefault('calls', []).append({'method': method, 'route': route})
state_path.write_text(json.dumps(state))
if state.get('fail_route') in (route, '*'):
    sys.stderr.write('HTTP 403: fixture refusal\n')
    raise SystemExit(1)

if method == 'POST':
    field = args[args.index('-F') + 1]
    assert route.endswith('/issues/1/comments') and field.startswith('body=@'), args
    result = {'id': len(state['comments']) + 1, 'user': {'login': 'github-actions[bot]'},
              'author_association': 'MEMBER', 'body': Path(field[6:]).read_text()}
    state['comments'].append(result)
elif method == 'DELETE':
    assert route.endswith('/labels/claude-review'), route
    state['label_removed'] = True
    result = None
elif route.endswith('/issues/1/comments'):
    result = state['comments']
elif route.endswith('/pulls/1/comments'):
    result = state.get('inline', [])
elif route.endswith('/pulls/1/reviews'):
    result = state.get('reviews', [])
elif route.endswith('/pulls/1/files'):
    result = [{'status': 'modified', 'filename': 'arithmetic.py'}]
elif route.endswith('/pulls/1'):
    heads = state.get('heads', [state['head']])
    index = state.get('head_reads', 0)
    state['head_reads'] = index + 1
    result = {'head': {'sha': heads[min(index, len(heads) - 1)]},
              'title': 'Synthetic arithmetic contract', 'user': {'login': 'fixture-author'},
              'body': 'Implement the documented arithmetic operations.'}
    if 'Accept: application/vnd.github.diff' in args:
        state_path.write_text(json.dumps(state))
        print(state.get('diff', 'synthetic diff'))
        raise SystemExit(0)
else:
    raise AssertionError((method, route))

state_path.write_text(json.dumps(state))
if '--silent' in args:
    raise SystemExit(0)
if '--slurp' in args:
    result = [result]
if '--jq' in args:
    query = args[args.index('--jq') + 1]
    outcome = subprocess.run(['jq', '-r', query], input=json.dumps(result), text=True)
    raise SystemExit(outcome.returncode)
print(json.dumps(result))
