from __future__ import annotations
from typing import List

from src.agents.base import BaseAgent
from src.messages import Message, Start, Task

class PlannerAgent(BaseAgent):
    name = "planner_agent"

    def handle(self, msg: Message, store, bus) -> List[Message]:
        # Planner reacts only to Start
        if msg.type != "Start":
            return []

        start = msg  # type: ignore
        if not isinstance(start, Start) or start.goal != "build_pages":
            return []

        # IMPORTANT:
        # Planner creates tasks dynamically at runtime.
        tasks: List[Message] = [
            Task(
                name="ParseProduct",
                requires=["raw_product_input"],
                produces=["product_model"],
            ),
            Task(
                name="GenerateQuestions",
                requires=["product_model"],
                produces=["question_bank"],
            ),
            Task(
                name="ComposeFAQ",
                requires=["product_model", "question_bank"],
                produces=["faq_content"],
            ),
            Task(
                name="RenderFAQPage",
                requires=["product_model", "faq_content"],
                produces=["faq_page_json"],
            ),
            Task(
                name="RenderProductPage",
                requires=["product_model"],
                produces=["product_page_json"],
            ),
            Task(
                name="BuildComparison",
                requires=["product_model"],
                produces=["product_b_model", "comparison_page_json"],
            ),
            Task(
                name="WriteOutputs",
                requires=["faq_page_json", "product_page_json", "comparison_page_json"],
                produces=["written_files"],
            ),
        ]
        import random
        random.shuffle(tasks)

        return tasks
