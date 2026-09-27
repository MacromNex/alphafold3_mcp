#!/usr/bin/env python3
"""Simple test script for AlphaFold3 MCP functionality."""

import sys
import tempfile
import json
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(src_dir.parent / "scripts"))

def test_create_simple_config():
    """Test creating a simple protein config directly."""
    try:
        # Create config directly (similar to what the MCP tool does)
        sequence = "MDPSSPNYDKWEMERT"
        name = "test_protein"

        # Validate sequence
        valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
        if not all(aa.upper() in valid_aa for aa in sequence):
            return False

        # Create config
        config = {
            "name": name,
            "sequences": [
                {
                    "protein": {
                        "id": ["A"],
                        "sequence": sequence
                    }
                }
            ],
            "modelSeeds": [1],
            "dialect": "alphafold3",
            "version": 1
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "input.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            if config_path.exists():
                print("✅ Simple protein config creation passed")
                print(f"   Config created: {config_path.name}")
                print(f"   Sequence length: {len(sequence)}")
                return True

        return False
    except Exception as e:
        print(f"❌ Simple protein config creation failed: {e}")
        return False

def test_job_manager():
    """Test job manager functionality."""
    try:
        from jobs.manager import job_manager

        # Test job listing
        jobs = job_manager.list_jobs()

        if jobs.get("status") == "success":
            print(f"✅ Job manager test passed")
            print(f"   Current jobs: {jobs['total']}")
            print(f"   Jobs directory: {job_manager.jobs_dir}")
            return True
        else:
            print(f"❌ Job manager failed: {jobs}")
            return False
    except Exception as e:
        print(f"❌ Job manager test failed: {e}")
        return False

def test_prepare_variants_import():
    """Test that prepare_variants module can be imported."""
    try:
        import prepare_variants

        # Test parse_fasta function
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(">test_protein_1\n")
            f.write("MDPSSPNYDKWEMERT\n")
            f.write(">test_protein_2\n")
            f.write("ACDEFGHIKLMNPQRSTVWY\n")
            fasta_path = f.name

        try:
            variants = prepare_variants.parse_fasta(fasta_path)

            if len(variants) == 2:
                print(f"✅ Prepare variants import test passed")
                print(f"   Parsed {len(variants)} sequences")
                print(f"   First variant: {variants[0].name} ({len(variants[0].sequence)} aa)")
                return True
            else:
                print(f"❌ Expected 2 variants, got {len(variants)}")
                return False
        finally:
            Path(fasta_path).unlink()  # Clean up temp file

    except Exception as e:
        print(f"❌ Prepare variants import test failed: {e}")
        return False

def test_alphafold_runner_import():
    """Test that alphafold3_runner module can be imported."""
    try:
        import alphafold3_runner

        # Test that main functions exist
        required_functions = ['run_default', 'run_with_a3m', 'run_with_msa', 'run_batch']

        for func_name in required_functions:
            if not hasattr(alphafold3_runner, func_name):
                print(f"❌ Missing function: {func_name}")
                return False

        print(f"✅ AlphaFold3 runner import test passed")
        print(f"   All required functions found: {required_functions}")
        return True

    except Exception as e:
        print(f"❌ AlphaFold3 runner import test failed: {e}")
        return False

def test_mcp_server_import():
    """Test that MCP server can be imported without errors."""
    try:
        # Import server module (this will create the mcp instance)
        import server

        # Check that server has the mcp instance
        if hasattr(server, 'mcp'):
            print(f"✅ MCP server import test passed")
            print(f"   Server name: {server.mcp.name}")
            return True
        else:
            print(f"❌ No mcp instance found in server module")
            return False

    except Exception as e:
        print(f"❌ MCP server import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Testing AlphaFold3 MCP Components")
    print("=" * 40)

    tests = [
        test_job_manager,
        test_create_simple_config,
        test_prepare_variants_import,
        test_alphafold_runner_import,
        test_mcp_server_import,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
        print()

    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)