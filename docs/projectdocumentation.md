
```md
# Project Documentation: Multi-Agent Content Generation System

## Problem Statement
Build a modular agentic automation system that takes the provided product dataset as the only input and generates structured JSON pages (FAQ, Product Description, Comparison).

## Solution Overview
I implemented an agent orchestration pipeline where each agent has a single responsibility and communicates via explicit artifacts. Content is produced deterministically using reusable logic blocks and a small template engine, ensuring no external facts are introduced.

## Scopes & Assumptions
- Scope: generate 3 pages as machine-readable JSON; no external facts.
- Assumption: input structure matches the dataset keys.
- Product B is fictional and explicitly labeled.

## System Design (Most Important)

### Agents and Responsibilities
1. ParseNormalizeAgent  
   Input: raw_product_input → Output: product_model  
   Normalizes/validates input and enforces allowed-field guardrails.

2. QuestionBankAgent  
   Input: product_model → Output: question_bank  
   Generates >=15 categorized user questions deterministically.

3. FAQComposerAgent  
   Input: product_model + question_bank → Output: faq_content  
   Selects 5 questions and answers strictly using product_model fields.

4. FAQPageAgent  
   Input: product_model + faq_content → Output: faq_page_json  
   Renders FAQ page JSON using template engine.

5. ProductPageAgent  
   Input: product_model → Output: product_page_json  
   Renders product page JSON using template engine + reusable blocks.

6. ComparisonAgent  
   Input: product_model → Outputs: product_b_model + comparison_page_json  
   Creates a fictional Product B structure and renders comparison JSON via template engine.

7. WriterAgent  
   Inputs: faq_page_json + product_page_json + comparison_page_json → Output: written_files  
   Writes JSON pages to disk.

### Orchestration Flow
The orchestrator executes agents when their required input artifacts exist (dependency-driven pipeline):

raw_product_input
→ ParseNormalizeAgent → product_model
→ QuestionBankAgent → question_bank
→ FAQComposerAgent → faq_content
→ FAQPageAgent → faq_page_json
product_model → ProductPageAgent → product_page_json
product_model → ComparisonAgent → (product_b_model, comparison_page_json)
→ WriterAgent writes out/*.json

### Reusable Logic Blocks
Reusable deterministic blocks include:
- summary_block, ingredients_block, benefits_block, usage_block, safety_block
- comparison_analysis (built from compare_price + compare_overlap)
- format_price_inr

### Template Engine
Templates are structured definitions of fields and their dependencies:
- faq_template
- product_page_template
- comparison_template

The TemplateEngine renders templates deterministically and validates dependencies.

### Machine-Readable Output
Final outputs are JSON files:
- out/faq.json
- out/product_page.json
- out/comparison_page.json
