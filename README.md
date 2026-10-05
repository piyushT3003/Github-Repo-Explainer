# Local GitHub Repository Code Explainer

## Objective

Build a local GenAI application that accepts a public GitHub repository URL and generates a simple-language explanation of the codebase.

## Required Flow

GitHub Repository
→ Repository Processing
→ Code Extraction
→ Local LLM
→ FastAPI Backend
→ Streamlit Frontend
→ Explanation

## Technology Stack

### Local GenAI
- Python
- Hugging Face Transformers
- One small open-source LLM
- Ollama local inference (default)
- Default local model: Qwen 2.5 3B

A Hugging Face Transformers local-inference adapter is also included and can
be enabled with:

```powershell
$env:LLM_PROVIDER="huggingface"
```

The optional Hugging Face adapter uses:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

and requires a local PyTorch installation.

### Backend
- FastAPI
- Pydantic
- Uvicorn

### Repository Processing
- GitPython
- Python
- Basic file handling

### Frontend
- Streamlit

## Repository Acquisition

GitPython is the primary repository-cloning implementation.

```python
git.Repo.clone_from(...)
```

If the machine does not have a usable system Git executable, the application
automatically falls back to the public GitHub repository archive endpoint so
the demo remains usable.

This means the required GitPython implementation is present while the final
application remains practical on machines where Git is not installed.

## UI

The application uses:

- Starry black background
- Glossy red accents
- Dark glassmorphism panels
- 3D hover motion
- Hover lift/glow
- Entrance reveal animation
- Button microinteractions
- Animated star-field/parallax-style motion
- Smooth analysis loader

Pages:

1. Home
2. Explain Repository
3. Repository Information
4. Code Structure
5. File Viewer
6. AI Explanation
7. Summary

These pages present the same project workflow; no unrelated product features
are included.

## Ports

- FastAPI: `http://127.0.0.1:8001`
- Streamlit: normally `http://localhost:8501`
- Ollama: `http://127.0.0.1:11434`

Port 8000 is intentionally unused.

## Setup

```powershell
.\setup.bat
```

Make sure the local model exists:

```powershell
ollama pull qwen2.5:3b
```

## Run

Terminal 1:

```powershell
.\run_backend.bat
```

Terminal 2:

```powershell
.\run_frontend.bat
```

Open:

```text
http://localhost:8501
```

## Test

Example public repository:

```text
https://github.com/octocat/Hello-World
```

A normal source-code repository is recommended for demonstrating code
explanation.

## API

FastAPI documentation:

```text
http://127.0.0.1:8001/docs
```

Health:

```text
http://127.0.0.1:8001/health
```

## API Keys

No cloud LLM API key is required.

The LLM explanation is generated locally using Ollama by default.

## Important Notes

- Public GitHub repositories are supported.
- Binary files, dependency folders, caches and build folders are skipped.
- Large repositories are limited before local LLM inference.
- The explanation is generated dynamically and is not hard-coded.

## Streamlit Community Cloud

For deployment on Streamlit Community Cloud, use `streamlit_app.py` as the
entrypoint. Cloud mode starts the FastAPI service inside the same Streamlit
process and switches local inference to Hugging Face Transformers with
`Qwen/Qwen2.5-0.5B-Instruct`, because a cloud worker cannot reach Ollama on a
personal computer.

See `DEPLOY_STREAMLIT.md` for the deployment steps.

## Deploying on Streamlit Community Cloud

Use `streamlit_app.py` as the Community Cloud entrypoint. The entrypoint starts the FastAPI backend on loopback within the same cloud worker and selects the Hugging Face Transformers provider with `Qwen/Qwen2.5-0.5B-Instruct` for cloud-local inference. The regular local run still uses Ollama + Qwen 2.5 3B.

Required deployment files:

- `streamlit_app.py`
- `requirements.txt`
- `packages.txt`
- `.streamlit/config.toml`
- `backend/`
- `frontend/`

No secrets are required for the default cloud mode.
