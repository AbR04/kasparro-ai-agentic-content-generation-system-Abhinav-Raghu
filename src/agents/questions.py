from __future__ import annotations
from typing import Dict, List

from src.agents.base import BaseAgent
from src.messages import Message, Task, NeedArtifact

class QuestionAgent(BaseAgent):
    name = "question_agent"

    def handle(self, msg: Message, store, bus) -> List[Message]:
        if msg.type != "Task":
            return []

        task = msg  # type: ignore
        if not isinstance(task, Task) or task.name != "GenerateQuestions":
            return []

        if not store.has("product_model"):
            return [NeedArtifact(task.name, "product_model", task)]

        p = store.require("product_model").value

        categories: Dict[str, List[str]] = {
            "Informational": [
                f"What is {p['product_name']}?",
                "What does the concentration mean?",
                "What are the key benefits of this product?",
            ],
            "Usage": [
                "When should I apply this serum?",
                "How many drops should I use?",
                "Can I use it daily?",
            ],
            "Safety": [
                "Are there any side effects?",
                "Is mild tingling normal?",
                "Who should be cautious while using it?",
            ],
            "Purchase": [
                "What is the price of the product?",
                "Is this product good value for money?",
                "What do I get at this price point?",
            ],
            "Fitment": [
                "Which skin types is it suitable for?",
                "Is it suitable for oily skin?",
                "Is it suitable for combination skin?",
            ],
            "Comparison": [
                "How does this compare to a generic Vitamin C serum?",
                "How does price compare to a basic competitor?",
                "How do ingredients compare to a simple competitor?",
            ],
        }

        total_questions = sum(len(v) for v in categories.values())

        question_bank = {
            "total_questions": total_questions,   # >= 15 guaranteed
            "categories": categories,
        }

        bus.put_artifact("question_bank", question_bank, produced_by=self.name)
        return []
