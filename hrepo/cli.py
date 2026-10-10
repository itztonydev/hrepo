from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .model import discover
from . import git
from .ops import commit, push, status, sync


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hrepo",
        description="Recursive Git submodule workspace orchestration.",
    )

    sub = p.add_subparsers(dest="command", required=True)

    for name in ("status", "graph", "sync", "push"):
        cmd = sub.add_parser(name)
        cmd.add_argument("path", nargs="?", default=".")

    cmd = sub.add_parser("commit")
    cmd.add_argument("-m", "--message", required=True)
    cmd.add_argument("path", nargs="?", default=".")

    return p


def print_result(result) -> None:
    mark = "OK " if result.ok else "ERR"
    print(f"{mark} {result.action:7} {result.repo} :: {result.detail}")


def print_graph(node, prefix: str = "") -> None:
    print(f"{prefix}{node.path.name or node.path}")
    for i, child in enumerate(node.children):
        branch = "└── " if i == len(node.children) - 1 else "├── "
        print(f"{prefix}{branch}", end="")
        print_graph(child, prefix + ("    " if i == len(node.children) - 1 else "│   "))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)

    try:
        node = discover(Path(args.path))

        if args.command == "graph":
            print_graph(node)
            return 0

        if args.command == "status":
            results = status(node)

        elif args.command == "commit":
            results = commit(node, args.message)

        elif args.command == "push":
            results = push(node)

        elif args.command == "sync":
            results = sync(node)

        else:
            raise AssertionError(args.command)

        failed = False
        for result in results:
            print_result(result)
            failed |= not result.ok

        return 1 if failed else 0

    except git.GitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
