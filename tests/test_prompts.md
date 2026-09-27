# AlphaFold3 MCP Server Test Prompts

This file contains comprehensive test prompts for validating the AlphaFold3 MCP server integration with Claude Code.

## Tool Discovery Tests

### Prompt 1: List All Available Tools
**Test Prompt:**
```
What MCP tools do you have access to from alphafold3? Give me a brief description of each tool and categorize them by function.
```

**Expected Response:**
- Should list 13 tools total
- Categories: Job Management, Sync Tools, Submit Tools, Information Tools
- Each tool should have a clear description

### Prompt 2: Get Server Information
**Test Prompt:**
```
Use the get_server_info tool to show me details about the AlphaFold3 MCP server capabilities.
```

**Expected Response:**
- Server name: "alphafold3"
- Lists sync tools, submit tools, and job management tools
- Shows scripts and jobs directory paths

### Prompt 3: Get Example Workflows
**Test Prompt:**
```
Show me example workflows for common AlphaFold3 use cases using the get_example_workflows tool.
```

**Expected Response:**
- Simple protein prediction workflow
- Protein variants analysis workflow
- Batch processing workflow
- Data requirements for each workflow

---

## Sync Tool Tests (Fast Operations)

### Prompt 4: Validate FASTA File
**Test Prompt:**
```
Use the validate_fasta_sequences tool to check the sequences in examples/data/sample_protein.fasta
```

**Expected Response:**
- Status: success
- Valid sequence count
- Sequence details with name and length
- Preview of sequence content

### Prompt 5: Create Simple Protein Config
**Test Prompt:**
```
Use create_simple_protein_config to create a configuration for this protein sequence:
MDPSSPSFLNSGFGRHPSDSPGDVQPQVVVTTRFKPEDLWRSKCPLQLDLLTNSNVDRYAQRMVPTLGGQRIWQTIPYVPKNLSNPEWKTECFTCQHTDEPEQLIRSFLRFPPVFQRNQARYLFDCGMTRGIDFAGLGFQQLISNHLMRGLHKQWDDLLRVPCKEIKELASRLPLSVLQKRVEQRQLQRQVQQRFDQPQPVAHLLQRDPRAQPPGIRSPCLPPPLLPPLLPPPLLPPPRQSGDSRPAQWLPLPPLPPALPPPPPPPPPPPPPPPPGSGIRPPPPPPPPPPPPPPPPQQRGPPPQAPPPPPPPPPPPPPQQQQTQTQTQTQTQTQTQTQTQTQTQRAEEEDQEPAQQVGSQDQQAAQQQQQLGLVQPVHQRQRQRQRQRQRQRQRQRQRQRGIRAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAIAI

Name it "test_kinase" and save to directory "test_output"
```

**Expected Response:**
- Status: success
- Config path created
- Sequence length confirmation
- Output directory path

### Prompt 6: Error Handling Test - Invalid File
**Test Prompt:**
```
Try to use validate_fasta_sequences with a non-existent file: "/fake/nonexistent.fasta"
```

**Expected Response:**
- Status: error
- Clear error message about file not found
- Helpful guidance

### Prompt 7: Error Handling Test - Invalid Sequence
**Test Prompt:**
```
Try to create a simple protein config with an invalid sequence containing numbers and special characters:
Sequence: "MDPSS123XYZ@#$INVALID"
```

**Expected Response:**
- Status: error
- Clear error message about invalid amino acids
- Validation feedback

---

## Submit API Tests (Long-Running Tasks)

### Prompt 8: Submit Simple Structure Prediction
**Test Prompt:**
```
First create a simple protein config using create_simple_protein_config with sequence "MDPSSPPSDLLPTRGTPHTLEMLQHWRTKTNLLQMTVHPFLSNGGQFHTVHRYDPTGEPVRFQPMLHRLPPQNPCLNPTSRYDLKQYLLKRRLSQEGGGGGGGGGGGGGASGSGSGSGSGSAGSRSDCDQSQRHRELAEFVEHIRPPNKPSLVPTNQTQTPAKGDLSLSFSTNGLSHPFSFAEDSLGMNPPFAPRGGPGSQRLLDPITDLGGLGQRGLAQGSSAVIASGIKGTPPPASSPGRRAARGAPGGSPRPSGSCSGNRMNPMRNSASPASPSPPQPSQPRTPARSFSQRPRPPPPPRPRPRPRPRPPRRRSRSRSRSRSRSRCSQMPGDMTTGQTPKGGSSSSSSSSSQSTTNQRRVGPPRPPQVQTQAPTSGSSSTRASSSSSSSSSSSTTNNQIPQSRQTSNNQNSQRSAQRSNQRQMPNTQSSPAPPSGRPASSFPSSTRRSSQRTSSRVRDRSISAKSSDSESSDSDSPSEDPDDDGFGGWAKPGKQFNVPDFDLRGLEEAFIAQFPLQEEAFLLASLYYDCRLNGQDNQNQNQ", name "membrane_protein", and output_dir "membrane_test".

Then submit this for structure prediction using submit_structure_prediction.
```

**Expected Response:**
- First: successful config creation
- Then: job submission with job_id
- Instructions to check status with get_job_status(job_id)
- Instructions to get results with get_job_result(job_id)

### Prompt 9: Check Job Status
**Test Prompt:**
```
Check the status of job [job_id from previous step] using get_job_status
```

**Expected Response:**
- Job ID confirmation
- Current status (pending/running/completed/failed)
- Timestamp information
- Progress indicators if available

### Prompt 10: Get Job Logs
**Test Prompt:**
```
Show me the last 20 lines of logs for job [job_id] using get_job_log
```

