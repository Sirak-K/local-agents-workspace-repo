# Official Project Terminology

This document is the canonical glossary for project-specific abbreviations. Generic technical terms are included only when they are part of the project's contracts or identifiers.

## Project goals and planning

### PG — Project Goal

- **PG-1:** General and Personal Chat Agent without tools.
- **PG-2:** The same General and Personal Chat Agent with controlled file read and write.
- **PG-3:** Story Creation specialization. Lumimaid and ComfyUI-related Story work are currently standby/legacy.

### RMS — Roadmap Step

The numbered operational step in a `[ROADMAP]` table. `RMS-X/Y` reports that step X of Y has started. RMS terminology is documentation-only and must not become a runtime identifier.

## Story artifact terminology

### SSC — Story Segment Core

The structured narrative authority derived from an approved premise. SSC owns Story facts, identities, scene and segment ordering, START/MID/END states, motion dependencies and continuity requirements used by downstream Story artifacts.

### PRMPRZ — Prompt-Realized

The compact filename identifier for Prompt-Realized artifacts. Prompt-Realized is the Story represented as workflow- and prompt-owner-specific runtime text. JSON is the machine-readable source; Markdown is its deterministic human-readable projection.

### VSSA — Version-Specific Story Artifact

A concrete, materialized artifact representing one intended Story version. A produced Story has exactly five VSSA variants:

- `VSSA_PREMISE` — byte-exact snapshot of the approved editable premise.
- `VSSA_SSC` — materialized Story Segment Core.
- `VSSA_FULL` — complete narrative prose derived from the premise and accepted SSC.
- `VSSA_PRMPRZ_JSON` — machine-readable Prompt-Realized source.
- `VSSA_PRMPRZ_MD` — deterministic Markdown projection of Prompt-Realized JSON.

Here, “Story version” means one of these intended representations, not a numbered historical revision.

### VSSADB — Version-Specific Story Artifact Design Blueprint

Pre-generation design instructions defining how one specific VSSA type must be created. A VSSADB is guidance and contract material, not a generated Story artifact.

### VSSDB — Version-Specific Story Design Blueprint

The version-specific narrative design—such as phrasing, formulation and paragraph structure—that is materialized inside a narrative VSSA. VSSDB is a creation-semantics concept, not an artifact filename.

### VSSA-QC-I — Version-Specific Story Artifact Quality Control Instructions

Pre-generation Quality Control instructions for reviewing one specific VSSA type. These instructions guide SAQC but are not themselves a Quality result.

### VSSAQC — Version-Specific Story Artifact Quality Control

A materialized Quality Control result for exactly one VSSA. Every started SAQC iteration produces five VSSAQC reports: Premise, SSC, Full, Prompt-Realized JSON and Prompt-Realized Markdown.

### SAQC — Story Artifact Quality Control

The integrated Story-level Quality Control stage after all five VSSA files have been assembled and before any ComfyUI workflow write. SAQC reviews SSC, Full and Prompt-Realized for language, narrative, semantic and cross-artifact correctness while deterministic validation protects schemas, hashes and exact machine contracts. SAQC aggregates the complete Story Quality outcome across the VSSAQC results.

### SAQC iteration

One complete Quality Control traversal in the fixed order SSC → Full → Prompt-Realized. `CORRECTIONS_APPLIED` requires a new complete iteration from SSC; `NO_CORRECTIONS_NEEDED` completes Story Quality Control. The maximum is three iterations, after which any unresolved defect produces `NOT_APPROVED`.

### QC — Quality Control

The general Quality Control concept. Within the Story pipeline, SAQC is the aggregate Story-level process and VSSAQC is the per-artifact result.

### Obsolete hybrid forms

`VSSA-DB` and `VSSA-QC` are obsolete or ambiguous. Use `VSSADB` for creation blueprints, `VSSA-QC-I` for review instructions and `VSSAQC` for materialized Quality results.

## Workflow terminology

### WF — Workflow

The project prefix for an active ComfyUI workflow responsibility.

- **WF-1-A:** Text-to-image reference production; exactly one generated reference image per run.
- **WF-1-B:** Image-to-image reference edit; exactly one external reference image in and one edited image out.
- **WF-2-A:** Reference-guided image-to-image keyframe production; START, MID and END from an external reference.
- **WF-2-B:** Pure text-to-image keyframe production; START, MID and END without an external reference image.
- **WF-3:** Image-to-video segment production from one START/MID/END triplet.
- **WF-4:** Non-generative video-to-video chronological assembly of approved WF-3 segments.
- **WF-5:** Video-to-video restoration and upscale.

### T2I — Text-to-Image

Image generation from text without an external source image. Used by WF-1-A and WF-2-B.

### I2I — Image-to-Image

Image generation or editing conditioned by an input image. Used by WF-1-B and WF-2-A.

### I2V — Image-to-Video

Video generation conditioned by one or more images. Used by WF-3.

### FLF2V — First/Last-Frame-to-Video

An I2V form conditioned by boundary frames. In WF-3, the START/MID/END triplet forms the chronological intervals START→MID and MID→END.

### V2V — Video-to-Video

Video processing whose input and output are video. Used by WF-4 assembly and WF-5 restoration/upscale.

## Integration terminology

### MCP — Model Context Protocol

The protocol boundary used by the standby Story agent to expose controlled project operations. MCP is not exposed to the active PG-1 no-tools agent.

### LLM — Large Language Model

The general model category used for conversational, generative and semantic-review responsibilities. Deterministic validation and persistence remain owned by project code rather than by the LLM.
