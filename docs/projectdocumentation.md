# Project Documentation  
## Multi-Agent Content Generation System (Agentic, Event-Driven)

---

## 1. Problem Statement

Design and implement a modular, agentic automation system that consumes a constrained product dataset (the only allowed input) and automatically generates structured, machine-readable content pages.

The system must:
- Parse and normalize the input dataset into a clean internal representation
- Generate categorized user questions automatically
- Use reusable content logic blocks
- Apply a template-driven page generation mechanism
- Produce three structured JSON pages:
  - FAQ Page
  - Product Description Page
  - Comparison Page (against a fictional Product B)
- Run entirely through a multi-agent orchestration mechanism rather than a static or sequential script

The focus of this assignment is system design, agent autonomy, and orchestration quality — not copywriting or domain expertise.

---

## 2. Solution Overview

This solution implements a **true agentic, event-driven architecture** where independent agents coordinate through message passing and shared state, rather than direct calls or hard-coded execution order.

A central MessageBus acts as the orchestrator:
- Routing messages to subscribed agents
- Managing a shared ArtifactStore
- Driving execution via an event loop

A Planner agent dynamically creates runtime Tasks based on a high-level goal. Worker agents independently decide whether they can execute a task based on available artifacts. If prerequisites are missing, agents block and emit NeedArtifact signals.

A dedicated Coordinator agent listens for these signals and requeues blocked tasks when required artifacts are created, enabling dynamic coordination, retry, and order-independent execution.

---

## 3. Scope & Assumptions

### In Scope
- Deterministic processing of the provided dataset
- Modular, independent agents with clear responsibilities
- Message-driven orchestration and dynamic coordination
- Reusable content logic blocks
- Template-based JSON page generation
- Order-independent task execution with retry/resume behavior

### Out of Scope
- External data enrichment or APIs
- UI or frontend rendering
- Persistent databases (beyond JSON output)
- LLM-based content generation
- Distributed or concurrent execution

### Assumptions
- The input dataset follows the structure defined in `PRODUCT_INPUT`
- “Agentic” implies autonomous components coordinated via events and shared artifacts, not necessarily LLM agents
- Fictional Product B must be clearly marked as fictional and rule-based

---

## 4. System Design (Most Important)

### 4.1 High-Level Architecture

The system consists of four layers:

1. **Input Layer**
   - Provides the constrained product dataset as an initial artifact

2. **Orchestration Layer**
   - MessageBus (event loop)
   - ArtifactStore (shared state)
   - Message types: Start, Task, NeedArtifact, ArtifactCreated, Done

3. **Agents Layer**
   - PlannerAgent (goal → tasks)
   - Worker agents (Parser, Question, FAQ, Pages, Writer)
   - TaskCoordinatorAgent (dynamic retry/resume)

4. **Content Engineering Layer**
   - Reusable logic blocks
   - Template engine and page templates

---

### 4.2 Message-Driven Orchestration

Agents do not call each other directly.  
All coordination occurs via messages routed by the MessageBus.

Key principles:
- Agents subscribe to message types
- Messages are queued and processed sequentially by the event loop
- Execution order emerges dynamically based on state and events

---

### 4.3 Agent Responsibilities

#### PlannerAgent
- Reacts to Start(goal)
- Dynamically creates Task messages at runtime
- Tasks describe *what* needs to be done, not *how* or *when*
- Task order is intentionally randomized to prove order independence

#### Worker Agents
Each worker agent:
- Subscribes to Task messages
- Checks whether the task is relevant
- Verifies required artifacts
- Executes if ready
- Emits NeedArtifact if dependencies are missing

#### TaskCoordinatorAgent
- Listens to NeedArtifact messages
- Stores blocked tasks keyed by missing artifacts
- Listens to ArtifactCreated events
- Requeues blocked tasks when dependencies become available
- Enables retry, resume, and dynamic coordination

#### WriterAgent
- Writes final JSON pages to disk
- Emits a Done signal to terminate the system

---

### 4.4 Artifact-Based Coordination

Artifacts represent shared state:
- product_model
- question_bank
- faq_content
- faq_page_json
- product_page_json
- comparison_page_json

Artifacts are immutable outputs produced by agents and stored centrally.  
Creation of an artifact automatically emits an ArtifactCreated event, enabling reactive behavior.

---

### 4.5 Reusable Logic Blocks

Pure, deterministic functions are used to:
- Extract ingredients
- Generate benefit summaries
- Format usage and safety sections
- Compare products (ingredients, benefits, price)

These blocks have no side effects and can be reused across templates and agents.

---

### 4.6 Template Engine

A lightweight custom template engine is implemented:
- Templates define structured fields
- Each field has:
  - A builder function
  - Explicit dependencies
- Rendering is deterministic and JSON-only

Templates exist for:
- FAQ Page
- Product Page
- Comparison Page

---

### 4.7 Execution Flow (Runtime)

1. Start(goal="build_pages") is published
2. PlannerAgent generates Tasks dynamically
3. Tasks are routed to worker agents
4. Agents execute or block based on artifact availability
5. Coordinator manages blocked tasks and retries
6. Pages are rendered once dependencies exist
7. WriterAgent outputs JSON files and ends the run

Execution order is **not predefined** and is resolved dynamically at runtime.

---

## 5. Extensibility

To add a new page or capability:
- Define new logic blocks
- Create a new template
- Add a new agent that reacts to a Task
- No changes to existing agents or orchestration logic are required

---

## 6. Summary

This system demonstrates a production-style, agentic architecture with:
- Autonomous agents
- Message-driven orchestration
- Dynamic coordination and retry
- Clear separation of responsibilities
- Structured, machine-readable outputs

The design prioritizes clarity, extensibility, and correctness over clever shortcuts.
