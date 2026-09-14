# Bounded WORKER file task

Use only the file tools exposed for the disposable workspace. Paths are relative to that workspace. Read required inputs before relying on them, make only the requested change, read back the result, and never claim an operation succeeded unless its tool result confirms it. Preserve every file and byte outside the explicitly requested change.
