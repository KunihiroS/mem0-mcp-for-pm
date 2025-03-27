#!/usr/bin/env python3
"""
デバッグ用エントリーポイント
"""

import os
import sys
import site
import pathlib

def main():
    """デバッグ情報を表示し、可能であればmem0_mcpをインポートして実行する"""
    # 基本情報を表示
    print("=== デバッグ情報 ===")
    print(f"実行パス: {__file__}")
    print(f"カレントディレクトリ: {os.getcwd()}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', '未設定')}")
    
    # 現在のPython実行環境の情報
    print(f"\nPython バージョン: {sys.version}")
    print(f"実行バイナリ: {sys.executable}")
    
    # sys.pathの内容を表示
    print("\n=== sys.path の内容 ===")
    for i, path in enumerate(sys.path):
        print(f"{i}: {path}")
    
    # サイトパッケージの場所を表示
    print("\n=== サイトパッケージの場所 ===")
    for path in site.getsitepackages():
        print(f"- {path}")
    
    # インストールされているパッケージを表示（親ディレクトリのみ）
    site_packages = site.getsitepackages()[0]
    print(f"\n=== {site_packages} 内のファイル ===")
    try:
        for item in pathlib.Path(site_packages).iterdir():
            print(f"- {item.name}")
    except Exception as e:
        print(f"エラー: {e}")
    
    # インポート試行
    print("\n=== mem0_mcpモジュールのインポート試行 ===")
    try:
        import mem0_mcp
        print(f"成功! モジュールパス: {mem0_mcp.__file__}")
        print(f"モジュール内容: {dir(mem0_mcp)}")
        print("\nmem0_mcp.main()を実行")
        return mem0_mcp.main()
    except ImportError as e:
        print(f"インポート失敗: {e}")
        
        # 手動探索を試みる
        print("\n=== 手動でmem0_mcpモジュールを探索 ===")
        for base_path in sys.path:
            module_path = os.path.join(base_path, "mem0_mcp")
            if os.path.isdir(module_path) and os.path.exists(os.path.join(module_path, "__init__.py")):
                print(f"見つかりました: {module_path}")
            
        return 1

if __name__ == "__main__":
    sys.exit(main())