# LOCAL AI ROLE PROFILES — ROADMAP

| Steg | Arbetsmängd | Status | Systemplikt | Berörd Fil | Praktisk Impl. | Klarsignal |
|---:|---|---|---|---|---|---|
| 1 | Låg | Utförd | Lås AGPR-3/4:s verkliga rollansvar före runtimeval. | `LOCAL_AGENTS/` | Etablera rollkriterier, negativa gränser och leveransartefakter. | Image Master kräver bildfil; Voice Master kräver ljudfil; UI/broker är separata. |
| 2 | Låg | Utförd | Skilj primärkällfakta från brainstorming och modellval. | `AG-*-MODEL/` | Dokumentera minsta realistiska generator-/TTS-kandidater och lokala oklarheter. | Ingen kandidat presenteras som vald eller 8 GB-bevisad utan mätning. |
| 3 | Medel | Utförd | Behavior-first underlag före stora nedladdningar/körningar. | `LOCAL_AGENTS/` | Lägg små modellneutrala Image-/Voice-kvalificeringsfall under respektive profil och testa struktur/invarianter offline. | Samma input, seed, relativa artefakter och klarsignal kan återanvändas utan att bli runtime-API. |
| 4 | Hög | Pågår | Walking skeleton för prioriterad Image Master. | `AGPR-3-IMAGE-MASTER/` | Kvalificera SANA-Sprint 0.6B direkt: instruktion → bildfil → justering utan disk-reload; A/B-testa director endast vid konkret gap. | Två iterationer fungerar inom 8 GB och loggar prompt/seed/tid/VRAM. |
| 5 | Hög | Pågår | Walking skeleton för Voice Master. | `AGPR-4-VOICE-MASTER/` | Kvalificera Dia2-1B: annoterad English-text + kvinnligt referensklipp → ljudfil. | Female voice, skratt, skrik och styrbar prosodi klarar baselinegaten. |
| 6 | Medel | Ej påbörjad | Orkestrering först efter bevisade separata kärnor. | `LOCAL_AGENTS/` | Härled explicit load/unload/restore och profilval utan samtidig AGPR-drift. | Profilbyte är reproducerbart och kärnadaptrar äger inte orkestrering/UI. |
| 7 | Låg | Explicit uppskjuten | Integration ska följa faktisk nytta. | `SillyTavern_UI/` | Bedöm inline-presentation/extensions och ComfyUI-koppling efter kärn-PASS. | Endast verifierade användningsgap motiverar integration. |
