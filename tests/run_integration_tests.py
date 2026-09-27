#!/usr/bin/env python3
"""
Automated Integration Test Runner for AlphaFold3 MCP Server

This script validates the MCP server functionality by testing:
- Server startup and tool discovery
- Sync tool execution
- Submit API workflow
- Error handling
- Job management
"""

import json
import subprocess
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class MCPTestRunner:
    def __init__(self, server_path: str = "src/server.py"):
        self.server_path = Path(server_path).resolve()
        self.project_root = self.server_path.parent.parent
        self.examples_dir = self.project_root / "examples"
        self.test_output_dir = self.project_root / "test_output"

        # Create test output directory
        self.test_output_dir.mkdir(exist_ok=True)

        self.results = {
            "test_date": datetime.now().isoformat(),
            "server_path": str(self.server_path),
            "project_root": str(self.project_root),
            "tests": {},
            "issues": [],
            "summary": {}
        }

        # Test data paths
        self.test_files = {
            "sample_fasta": self.examples_dir / "data" / "sample_protein.fasta",
            "variants_fasta": self.examples_dir / "data" / "protein_variants.fasta",
            "wt_data_json": self.examples_dir / "1iep_a3m_fix" / "1iep_a3m_fix_data.json",
        }

    def log_test(self, test_name: str, status: str, output: str = "", error: str = "", duration: float = 0):
        """Log test result"""
        self.results["tests"][test_name] = {
            "status": status,
            "output": output,
            "error": error,
            "duration_seconds": round(duration, 2)
        }

        status_emoji = "✅" if status == "passed" else "❌" if status == "failed" else "⚠️"
        print(f"{status_emoji} {test_name}: {status.upper()} ({duration:.2f}s)")
        if error:
            print(f"   Error: {error}")

    def test_server_startup(self) -> bool:
        """Test that server starts and imports correctly"""
        start_time = time.time()

        try:
            # Test import
            result = subprocess.run([
                "python", "-c",
                "from src.server import mcp; print(f'Server: {mcp.name}'); import asyncio; print(f'Tools: {len(asyncio.run(mcp.get_tools()))}')"
            ], capture_output=True, text=True, timeout=30, cwd=self.project_root)

            duration = time.time() - start_time

            if result.returncode == 0:
                self.log_test("server_startup", "passed", result.stdout, "", duration)
                return True
            else:
                self.log_test("server_startup", "failed", result.stdout, result.stderr, duration)
                return False

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log_test("server_startup", "failed", "", "Timeout after 30 seconds", duration)
            return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("server_startup", "error", "", str(e), duration)
            return False

    def test_sync_tool(self, tool_name: str, params: dict) -> bool:
        """Test a synchronous tool"""
        start_time = time.time()

        try:
            # Build Python test command
            params_str = ", ".join([f"{k}='{v}'" for k, v in params.items()])
            test_code = f"""
import asyncio
from src.server import mcp

async def test_tool():
    try:
        result = await mcp.call_tool('{tool_name}', {repr(params)})
        print(f"SUCCESS: {{result}}")
        return True
    except Exception as e:
        print(f"ERROR: {{e}}")
        return False

success = asyncio.run(test_tool())
exit(0 if success else 1)
"""

            result = subprocess.run([
                "python", "-c", test_code
            ], capture_output=True, text=True, timeout=60, cwd=self.project_root)

            duration = time.time() - start_time

            if result.returncode == 0:
                self.log_test(f"sync_tool_{tool_name}", "passed", result.stdout, "", duration)
                return True
            else:
                self.log_test(f"sync_tool_{tool_name}", "failed", result.stdout, result.stderr, duration)
                return False

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log_test(f"sync_tool_{tool_name}", "failed", "", "Timeout after 60 seconds", duration)
            return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(f"sync_tool_{tool_name}", "error", "", str(e), duration)
            return False

    def test_job_workflow(self) -> bool:
        """Test submit -> status -> result workflow"""
        start_time = time.time()

        try:
            # Submit a simple job (just config creation)
            test_code = """
import asyncio
from src.server import mcp
import json

async def test_workflow():
    try:
        # Create simple config first
        config_result = await mcp.call_tool('create_simple_protein_config', {
            'sequence': 'MDPSSPPSDLLPTRGTPHTLEMLQHWR',
            'name': 'test_job',
            'output_dir': 'test_output/job_test'
        })

        if config_result.get('status') != 'success':
            print(f"CONFIG_ERROR: {config_result}")
            return False

        # Test job management tools
        jobs_result = await mcp.call_tool('list_jobs', {})
        print(f"LIST_JOBS_SUCCESS: {len(jobs_result.get('jobs', []))} jobs found")

        # Test server info
        info_result = await mcp.call_tool('get_server_info', {})
        print(f"SERVER_INFO_SUCCESS: {info_result['server_name']}")

        return True
    except Exception as e:
        print(f"WORKFLOW_ERROR: {e}")
        return False

success = asyncio.run(test_workflow())
exit(0 if success else 1)
"""

            result = subprocess.run([
                "python", "-c", test_code
            ], capture_output=True, text=True, timeout=120, cwd=self.project_root)

            duration = time.time() - start_time

            if result.returncode == 0:
                self.log_test("job_workflow", "passed", result.stdout, "", duration)
                return True
            else:
                self.log_test("job_workflow", "failed", result.stdout, result.stderr, duration)
                return False

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log_test("job_workflow", "failed", "", "Timeout after 120 seconds", duration)
            return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("job_workflow", "error", "", str(e), duration)
            return False

    def test_error_handling(self) -> bool:
        """Test error handling with invalid inputs"""
        start_time = time.time()

        try:
            test_code = """
import asyncio
from src.server import mcp

async def test_errors():
    try:
        # Test invalid file path
        result1 = await mcp.call_tool('validate_fasta_sequences', {
            'fasta_path': '/nonexistent/file.fasta'
        })

        if result1.get('status') != 'error':
            print("ERROR_HANDLING_FAILED: Should have returned error status")
            return False

        # Test invalid sequence
        result2 = await mcp.call_tool('create_simple_protein_config', {
            'sequence': 'INVALID123XYZ',
            'name': 'test',
            'output_dir': 'test_output'
        })

        if result2.get('status') != 'error':
            print("ERROR_HANDLING_FAILED: Should have returned error for invalid sequence")
            return False

        print("ERROR_HANDLING_SUCCESS: All error cases handled properly")
        return True

    except Exception as e:
        print(f"ERROR_HANDLING_EXCEPTION: {e}")
        return False

success = asyncio.run(test_errors())
exit(0 if success else 1)
"""

            result = subprocess.run([
                "python", "-c", test_code
            ], capture_output=True, text=True, timeout=60, cwd=self.project_root)

            duration = time.time() - start_time

            if result.returncode == 0:
                self.log_test("error_handling", "passed", result.stdout, "", duration)
                return True
            else:
                self.log_test("error_handling", "failed", result.stdout, result.stderr, duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("error_handling", "error", "", str(e), duration)
            return False

    def test_file_operations(self) -> bool:
        """Test file operations and path resolution"""
        start_time = time.time()

        # Ensure test file exists
        if not self.test_files["sample_fasta"].exists():
            # Create a simple test FASTA file
            self.test_files["sample_fasta"].parent.mkdir(parents=True, exist_ok=True)
            self.test_files["sample_fasta"].write_text(">test_protein\nMDPSSPPSDLLPTRGTPHTLEMLQHWR\n")

        try:
            test_code = f"""
import asyncio
from src.server import mcp

async def test_files():
    try:
        # Test with relative path
        result1 = await mcp.call_tool('validate_fasta_sequences', {{
            'fasta_path': 'examples/data/sample_protein.fasta'
        }})

        # Test with absolute path
        result2 = await mcp.call_tool('validate_fasta_sequences', {{
            'fasta_path': '{self.test_files["sample_fasta"]}'
        }})

        if result1.get('status') == 'success' and result2.get('status') == 'success':
            print("FILE_OPERATIONS_SUCCESS: Both relative and absolute paths work")
            return True
        else:
            print(f"FILE_OPERATIONS_FAILED: result1={result1}, result2={result2}")
            return False

    except Exception as e:
        print(f"FILE_OPERATIONS_EXCEPTION: {{e}}")
        return False

success = asyncio.run(test_files())
exit(0 if success else 1)
"""

            result = subprocess.run([
                "python", "-c", test_code
            ], capture_output=True, text=True, timeout=60, cwd=self.project_root)

            duration = time.time() - start_time

            if result.returncode == 0:
                self.log_test("file_operations", "passed", result.stdout, "", duration)
                return True
            else:
                self.log_test("file_operations", "failed", result.stdout, result.stderr, duration)
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("file_operations", "error", "", str(e), duration)
            return False

    def check_dependencies(self) -> bool:
        """Check that all required dependencies are available"""
        start_time = time.time()

        try:
            # Check fastmcp
            result = subprocess.run([
                "python", "-c", "import fastmcp; print(f'fastmcp version: {fastmcp.__version__}')"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                self.log_test("dependencies", "failed", "", "fastmcp not available", time.time() - start_time)
                return False

            # Check loguru
            result = subprocess.run([
                "python", "-c", "import loguru; print('loguru available')"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                self.log_test("dependencies", "failed", "", "loguru not available", time.time() - start_time)
                return False

            duration = time.time() - start_time
            self.log_test("dependencies", "passed", "All dependencies available", "", duration)
            return True

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("dependencies", "error", "", str(e), duration)
            return False

    def run_all_tests(self) -> Dict:
        """Run all tests and return comprehensive results"""
        print(f"🚀 Starting MCP Integration Tests")
        print(f"📍 Project: {self.project_root}")
        print(f"📍 Server: {self.server_path}")
        print("-" * 60)

        # 1. Check dependencies
        print("1️⃣ Checking dependencies...")
        self.check_dependencies()

        # 2. Test server startup
        print("2️⃣ Testing server startup...")
        server_ok = self.test_server_startup()

        if not server_ok:
            print("❌ Server startup failed, skipping remaining tests")
            return self.generate_report()

        # 3. Test sync tools
        print("3️⃣ Testing sync tools...")
        self.test_sync_tool("get_server_info", {})
        self.test_sync_tool("get_example_workflows", {})

        # Test with valid data if files exist
        if self.test_files["sample_fasta"].exists():
            self.test_sync_tool("validate_fasta_sequences", {
                "fasta_path": str(self.test_files["sample_fasta"])
            })

        # Test config creation
        self.test_sync_tool("create_simple_protein_config", {
            "sequence": "MDPSSPPSDLLPTRGTPHTLEMLQHWR",
            "name": "test_protein",
            "output_dir": str(self.test_output_dir / "config_test")
        })

        # 4. Test job workflow
        print("4️⃣ Testing job management...")
        self.test_job_workflow()

        # 5. Test error handling
        print("5️⃣ Testing error handling...")
        self.test_error_handling()

        # 6. Test file operations
        print("6️⃣ Testing file operations...")
        self.test_file_operations()

        return self.generate_report()

    def generate_report(self) -> Dict:
        """Generate final test report"""
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"].values() if test["status"] == "passed")
        failed_tests = sum(1 for test in self.results["tests"].values() if test["status"] == "failed")
        error_tests = sum(1 for test in self.results["tests"].values() if test["status"] == "error")

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "pass_rate": f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "0%",
            "ready_for_production": failed_tests == 0 and error_tests == 0
        }

        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        print(f"Pass Rate: {self.results['summary']['pass_rate']}")
        print(f"Production Ready: {'✅ YES' if self.results['summary']['ready_for_production'] else '❌ NO'}")

        # Save detailed report
        report_path = self.project_root / "reports" / "integration_test_results.json"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"📝 Detailed report saved: {report_path}")

        return self.results

def main():
    """Main test runner entry point"""
    runner = MCPTestRunner()
    results = runner.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if results["summary"]["ready_for_production"] else 1)

if __name__ == "__main__":
    main()