**Expected Response:**
- Recent log entries
- Execution progress
- Any error messages or warnings

### Prompt 11: List All Jobs
**Test Prompt:**
```
Use list_jobs to show me all submitted jobs with status 'running'
```

**Expected Response:**
- List of jobs filtered by status
- Job IDs, names, and timestamps
- Current status for each job

### Prompt 12: Cancel Job (if needed)
**Test Prompt:**
```
If there's a long-running job, cancel it using cancel_job with the job ID
```

**Expected Response:**
- Confirmation of cancellation attempt
- Success or error message
- Updated job status

---

## Batch Processing Tests

### Prompt 13: Prepare Variants
**Test Prompt:**
```
Use prepare_variants to prepare variant configurations:
- variants_fasta: "examples/data/protein_variants.fasta"
- wt_data_json: "examples/1iep_a3m_fix/1iep_a3m_fix_data.json"
- output_dir: "test_variants"
```

**Expected Response:**
- Status: success
- Number of variants created
- Number of variants skipped
- List of variant directories

### Prompt 14: Submit Batch Variants
**Test Prompt:**
```
Submit batch variant processing for the variants prepared in the previous step using submit_batch_variants with input_dir "test_variants"
```

**Expected Response:**
- Job submission confirmation
- Batch job ID
- Instructions for monitoring progress

---

## End-to-End Workflow Tests

### Prompt 15: Complete Variant Analysis Workflow
**Test Prompt:**
```
I want to analyze protein variants end-to-end. Please:

1. First validate the sequences in examples/data/protein_variants.fasta
2. If valid, prepare variant configurations using examples/1iep_a3m_fix/1iep_a3m_fix_data.json as wild-type reference
3. Then submit the complete workflow using submit_prepare_and_predict_variants
4. Show me how to monitor the progress
```

**Expected Response:**
- Step-by-step execution
- Validation results first
- Configuration preparation
- End-to-end job submission
- Progress monitoring instructions

### Prompt 16: Error Recovery Scenario
**Test Prompt:**
```
Submit a structure prediction job that might fail by using a malformed input. Then show me:
1. How to detect the failure
2. How to view the error logs
3. What the error messages suggest for fixing the issue
```

**Expected Response:**
- Job submission
- Status checking showing failure
- Error log retrieval
- Diagnostic information and suggested fixes

### Prompt 17: Performance Comparison
**Test Prompt:**
```
Compare the execution time and approach between:
1. Using create_simple_protein_config + submit_structure_prediction (two steps)
2. Using submit_prepare_and_predict_variants for end-to-end processing

Which approach is better for different scenarios?
```

**Expected Response:**
- Timing analysis
- Use case recommendations
- Pros and cons of each approach
- Guidance on when to use which method

---

## Integration Validation Tests

### Prompt 18: Path Resolution Test
**Test Prompt:**
```
Test both absolute and relative paths:
1. Use validate_fasta_sequences with absolute path: "/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/alphafold3_mcp/examples/data/sample_protein.fasta"
2. Use the same tool with relative path: "examples/data/sample_protein.fasta"
3. Compare the results
```

**Expected Response:**
- Both paths should work correctly
- Same validation results
- No path resolution errors

### Prompt 19: Concurrent Job Management
**Test Prompt:**
```
1. Submit 2 different structure prediction jobs
2. List all jobs to see both running
3. Check status of each job individually
4. Cancel one job while keeping the other running
5. Verify the status changes correctly
```

**Expected Response:**
- Multiple job submission success
- Correct job listing
- Individual status tracking
- Successful cancellation of one job
- Proper status updates

### Prompt 20: Resource Cleanup Test
**Test Prompt:**
```
After running several test jobs:
1. List all completed and failed jobs
2. Check if job directories and logs are properly maintained
3. Verify that cancelled jobs are cleaned up appropriately
```

**Expected Response:**
- Complete job history
- Proper file organization
- Clean job state management
- No resource leaks

---

## Success Criteria Checklist

For each test, verify:
- ✅ Tool executes without Python errors
- ✅ Returns properly structured JSON responses
- ✅ Error handling provides helpful messages
- ✅ File paths resolve correctly (both absolute and relative)
- ✅ Job management workflow completes properly
- ✅ Status updates occur in real-time
- ✅ Logs are accessible and informative
- ✅ Resource cleanup happens appropriately

## Performance Benchmarks

Expected performance targets:
- Sync tools: Complete within 10 seconds
- Job submission: Complete within 5 seconds
- Status checks: Complete within 2 seconds
- Log retrieval: Complete within 3 seconds
- Tool discovery: Complete within 1 second

## Known Issues to Watch For

1. **Path Resolution**: Ensure relative paths work from any working directory
2. **Long Job Names**: Very long job names might cause filesystem issues
3. **Concurrent Access**: Multiple rapid job submissions should queue properly
4. **Error Propagation**: Python exceptions should convert to helpful error messages
5. **Resource Limits**: Large FASTA files might hit memory limits

## Troubleshooting Guide

If tests fail:

1. **Server Connection Issues**
   ```bash
   claude mcp list  # Check server status
   ```

2. **Python Import Errors**
   ```bash
   python -c "from src.server import mcp"  # Test imports
   ```

3. **File Not Found Errors**
   ```bash
   ls -la examples/data/  # Verify test files exist
   ```

4. **Job Directory Issues**
   ```bash
   ls -la jobs/  # Check job directory structure
   ```

5. **Environment Issues**
   ```bash
   which python  # Verify correct Python environment
   pip show fastmcp  # Verify fastmcp installation
   ```