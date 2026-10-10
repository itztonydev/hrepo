# hrepo Requirements

## 1. Purpose

Provide a thin Python command-line layer over Git for projects composed of
recursively nested Git submodules.

The tool must make a recursive multi-repository project feel like one
workspace while preserving independent Git repositories and histories.

## 2. Non-goals

hrepo is not:

- a replacement for Git
- a new version-control system
- a package manager
- a lockfile format
- a monorepo filesystem implementation
- a distributed transaction system

Git remains authoritative.

## 3. Repository model

A valid project may contain:

```text
root
├── child-a
│   ├── grandchild-a
│   └── grandchild-b
└── child-b
```

Every node is a real Git repository.

Parent-to-child relationships must be native Git submodules.

The parent repository stores the child's exact commit using Git's mode
`160000` gitlink.

## 4. Commit requirements

### R1 — Recursive discovery

The tool MUST discover Git submodules recursively.

### R2 — Bottom-up commit

The tool MUST commit descendants before ancestors.

For:

```text
A -> B -> C
```

the order is:

```text
C
B
A
```

### R3 — Identical commit message

A single invocation:

```bash
hrepo commit -m "message"
```

MUST use the exact supplied message for every repository that receives a
commit.

### R4 — No duplicate history

The tool MUST NOT copy a child commit into the parent.

The parent commit only records the changed child gitlink.

### R5 — No empty commits

A repository with no staged changes MUST NOT receive a commit.

### R6 — Failure stops ancestors

If a child commit fails, its ancestors MUST NOT be committed by the same
operation.

This prevents a parent from recording an incomplete subtree.

### R7 — Partial success is explicit

If a descendant commits successfully and an ancestor later fails, hrepo MUST
report the partial result. It MUST NOT pretend the operation is atomic.

## 5. Push requirements

### R8 — Bottom-up push

Recursive push MUST push descendants before ancestors.

This ensures that when a parent references child commit `X`, `X` has already
been sent to the remote by hrepo.

### R9 — No force push

hrepo MUST NOT force push.

## 6. Sync requirements

`hrepo sync` SHOULD map to Git's native:

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

No custom dependency resolution is required.

## 7. Status requirements

Status MUST identify:

- repository path
- clean/modified state
- uninitialized submodules
- failures

## 8. Safety requirements

The first version MUST NOT automatically:

- reset
- clean
- stash
- rebase
- merge
- checkout
- amend
- force push
- pull

These are intentionally left to Git.

## 9. Future requirements

Potential future commands:

```text
hrepo foreach COMMAND
hrepo diff
hrepo log
hrepo fetch
hrepo branch
hrepo checkout
hrepo commit --dry-run
hrepo push --dry-run
hrepo doctor
hrepo init
```

Potential advanced features:

- concurrent status/fetch
- signed commits
- commit trailers identifying the hrepo operation
- configurable commit policy
- hooks
- machine-readable JSON output
- colorized output
- transaction journal for recovery guidance
