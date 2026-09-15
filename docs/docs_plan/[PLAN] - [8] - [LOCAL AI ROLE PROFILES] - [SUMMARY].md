# LOCAL AI ROLE PROFILES — SUMMARY

## Goal

Projektet ska leverera flexibla, lokalt hostade AI-profiler kring SillyTavern och i första hand KoboldCpp. Storyteller är den primära och normalt använda chattprofilen. Image Master och Voice Master är smala mediaprofiler och behöver inte vara konversationsagenter. Byte av SillyTavern eller KoboldCpp som huvudplattform kräver mycket hög verifierad ROI.

## TAR-definition

`TAR` betyder `Target Agentic Role` och är en separat valbar **agentprofil och/eller modellprofil**. En TAR identifieras av sitt avsedda ansvar och sin reproducerbara konfiguration. Den behöver inte vara konverserande och måste inte ha en unik motor, process eller fysisk modellfil.

En TAR kan binda de komponenter som dess roll behöver, exempelvis språkmodell, vision projector, system-/agentinstruktioner, template, samplers, kontext- och runtimeinställningar samt senare en separat mediamotor. Exakt persistent profilformat bestäms först genom respektive implementationsslice.

## Aktiveringsmodell

I SillyTavern interagerar Team Master med maximalt en individuell modell/agent-karaktär åt gången. Storyteller är normalt denna aktiva chattprofil. Smala mediajobb utförs sekventiellt genom vald Image Master- eller Voice Master-profil; samtidig multi-agentorkestrering, parallella agentkonversationer och samtidig GPU-residency är inte grundkrav.

Byte mellan TAR-profiler ska vara explicit, sekventiellt och reproducerbart. Inaktiva TAR-profiler får vara helt avlastade från GPU och RAM; deras sparade profiler finns kvar för senare val. Grundflödet är `stop/unload → load → connect/select`, inte samtidig drift eller automatisk hot-swap.

## Roller och prioritet

| TAR | Roll | Minsta nuvarande modellval | Status |
|---|---|---|---|
| TAR-1 | Storyteller — primär profil för chatt och berättelseskapande | DefiantFable Q4_K_S; mmproj F16 för redan fungerande vision | Aktiv P0 och normalt använd profil; grundchatten är smoke-testad, avancerad profil och prestanda härdas nu |
| TAR-2 | Image Master — smal profil för captioning och/eller bildgenerering | Inte beslutad | Fastställd framtida mediaprofil; implementation och modellval väntar |
| TAR-3 | Voice Master — initialt smal ljudgenererings-/TTS-profil för emotionell novel narration och senare önskad icke-verbal uttrycksförmåga | Inte beslutad | Fastställd framtida mediaprofil; chattförmåga är en möjlig avancerad utökning, inte primitivt krav |

## Tvärgående kvalitetsmål

- Maximal praktisk flexibilitet i SillyTavern- och AI-konfiguration.
- Reproducerbara, verifierade och enkelt valbara profiler.
- Maximal realistisk prestanda utan att offra stabilitet eller tidigare bevisad kvalitet.
- Omfattande men bounded, integritetsmedveten och ägarspecifik loggning.
- En återanvändbar SillyTavern-extensionmall först när en konkret extension-slice ger ett verkligt kontrakt att härleda mallen från.
- ComfyUI-koppling senare och uttryckligen lågprioriterad.

## Aktiv implementationsordning

TAR-1 färdigställs som första vertikala och normalt använda profil innan gemensamma profilmönster generaliseras eller TAR-2/TAR-3 implementeras. TAR-2 och TAR-3 behöver endast sina snäva mediaansvar. Deras modeller eller motorer får laddas och köras sekventiellt inom 8 GB VRAM-budgeten; de behöver inte dela Storytellers chattförmåga eller vara samtidigt residenta.
