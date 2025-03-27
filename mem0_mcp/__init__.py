"""
mem0 MCP for Project Management - Main Package

このパッケージは、mem0サービスとMCP Hostを連携するためのサーバーを提供します。
プロジェクト管理情報の保存、検索、更新などの機能を実装しています。
"""

import sys
import asyncio
from .server import serve

def main():
    """
    エントリーポイント関数 - pipx/uvx経由で実行される
    コマンドライン引数を解析し、サーバーを起動します
    """
    debug = "--debug" in sys.argv
    asyncio.run(serve(debug=debug))
    
    return 0  # 正常終了