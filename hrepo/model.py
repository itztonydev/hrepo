from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import git


@dataclass
class RepoNode:
    path: Path
    children: list["RepoNode"] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.name or str(self.path)

    @property
    def initialized(self) -> bool:
        return git.is_repo(self.path)

    def walk_postorder(self):
        for child in self.children:
            yield from child.walk_postorder()
        yield self


def discover(path: Path) -> RepoNode:
    repo = git.root(path)
    return _discover_repo(repo, seen=set())


def _discover_repo(repo: Path, seen: set[Path]) -> RepoNode:
    repo = repo.resolve()

    if repo in seen:
        raise RuntimeError(f"submodule cycle detected at {repo}")
    seen.add(repo)

    node = RepoNode(repo)

    for sm in git.submodules(repo):
        if not sm.path.exists():
            # Keep an uninitialized/missing child in the graph.
            node.children.append(RepoNode(sm.path))
            continue

        if not git.is_repo(sm.path):
            node.children.append(RepoNode(sm.path))
            continue

        node.children.append(_discover_repo(sm.path, seen.copy()))

    return node
