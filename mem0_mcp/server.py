"""
mem0 MCP Server Core Implementation

このモジュールは、mem0サービスと統合するMCPサーバーのコア実装を提供します。
標準入出力（stdio）ベースの通信を使用して、MCP Hostとの連携を実現します。
"""

import json
import os
from typing import Sequence, Dict, List, Union, Optional, Any

from mem0 import MemoryClient  # Corrected import name
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError

# mem0クライアントの初期化関数
def init_mem0_client() -> MemoryClient:
    """mem0クライアントの初期化と設定"""
    import os
    import sys
    
    # APIキーの確認
    api_key = os.environ.get("MEM0_API_KEY")
    if not api_key:
        print("エラー: MEM0_API_KEY環境変数が設定されていません", file=sys.stderr)
        sys.exit(1)
        
    client = MemoryClient()
    
    # カスタム指示の設定
    custom_instructions = """
    Interpret and Extract Project Management Information:

    # Primary Extraction Categories
    - Project Status: Extract current progress state, completion levels, and overall status.
    - Task Management: Identify tasks with their priorities, dependencies, statuses, and deadlines.
    - Decision Records: Document decisions, their rationale, implications, and related constraints.
    - Resource Allocation: Capture information about resource usage, assignments, and availability.
    - Risk Assessment: Identify potential risks, their impact ratings, and mitigation strategies.
    - Technical Artifacts: Extract technical specifications, dependencies, and implementation notes.

    # Memory Structure and Templates
    - Use the following templates to structure your input:
      - Project Status: Track overall project progress and current focus. Mandatory Fields: `name`, `purpose`. Optional Fields: `version`, `phase`, `completionLevel`, `milestones`, `currentFocus`.
      - Task Management: Manage task priorities, statuses, and dependencies. Mandatory Fields: `description`, `status`. Optional Fields: `deadline`, `assignee`, `dependencies`.
      - Decision Records: Document decisions, their rationale, implications, and constraints. Mandatory Fields: `topic`, `selected`, `rationale`. Optional Fields: `options`, `implications`, `constraints`, `responsible`, `stakeholders`.
      - Resource Allocation: Capture information about resource usage, assignments, and availability. Mandatory Fields: None. Optional Fields: `team`, `infrastructure`, `budget`.
      - Risk Assessment: Identify potential risks, their impact ratings, and mitigation strategies. Mandatory Fields: `description`, `impact`, `probability`. Optional Fields: `mitigation`, `owner`, `monitoringItems`.
      - Technical Artifacts: Extract technical specifications, dependencies, and implementation notes. Mandatory Fields: None. Optional Fields: `architecture`, `technologies`, `standards`.
    - Refer to the 'Memory Structure and Templates' section in the documentation for detailed descriptions and examples.

    # Metadata Extraction (when available)
    - Temporal Context: Extract timestamps, durations, deadlines, and sequence information. Format dates and times using ISO 8601 format.
    - Project Context: Identify project names, phases, domains, and scope indicators.
    - Relationship Mapping: Extract relationships between extracted elements, such as:
      - 'relatedTo': Elements that are related to each other (bidirectional).
      - 'enables': Element A enables element B (directional).
      - 'blockedBy': Element A is blocked by element B (directional).
      - 'dependsOn': Element A depends on element B (directional).
      - Relationships should be extracted as strings or arrays of strings.

    # Interpretation Guidelines
    - For structured input (JavaScript/JSON objects): Preserve the structural hierarchy while enriching with contextual metadata, and extract key-value pairs.
    - For code-structured representations: Analyze both the structural patterns (e.g., variable names, function names, class names) and the semantic content (e.g., comments, descriptions, code logic).
    - For mixed-format input: Prioritize semantic content while acknowledging structural hints (e.g., headings, lists, tables). Extract information from text, code snippets, and structured data blocks.

    # Output Structure Formation
    - Extracted information should be categorized according to the Primary Extraction Categories.
    - Preserve original identifiers and reference keys (e.g., project name, task ID) for continuity.
    - When metadata such as project name and timestamp are not explicitly provided as top-level keys, attempt to infer them from the context (e.g., from comments).
    - The output should be a JSON object with the following structure:
      {
        "category": "string",  // Primary Extraction Category (e.g., "Task Management")
        "content": "any",      // Extracted content (e.g., task details)
        "metadata": "object",  // Extracted metadata (e.g., {"project": "ProjectA", "deadline": "2023-12-01"})
        "relationships": "array"  // Extracted relationships (e.g., [{"type": "dependsOn", "target": "TaskB"}])
      }
    """
    client.update_project(custom_instructions=custom_instructions)
    return client

