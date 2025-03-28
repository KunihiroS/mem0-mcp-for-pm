"""
mem0-mcp-for-pm

このモジュールはmem0サービスと統合するMCPサーバーのエントリーポイントです。
モジュールとして直接実行された場合、メインエントリーポイントを呼び出します。

使用例:
    python -m mem0_mcp
    uvx run mem0-mcp-for-pm
    pipx run mem0-mcp-for-pm
"""

from mem0_mcp_pm import main # Adjusted import path

if __name__ == "__main__":
    main()
