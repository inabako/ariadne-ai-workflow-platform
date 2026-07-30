from __future__ import annotations

import json
import re
from typing import Any
from urllib import error, request
from urllib.parse import quote

from runtime.common import env_value
from runtime.constants.runtime_values import GITHUB_API_TIMEOUT_SECONDS


def github_api_base_url(settings: dict[str, str]) -> str:
    explicit = env_value(settings, "GITHUB_API_URL", "GH_API_URL")
    if explicit:
        return explicit.rstrip("/")
    host = env_value(settings, "GH_HOST", "GITHUB_HOST", default="github.com").strip() or "github.com"
    if host == "github.com":
        return "https://api.github.com"
    host = re.sub(r"^https?://", "", host).rstrip("/")
    return f"https://{host}/api/v3"


def github_graphql_url(settings: dict[str, str]) -> str:
    explicit = env_value(settings, "GITHUB_GRAPHQL_URL", "GH_GRAPHQL_URL")
    if explicit:
        return explicit.rstrip("/")
    api_url = env_value(settings, "GITHUB_API_URL", "GH_API_URL").rstrip("/")
    if api_url:
        if api_url == "https://api.github.com":
            return "https://api.github.com/graphql"
        if api_url.endswith("/api/v3"):
            return f"{api_url[:-7]}/api/graphql"
        return f"{api_url}/graphql"
    host = env_value(settings, "GH_HOST", "GITHUB_HOST", default="github.com").strip() or "github.com"
    if host == "github.com":
        return "https://api.github.com/graphql"
    host = re.sub(r"^https?://", "", host).rstrip("/")
    return f"https://{host}/api/graphql"


def github_token(settings: dict[str, str]) -> str:
    token = env_value(settings, "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_API_TOKEN", "GITHUB_API_KEY")
    if not token:
        raise ValueError("GitHub API token is required. Set GITHUB_TOKEN in repository root .env.")
    return token


def github_api_json(
    settings: dict[str, str],
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    api_url = f"{github_api_base_url(settings)}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    http_request = request.Request(
        api_url,
        data=data,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token(settings)}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method,
    )
    try:
        with request.urlopen(http_request, timeout=GITHUB_API_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body) if response_body else {}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            detail = parsed.get("message", detail)
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"GitHub API request failed ({exc.code}): {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc


def github_graphql_json(
    settings: dict[str, str],
    query: str,
    variables: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    http_request = request.Request(
        github_graphql_url(settings),
        data=data,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token(settings)}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=GITHUB_API_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8")
            parsed = json.loads(response_body) if response_body else {}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed_detail = json.loads(detail)
            detail = parsed_detail.get("message", detail)
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"GitHub GraphQL request failed ({exc.code}): {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"GitHub GraphQL request failed: {exc.reason}") from exc

    errors = parsed.get("errors")
    if errors:
        messages = "; ".join(str(item.get("message", item)) for item in errors)
        raise RuntimeError(f"GitHub GraphQL request failed: {messages}")
    return parsed.get("data", {})


def get_branch_sha(settings: dict[str, str], github_repo: str, branch: str) -> str:
    owner, repo = github_repo.split("/", 1)
    data = github_api_json(
        settings,
        "GET",
        f"/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/branches/{quote(branch, safe='')}",
    )
    sha = data.get("commit", {}).get("sha")
    if not sha:
        raise RuntimeError(f"GitHub API response did not include commit sha for {github_repo}:{branch}.")
    return str(sha)


def get_repository_issue_graphql_context(
    settings: dict[str, str],
    github_repo: str,
    issue_number: str,
    base_branch: str,
) -> dict[str, str]:
    owner, repo = github_repo.split("/", 1)
    query = """
    query IssueBranchContext($owner: String!, $name: String!, $issueNumber: Int!, $baseBranch: String!) {
      repository(owner: $owner, name: $name) {
        id
        issue(number: $issueNumber) {
          id
          number
        }
        ref(qualifiedName: $baseBranch) {
          target {
            oid
          }
        }
      }
    }
    """
    data = github_graphql_json(
        settings,
        query,
        {
            "owner": owner,
            "name": repo,
            "issueNumber": int(issue_number),
            "baseBranch": base_branch,
        },
    )
    repository = data.get("repository") or {}
    issue = repository.get("issue") or {}
    ref = repository.get("ref") or {}
    target = ref.get("target") or {}
    repository_id = repository.get("id")
    issue_id = issue.get("id")
    base_oid = target.get("oid")
    if not repository_id:
        raise RuntimeError(f"GitHub GraphQL response did not include repository id for {github_repo}.")
    if not issue_id:
        raise RuntimeError(f"GitHub GraphQL response did not include issue id for {github_repo}#{issue_number}.")
    if not base_oid:
        raise RuntimeError(f"GitHub GraphQL response did not include base oid for {github_repo}:{base_branch}.")
    return {
        "repository_id": str(repository_id),
        "issue_id": str(issue_id),
        "base_oid": str(base_oid),
    }


def create_linked_branch(
    settings: dict[str, str],
    github_repo: str,
    issue_number: str,
    branch: str,
    base_branch: str,
) -> dict[str, Any]:
    context = get_repository_issue_graphql_context(settings, github_repo, issue_number, base_branch)
    mutation = """
    mutation CreateIssueLinkedBranch($input: CreateLinkedBranchInput!) {
      createLinkedBranch(input: $input) {
        issue {
          id
          number
        }
        linkedBranch {
          id
          ref {
            name
            target {
              oid
            }
          }
        }
      }
    }
    """
    data = github_graphql_json(
        settings,
        mutation,
        {
            "input": {
                "issueId": context["issue_id"],
                "repositoryId": context["repository_id"],
                "name": branch,
                "oid": context["base_oid"],
            }
        },
    )
    payload = data.get("createLinkedBranch") or {}
    linked_branch = payload.get("linkedBranch") or {}
    linked_ref = linked_branch.get("ref") or {}
    target = linked_ref.get("target") or {}
    return {
        "status": "created",
        "linked_branch_id": linked_branch.get("id"),
        "linked_branch_name": linked_ref.get("name") or branch,
        "linked_branch_oid": target.get("oid") or context["base_oid"],
        "issue_id": context["issue_id"],
        "repository_id": context["repository_id"],
        "base_oid": context["base_oid"],
    }


def create_branch_ref(settings: dict[str, str], github_repo: str, branch: str, sha: str) -> str:
    owner, repo = github_repo.split("/", 1)
    data = github_api_json(
        settings,
        "POST",
        f"/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/git/refs",
        {
            "ref": f"refs/heads/{branch}",
            "sha": sha,
        },
    )
    ref = data.get("ref")
    if not ref:
        raise RuntimeError(f"GitHub API response did not include created ref for {github_repo}:{branch}.")
    return str(ref)
