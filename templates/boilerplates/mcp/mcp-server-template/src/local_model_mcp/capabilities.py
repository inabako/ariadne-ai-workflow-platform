from __future__ import annotations


PROMPTS = {
    "workflow_instruction": "Objective: {objective}\nConstraints: {constraints}\nExpected artifacts: {artifacts}",
    "repository_analysis": "Analyze repository structure, tests, risks, and evidence gaps for: {repository}",
    "implementation_plan": "Create an implementation plan for: {task}\nInclude artifacts and completion criteria.",
}

RESOURCES = {
    "workflow://definitions": {"workflows": ["repository-analysis", "implementation-task"]},
    "project://context": {"description": "Project context summary is supplied by the host application."},
    "model://information": {"provider": "mock", "supports_streaming": False},
    "artifact://outputs": {"description": "Artifacts written under the configured output root."},
}

TOOLS = [
    "health_check",
    "list_workspace_files",
    "read_workspace_file",
    "invoke_local_model",
    "write_output_artifact",
]

