from __future__ import annotations
import json

from src.data import PRODUCT_INPUT
from src.orchestrator import Artifact, GraphRunner, Store
from src.agents import (
    ParseNormalizeAgent,
    QuestionBankAgent,
    FAQComposerAgent,
    FAQPageAgent,
    ProductPageAgent,
    ComparisonAgent,
    WriterAgent,
)


def main() -> None:
    store = Store()

    # Seed the pipeline with the only allowed input.
    store.put(Artifact("raw_product_input", PRODUCT_INPUT, {"source": "src/data.py"}))

    agents = [
        ParseNormalizeAgent(),
        QuestionBankAgent(),
        FAQComposerAgent(),
        FAQPageAgent(),
        ProductPageAgent(),
        ComparisonAgent(),
        WriterAgent(),
    ]

    runner = GraphRunner(agents)
    runner.run(store)

    print("✅ Pipeline complete.")
    print("Graph:", json.dumps(runner.describe(), indent=2))
    print("Outputs:", store.require("written_files").payload)


if __name__ == "__main__":
    main()
