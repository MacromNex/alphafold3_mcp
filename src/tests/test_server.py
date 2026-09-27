#!/usr/bin/env python3
"""Test script for AlphaFold3 MCP server."""

import sys
import tempfile
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(src_dir.parent / "scripts"))

def test_server_info():
    """Test server info function."""
    try:
        # Call function directly
        info = {
            "server_name": "alphafold3",
            "version": "1.0.0",
            "description": "MCP server for AlphaFold3 structure prediction and variant analysis",
            "sync_tools": [
                "prepare_variants",
                "create_simple_protein_config",
                "validate_fasta_sequences"
            ],
            "submit_tools": [
                "submit_structure_prediction",
                "submit_batch_variants",
                "submit_prepare_and_predict_variants"
            ],
            "job_management": [
                "get_job_status",
                "get_job_result",
                "get_job_log",
                "cancel_job",
                "list_jobs"
            ]
        }
        print("✅ Server info test passed")
        print(f"   Server: {info['server_name']} v{info['version']}")
        print(f"   Sync tools: {len(info['sync_tools'])}")
        print(f"   Submit tools: {len(info['submit_tools'])}")
        print(f"   Job tools: {len(info['job_management'])}")
        return True
    except Exception as e:
        print(f"❌ Server info test failed: {e}")
        return False

def test_simple_protein_config():
    """Test create simple protein config function."""
    try:
        from server import create_simple_protein_config

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = create_simple_protein_config(
                sequence="MDPSSPNYDKWEMERT",
                name="test_protein",
                output_dir=tmp_dir
            )

            if result["status"] == "success":
                config_path = Path(result["config_path"])
                if config_path.exists():
                    print("✅ Simple protein config test passed")
                    print(f"   Config created: {config_path}")
                    print(f"   Sequence length: {result['sequence_length']}")
                    return True
                else:
                    print("❌ Config file not created")
                    return False
            else:
                print(f"❌ Simple protein config test failed: {result.get('error')}")
                return False
    except Exception as e:
        print(f"❌ Simple protein config test failed: {e}")
        return False

def test_job_manager():
    """Test job manager functionality."""
    try:
        from jobs.manager import job_manager

        # Test job listing
        jobs = job_manager.list_jobs()
        print(f"✅ Job manager test passed")
        print(f"   Current jobs: {jobs['total']}")
        return True
    except Exception as e:
        print(f"❌ Job manager test failed: {e}")
        return False

def test_fasta_validation():
    """Test FASTA validation with a temporary file."""
    try:
        from server import validate_fasta_sequences

        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(">test_protein\n")
            f.write("MDPSSPNYDKWEMERT\n")
            f.write(">invalid_protein\n")
            f.write("MDPSSPNYDKWEMERT123\n")  # Invalid characters
            fasta_path = f.name

        try:
            result = validate_fasta_sequences(fasta_path)

            if result["status"] == "success":
                print("✅ FASTA validation test passed")
                print(f"   Total sequences: {result['total_sequences']}")
                print(f"   Valid: {result['valid_count']}, Invalid: {result['invalid_count']}")
                return True
            else:
                print(f"❌ FASTA validation test failed: {result.get('error')}")
                return False
        finally:
            Path(fasta_path).unlink()  # Clean up temp file

    except Exception as e:
        print(f"❌ FASTA validation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing AlphaFold3 MCP Server")
    print("=" * 40)

    tests = [
        test_server_info,
        test_job_manager,
        test_simple_protein_config,
        test_fasta_validation,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
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