# AGPR-4 VOICE MASTER — MODEL FACTS

Status: Verifierade kandidatfakta. Ingen modell är vald eller installerad genom detta dokument.

| Kandidat | Verifierad relevant kapacitet | Måste fortfarande bevisas lokalt |
|---|---|---|
| Dia 1.6B | English; audio conditioning/voice cloning; officiella cues inkluderar bland annat `(laughs)` och `(screams)`; officiellt cirka 4,4 GB VRAM i BF16/FP16 på RTX 4090. | Female-presets, röststabilitet, faktisk 3070 Ti-prestanda, unrestricted-text och cue-träffsäkerhet. |
| Dia2-1B / Dia2-2B | English; streamingarkitektur; prefix-conditioning; 1B/2B; upp till två minuters generation; officiell CUDA 12.8+-väg. | VRAM på 8 GB, kvinnlig röstkvalitet, komplett icke-verbal vokabulär, skrik, seed/retry och stabil lång narration. |
| Chatterbox Turbo | English; 350M; låg compute/VRAM relativt större modeller; referensröst; officiellt stödda cues inkluderar `[laugh]`, `[chuckle]`, `[cough]`, `[sigh]` och `[gasp]`. | Högintensivt skrik saknar verifierad officiell cue; långform, unrestricted-text, röststabilitet och uttryckskontroll måste A/B-testas. |

Ingen kandidat är vald baseline enbart genom dokumenterad featurelista. Dia 1.6B har starkast verifierat cue-stöd för exakt skratt + skrik; Dia2 har starkare dokumenterad streaming/längd; Chatterbox Turbo är en hög-ROI lågkostnadskandidat på 8 GB. Resultatkvalitet och praktisk stabilitet avgör.

## Primärkällor

- Nari Labs Dia: https://github.com/nari-labs/dia
- Nari Labs Dia2: https://github.com/nari-labs/dia2
- Dia2-1B: https://huggingface.co/nari-labs/Dia2-1B
- Dia2-2B: https://huggingface.co/nari-labs/Dia2-2B
- Resemble AI Chatterbox: https://github.com/resemble-ai/chatterbox
