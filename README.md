# hrepo

`hrepo` is a small Python CLI for recursively nested Git repositories implemented
with native Git submodules.

I do use this and is heavy testing expect breaking changes if any

It does **not** introduce a second lockfile or duplicate Git history (yet probably).

## Model

```text
root.git
├── services/api.git
│   ├── auth.git
│   └── users.git
└── infra.git
```

Each repository owns its own history.

A parent stores only a Git gitlink pointing at the exact child commit:

```text
root @ R2
└── api @ A4
    ├── auth @ H7
    └── users @ U3
```

## Core invariant

Recursive commit is always bottom-up:

```text
leaf commit
    ↓
child gitlink updated + child commit
    ↓
parent gitlink updated + parent commit
    ↓
grandparent gitlink updated + grandparent commit
```

The same commit message is used at every repository that receives a commit.

Recursive push is also bottom-up.

## Installation

```bash
python -m pip install .
```

Or during development:

```bash
python -m pip install -e .
```

## Interface

```text
hrepo status [PATH] [--recursive]
hrepo graph [PATH]
hrepo commit -m MESSAGE [PATH] [--recursive]
hrepo push [PATH] [--recursive]
hrepo sync [PATH] [--recursive]
```

`PATH` defaults to the current directory.

### Status

```bash
hrepo status
```

Shows repository state recursively and identifies uninitialized submodules.

### Graph

```bash
hrepo graph
```

Prints the repository/submodule tree.

### Commit

```bash
hrepo commit -m "fix household permissions"
```

Recursively commits dirty repositories bottom-up.

For:

```text
A
└── B
    └── C
```

the operation is:

```text
C commit
B commit (records C gitlink)
A commit (records B gitlink)
```

If a repository has no staged changes after `git add -A`, no commit is created.

### Push

```bash
hrepo push
```

Pushes repositories bottom-up.

This matters because a parent may reference a child commit that must already
exist on the remote.

### Sync

```bash
hrepo sync
```

Runs:

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

It does not change commits.

## Safety

The initial implementation intentionally does NOT:

- force push
- amend commits
- rebase
- reset
- checkout branches
- resolve merge conflicts
- automatically pull
- automatically stash
- create commits if there are no changes
- rewrite commit messages

The tool delegates all history semantics to Git.

## Failure semantics

If a child commit succeeds but a parent commit fails:

```text
child: committed
parent: failed
```

the child commit is not rolled back.

This is intentional: Git commits are immutable history, and a fake
cross-repository transaction would be misleading.

Run:

```bash
hrepo status
hrepo commit -m "same message"
```

to reconcile the parent gitlink.

## Design principle

Git is the database.

Submodule gitlinks are the lock/snapshot mechanism.

`hrepo` is only recursive orchestration.
