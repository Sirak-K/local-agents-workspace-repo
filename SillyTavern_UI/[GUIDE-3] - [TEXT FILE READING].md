# GUIDE 3 — TEXT FILE READING

**Current-sprint objective:** prove useful local text-file reading quickly on the stable Guide-2 baseline. Full PDF/RAG tuning is deferred to later Codex hardening.

## Repo fixtures

AutoSync provides two synthetic files:

```text
SillyTavern_UI/fixtures/guide3/fixture-a.md
SillyTavern_UI/fixtures/guide3/fixture-b.txt
```

They contain unique facts that cannot reasonably be guessed from the question alone.

## Fast validation

Attach **both files directly to the same clean SillyTavern chat**. Do not enable Data Bank/RAG for this fast test.

Send exactly:

```text
Answer only from the attached files.
1. What is the project codename?
2. Who is the caretaker?
3. Which room contains the archive?
4. What exactly does the red key open?
5. What is the transit vessel called?
6. Who is the quartermaster?
7. What does the blue seal authorize access to?
8. What is the launch date of Silver Finch?
```

Expected source facts:

```text
Project codename: Silver Finch
Caretaker: Mara Venn
Archive room: C-17
Red key: only the northern cabinet
Transit vessel: Ember Kite
Quartermaster: Oren Vale
Blue seal: only the east storage bay
Silver Finch launch date: NOT PRESENT
```

## PASS for current fast-track sprint

- `.md` facts are read correctly,
- `.txt` facts are read correctly,
- facts from both files can be combined in one answer,
- the missing launch-date question is identified as absent/unknown rather than invented.

If this passes, Guide 3 is closed for the current sprint.

## Deferred hardening

Later Codex work may add/verify without blocking the current sprint:

- text-layer PDF direct attachment,
- Data Bank/RAG with two or more documents,
- Local Transformers embeddings,
- chunk/retrieval tuning,
- larger real project documents,
- latency/quality profiling.

Failure attribution rule remains strict: attachment parsing, retrieval and embedding failures are not model failures unless the model is independently isolated as the cause.
