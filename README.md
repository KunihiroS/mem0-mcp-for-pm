# Simple MCP

A simple MCP (Memex Communication Protocol) server implementation using stdio transport.

## Installation

```bash
pipx install .
Usage
After installation, you can run the server:
bashコピーsimple-mcp
The server accepts JSON requests via stdin and returns responses via stdout.
コピー
## 3. パッケージのインストールとテスト

### 3.1 ローカル開発モードでインストール

まずは開発モードでインストールして動作確認します。

```bash
# 仮想環境を作成するとクリーンにテストできます（オプション）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# または
# .venv\Scripts\activate  # Windows

# インストール
pip install -e .
