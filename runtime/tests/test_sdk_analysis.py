from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.common import ctl
from runtime.workflow import sdk_analysis, work_cleanup


def test_sdk_analysis_skips_when_sdk_input_is_missing(tmp_path: Path) -> None:
    repo_root = tmp_path

    result = sdk_analysis.run_analysis(repo_root, work_id="issue-123", write_knowledge=False)

    assert result["status"] == "skipped"
    assert result["skip_reason"] == "missing-or-empty-sdk-input"
    assert result["source"]["path"] == "work/requirements/sdk"
    assert "skipped" in result["message"]


def test_sdk_analysis_writes_context_report_requirements_and_knowledge(tmp_path: Path) -> None:
    repo_root = tmp_path
    sdk_dir = repo_root / "work" / "requirements" / "sdk"
    sdk_dir.mkdir(parents=True)
    (sdk_dir / "README.md").write_text(
        "# Example SDK\n\nUse OAuth bearer token auth. Retry on timeout and respect rate limit. Sandbox tests are supported.\n",
        encoding="utf-8",
    )
    (sdk_dir / "package.json").write_text(
        json.dumps({"name": "@example/robot-sdk", "version": "1.2.3", "license": "MIT"}),
        encoding="utf-8",
    )
    (sdk_dir / "src").mkdir()
    (sdk_dir / "src" / "client.ts").write_text("export const endpoint = 'https://api.example.invalid';\n", encoding="utf-8")

    result = sdk_analysis.run_analysis(repo_root, work_id="issue-123")

    assert result["status"] == "available"
    assert result["sdk"]["names"] == ["@example/robot-sdk"]
    assert result["sdk"]["versions"] == ["1.2.3"]
    assert result["sdk"]["licenses"] == ["MIT"]
    assert result["findings"]["auth"]
    assert result["findings"]["network"]
    assert result["findings"]["tests"]
    assert (repo_root / "work" / "issue-123" / "reports" / "sdk-analysis-report.md").exists()
    assert (repo_root / "work" / "issue-123" / "requirements" / "sdk-integration-requirements.md").exists()
    context = json.loads((repo_root / "work" / "issue-123" / "context" / "sdk-analysis-context.json").read_text(encoding="utf-8"))
    assert context["artifact_type"] == "sdk-analysis-context"
    assert context["artifacts"]["knowledge_json"].startswith("work/db/ariadne-knowledge-platform/rag/jsonized/")
    assert context["work_cleanup"]["ready_for_check"] is True
    assert context["next_action"]["action"] == "check-work-cleanup"
    assert context["artifacts"]["work_cleanup_check"] == "aiwfctl work cleanup-check --work-id issue-123"
    assert "sdk-analysis" in context["manifest_contexts"]
    artifact_index = json.loads((repo_root / "work" / "issue-123" / "context" / "artifact-index.json").read_text(encoding="utf-8"))
    assert artifact_index["artifacts"][0]["id"] == "SDK-ANALYSIS-KNOWLEDGE"
    check = work_cleanup.cleanup_check(
        argparse.Namespace(work_id="issue-123", repo_root=str(repo_root), recursive=False, required_artifact=[])
    )
    assert check["status"] == "ready"
    knowledge_files = list((repo_root / "work" / "db" / "ariadne-knowledge-platform" / "rag" / "jsonized").glob("*.json"))
    assert len(knowledge_files) == 1
    knowledge = json.loads(knowledge_files[0].read_text(encoding="utf-8"))
    assert knowledge["artifact_type"] == "sdk-analysis-knowledge"
    assert "OAuth" not in knowledge["content"]


def test_sdk_analysis_detects_secret_like_literals_without_copying_values(tmp_path: Path) -> None:
    repo_root = tmp_path
    sdk_dir = repo_root / "work" / "requirements" / "sdk"
    sdk_dir.mkdir(parents=True)
    (sdk_dir / "README.md").write_text(
        "api_key = \"sk_live_abcdefghijklmnopqrstuvwxyz\"\n",
        encoding="utf-8",
    )

    result = sdk_analysis.run_analysis(repo_root, work_id="issue-777")

    assert result["status"] == "human-check-required"
    assert result["secret_findings"] == [
        {
            "file": "README.md",
            "finding": "secret-like literal was detected; value is intentionally not copied.",
        }
    ]
    context_text = (repo_root / "work" / "issue-777" / "context" / "sdk-analysis-context.json").read_text(encoding="utf-8")
    assert "sk_live_abcdefghijklmnopqrstuvwxyz" not in context_text


