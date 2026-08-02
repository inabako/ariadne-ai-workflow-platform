from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.ctl.ctl_adapter_utils import save_plan_output_if_requested
from runtime.workflow import workflow_doctor


def run_doctor(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    result = workflow_doctor.run(
        argparse.Namespace(
            repo_root=str(repo_root),
            fail_on_warning=args.fail_on_warning,
            skip_ut_spec_sync=args.skip_ut_spec_sync,
            repair_encoding=args.repair_encoding,
            repair_spec_index=args.repair_spec_index,
            dry_run=getattr(args, "dry_run", False),
            fix_suggestion_only=getattr(args, "fix_suggestion_only", False),
            encoding_paths=args.encoding_paths,
            encoding_extensions=args.encoding_extensions,
        )
    )
    if getattr(args, "dry_run", False):
        return save_plan_output_if_requested(args, repo_root, result)
    return result
