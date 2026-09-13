---
name: general-file-work
description: Use when the user asks the general-purpose agent to discover, inspect, search, create, or update text files in the approved workspace.
compatibility: LM Studio Bionic Agent Profile 1 with the verified PG-2 bounded filesystem surface.
---

# General File Work

Use this skill only when the current request actually requires filesystem work. Ordinary conversation should not trigger file tools.

1. For project text files, use the bounded PG-2 filesystem tools when available: `list_directory`, `read_text_file`, `search_text`, `file_state`, `create_text_file`, and `replace_text_file`.
2. Discover only as much of the workspace as needed to identify the intended file. Prefer bounded directory listing or focused search over broad recursive dumping.
3. Read the smallest useful file or slice before making claims about its contents. Preserve the SHA-256 returned by the read/state that established the version being modified.
4. Treat create and replace as different operations. Do not overwrite an existing file as an implicit fallback for create.
5. For replace, pass the SHA-256 from the read/state the requested edit is based on. If the tool reports stale state, stop and report the conflict; do not reread merely to obtain a new hash and force the original edit through.
6. Report a write as successful only after the bounded tool result says `APPROVED`; when practical, verify the written content with `read_text_file`.
7. Surface paths to the user in project-relative form when the active tool/runtime provides enough information to do so accurately.
8. If a bounded tool rejects a path, write, encoding, size, symlink/reparse, stale state or other operation, preserve that failure. Do not bypass it through Bionic-native filesystem tools, permission escalation, shell, Python or Git.
9. Do not use delete, move, rename, copy, shell execution, Git mutation, or other broader capabilities merely because a host exposes them. Use only capabilities that are part of the currently approved agent contract and requested by the user.
