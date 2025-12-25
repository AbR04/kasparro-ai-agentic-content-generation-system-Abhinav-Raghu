# Project Documentation: Multi-Agent Content Generation System

**Candidate:** Abhinav Raghu
**Repository:** kasparro-ai-agentic-content-generation-system-Abhinav-Raghu  
**Execution Command:** `python -m src.main`

---

## Problem Statement
Design and implement a modular agentic automation system that takes a constrained product dataset (the only allowed input) and automatically generates structured, machine-readable content pages.

The system must:
- parse and normalize product data into a clean internal model
- generate at least 15 categorized user questions
- define and use a template mechanism for page generation
- implement reusable content logic blocks
- assemble three pages:
  - FAQ Page (minimum 5 Q&As)
  - Product Description Page
  - Comparison Page (GlowBoost vs fictional Product B)
- output each page as clean JSON
- run the entire pipeline through multiple agents and an orchestration flow (not a single monolithic script)

The assignment evaluates engineering design, modularity, and orchestration clarity rather than domain expertise or copywriting quality.

---

## Solution Overview
This solution implements a deterministic, modular multi-agent pipeline. Each agent has a single responsibility, consumes named input artifacts, and produces named output artifacts. An orchestrator (`GraphRunner`) executes agents based on dependency readiness: an agent runs only when all its required input artifacts exist in a shared `Store`.

To strictly comply with the “no new facts” constraint, the system avoids LLM-based generation. All content is produced deterministically from the provided dataset using reusable logic blocks and a lightweight custom template engine.

Final outputs are machine-readable JSON files written to disk:
- `out/faq.json`
- `out/product_page.json`
- `out/comparison_page.json`

---

## Scopes & Assumptions

### Scope
**Included:**
- deterministic parsing and normalization of the provided input dataset
- generation of a categorized question bank (≥ 15 questions)
- reusable content logic blocks for summary, ingredients, benefits, usage, safety, and comparison analysis
- a custom template engine with explicit field rules and dependencies
- three JSON page outputs (FAQ, Product, Comparison)
- an orchestration flow that demonstrates agent boundaries and message passing

**Not included (intentionally out of scope):**
- UI or website rendering
- external data enrichment or research
- databases or persistent storage beyond JSON file outputs
- concurrency, distributed execution, or queue-based orchestration
- multilingual generation or advanced natural language generation variations

### Assumptions
- The input dataset strictly follows the structure defined in `src/data.py`.
- “Agentic” refers to modular autonomous components coordinated by an orchestrator and communicating via artifacts, not necessarily LLM-based agents.
- Product B is fictional, structured, and explicitly marked as fictional.
- The system must not introduce new factual claims beyond the provided dataset.

---

## System Design (Mandatory — Most Important)

### High-Level Architecture
The system is organized into four conceptual layers:

#### 1. Input Layer
- Provides the only allowed dataset (`src/data.py`) as a structured Python dictionary.
- This data is injected into the pipeline as the initial artifact (`raw_product_input`).

#### 2. Orchestration Layer
- Implemented in `src/orchestrator.py`.

**Core components:**
- **Artifact:** a named message carrying structured data and provenance metadata.
- **Store:** an orchestrator-owned repository of artifacts.
- **AgentSpec:** explicitly defines each agent’s name, required inputs, and produced outputs.
- **GraphRunner:** executes agents when all required input artifacts are available, forming a dependency-driven (DAG-like) pipeline.

Agents do not call each other directly; all coordination is handled by the orchestrator.

#### 3. Content Engineering Layer
- **Reusable logic blocks (`src/logic.py`):**
  - summary generation
  - ingredient listing
  - benefit listing
  - usage instructions
  - safety information
  - deterministic comparison analysis (price and overlap)

All logic blocks are pure functions with no side effects and derive output strictly from input data.

- **Template engine and templates (`src/templates.py`):**
  - a template is a list of `FieldRule`s
  - each `FieldRule` defines a field name, a builder function, and explicit dependencies
  - the engine validates dependencies and renders fields deterministically into JSON

#### 4. Agents Layer
- Implemented in `src/agents.py`.
- Each agent has a single responsibility and explicit artifact inputs/outputs.
- Given the same input dataset, the pipeline always produces the same outputs.

