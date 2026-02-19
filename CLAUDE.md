# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AlphaFold3 MCP is a Model Context Protocol server that exposes AlphaFold3 protein structure prediction as tools for AI assistants. It wraps the AlphaFold3 codebase (cloned at `repo/alphafold3/`) and provides 5 MCP tools across two tool families.

## Common Commands

```bash
# Run the MCP server
./env/bin/python src/server.py

# Run tests
./env/bin/python src/tests/test_simple.py
./env/bin/python src/tests/test_server.py

# Environment setup (creates conda env at ./env)
bash quick_setup.sh

# Docker build and run
docker build -t alphafold3-mcp .
docker run --gpus all \
  -v /path/to/model:/app/repo/alphafold3/model \
  -v /path/to/alphafold3_db:/app/repo/alphafold3/alphafold3_db \
  alphafold3-mcp
```

## Architecture

**Server composition pattern**: `src/server.py` creates a root `FastMCP(name="alphafold3")` and mounts two sub-MCPs:
- `af3_predict_mcp` from `src/tools/af3_predict_structure.py` — 3 tools for structure prediction
- `af3_variants_mcp` from `src/tools/af3_prepare_variants.py` — 2 tools for variant preparation

**Tool execution model**: Tools shell out to AlphaFold3 runner scripts (`run_alphafold.py`, `run_alphafold_with_a3m.py`, `run_alphafold_with_a3m_batch.py`) via `subprocess.Popen`. Real-time log streaming is handled by `_log_stream()` on a background thread.

**Path resolution**: `_get_af3_path()` resolves the AF3 repo as `Path(__file__).parent.parent.parent / "repo" / "alphafold3"` — two levels up from the tool files. In Docker, this maps to `/app/repo/alphafold3/`. Model weights and databases are expected at `repo/alphafold3/model/` and `repo/alphafold3/alphafold3_db/`.

**Job management**: `src/jobs/manager.py` provides a `JobManager` class with UUID-based job tracking, background threading, and persistent state in `jobs/{job_id}/metadata.json`. A global `job_manager` singleton is exported.

**Dual interface**: Standalone scripts in `scripts/clean/` mirror MCP tool functionality for direct CLI use, sharing utilities from `scripts/lib/`.

## Prediction Modes

- **default**: Full MSA search + template search + inference (calls `run_alphafold.py`)
- **a3m**: Pre-computed A3M MSA + optional template search (calls `run_alphafold_with_a3m.py`)
- **msa**: Inference only with embedded MSA/templates (fastest, for variant batches)

## Key Environment Variables

```bash
CUDA_VISIBLE_DEVICES=0              # GPU selection
XLA_FLAGS="--xla_gpu_enable_triton_gemm=false"  # Required for stable XLA compilation
XLA_PYTHON_CLIENT_PREALLOCATE=true  # Memory pre-allocation
XLA_CLIENT_MEM_FRACTION=0.95        # GPU memory fraction
```

## Docker Setup

Multi-stage build using `nvidia/cuda:12.6.0-base-ubuntu22.04`. Builder stage installs Python 3.11 (deadsnakes PPA), compiles HMMER 3.4 from source, installs pip deps, and clones+builds `github.com/charlesxu90/alphafold3`. Runtime stage copies the venv, HMMER binaries, and repo. Model weights and databases must be mounted as volumes at runtime.

GitHub Actions (`.github/workflows/docker.yml`) builds and pushes to `ghcr.io` on pushes to main or version tags.

## Dependencies

Core stack: JAX 0.4.35 + CUDA 12.6, dm-haiku 0.0.13, RDKit 2024.3.5, NumPy 2.1.3. MCP framework: fastmcp + loguru. System: HMMER 3.4, Python 3.11. All pinned in `requirements.txt`; conda environment spec in `environment.yml`.

## Gitignored Directories

`repo/`, `env/`, `jobs/`, `output/`, `test_output/`, `examples/`, `reports/`, `tests/`, `tmp/` are all gitignored. The Docker build clones `repo/` fresh. Config files in `configs/` are tracked.
