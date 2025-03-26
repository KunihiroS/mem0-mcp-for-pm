# mem0 MCP Server for project management

mem0 MCP Server is a bridge between MCP Host applications and the mem0 cloud service, providing memory capabilities for MCP Host AI.

This is forked in order to change the scope from coding to project management.
The forked deals more higher level context related with project management topics.

Additionally, this forked experimentally integrate cording format into high level context like human protocol.

## Features

- Forked in order to change the usage from original coding scope to project management scope.
- Project memory storage and retrieval
- Semantic search for finding relevant project information
- Structured project management data handling

## Installation and usage

### Pre-condition and requirement

- Python 12.0 or newer,
- mcp-proxy (in case Cline or Roo code)


### Details

1. Clone the repository and move into.

2. Set up virtual environment using `uv`.

```bash
uv venv --python 3.12
```
3. Activate virtual environment using `uv`.

```bash
source .venv/bin/activate
```

4. Install the dependencies using `uv`.

```bash
# Install in editable mode from pyproject.toml
uv pip install -e .
```

5. Create .gitignore in repo root.

```bash
touch .gitignore
```

6. Update .gitignore

```sample
# Python
__pycache__/
*.py[cod]
*.egg-info/

# Environment variables
.env

# Egg info
mem0_mcp.egg-info/
```

7. Create .env in repo root.

```bash
touch .env
```

8. Update .env

```
MEM0_API_KEY={your API Key}
```

9. Clone and install the following OSS.

https://github.com/sparfenyuk/mcp-proxy

10. Add MCP Server settings.

- Cline

```cline_mcp_settings.json
"mem0": {
      "command": "PATH_TO/mcp-proxy", # ex: /home/{user}/.local/bin/mcp-proxy
      "args": [
        "http://127.0.0.1:6789/sse" # configure port as you need
      ]
    }
```

11. Launch MCP Server (activated virtual env required)

```bash
python main.py --host 127.0.0.1 --port 6789
```

12. Check the functionality by MCP Host (like Cline)

```
Hey, can you get all memories on mem0?
```

## Operation

- Ensure run MCP Server fast.
- There are several ways automatic run server, like adding script .bashrc
- Set up automatic as your environment is easier usage.

## Available Tools

- add_project_memory: Add new project management information
- get_all_project_memories: Retrieve all stored project information
- search_project_memories: Search for specific project information

## Technical details

The uniqueness of this forked is the structured format between MCP Host and mem0 is expected in coding format like Javascript object.
Make sure you set the custom instruction to be able to handle better.

## Custom instruction

In order to make mem0 working as fitting to project management purpose, this forked has the following instruction for AI.

### For mem0

- Check the source code.

### For MCP Host

- [Host_inst.md] is just sample, find the best by yourself !!

# mem0-mcp-for-pm

このプロジェクトは、mem0サービスと統合するMCPサーバーの実装例です。  
主にSSEトランスポート方式による常時稼働サーバーとして設計されています。

## 使い方

pipx または uvx を用いて実行可能です。

## 依存関係

- Python >= 3.12
- httpx, mcp, mem0ai など

（以下、プロジェクトのその他のドキュメントがここに含まれます）

## 改修計画

### 背景

現行のmem0-mcpはSSEトランスポート方式を用いた常時稼働型サーバーとして実装されていますが、  
リソース消費やポート管理の問題があり、ユーザーの利便性が低い点が課題でした。  
そのため、pipx/uvx経由で動的に起動できる、軽量なスタイルへの改修が求められています。

### 概要

- プロジェクト構造の再構築：__init__.py, __main__.py, server.pyに分割  
- 標準入出力（stdio）を利用した通信方式への切り替え  
- ツール定義（Mem0Toolsクラス）の再設計とAPI連携の強化  
- 環境変数を利用したセキュアな設定管理  
- pipx/uvxによる簡易なインストールと実行

### 実装戦略

1. 準備段階：既存コードを分析し、依存関係を整理する。  
2. 実装段階：新しいディレクトリ構造に合わせ、stdioサーバー実装を中心にコード改修を行う。  
3. テスト段階：単体テストおよび統合テストを実施し、動作とエラーハンドリングを検証する。  
4. パッケージングと配布：pyproject.tomlを整備し、pipx/uvxでの簡単なインストール・実行を実現する。

### まとめ

本改修計画により、mem0-mcpは動的に起動可能な軽量サーバーとして再構築され、  
ユーザーはpipx/uvxを通じて手軽に利用できるようになります。  
また、将来的なビジネスロジックの分離や他サービスへの転用も視野に入れた設計となっております.
  
――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
以上

## 改修計画追記

以下は、Tavily SearchやBrave Searchなどの外部情報源を参照して、MCPアーキテクチャの調査および裏付けを行った結果に基づく、改修計画の追加情報です.

### 調査結果の裏付け

- MCPの仕様文書や業界情報から、stdioトランスポート方式が動的起動に適していることが確認されました。これにより、従来のSSE方式に比べ、リソース消費の削減とユーザーの利便性向上が期待されます.
- Brave Searchなどの調査結果から、オンデマンド実行環境に最適なMCPサーバーの動的起動が、クラウドネイティブな運用において実績を持つことが裏付けられました.

### 改修計画の概要

1. **プロジェクト構造の再構築**  
   既存のコードを、__init__.py, __main__.py, server.pyの3ファイルに分割して再構築し、可読性と拡張性を向上させます.

2. **通信方式の切り替え**  
   現行のSSE方式から、標準入出力（stdio）を利用した通信方式に切り替え、動的なプロセス起動を可能にし、リソース消費とポート管理の負担を軽減します.

3. **ツール定義とAPI連携の強化**  
   Mem0Toolsクラスを中心に、mem0 APIとの連携および各種ツールの入力スキーマを明確に定義します.

4. **環境変数による設定管理**  
   MEM0_API_KEYなどの重要情報を環境変数で管理し、セキュリティおよび実行環境の柔軟性を確保します.

5. **パッケージングと配布の簡易化**  
   pyproject.tomlを整備し、pipx/uvxを通じたインストールと実行を容易にします.

### まとめ

追加調査に基づく本改修計画は、動的に起動可能な軽量MCPサーバーの実現により、ユーザーが手間なくmem0サービスと統合された環境を利用できる最適なアプローチであると確信しています。さらに、将来的な機能拡張および他サービスへの転用も視野に入れた設計となっています.

以上が、追記された改修計画の追加情報です.