def test_aiwfctl_sdk_analyze_command(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    sdk_dir = repo_root / "work" / "requirements" / "sdk"
    sdk_dir.mkdir(parents=True)
    (sdk_dir / "pyproject.toml").write_text(
        '[project]\nname = "robot-sdk"\nversion = "0.1.0"\nlicense = { text = "Apache-2.0" }\n',
        encoding="utf-8",
    )

    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root), "sdk", "analyze", "--work-id", "issue-9"])
    code, output = ctl.run(args)

    assert code == 0
    assert "SDK Analysis" in output
    assert "work/issue-9/context/sdk-analysis-context.json" in output


def test_sdk_discovery_skips_when_sdk_program_input_is_missing(tmp_path: Path) -> None:
    repo_root = tmp_path

    result = sdk_analysis.run_discovery(repo_root, work_id="issue-404")

    assert result["status"] == "skipped"
    assert result["artifact_type"] == "sdk-external-discovery"
    assert result["source"]["path"] == "work/requirements/sdk"
    assert (repo_root / "work" / "issue-404" / "context" / "sdk-external-discovery.json").exists()


def test_sdk_discovery_generates_external_candidates_queries_and_context(tmp_path: Path) -> None:
    repo_root = tmp_path
    sdk_dir = repo_root / "work" / "requirements" / "sdk"
    sdk_dir.mkdir(parents=True)
    (sdk_dir / "README.md").write_text(
        "# Robot SDK\n\nDocs: https://docs.example.invalid/robot-sdk\n",
        encoding="utf-8",
    )
    (sdk_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "@example/robot-sdk",
                "version": "2.0.0",
                "license": "MIT",
                "homepage": "https://example.invalid/robot-sdk",
                "repository": {"url": "https://github.com/example/robot-sdk"},
            }
        ),
        encoding="utf-8",
    )

    result = sdk_analysis.run_discovery(repo_root, work_id="issue-55")

    assert result["status"] == "available"
    urls = {item["url"] for item in result["external_source_candidates"]}
    assert "https://www.npmjs.com/package/@example/robot-sdk" in urls
    assert "https://example.invalid/robot-sdk" in urls
    assert "https://github.com/example/robot-sdk" in urls
    assert "https://docs.example.invalid/robot-sdk" in urls
    assert any(item["purpose"] == "security" for item in result["search_queries"])
    assert "sdk-external-discovery" in result["manifest_contexts"]
    assert (repo_root / "work" / "issue-55" / "reports" / "sdk-external-discovery-report.md").exists()
    assert (repo_root / "work" / "issue-55" / "requirements" / "sdk-external-requirements.md").exists()


def test_sdk_analysis_detects_aws_and_gcp_cloud_sdk_metadata(tmp_path: Path) -> None:
    repo_root = tmp_path
    sdk_dir = repo_root / "work" / "requirements" / "sdk"
    sdk_dir.mkdir(parents=True)
    (sdk_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "cloud-sdk-composition",
                "version": "1.0.0",
                "dependencies": {
                    "@aws-sdk/client-s3": "^3.600.0",
                    "@google-cloud/pubsub": "^4.0.0",
                },
            }
        ),
        encoding="utf-8",
    )
    (sdk_dir / "README.md").write_text(
        "Uses AWS S3 and Google Pub/Sub. Configure region, project, IAM role, and service account.",
        encoding="utf-8",
    )

    result = sdk_analysis.run_analysis(repo_root, work_id="issue-cloud")

    assert result["cloud"]["provider"] == "multiple"
    assert set(result["cloud"]["providers"]) == {"aws", "gcp"}
    assert "s3" in result["cloud"]["services"]
    assert "pubsub" in result["cloud"]["services"]
    assert "AWS Region" in result["cloud"]["region_project_requirements"]
    assert "GCP Project" in result["cloud"]["region_project_requirements"]
    assert result["cloud"]["adoption_status"] == "needs_human_check"
    inventory = json.loads((repo_root / "work" / "issue-cloud" / "context" / "sdk-files.json").read_text(encoding="utf-8"))
    assert inventory["artifact_type"] == "sdk-file-inventory"
    assert inventory["files"][0]["sha256"]


