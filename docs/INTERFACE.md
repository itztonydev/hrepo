# hrepo Interface Specification

## CLI

### `hrepo graph [PATH]`

Display the recursive repository graph.

Example:

```text
root
├── api
│   ├── auth
│   └── users
└── infra
```

### `hrepo status [PATH]`

Recursively inspect every initialized repository.

Exit codes:

```text
0  all repositories inspected successfully
1  one or more repositories are missing/uninitialized
2  command/tool error
```

### `hrepo commit -m MESSAGE [PATH]`

Commit all changes in the recursive repository tree.

Algorithm:

```text
discover tree
validate initialized children
walk postorder
    git add --all
    if staged changes:
        git commit -m MESSAGE
stop on failure
```

Example:

```text
root
└── api
    └── auth
```

Produces, if all three are dirty:

```text
auth: commit M
api:  commit M
root: commit M
```

The commit IDs are different. The commit message is identical.

### `hrepo push [PATH]`

Walk the tree postorder and run:

```bash
git push
```

at each repository.

Stops at the first failure.

### `hrepo sync [PATH]`

At the root, run:

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

## Python API

The initial implementation exposes simple modules:

```python
from pathlib import Path

from hrepo.model import discover
from hrepo.ops import commit, push, status, sync

tree = discover(Path("."))

status(tree)

commit(tree, "fix household permissions")

push(tree)

sync(tree)
```

## Extension point

The implementation deliberately separates:

```text
hrepo.git       Git subprocess boundary
hrepo.model     repository graph
hrepo.ops       recursive operations
hrepo.cli       user interface
```

This allows later replacement of the CLI without changing repository semantics.

## Important semantic rule

The parent does not "receive" the child's commit.

Instead:

```text
child:
    C1 -> C2

parent:
    P1 -> P2
          |
          +-- child gitlink: C2
```

The parent only records the new child commit through its normal Git tree.
