from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.workflow import workflow_doctor


def run_doctor(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    return workflow_doctor.run(
        argparse.Namespace(
            repo_root=str(repo_root),
            fail_on_warning=args.fail_on_warning,
            skip_ut_spec_sync=args.skip_ut_spec_sync,
            repair_encoding=args.repair_encoding,
            repair_spec_index=args.repair_spec_index,
            encoding_paths=args.encoding_paths,
            encoding_extensions=args.encoding_extensions,
        )
    )
