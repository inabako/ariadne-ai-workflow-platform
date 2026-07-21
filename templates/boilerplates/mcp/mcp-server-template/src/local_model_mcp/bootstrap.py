from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .adapters.outbound.local_model import LocalModelPortAdapter
from .adapters.outbound.workspace import WorkspaceRepository
from .application.use_cases import LocalModelCapabilityUseCase
from .audit import AuditRecorder
from .config import ServerConfig
from .config_loader import load_config_from_env
from .model_adapter import LocalModelAdapter, MockModelAdapter
from .security import WorkspacePathPolicy
from .tool_policy import ToolPolicy


@dataclass
class ApplicationContainer:
    config: ServerConfig
    path_policy: WorkspacePathPolicy
    audit: AuditRecorder
    tool_policy: ToolPolicy
    capability_use_case: LocalModelCapabilityUseCase


def create_application_container(
    config: ServerConfig,
    *,
    model_adapter: LocalModelAdapter | None = None,
) -> ApplicationContainer:
    config.input_root.mkdir(parents=True, exist_ok=True)
    config.output_root.mkdir(parents=True, exist_ok=True)
    path_policy = WorkspacePathPolicy(config.input_root, config.output_root)
    audit = AuditRecorder()
    workspace = WorkspaceRepository(path_policy=path_policy, audit=audit)
    model = LocalModelPortAdapter(model_adapter or MockModelAdapter())
    capability_use_case = LocalModelCapabilityUseCase(config=config, workspace=workspace, model=model)
    return ApplicationContainer(
        config=config,
        path_policy=path_policy,
        audit=audit,
        tool_policy=ToolPolicy(),
        capability_use_case=capability_use_case,
    )


def create_application(base_dir: Path | None = None) -> ApplicationContainer:
    return create_application_container(load_config_from_env(base_dir))
