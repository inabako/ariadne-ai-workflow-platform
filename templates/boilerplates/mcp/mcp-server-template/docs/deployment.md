# Deployment

The template can be packaged and run as a standalone Python project.

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m local_model_mcp --health
```

Docker smoke start:

```bash
docker build -t local-model-mcp-template .
docker run --rm local-model-mcp-template
```

Compose smoke start:

```bash
docker compose up --build
```

The image does not include `.env`, evidence output, model weights, or workspace files. Mount runtime input and output directories explicitly.
