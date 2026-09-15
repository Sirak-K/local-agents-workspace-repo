# GUIDE 3 — TEXT FILE READING

**Current-sprint status: PASS / CLOSED (2026-09-15).**

**Objective:** prove useful local text-file reading quickly on the stable Guide-2 baseline. Full PDF/RAG tuning is deferred to later Codex hardening.

## Repo fixtures

```text
SillyTavern_UI/fixtures/guide3/fixture-a.md
SillyTavern_UI/fixtures/guide3/fixture-b.txt
```

## Verified test

Both files were attached directly to the same SillyTavern message and the model was asked for seven source facts plus one deliberately absent fact.

Observed result:

```text
Project codename: Silver Finch        PASS
Caretaker: Mara Venn                  PASS
Archive room: C-17                    PASS
Red key: only the northern cabinet    PASS
Transit vessel: Ember Kite            PASS
Quartermaster: Oren Vale              PASS
Blue seal: only the east storage bay  PASS
Silver Finch launch date: absent      PASS (not invented)
```

This verifies for the current sprint:

- direct `.md` reading,
- direct `.txt` reading,
- combining facts from two attachments,
- refusing to invent a deliberately missing fact.

No visible `<think>` leakage occurred on the restored stable text baseline during this test.

## SillyTavern UI note

In pinned SillyTavern `1.19.0`, new-message file attachment is exposed through:

```text
Magic Wand -> Attach a File
```

The feature is supplied by the built-in `Data Bank (Chat Attachments)` extension. Message-action paperclip controls on existing messages are a different UI path.

## Deferred hardening

Later Codex work may add/verify without reopening this gate:

- text-layer PDF direct attachment,
- Data Bank/RAG with two or more documents,
- Local Transformers embeddings,
- chunk/retrieval tuning,
- larger real project documents,
- latency/quality profiling.

Failure attribution remains strict: attachment parsing, retrieval and embedding failures are not model failures unless the model is independently isolated as the cause.

# GUIDE-3 PASS

Guide 3 is closed for the current sprint.
