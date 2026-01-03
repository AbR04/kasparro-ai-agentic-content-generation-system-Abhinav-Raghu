# Kasparro – Agentic Content Generation System

This project implements a true multi-agent, event-driven system that converts a constrained product dataset into structured, machine-readable JSON content pages.

## Outputs
The system generates:
- `out/faq.json`
- `out/product_page.json`
- `out/comparison_page.json`

## Architecture Highlights
- Message-driven orchestration (event loop + message bus)
- Autonomous agents with clear responsibilities
- Dynamic task generation and coordination
- Dependency-aware blocking and retry via a coordinator agent
- Order-independent execution

## Setup & Run

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # if present
python -m src.main
