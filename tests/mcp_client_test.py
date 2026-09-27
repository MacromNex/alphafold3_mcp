#!/usr/bin/env python3
"""
MCP Client Test for AlphaFold3 Server

Tests the MCP server by communicating with it over stdio like a real MCP client would.
"""

import json
import subprocess
import time
from pathlib import Path
import sys

class MCPClient:
    """Simple MCP client for testing"""

    def __init__(self, server_command):
        self.server_command = server_command
        self.request_id = 0

    def call_tool(self, tool_name: str, arguments: dict = None, timeout: int = 30):
        """Call a tool through the MCP server"""
        self.request_id += 1

        # MCP initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        # Tool call request
        self.request_id += 1
        tool_request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }

        try:
            # Start the server process
            process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send initialize request
            init_json = json.dumps(init_request) + "\n"

            # Send tool call request
            tool_json = json.dumps(tool_request) + "\n"

            # Send both requests
            input_data = init_json + tool_json

            stdout, stderr = process.communicate(input=input_data, timeout=timeout)

            # Parse responses (expecting two JSON responses)
            responses = []
            for line in stdout.strip().split('\n'):
                if line.strip():
                    try:
                        responses.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            # Find the tool response
            tool_response = None
            for response in responses:
                if response.get('id') == self.request_id:
                    tool_response = response
                    break

            if tool_response and 'result' in tool_response:
                return {
                    'success': True,
                    'result': tool_response['result'],
                    'error': None
                }
            elif tool_response and 'error' in tool_response:
                return {
                    'success': False,
                    'result': None,
                    'error': tool_response['error']
                }
            else:
                return {
                    'success': False,
                    'result': None,
                    'error': f"No valid response found. Responses: {responses}"
                }

        except subprocess.TimeoutExpired:
            process.kill()
            return {
                'success': False,
                'result': None,
                'error': f"Timeout after {timeout} seconds"
            }
        except Exception as e:
            return {
                'success': False,
                'result': None,
                'error': str(e)
            }

def test_mcp_server():
    """Test MCP server through stdio interface"""
    project_root = Path(__file__).parent.parent
    server_path = project_root / "src" / "server.py"
    python_path = "/home/xux/miniforge3/envs/protein-mcp/bin/python"

    client = MCPClient([python_path, str(server_path)])

    print("🚀 Testing AlphaFold3 MCP Server via stdio interface")
    print(f"📍 Server: {server_path}")
    print("-" * 60)

    tests = [
        {
            "name": "get_server_info",
            "description": "Server information",
            "arguments": {}
        },
        {
            "name": "get_example_workflows",
            "description": "Example workflows",
            "arguments": {}
        },
        {
            "name": "create_simple_protein_config",
            "description": "Create protein config",
            "arguments": {
                "sequence": "MDPSSPPSDLLPTRGTPHTLEMLQHWR",
                "name": "test_protein",
                "output_dir": str(project_root / "test_output" / "mcp_test")
            }
        },
        {
            "name": "validate_fasta_sequences",
            "description": "Validate FASTA (should fail with fake file)",
            "arguments": {
                "fasta_path": "/fake/nonexistent.fasta"
            }
        },
        {
            "name": "list_jobs",
            "description": "List current jobs",
            "arguments": {}
        }
    ]

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n🧪 Testing: {test['description']}")
        print(f"   Tool: {test['name']}")

        start_time = time.time()
        result = client.call_tool(test['name'], test['arguments'])
        duration = time.time() - start_time

        if result['success']:
            print(f"✅ PASSED ({duration:.2f}s)")
            print(f"   Result: {json.dumps(result['result'], indent=2)[:200]}...")
            passed += 1
        else:
            print(f"❌ FAILED ({duration:.2f}s)")
            print(f"   Error: {result['error']}")
            failed += 1

    print("\n" + "="*60)
    print("📊 MCP STDIO TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Pass Rate: {passed/len(tests)*100:.1f}%")

    if passed == len(tests):
        print("🎉 All MCP stdio tests passed!")
        print("✅ MCP server is working correctly through stdio interface")
    else:
        print(f"⚠️  {failed} test(s) failed")

    return passed == len(tests)

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)