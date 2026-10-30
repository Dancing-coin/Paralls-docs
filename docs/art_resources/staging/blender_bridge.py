"""Send one JSONL command to the user's live Blender MCP GUI bridge."""
import json
import socket
import sys
from pathlib import Path

command = sys.argv[1]
args = {}
if command == 'script':
    source = Path(sys.argv[2]).read_text(encoding='utf-8-sig')
    args = {'python_code': 'namespace = {"bpy": bpy}\nexec(' + repr(source) + ', namespace)\nresult = namespace.get("result")'}
    command = 'exec_python'
elif len(sys.argv) > 2:
    args = json.loads(sys.argv[2])
with socket.create_connection(('127.0.0.1', 9877), timeout=60) as connection:
    connection.sendall((json.dumps({'command': command, 'args': args}) + '\n').encode())
    response = json.loads(connection.makefile('rb').readline())
print(json.dumps(response, ensure_ascii=False))
if not response.get('ok'):
    sys.exit(1)
