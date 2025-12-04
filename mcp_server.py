#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from fastmcp import FastMCP

# Use environment variable for managed directory in Docker, fallback to config
MANAGED_DIR = Path(os.getenv('MANAGED_DIR', '/app/managed_fs'))
SERVER_NAME = os.getenv('MCP_SERVER_NAME', 'System Administrator Tools')

mcp = FastMCP(SERVER_NAME)

@mcp.tool()
def get_file_content(file_path: str) -> str:
    """
    Read and return the content of a file from the managed filesystem.
    
    Args:
        file_path: Relative path to the file from the managed directory
        
    Returns:
        File content as string
    """
    try:
        full_path = MANAGED_DIR / file_path
        full_path = full_path.resolve()
        
        if not str(full_path).startswith(str(MANAGED_DIR.resolve())):
            return f"Error: Access denied - path outside managed directory"
        
        if not full_path.exists():
            return f"Error: File '{file_path}' not found"
        
        if not full_path.is_file():
            return f"Error: '{file_path}' is not a file"
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    except PermissionError:
        return f"Error: Permission denied for '{file_path}'"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def list_directory(dir_path: str = ".") -> list[str]:
    """
    List contents of a directory in the managed filesystem.
    
    Args:
        dir_path: Relative path to directory. Use "." for root.
        
    Returns:
        List of files and directories with type indicators
    """
    try:
        full_path = MANAGED_DIR / dir_path
        full_path = full_path.resolve()
        
        if not str(full_path).startswith(str(MANAGED_DIR.resolve())):
            return ["Error: Access denied - path outside managed directory"]
        
        if not full_path.exists():
            return [f"Error: Directory '{dir_path}' not found"]
        
        if not full_path.is_dir():
            return [f"Error: '{dir_path}' is not a directory"]
        
        items = []
        for item in sorted(full_path.iterdir()):
            if item.is_dir():
                items.append(f"[DIR]  {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"[FILE] {item.name} ({size} bytes)")
        
        return items if items else ["Directory is empty"]
    
    except PermissionError:
        return [f"Error: Permission denied for '{dir_path}'"]
    except Exception as e:
        return [f"Error listing directory: {str(e)}"]


# Create ASGI app for SSE transport (required for Google ADK SseConnectionParams)
app = mcp.http_app(transport='sse')

if __name__ == '__main__':
    try:
        # Get configuration from environment variables
        transport = os.getenv('MCP_TRANSPORT', 'stdio')

        print(f"Starting MCP server for directory: {MANAGED_DIR}")
        print(f"Transport: {transport}")

        if transport == 'http':
            # For HTTP transport, we export the app and let uvicorn run it
            # This script should be run with: uvicorn mcp_server:app --host 0.0.0.0 --port 8000
            print("Note: HTTP transport should be run with uvicorn")
            print("Example: uvicorn mcp_server:app --host 0.0.0.0 --port 8000")
        else:
            mcp.run(transport='stdio')
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
