"""Executable Code Reviewer implementation used by the MCP adapter."""

from __future__ import annotations

import os
from typing import List

import anthropic
import httpx

SYSTEM_PROMPT = """
You are a senior software engineer conducting a thorough code review.
For each code chunk, identify:
1. BUGS — logic errors, off-by-one, null dereferences, race conditions
2. SECURITY — hardcoded secrets, injection vectors, improper auth
3. STYLE — naming, complexity, dead code, missing docs
4. PERFORMANCE — N+1 queries, missing indexes, inefficient loops

Format each issue as:
**[SEVERITY: critical|major|minor]** `file.py:line` — Description + suggested fix.

If a chunk looks good, say "LGTM" with one sentence of praise.
"""

def get_pr_diff(repo: str, pr_number: int, token: str) -> str:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3.diff"}
    response = httpx.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
        headers=headers,
        timeout=30.0,
    )
    response.raise_for_status()
    return response.text

def split_diff_into_chunks(diff: str, max_lines: int = 80) -> List[str]:
    """Split large diffs into reviewable chunks by file boundary."""
    chunks: list[str] = []
    current: list[str] = []
    for line in diff.splitlines():
        if line.startswith("diff --git") and current:
            chunks.append("\n".join(current))
            current = []
        current.append(line)
        if len(current) >= max_lines:
            chunks.append("\n".join(current))
            current = []
    if current:
        chunks.append("\n".join(current))
    return chunks

def review_chunk(chunk: str, client: anthropic.Anthropic | None = None) -> str:
    """Review one diff chunk using the configured Anthropic client."""
    client = client or anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Review this diff:\n\n```diff\n{chunk}\n```"}],
    )
    return response.content[0].text

def review_pull_request(repo: str, pr_number: int, github_token: str, client: anthropic.Anthropic | None = None) -> List[str]:
    """Fetch and review a GitHub pull request diff."""
    diff = get_pr_diff(repo, pr_number, github_token)
    return [review_chunk(chunk, client=client) for chunk in split_diff_into_chunks(diff)]