# mem0ツール実装クラス
class Mem0Tools:
    """mem0 APIとの連携機能を提供するツールセット
    
    このクラスは、プロジェクト情報の追加、検索、更新、削除などの
    mem0 APIと連携する機能を提供します。
    """
    
    def __init__(self):
        """初期化"""
        self.client = init_mem0_client()
        self.default_user_id = "cursor_mcp"
    
    def add_project_memory(
        self, 
        text: str, 
        run_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        immutable: bool = False,
        expiration_date: Optional[str] = None,
        custom_categories: Optional[Dict] = None,
        includes: Optional[str] = None,
        excludes: Optional[str] = None,
        infer: Optional[bool] = None
    ) -> Dict:
        """プロジェクト情報をmem0に追加
        
        Args:
            text: 追加するプロジェクト情報テキスト
            run_id: セッション識別子（オプション）
            metadata: 追加メタデータ（オプション）
            immutable: 変更不可フラグ（オプション）
            expiration_date: 有効期限（オプション）
            custom_categories: カスタムカテゴリ（オプション）
            includes: 含めるコンテンツ指定（オプション）
            excludes: 除外するコンテンツ指定（オプション）
            infer: 構造推論フラグ（オプション）
            
        Returns:
            Dict: 処理結果を含む辞書
        """
        try:
            messages = [{"role": "user", "content": text}]
            
            # APIパラメータの構築
            api_params = {
                "messages": messages,
                "user_id": self.default_user_id,
                "output_format": "v1.1",
                "version": "v2"
            }
            
            # オプションパラメータの追加
            if run_id:
                api_params["run_id"] = run_id
            if metadata:
                api_params["metadata"] = metadata
            if immutable:
                api_params["immutable"] = immutable
            if expiration_date:
                api_params["expiration_date"] = expiration_date
            if custom_categories:
                api_params["custom_categories"] = custom_categories
            if includes:
                api_params["includes"] = includes
            if excludes:
                api_params["excludes"] = excludes
            if infer is not None:
                api_params["infer"] = infer
                
            # API呼び出し
            response = self.client.add(**api_params)
            
            # 成功情報の構築
            success_parts = ["Successfully added project information"]
            
            # 使用パラメータ情報を追加
            param_details = []
            if run_id:
                param_details.append(f"run_id: '{run_id}'")
            if metadata:
                param_details.append(f"metadata: {metadata}")
            if immutable:
                param_details.append("immutable: True")
            if expiration_date:
                param_details.append(f"expiration_date: '{expiration_date}'")
            if custom_categories:
                param_details.append(f"custom_categories: {len(custom_categories)} categories")
            if includes or excludes or infer is not None:
                param_details.append("content filtering applied")
                
            # パラメータ情報をレスポンスに含める
            if param_details:
                success_parts.append("with " + ", ".join(param_details))
                
            return {"success": True, "message": " ".join(success_parts)}
        except Exception as e:
            error_message = str(e)
            error_type = type(e).__name__
            return {"success": False, "error": f"{error_type}: {error_message}"}
    
    def get_all_project_memories(
        self, 
        page: int = 1, 
        page_size: int = 50, 
        filters: Optional[Dict] = None
    ) -> Dict:
        """保存されたプロジェクト情報をすべて取得
        
        Args:
            page: ページ番号（デフォルト: 1）
            page_size: ページあたりの項目数（デフォルト: 50）
            filters: フィルタ条件（オプション）
            
        Returns:
            Dict: 取得結果を含む辞書
        """
        try:
            response = self.client.get_all(
                user_id=self.default_user_id,
                page=page,
                page_size=page_size,
                version="v2",
                filters=filters
            )
            return response
        except Exception as e:
            return {"error": f"Error retrieving project information: {str(e)}"}
    
    def search_project_memories(
        self, 
        query: str, 
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """プロジェクト情報を検索
        
        Args:
            query: 検索クエリ文字列
            filters: フィルタ条件（オプション）
            
        Returns:
            List[Dict]: 検索結果のリスト
        """
        try:
            memories = self.client.search(
                query, 
                user_id=self.default_user_id, 
                version="v2", 
                filters=filters
            )
            return memories
        except Exception as e:
            return {"error": f"Error searching project information: {str(e)}"}
    
    def update_project_memory(
        self,
        memory_id: str,
        text: str
    ) -> Dict:
        """既存のプロジェクト情報を更新
        
        Args:
            memory_id: 更新対象のメモリID
            text: 新しいコンテンツ
            
        Returns:
            Dict: 更新結果を含む辞書
        """
        try:
            updated_memory = self.client.update(memory_id, text)
            return updated_memory
        except Exception as e:
            return {"error": f"Error updating project memory: {str(e)}"}
    
    def delete_project_memory(
        self,
        memory_id: str
    ) -> Dict:
        """特定のプロジェクト情報を削除
        
        Args:
            memory_id: 削除対象のメモリID
            
        Returns:
            Dict: 削除結果を含む辞書
        """
        try:
            self.client.delete(memory_id=memory_id)
            return {"success": True, "message": f"Successfully deleted project memory with ID: {memory_id}"}
        except Exception as e:
            return {"success": False, "error": f"Error deleting project memory: {str(e)}"}
    
    def delete_all_project_memories(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        org_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict:
        """条件に一致するプロジェクト情報をすべて削除
        
        Args:
            user_id: ユーザーID（オプション）
            agent_id: エージェントID（オプション）
            app_id: アプリID（オプション）
            run_id: 実行ID（オプション）
            metadata: メタデータ（オプション）
            org_id: 組織ID（オプション）
            project_id: プロジェクトID（オプション）
            
        Returns:
            Dict: 削除結果を含む辞書
        """
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
                
            # フィルタ条件の説明を生成
            filter_description = ", ".join([f"{k}={v}" for k, v in filter_params.items()]) if filter_params else "no filters (ALL memories)"
            
            # APIクライアントを使用して削除を実行
            self.client.delete_all(**filter_params)
            
            return {"success": True, "message": f"Successfully deleted project memories with filters: {filter_description}"}
        except Exception as e:
            return {"success": False, "error": f"Error deleting project memories: {str(e)}"}

# MCPサーバーのメイン実装
async def serve(debug: bool = False) -> None:
    """MCPサーバーメイン実装
    
    標準入出力（stdio）を使用してMCP Hostと通信し、
    mem0ツールを提供します。
    
    Args:
        debug: デバッグモードフラグ（デフォルト: False）
    """
    # サーバーとツールの初期化
    server = Server("mem0-mcp-for-pm")
    mem0_tools = Mem0Tools()
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """利用可能なツールのリストを返す"""
        return [
            Tool(
                name="add_project_memory",
                description="Add or update structured project information in mem0 using v2 API.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The project information to add to mem0."
                        },
                        "run_id": {
                            "type": "string",
                            "description": "Session identifier for organizing related memories."
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional structured information about this memory."
                        },
                        "immutable": {
                            "type": "boolean",
                            "description": "If true, this memory cannot be modified later."
                        },
                        "expiration_date": {
                            "type": "string",
                            "description": "Date when this memory should expire (YYYY-MM-DD)."
                        },
                        "custom_categories": {
                            "type": "object",
                            "description": "Custom categories for organizing project information."
                        },
                        "includes": {
                            "type": "string",
                            "description": "Specific aspects to include in the memory."
                        },
                        "excludes": {
                            "type": "string",
                            "description": "Specific aspects to exclude from the memory."
                        },
                        "infer": {
                            "type": "boolean",
                            "description": "Whether to infer structured data from the input."
                        }
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="get_all_project_memories",
                description="Retrieve all stored project management information for the default user (v2 API).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "The page number to retrieve. Default is 1."
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "The number of items per page. Default is 50."
                        },
                        "filters": {
                            "type": "object",
                            "description": "A dictionary of filters to apply."
                        }
                    }
                }
            ),
            Tool(
                name="search_project_memories",
                description="Search through stored project management information using semantic search (v2 API).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query string."
                        },
                        "filters": {
                            "type": "object",
                            "description": "A dictionary of filters to apply to the search."
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="update_project_memory",
                description="Update an existing project memory with new content.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "The unique identifier of the memory to update."
                        },
                        "text": {
                            "type": "string",
                            "description": "The new content for the memory."
                        }
                    },
                    "required": ["memory_id", "text"]
                }
            ),
            Tool(
                name="delete_project_memory",
                description="Delete a specific project memory from mem0.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "The unique identifier of the memory to delete."
                        }
                    },
                    "required": ["memory_id"]
                }
            ),
            Tool(
                name="delete_all_project_memories",
                description="Delete multiple project memories based on specified filters.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Filter memories by user ID."
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Filter memories by agent ID."
                        },
                        "app_id": {
                            "type": "string",
                            "description": "Filter memories by app ID."
                        },
                        "run_id": {
                            "type": "string",
                            "description": "Filter memories by run ID."
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Filter memories by metadata."
                        },
                        "org_id": {
                            "type": "string",
                            "description": "Filter memories by organization ID."
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Filter memories by project ID."
                        }
                    }
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """ツール呼び出し処理"""
        try:
            result = None
            
            # ツール名に応じた処理の振り分け
            if name == "add_project_memory":
                result = mem0_tools.add_project_memory(**arguments)
            elif name == "get_all_project_memories":
                result = mem0_tools.get_all_project_memories(**arguments)
            elif name == "search_project_memories":
                result = mem0_tools.search_project_memories(**arguments)
            elif name == "update_project_memory":
                result = mem0_tools.update_project_memory(**arguments)
            elif name == "delete_project_memory":
                result = mem0_tools.delete_project_memory(**arguments)
            elif name == "delete_all_project_memories":
                result = mem0_tools.delete_all_project_memories(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            # デバッグ出力
            if debug:
                print(f"Tool '{name}' called with arguments: {arguments}")
                print(f"Result: {result}")
            
            # 結果をJSON形式で返却
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            error_message = str(e)
            error_type = type(e).__name__
            if debug:
                import traceback
                traceback.print_exc()
            raise ValueError(f"Error processing mem0-mcp-for-pm tool call: {error_type} - {error_message}")
    
    try:
        # 標準入出力通信の確立
        options = server.create_initialization_options()
        if debug:
            print("Starting mem0-mcp-for-pm server using stdio transport")
            print("Initialization options:", options)
        
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                options
            )
    except Exception as e:
        error_message = str(e)
        if debug:
            import traceback
            traceback.print_exc()
        print(f"Error in mem0-mcp-for-pm server: {error_message}", file=os.sys.stderr)
        raise

