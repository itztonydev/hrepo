from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitError(RuntimeError):
    def __init__(self, repo: Path, args: list[str], returncode: int, output: str):
        self.repo = repo
        self.args = args
        self.returncode = returncode
        self.output = output
        super().__init__(
            f"git {' '.join(args)} failed in {repo} "
            f"(exit {returncode}): {output.strip()}"
        )


def run(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if check and proc.returncode:
        raise GitError(repo, list(args), proc.returncode, proc.stdout)
    return proc.stdout


def is_repo(path: Path) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--git-dir"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


def root(path: Path) -> Path:
    return Path(run(path, "rev-parse", "--show-toplevel").strip()).resolve()


@dataclass(frozen=True)
class Submodule:
    path: Path
    name: str


def submodules(repo: Path) -> list[Submodule]:
    # mode 160000 entries are Git submodule gitlinks.
    output = run(repo, "ls-files", "-s")
    result: list[Submodule] = []

    for line in output.splitlines():
        fields = line.split(maxsplit=3)
        if len(fields) != 4:
            continue

        mode, _object_id, _stage, relpath = fields
        if mode != "160000":
            continue

        child = (repo / relpath).resolve()
        result.append(Submodule(child, relpath))

    return sorted(result, key=lambda x: x.name)


def status_porcelain(repo: Path) -> str:
    return run(repo, "status", "--porcelain=v1", "--untracked-files=all")


def dirty(repo: Path) -> bool:
    return bool(status_porcelain(repo).strip())


def head(repo: Path) -> str:
    return run(repo, "rev-parse", "HEAD").strip()


def add_all(repo: Path) -> None:
    run(repo, "add", "--all")


def staged_changes(repo: Path) -> bool:
    return bool(run(repo, "diff", "--cached", "--name-only").strip())


def commit(repo: Path, message: str) -> str:
    return run(repo, "commit", "-m", message)


def push(repo: Path) -> str:
    return run(repo, "push")


def sync(repo: Path) -> str:
    return run(repo, "submodule", "sync", "--recursive")


def update(repo: Path) -> str:
    return run(repo, "submodule", "update", "--init", "--recursive")
