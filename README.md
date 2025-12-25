# Kasparro – Multi-Agent Content Generation System (Deterministic)

This repository contains a deterministic, agentic content generation system built as part of the Kasparro Applied AI Engineer assignment.

The system converts the provided product dataset into three structured, machine-readable JSON pages using a modular agent pipeline and dependency-driven orchestration.

## Outputs
The pipeline generates the following files:
- `out/faq.json`
- `out/product_page.json`
- `out/comparison_page.json`

## Design Summary
- Each agent has a single responsibility and communicates via explicit artifacts.
- An orchestrator executes agents based on input availability (DAG-style flow).
- Reusable logic blocks and a custom template engine generate structured JSON output.
- No external data or LLM-based generation is used, ensuring compliance with the “no new facts” constraint.

## Run Instructions
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m src.main
