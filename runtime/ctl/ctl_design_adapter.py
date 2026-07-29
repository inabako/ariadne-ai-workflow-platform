from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.design import expectation


def run_design(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    args.repo_root = str(repo_root)
    design_area = getattr(args, "design_area", "")
    if design_area == "candidate":
        candidate_command = getattr(args, "candidate_command", "")
        if candidate_command == "generate":
            return expectation.candidate_scaffold(args)
        if candidate_command == "evaluate":
            return expectation.evaluate_design(args)
        if candidate_command == "compare":
            return expectation.compare_design(args)
        raise KeyError(candidate_command or design_area)
    if design_area != "expectation":
        raise KeyError(design_area or command)
    expectation_command = getattr(args, "expectation_command", "")
    if expectation_command == "init":
        return expectation.init_design(args)
    if expectation_command == "candidate-scaffold":
        return expectation.candidate_scaffold(args)
    if expectation_command == "candidate" and getattr(args, "candidate_command", "") == "generate":
        return expectation.candidate_scaffold(args)
    if expectation_command == "feasibility":
        return expectation.feasibility_design(args)
    if expectation_command == "extract":
        return expectation.extract_design(args)
    if expectation_command == "review":
        return expectation.review_design(args)
    if expectation_command == "evaluate":
        return expectation.evaluate_design(args)
    if expectation_command == "multi-axis":
        return expectation.multi_axis_design(args)
    if expectation_command == "compare":
        return expectation.compare_design(args)
    if expectation_command == "gate":
        return expectation.gate_design(args)
    if expectation_command == "run":
        return expectation.gate_design(args)
    if expectation_command == "refine":
        return expectation.refine_design(args)
    if expectation_command == "contracts":
        return expectation.contracts_design(args)
    if expectation_command == "verify":
        return expectation.verify_design(args)
    if expectation_command == "feedback":
        return expectation.feedback_design(args)
    if expectation_command == "dispatch":
        return expectation.dispatch_design(args)
    if expectation_command == "council-sync":
        return expectation.council_sync_design(args)
    raise KeyError(expectation_command)