---

### Design Goals and How They Are Met

#### 1) Clear Agent Boundaries
Each agent:
- performs a single well-defined task
- declares inputs and outputs via `AgentSpec`
- communicates only through artifacts
- does not call other agents directly
- does not rely on hidden global state

#### 2) Automation Flow / Orchestration Graph
Instead of a monolithic script, the system uses:
- a `Store` to hold intermediate artifacts
- a `GraphRunner` that executes agents only when dependencies are satisfied

This results in a dependency-driven, DAG-style execution flow.

#### 3) Reusable Logic Blocks
Logic blocks are pure, deterministic functions and can be reused across templates and future pages.

Examples:
- `summary_block(product)`
- `ingredients_block(product)`
- `comparison_analysis(product_a, product_b)`

#### 4) Template Engine of Own Design
The template engine is explicit and deterministic:
- a **Template** consists of multiple `FieldRule`s
- each `FieldRule` specifies:
  - output field name
  - builder function (`context → value`)
  - declared dependencies
- dependencies are validated before rendering

This demonstrates structured template-based generation beyond simple string formatting.

#### 5) Machine-Readable Output
All final pages are produced as structured JSON objects and written to disk by a dedicated `WriterAgent`, ensuring downstream automation compatibility.

---

### Core Data Model and Constraints

#### Input Dataset (Only Allowed Facts)
The system accepts only these keys:
- `product_name`
- `concentration`
- `skin_type`
- `key_ingredients`
- `benefits`
- `how_to_use`
- `side_effects`
- `price_inr`

#### Guardrails: No New Facts
During parsing and normalization, a guardrail check ensures that only the permitted fields are present in the internal product model. This prevents accidental enrichment or leakage of non-permitted data.

---

### Agents and Artifacts

#### Agent 1: ParseNormalizeAgent
- **Inputs:** `raw_product_input`
- **Outputs:** `product_model`
- **Responsibility:** validate allowed keys and normalize data types

#### Agent 2: QuestionBankAgent
- **Inputs:** `product_model`
- **Outputs:** `question_bank`
- **Responsibility:** generate ≥ 15 categorized questions deterministically

#### Agent 3: FAQComposerAgent
- **Inputs:** `product_model`, `question_bank`
- **Outputs:** `faq_content`
- **Responsibility:** select ≥ 5 questions and answer strictly from product data

#### Agent 4: FAQPageAgent
- **Inputs:** `product_model`, `faq_content`
- **Outputs:** `faq_page_json`
- **Responsibility:** render FAQ page using the template engine

#### Agent 5: ProductPageAgent
- **Inputs:** `product_model`
- **Outputs:** `product_page_json`
- **Responsibility:** render product page using reusable logic blocks

#### Agent 6: ComparisonAgent
- **Inputs:** `product_model`
- **Outputs:** `product_b_model`, `comparison_page_json`
- **Responsibility:** create a fictional Product B and render a deterministic comparison page

#### Agent 7: WriterAgent
- **Inputs:** all page JSON artifacts
- **Outputs:** `written_files`
- **Responsibility:** write JSON outputs to disk

---

### Orchestration Flow
Execution proceeds based on artifact availability:

1. `raw_product_input`
2. ParseNormalizeAgent → `product_model`
3. QuestionBankAgent → `question_bank`
4. FAQComposerAgent → `faq_content`
5. FAQPageAgent → `faq_page_json`
6. ProductPageAgent → `product_page_json`
7. ComparisonAgent → `product_b_model`, `comparison_page_json`
8. WriterAgent → writes JSON files

Downstream agents never execute until all required inputs exist, ensuring correctness of flow.

---

## Optional: Diagram / Flowchart

```mermaid
flowchart TD
  A["raw_product_input"] --> B["ParseNormalizeAgent"]
  B --> C["QuestionBankAgent"]
  C --> D["FAQComposerAgent"]
  D --> E["FAQPageAgent"]
  B --> F["ProductPageAgent"]
  B --> G["ComparisonAgent"]
  E --> H["WriterAgent"]
  F --> H
  G --> H
