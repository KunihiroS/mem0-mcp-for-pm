import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:8080/messages/"

def test_add_project_memory():
    """Test adding project information"""
    payload = {
        "jsonrpc": "2.0",
        "method": "add_project_memory",
        "params": {
            "text": "// [PROJECT: test-project] [TIMESTAMP: 2025-03-11T10:00:00+09:00]\nconst projectStatus = {\n  name: 'Test Project',\n  progress: 0.5,\n  status: 'in-progress'\n};"
        },
        "id": "1"
    }
    
    response = requests.post(BASE_URL, json=payload)
    result = response.json()
    print(f"Add Project Memory Test: {'Success' if 'result' in result else 'Failed'}")
    return 'result' in result

def test_search_project_memories():
    """Test searching project information"""
    # Give time for the added memory to be indexed
    time.sleep(2)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "search_project_memories",
        "params": {
            "query": "test-project status"
        },
        "id": "2"
    }
    
    response = requests.post(BASE_URL, json=payload)
    result = response.json()
    print(f"Search Project Memories Test: {'Success' if 'result' in result else 'Failed'}")
    return 'result' in result

def test_get_all_project_memories():
    """Test retrieving all project information"""
    payload = {
        "jsonrpc": "2.0",
        "method": "get_all_project_memories",
        "params": {},
        "id": "3"
    }
    
    response = requests.post(BASE_URL, json=payload)
    result = response.json()
    print(f"Get All Project Memories Test: {'Success' if 'result' in result else 'Failed'}")
    return 'result' in result

if __name__ == "__main__":
    print("Running mem0 MCP Server tests...")
    
    # Start tests
    all_passed = (
        test_add_project_memory() and
        test_search_project_memories() and
        test_get_all_project_memories()
    )
    
    print(f"\nOverall test result: {'All tests passed' if all_passed else 'Some tests failed'}")