def test_sdk_discovery_carries_cloud_sdk_metadata(tmp_path: Path) -> None:
    repo_root = tmp_path
    sdk_dir = repo_root / "work" / "requirements" / "sdk"
    sdk_dir.mkdir(parents=True)
    (sdk_dir / "requirements.txt").write_text(
        "boto3==1.34.0\ngoogle-cloud-storage==2.16.0\n",
        encoding="utf-8",
    )

    result = sdk_analysis.run_discovery(repo_root, work_id="issue-cloud-discovery")

    assert result["cloud"]["provider"] == "multiple"
    assert set(result["cloud"]["providers"]) == {"aws", "gcp"}
    assert any(item["purpose"] == "official-docs" for item in result["search_queries"])
    assert (repo_root / "work" / "issue-cloud-discovery" / "context" / "sdk-external-discovery.json").exists()


def test_sdk_analysis_detects_stripe_payment_sdk_metadata(tmp_path: Path) -> None:
    repo_root = tmp_path
    sdk_dir = repo_root / "work" / "requirements" / "sdk"
    sdk_dir.mkdir(parents=True)
    (sdk_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "payment-sdk-composition",
                "version": "1.0.0",
                "dependencies": {
                    "stripe": "^16.0.0",
                    "@stripe/stripe-js": "^4.0.0",
                },
            }
        ),
        encoding="utf-8",
    )
    (sdk_dir / "README.md").write_text(
        "Uses Stripe Checkout, PaymentIntent, webhook signature verification, test mode, and idempotency keys.",
        encoding="utf-8",
    )

    result = sdk_analysis.run_analysis(repo_root, work_id="issue-stripe")

    assert result["payment"]["vendor"] == "stripe"
    assert result["payment"]["vendors"] == ["stripe"]
    assert "checkout" in result["payment"]["services"]
    assert "payment_intents" in result["payment"]["services"]
    assert "webhooks" in result["payment"]["services"]
    assert "Stripe CLI webhook forwarding" in result["payment"]["local_testing"]["candidates"]
    assert "Webhook signing secret" in result["payment"]["authentication_candidates"]
    assert result["payment"]["adoption_status"] == "needs_human_check"
    assert any("idempotency" in item for item in result["payment"]["human_checks"])
    assert any("Stripe" in item for item in result["human_checks"])


def test_sdk_discovery_carries_stripe_payment_sdk_metadata(tmp_path: Path) -> None:
    repo_root = tmp_path
    sdk_dir = repo_root / "work" / "requirements" / "sdk"
    sdk_dir.mkdir(parents=True)
    (sdk_dir / "requirements.txt").write_text("stripe==9.12.0\n", encoding="utf-8")

    result = sdk_analysis.run_discovery(repo_root, work_id="issue-stripe-discovery")

    assert result["payment"]["vendor"] == "stripe"
    assert result["payment"]["vendors"] == ["stripe"]
    assert any(item["query"] == "Stripe official SDK documentation" for item in result["search_queries"])
    assert any(item["purpose"] == "webhook" for item in result["search_queries"])
    assert (repo_root / "work" / "issue-stripe-discovery" / "context" / "sdk-external-discovery.json").exists()


def test_aiwfctl_sdk_discover_command(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / ".git").mkdir()
    sdk_dir = repo_root / "work" / "requirements" / "sdk"
    sdk_dir.mkdir(parents=True)
    (sdk_dir / "pyproject.toml").write_text(
        '[project]\nname = "robot-sdk"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )

    args = ctl.build_parser().parse_args(["--repo-root", str(repo_root), "sdk", "discover", "--work-id", "issue-10"])
    code, output = ctl.run(args)

    assert code == 0
    assert "SDK External Discovery" in output
    assert "work/issue-10/context/sdk-external-discovery.json" in output
