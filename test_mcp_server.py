# テスト用のラッパースクリプト
import json
import subprocess
import sys
import threading
import time

# サーバープロセスを起動
print("Starting server process...", file=sys.stderr)
proc = subprocess.Popen(
    ["python", "-m", "mem0_mcp_pm", "--debug"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE, # Keep stderr separate
    text=True,
    bufsize=1 # Line buffered
)

# Function to read and print stderr in a separate thread
def print_stderr(pipe):
    try:
        while True:
            line = pipe.readline()
            if not line:
                break
            print(f"SERVER STDERR: {line.strip()}", file=sys.stderr)
    except Exception as e:
        print(f"Error reading stderr: {e}", file=sys.stderr)

stderr_thread = threading.Thread(target=print_stderr, args=(proc.stderr,), daemon=True)
stderr_thread.start()
print("Stderr reader thread started.", file=sys.stderr)

# Give server a moment to start
time.sleep(1)

# 初期化リクエスト送信
init_request = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {"clientInfo": {"name": "test-client"}, "capabilities": {}, "protocolVersion": "1.0"}, # Added missing params
    "id": 0
}
print(f"Sending: {json.dumps(init_request)}", file=sys.stderr)
proc.stdin.write(json.dumps(init_request) + "\n")
proc.stdin.flush()

# 初期化レスポンス読み取り
print("Waiting for init response...", file=sys.stderr)
init_response_line = proc.stdout.readline() # Read one line
print(f"Received init line: {init_response_line.strip()}", file=sys.stderr)
if not init_response_line:
    print("Error: Received empty init response line.", file=sys.stderr)
    proc.terminate()
    sys.exit(1)
try:
    init_response = json.loads(init_response_line)
    print("Init response:", init_response)
except json.JSONDecodeError as e:
    print(f"Error decoding init response JSON: {e}", file=sys.stderr)
    print(f"Raw init response line: {init_response_line!r}", file=sys.stderr)
    proc.terminate()
    sys.exit(1)


# ツールリスト要求送信
tools_request = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
}
print(f"Sending: {json.dumps(tools_request)}", file=sys.stderr)
proc.stdin.write(json.dumps(tools_request) + "\n")
proc.stdin.flush()

# ツールリスト応答読み取り
print("Waiting for tools response...", file=sys.stderr)
tools_response_line = proc.stdout.readline() # Read one line
print(f"Received tools line: {tools_response_line.strip()}", file=sys.stderr)
if not tools_response_line:
    print("Error: Received empty tools response line.", file=sys.stderr)
    proc.terminate()
    sys.exit(1)
try:
    tools_response = json.loads(tools_response_line)
    print("Tools response:", tools_response)
except json.JSONDecodeError as e:
    print(f"Error decoding tools response JSON: {e}", file=sys.stderr)
    print(f"Raw tools response line: {tools_response_line!r}", file=sys.stderr)
    proc.terminate()
    sys.exit(1)

# 終了処理
print("Closing stdin and terminating process...", file=sys.stderr)
proc.stdin.close() # Close stdin to signal server
proc.wait(timeout=5) # Wait for server to exit gracefully
if proc.poll() is None:
    print("Server did not exit gracefully, terminating...", file=sys.stderr)
    proc.terminate()

# Wait for stderr thread to finish
stderr_thread.join(timeout=1)

print("Test script finished.", file=sys.stderr)
