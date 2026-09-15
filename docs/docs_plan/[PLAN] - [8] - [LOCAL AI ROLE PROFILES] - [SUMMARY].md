# LOCAL AI ROLE PROFILES — SUMMARY

## Goal

Projektet ska leverera flexibla, lokalt hostade AI-profiler kring SillyTavern och i första hand KoboldCpp. Storyteller är den primära och normalt använda chattprofilen. Image Master och Voice Master är smala mediaprofiler och behöver inte vara konversationsagenter. Byte av SillyTavern eller KoboldCpp som huvudplattform kräver mycket hög verifierad ROI.

## AGPR-definition

`AGPR` betyder `Agent Profile` och är en separat valbar **agentprofil och/eller modellprofil**. En AGPR identifieras av sitt avsedda ansvar och sin reproducerbara konfiguration. Den behöver inte vara konverserande och måste inte ha en unik motor, process eller fysisk modellfil.

En AGPR kan binda de komponenter som dess roll behöver, exempelvis språkmodell, vision projector, system-/agentinstruktioner, template, samplers, kontext- och runtimeinställningar samt senare en separat mediamotor. Exakt persistent profilformat bestäms först genom respektive implementationsslice.

## Aktiveringsmodell

I SillyTavern interagerar Team Master med maximalt en individuell modell/agent-karaktär åt gången. Storyteller är normalt denna aktiva chattprofil. Smala mediajobb utförs sekventiellt genom vald Image Master- eller Voice Master-profil; samtidig multi-agentorkestrering, parallella agentkonversationer och samtidig GPU-residency är inte grundkrav.

Byte mellan AGPR-profiler ska vara explicit, sekventiellt och reproducerbart. Inaktiva AGPR-profiler får vara helt avlastade från GPU och RAM; deras sparade profiler finns kvar för senare val. Grundflödet är `stop/unload → load → connect/select`, inte samtidig drift eller automatisk hot-swap.

## Roller och prioritet

| AGPR | Roll | Minsta nuvarande modellval | Status |
|---|---|---|---|
| AGPR-2 | Storyteller — primär profil för chatt och berättelseskapande | DefiantFable Q4_K_S; mmproj F16 för redan fungerande vision | Aktiv P0 och normalt använd profil; grundchatten är smoke-testad, avancerad profil och prestanda härdas nu |
| AGPR-3 | Image Master — snabb bildgenerering och iterativ justering; captioning sekundärt | SANA-Sprint 0.6B är första kvalificeringskandidat; director installeras endast vid bevisat gap | Aktiv implementation; direkt generatorväg ska bevisa två varma iterationer inom 8 GB |
| AGPR-4 | Voice Master — smal English TTS-profil för kvinnlig, emotionell och icke-verbal novel narration | Dia2-1B är första kvalificeringskandidat; Dia 1.6B är endast reserv vid relevant FAIL | Aktiv implementation; Storyteller äger text/cue-placering och Voice Master ska bevisa ljudfil, röststabilitet, skratt och skrik |

## Tvärgående kvalitetsmål

- Maximal praktisk flexibilitet i SillyTavern- och AI-konfiguration.
- Reproducerbara, verifierade och enkelt valbara profiler.
- Maximal realistisk prestanda utan att offra stabilitet eller tidigare bevisad kvalitet.
- Omfattande men bounded, integritetsmedveten och ägarspecifik loggning.
- En återanvändbar SillyTavern-extensionmall först när en konkret extension-slice ger ett verkligt kontrakt att härleda mallen från.
- ComfyUI-koppling senare och uttryckligen lågprioriterad.

## Aktiv implementationsordning

AGPR-3 och AGPR-4 utvecklas nu före Storytellers återstående live/E2E- och prestandatester. Storytellers fungerande baseline bevaras. Mediaprofilerna behöver endast sina snäva ansvar och får laddas sekventiellt inom 8 GB-budgeten; de behöver inte dela Storytellers chattförmåga eller vara samtidigt aktiva med andra AGPR-profiler.

AGPR-4:s låsta minimum är lokal unrestricted English rendering, trovärdigt skratt och högintensivt skrik, minst en reproducerbar kvinnlig röst samt icke-monoton och flexibelt styrbar narration. Första leveransen är en beständig ljudfil. Inline-spelare är uttryckligen inte ett baselinekrav; broker/API och automatisk profilåtergång är separata framtida integrationsbeslut.