# --- stdioサーバーモードの追加 ---
def main():
    """
    標準入出力ベースのmem0 MCPサーバー（最小構成）。
    1行ごとにJSONリクエストを受け取り、Mem0Tools経由でツールを呼び出し、JSONレスポンスを返す。
    リクエスト例: {"tool": "add_project_memory", "arguments": {...}}
    """
    import sys
    import logging
    mem0_tools = Mem0Tools()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='mem0-mcp-stdio.log'
    )
    print("mem0-mcp stdio server is running. Send JSON requests via stdin.", file=sys.stderr)
    for line in sys.stdin:
        try:
            req = json.loads(line)
            tool = req.get("tool")
            arguments = req.get("arguments", {})
            if not tool:
                raise ValueError("toolフィールドが必要です")
            # Mem0Toolsのメソッドにディスパッチ
            if not hasattr(mem0_tools, tool):
                raise ValueError(f"未対応のツール: {tool}")
            method = getattr(mem0_tools, tool)
            result = method(**arguments)
            resp = {"status": "success", "result": result}
            print(json.dumps(resp, ensure_ascii=False), flush=True)
            logging.info(f"tool={tool} arguments={arguments} result={result}")
        except Exception as e:
            err = {"status": "error", "error": str(e)}
            print(json.dumps(err, ensure_ascii=False), flush=True)
            logging.error(f"error: {e}")

if __name__ == "__main__":
    main()