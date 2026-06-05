from __future__ import annotations

import json
import re
from typing import Any
from urllib import error, request
from urllib.parse import quote

from runtime.common import env_value


def github_api_base_url(settings: dict[str, str]) -> str:
    explicit = env_value(settings, "GITHUB_API_URL", "GH_API_URL")
    if explicit:
        return explicit.rstrip("/")
    host = env_value(settings, "GH_HOST", "GITHUB_HOST", default="github.com").strip() or "github.com"
    if host == "github.com":
        return "https://api.github.com"
    host = re.sub(r"^https?://", "", host).rstrip("/")
    return f"https://{host}/api/v3"


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
        with request.urlopen(http_request, timeout=30) as response:
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
