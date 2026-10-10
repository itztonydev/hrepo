from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import git
from .model import RepoNode


@dataclass
class OperationResult:
    repo: Path
    action: str
    ok: bool
    detail: str = ""


def status(node: RepoNode) -> list[OperationResult]:
    results: list[OperationResult] = []

    for current in node.walk_postorder():
        if not current.initialized:
            results.append(
                OperationResult(current.path, "missing", False, "not initialized")
            )
            continue

        state = git.status_porcelain(current.path)
        detail = "clean" if not state.strip() else "modified"
        results.append(OperationResult(current.path, "status", True, detail))

    return results


def commit(node: RepoNode, message: str) -> list[OperationResult]:
    results: list[OperationResult] = []

    # Preflight the complete tree. A recursive commit must not partially
    # operate simply because a descendant was not initialized.
    missing = [current.path for current in node.walk_postorder() if not current.initialized]
    if missing:
        return [
            OperationResult(
                node.path,
                "commit",
                False,
                "uninitialized repositories: " + ", ".join(map(str, missing)),
            )
        ]

    for current in node.walk_postorder():
        if not current.initialized:
            results.append(
                OperationResult(current.path, "commit", False, "not initialized")
            )
            continue

        try:
            git.add_all(current.path)

            if not git.staged_changes(current.path):
                results.append(
                    OperationResult(current.path, "commit", True, "nothing to commit")
                )
                continue

            output = git.commit(current.path, message)
            results.append(OperationResult(current.path, "commit", True, output.strip()))

        except git.GitError as exc:
            results.append(OperationResult(current.path, "commit", False, exc.output.strip()))
            # Stop: an ancestor cannot safely be committed until this level is resolved.
            break

    return results


def push(node: RepoNode) -> list[OperationResult]:
    results: list[OperationResult] = []

    for current in node.walk_postorder():
        if not current.initialized:
            results.append(
                OperationResult(current.path, "push", False, "not initialized")
            )
            continue

        try:
            output = git.push(current.path)
            results.append(OperationResult(current.path, "push", True, output.strip()))
        except git.GitError as exc:
            results.append(OperationResult(current.path, "push", False, exc.output.strip()))
            break

    return results


def sync(node: RepoNode) -> list[OperationResult]:
    try:
        output = git.sync(node.path)
        output += git.update(node.path)
        return [OperationResult(node.path, "sync", True, output.strip())]
    except git.GitError as exc:
        return [OperationResult(node.path, "sync", False, exc.output.strip())]
