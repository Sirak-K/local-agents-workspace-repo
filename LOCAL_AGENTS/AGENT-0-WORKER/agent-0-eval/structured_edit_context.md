Evaluation-only rules for the structured edit task:

- A slash-separated path starts at the supplied JSON document. A decimal path segment selects a zero-based array item; any other segment selects an existing object key.
- A `set` operation replaces only the value at its existing path. Apply operations in the stated order. Do not create paths or change unrelated values.
- Preserve JSON value types. Return the complete resulting JSON document, not a description of the edits.
