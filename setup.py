from setuptools import setup, find_packages
import os

# パッケージルートパスを取得
package_root = os.path.abspath(os.path.dirname(__file__))

setup(
    name="mem0-mcp-for-pm",
    version="0.1.0",
    description="MCP Server for mem0 project management integration",
    packages=["mem0_mcp"],  # mem0_mcpパッケージを明示的に指定
    package_dir={"mem0_mcp": "mem0_mcp"},  # パッケージディレクトリを明示
    python_requires=">=3.12",
    install_requires=[
        "httpx>=0.28.1",
        "mcp>=1.3.0",
        "mem0ai>=0.1.55",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        'console_scripts': [
            'mem0-mcp-for-pm=mem0_mcp_wrapper:main',  # ラッパーモジュールを使用
        ],
    },
    include_package_data=True,
    py_modules=["mem0_mcp_wrapper"],  # ラッパースクリプトをモジュールとして含める
    zip_safe=False,
)