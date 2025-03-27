from .server import serve

def main():
    """MCP Server for mem0 project management - CLI entry point
    
    このモジュールは、mem0サービスと統合するMCPサーバーのコマンドラインインターフェースを提供します。
    uvx/pipxから直接実行可能な設計となっており、環境変数からの設定読み込みに対応しています。
    """
    import argparse
    import asyncio
    import os
    import sys
    
    # 環境変数の検証
    api_key = os.environ.get("MEM0_API_KEY")
    if not api_key:
        print("エラー: MEM0_API_KEY環境変数が設定されていません", file=sys.stderr)
        print("MEM0_API_KEYを環境変数として設定してください。例: export MEM0_API_KEY=your_key", file=sys.stderr)
        sys.exit(1)
    
    # コマンドライン引数の処理
    parser = argparse.ArgumentParser(
        description="mem0 MCP Server for project management integration"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="デバッグモードを有効化"
    )
    parser.add_argument(
        "--version", 
        action="store_true", 
        help="バージョン情報を表示"
    )
    
    args = parser.parse_args()
    
    # バージョン表示
    if args.version:
        print("mem0-mcp-for-pm v0.1.0")
        sys.exit(0)
    
    # デバッグモード設定
    debug_mode = args.debug
    if debug_mode:
        print("デバッグモードが有効化されました")
        # 将来的なロギング設定もここで実施
    
    try:
        # サーバー実行
        asyncio.run(serve(debug=debug_mode))
    except KeyboardInterrupt:
        print("\nユーザーによる中断を検出しました。終了します。")
        sys.exit(0)
    except Exception as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        if debug_mode:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()