# Placeholder for integration tests.
#
# Recommended test strategy:
#
# 1. Create temporary repositories A, B, C.
# 2. Add C as a submodule of B.
# 3. Add B as a submodule of A.
# 4. Modify all three.
# 5. Run hrepo commit.
# 6. Assert three commits exist and messages are identical.
# 7. Assert A's gitlink points to B's new HEAD.
# 8. Assert B's gitlink points to C's new HEAD.
#
# Integration tests should use the real `git` executable because the tool's
# contract is fundamentally about Git repository behavior.
