#!/usr/bin/env python3
"""
mem0-mcp-for-pmスタンドアロン実行スクリプト

すべての機能を1つのファイルに統合した実行可能なスクリプトです。
pipx/uvxによるオンデマンド実行に最適化されています。
"""

import os
import sys
import asyncio
import json
from typing import Dict, List, Optional, Union, Any

# 環境変数からAPIキーを取得
from dotenv import load_dotenv
load_dotenv()  # .envファイルから環境変数を読み込む

# MCPサーバーの依存関係
from mcp import Server, StdioServerTransport
from mcp.server import Message, ServerCapabilities
from mem0ai import MemoryClient

# デバッグフラグ（コマンドライン引数から取得）
DEBUG = "--debug" in sys.argv

# Mem0クライアントの初期化
mem0_client = MemoryClient()
DEFAULT_USER_ID = "mem0_mcp_user"

# MCPツール実装
async def add_project_memory(
    text: str, 
    run_id: str = None, 
    metadata: dict = None, 
    immutable: bool = False, 
    expiration_date: str = None,
    custom_categories: dict = None,
    includes: str = None,
    excludes: str = None,
    infer: bool = None
) -> str:
    """プロジェクト管理情報をmem0に追加します"""
    try:
        messages = [{"role": "user", "content": text}]
        
        # APIパラメータの構築
        api_params = {
            "messages": messages,
            "user_id": DEFAULT_USER_ID,
            "output_format": "v1.1",
            "version": "v2"
        }
        
        # オプションパラメータの追加
        if run_id: api_params["run_id"] = run_id
        if metadata: api_params["metadata"] = metadata
        if immutable: api_params["immutable"] = immutable
        if expiration_date: api_params["expiration_date"] = expiration_date
        if custom_categories: api_params["custom_categories"] = custom_categories
        if includes: api_params["includes"] = includes
        if excludes: api_params["excludes"] = excludes
        if infer is not None: api_params["infer"] = infer
            
        # API呼び出し
        mem0_client.add(**api_params)
        
        return "プロジェクト情報を正常に追加しました"
    except Exception as e:
        return f"プロジェクト情報の追加に失敗しました: {str(e)}"

async def get_all_project_memories(
    page: int = 1, 
    page_size: int = 50, 
    filters: dict = None
) -> Union[List[Dict], Dict]:
    """保存されているすべてのプロジェクト管理情報を取得します"""
    try:
        return mem0_client.get_all(
            user_id=DEFAULT_USER_ID, 
            page=page, 
            page_size=page_size, 
            version="v2", 
            filters=filters
        )
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        return {"error": f"プロジェクト情報の取得に失敗しました: {str(e)}"}

async def search_project_memories(
    query: str, 
    filters: dict = None
) -> List[Dict]:
    """保存されているプロジェクト管理情報を検索します"""
    try:
        return mem0_client.search(query, user_id=DEFAULT_USER_ID, version="v2", filters=filters)
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        return {"error": f"プロジェクト情報の検索に失敗しました: {str(e)}"}

async def update_project_memory(
    memory_id: str, 
    text: str
) -> Dict:
    """既存のプロジェクトメモリを新しい内容で更新します"""
    try:
        return mem0_client.update(memory_id, text)
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        return {"error": f"プロジェクトメモリの更新に失敗しました: {str(e)}"}

async def delete_project_memory(memory_id: str) -> str:
    """特定のプロジェクトメモリをmem0から削除します"""
    try:
        mem0_client.delete(memory_id=memory_id)
        return f"ID: {memory_id} のプロジェクトメモリを正常に削除しました"
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        return f"プロジェクトメモリの削除に失敗しました: {str(e)}"

async def delete_all_project_memories(
    user_id: str = None,
    agent_id: str = None,
    app_id: str = None,
    run_id: str = None,
    metadata: dict = None,
    org_id: str = None,
    project_id: str = None
) -> str:
    """指定されたフィルタに基づいて複数のプロジェクトメモリを削除します"""
    try:
        # フィルタパラメータの構築
        filter_params = {}
        if user_id is not None:
            filter_params['user_id'] = user_id
        if agent_id is not None:
            filter_params['agent_id'] = agent_id
        if app_id is not None:
            filter_params['app_id'] = app_id
        if run_id is not None:
            filter_params['run_id'] = run_id
        if metadata is not None:
            filter_params['metadata'] = metadata
        if org_id is not None:
            filter_params['org_id'] = org_id
        if project_id is not None:
            filter_params['project_id'] = project_id
            
        # 削除の実行
        mem0_client.delete_all(**filter_params)
        
        filter_description = ", ".join([f"{k}={v}" for k, v in filter_params.items()]) if filter_params else "フィルタなし（すべてのメモリ）"
        return f"フィルタ: {filter_description} に一致するプロジェクトメモリを正常に削除しました"
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        return f"プロジェクトメモリの削除に失敗しました: {str(e)}"

# MCPサーバーの設定と実行
async def serve(debug: bool = False):
    """MCPサーバーを起動して実行します"""
    # 環境変数のチェック
    if not os.environ.get("MEM0_API_KEY"):
        print("環境変数MEM0_API_KEYが設定されていません", file=sys.stderr)
        return 1
    
    # StdioServerTransportを使用（pipx/uvx対応）
    transport = StdioServerTransport()
    
    # メッセージハンドラー
    async def handle_message(message: Message) -> Any:
        """受信したメッセージを処理します"""
        if debug:
            print(f"受信メッセージ: {message.method}, パラメータ: {message.params}", file=sys.stderr)
        
        # ツール呼び出しの処理
        if message.method == "add_project_memory":
            return await add_project_memory(**message.params)
        elif message.method == "get_all_project_memories":
            return await get_all_project_memories(**message.params)
        elif message.method == "search_project_memories":
            return await search_project_memories(**message.params)
        elif message.method == "update_project_memory":
            return await update_project_memory(**message.params)
        elif message.method == "delete_project_memory":
            return await delete_project_memory(**message.params)
        elif message.method == "delete_all_project_memories":
            return await delete_all_project_memories(**message.params)
        else:
            return {"error": f"不明なメソッド: {message.method}"}
    
    # サーバーの初期化
    server = Server(
        name="mem0-mcp-for-pm", 
        version="0.1.0",
        capabilities=ServerCapabilities(
            experimental={},
        ),
        transport=transport,
        message_handler=handle_message
    )
    
    if debug:
        print("mem0-mcp-for-pmサーバーを起動中（stdio transport使用）", file=sys.stderr)
    
    # 標準入出力ストリームの設定
    input_stream = asyncio.StreamReader()
    output_stream = asyncio.StreamWriter(sys.stdout.buffer, None)
    
    # サーバーの実行
    await server.run(
        input_stream=input_stream,
        output_stream=output_stream,
        initialization_options=server.create_initialization_options()
    )
    
    return 0

def main():
    """メインエントリーポイント"""
    if DEBUG:
        print(f"実行パス: {__file__}", file=sys.stderr)
        print(f"Pythonバージョン: {sys.version}", file=sys.stderr)
        print(f"コマンドライン引数: {sys.argv}", file=sys.stderr)
    
    return asyncio.run(serve(debug=DEBUG))

if __name__ == "__main__":
    sys.exit(main())