"""
mem0 MCP for Project Management - Main Package

このパッケージは、mem0サービスとMCP Hostを連携するためのサーバーを提供します。
プロジェクト管理情報の保存、検索、更新などの機能を実装しています。
"""

import sys
from .server import main as server_main

def main():
    """
    エントリーポイント関数 - pipx/uvx経由で実行される
    """
    return server_main()