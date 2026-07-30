from __future__ import annotations

from .....capabilities import PROMPTS


def render_workflow_instruction(objective: str, constraints: str = "", artifacts: str = "") -> str:
    return PROMPTS["workflow_instruction"].format(
        objective=objective,
        constraints=constraints,
        artifacts=artifacts,
    )
