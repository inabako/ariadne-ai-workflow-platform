from __future__ import annotations

import argparse
from pathlib import Path

from .runtime import AgentRuntime
from .workflow import Workflow, WorkflowStep


def demo() -> None:
    workflow = Workflow(
        name="repository-analysis",
        steps=[
            WorkflowStep(name="inspect", action="read repository"),
            WorkflowStep(name="report", action="write report", produces_artifact="analysis-report.md"),
        ],
        required_artifacts=["analysis-report.md"],
    )
    runtime = AgentRuntime(Path("workspace/checkpoints"))
    job, result = runtime.submit_and_run("Analyze repository", workflow)
    print({"job_id": job.job_id, "state": job.state.value, "complete": result.complete})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        demo()


if __name__ == "__main__":
    main()

