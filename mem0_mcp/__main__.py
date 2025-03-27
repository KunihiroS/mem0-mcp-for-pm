"""
mem0 MCP for Project Management - モジュール実行ポイント

このモジュールは、'python -m mem0_mcp'として実行された場合のエントリーポイントを提供します。
"""

from . import main

if __name__ == "__main__":
    # python -m mem0_mcp として実行された場合のエントリーポイント
    exit(main())