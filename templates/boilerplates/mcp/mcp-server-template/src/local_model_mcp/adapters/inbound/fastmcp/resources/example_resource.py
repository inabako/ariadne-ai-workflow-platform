from __future__ import annotations

from .....capabilities import RESOURCES
from .....bootstrap import ApplicationContainer


def read_model_information(container: ApplicationContainer) -> dict[str, object]:
    return {**RESOURCES["model://information"], "model_id": container.config.model_id}
