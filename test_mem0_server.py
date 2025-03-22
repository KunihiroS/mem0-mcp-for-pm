# improved_test_mcp_server.py
import requests
import json
import time
import asyncio
import httpx
import sseclient  # SSEクライアントライブラリ
from threading import Thread

SERVER_HOST = "localhost"
SERVER_PORT = 8080
SSE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/sse"
MESSAGE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/messages/"

class MCPTestClient:
    """MCP プロトコルに準拠したテストクライアント"""
    
    def __init__(self):
        self.response_queue = asyncio.Queue()
        self.sse_client = None
        self.sse_thread = None
    
    def start_sse_connection(self):
        """SSE 接続を確立し、応答を非同期キューに格納"""
        def _sse_listener():
            try:
                response = requests.get(SSE_URL, stream=True)
                self.sse_client = sseclient.SSEClient(response)
                
                for event in self.sse_client.events():
                    if event.data:
                        try:
                            data = json.loads(event.data)
                            asyncio.run(self.response_queue.put(data))
                        except json.JSONDecodeError:
                            print(f"無効な JSON データ: {event.data}")
            except Exception as e:
                print(f"SSE 接続エラー: {str(e)}")
        
        self.sse_thread = Thread(target=_sse_listener)
        self.sse_thread.daemon = True
        self.sse_thread.start()
        time.sleep(1)  # 接続確立を待機
    
    async def send_command(self, method, params=None):
        """コマンドを送信し、対応する応答を待機"""
        request_id = str(int(time.time()))
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }
        
        # メッセージ送信
        async with httpx.AsyncClient() as client:
            await client.post(MESSAGE_URL, json=payload)
        
        # 対応する応答を待機
        timeout = 5.0  # 5秒タイムアウト
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = await asyncio.wait_for(
                    self.response_queue.get(), 
                    timeout=timeout - (time.time() - start_time)
                )
                
                if isinstance(response, dict) and response.get("id") == request_id:
                    return response
            except asyncio.TimeoutError:
                break
        
        return None
    
    def close(self):
        """接続をクリーンアップ"""
        if self.sse_client:
            self.sse_client.close()
        if self.sse_thread and self.sse_thread.is_alive():
            self.sse_thread.join(timeout=1.0)

async def run_tests():
    """テストスイートを実行"""
    client = MCPTestClient()
    
    try:
        print("MCP サーバーテスト開始...")
        client.start_sse_connection()
        
        # プロジェクトメモリ追加テスト
        print("テスト 1: プロジェクトメモリ追加...")
        add_result = await client.send_command(
            "add_project_memory", 
            {
                "text": "// [PROJECT: test-project] [TIMESTAMP: 2025-03-11T10:00:00+09:00]\n"
                        "const projectStatus = {\n"
                        "  name: 'Test Project',\n"
                        "  progress: 0.5,\n"
                        "  status: 'in-progress'\n"
                        "};"
            }
        )
        print(f"結果: {add_result}")
        
        # 検索テスト
        print("テスト 2: プロジェクトメモリ検索...")
        search_result = await client.send_command(
            "search_project_memories",
            {"query": "test-project status"}
        )
        print(f"結果: {search_result}")
        
        # 全メモリ取得テスト
        print("テスト 3: 全プロジェクトメモリ取得...")
        all_result = await client.send_command("get_all_project_memories", {})
        print(f"結果: {all_result}")
        
        # 成功判定
        all_passed = (
            add_result and 'result' in add_result and
            search_result and 'result' in search_result and
            all_result and 'result' in all_result
        )
        
        print(f"\n総合結果: {'全テスト成功' if all_passed else '一部テスト失敗'}")
        return all_passed
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(run_tests())