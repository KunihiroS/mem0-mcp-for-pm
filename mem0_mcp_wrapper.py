#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mem0-mcp-for-pm エントリーポイント

このスクリプトは、pipx/uvxでオンデマンド実行するためのエントリーポイントです。
"""

import os
import sys
import pathlib
import importlib.util
import importlib.machinery

def main():
    """メイン実行関数"""
    # スクリプトのディレクトリとパスを取得
    script_path = pathlib.Path(__file__).resolve()
    script_dir = script_path.parent
    
    # mem0_mcpディレクトリへのパス
    module_dir = script_dir / "mem0_mcp"
    
    # デバッグモードの確認
    debug = "--debug" in sys.argv
    
    if debug:
        print(f"実行パス: {__file__}", file=sys.stderr)
        print(f"カレントディレクトリ: {os.getcwd()}", file=sys.stderr)
        print(f"スクリプトディレクトリ: {script_dir}", file=sys.stderr)
        print(f"モジュールディレクトリ: {module_dir}", file=sys.stderr)
        print(f"sys.path: {sys.path}", file=sys.stderr)
    
    # モジュールがあるかチェック
    if module_dir.exists() and (module_dir / "__init__.py").exists():
        # sys.pathにスクリプトディレクトリを追加
        sys.path.insert(0, str(script_dir))
        
        try:
            # mem0_mcpモジュールをインポート
            from mem0_mcp import main as mem0_main
            
            # 環境変数をチェック
            if not os.environ.get("MEM0_API_KEY"):
                print("エラー: MEM0_API_KEY環境変数が設定されていません", file=sys.stderr)
                return 1
                
            # main関数を実行
            return mem0_main()
        except ImportError as e:
            if debug:
                print(f"エラー: 通常のインポート方法でmem0_mcpモジュールのインポートに失敗しました: {e}", file=sys.stderr)
            
            # 代替のインポート方法を試す
            try:
                # 明示的にモジュールをロード
                init_path = module_dir / "__init__.py"
                spec = importlib.util.spec_from_file_location("mem0_mcp", init_path)
                mem0_module = importlib.util.module_from_spec(spec)
                sys.modules["mem0_mcp"] = mem0_module
                spec.loader.exec_module(mem0_module)
                
                # main関数を取得
                mem0_main = mem0_module.main
                
                # 環境変数をチェック
                if not os.environ.get("MEM0_API_KEY"):
                    print("エラー: MEM0_API_KEY環境変数が設定されていません", file=sys.stderr)
                    return 1
                
                # main関数を実行
                return mem0_main()
            except Exception as e2:
                print(f"エラー: 代替方法でもmem0_mcpモジュールのインポートに失敗しました: {e2}", file=sys.stderr)
                return 1
    else:
        print(f"エラー: mem0_mcpモジュールが見つかりません: {module_dir}", file=sys.stderr)
        
        # パッケージのありそうな場所を探して表示（デバッグ用）
        if debug:
            for path in sys.path:
                p = pathlib.Path(path)
                if p.exists():
                    print(f"検索: {p}", file=sys.stderr)
                    for item in p.iterdir():
                        if item.name == "mem0_mcp" or item.name.startswith("mem0_mcp-"):
                            print(f"  見つかりました: {item}", file=sys.stderr)
        
        return 1

if __name__ == "__main__":
    sys.exit(main())