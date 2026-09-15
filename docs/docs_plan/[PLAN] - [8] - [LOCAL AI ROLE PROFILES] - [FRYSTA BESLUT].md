# LOCAL AI ROLE PROFILES — FRYSTA BESLUT

## Produkt- och plattformsgräns

- Slutmålet är lokalt hostade AI-profiler där Storyteller är den primära personliga chattagenten och Image Master/Voice Master har snäva mediaansvar.
- SillyTavern är minsta gemensamma UI och KoboldCpp är minsta gemensamma text-/konversationsmotor. De ersätts endast vid mycket hög verifierad ROI.
- `AGPR` (`Agent Profile`) är en separat agentprofil och/eller modellprofil. En AGPR behöver inte vara konverserande. AGPR-identiteten är inte samma sak som en process, endpoint, modellfil eller inferensmotor.
- I SillyTavern får Team Master interagera med maximalt en individuell modell/agent-karaktär åt gången. Samtidig multi-agentorkestrering och parallella aktiva AGPR-profiler ingår inte i produktkravet.
- Inaktiva AGPR-profiler får vara helt avlastade från GPU och RAM. Profilbyte ska vara explicit, sekventiellt och reproducerbart genom `stop/unload → load → connect/select`; samtidig modellresidency och automatisk hot-swap är inte grundkrav.

## Fastställda AGPR-profiler

- AGPR-2 är `Storyteller`: primär och normalt vald profil för chatting and creating stories. DefiantFable Q4_K_S är nuvarande minimimodell och den befintliga F16-mmproj-filen är nuvarande visionkomponent.
- AGPR-3 är `Image Master`: smal profil för snabb bildgenerering och iterativ justering. Captioning är sekundärt och får inte styra första implementationen.
- AGPR-4 är `Voice Master`: i sin primitiva form en smal ljudgenererings-/TTS-profil för emotionell novel narration. Den behöver inte kunna chatta; trovärdigt skratt och högintensivt skrik ingår däremot i första implementationens gate.
- En AGPR får definiera flera modell-/mediekomponenter när rollens kapacitet kräver det. De behöver inte vara residenta eller köras samtidigt; 8 GB VRAM-budgeten får hanteras genom sekventiell avlastning och laddning inom den valda AGPR-profilens arbetsflöde.

## Implementations- och ägargräns

- AGPR-3 Image Master och AGPR-4 Voice Master är nu aktiva implementationsprioriteter före återstående live/E2E- och prestandahärdning av AGPR-2. Storytellers fungerande baseline och återställningsväg ska bevaras medan dess avancerade promotion är pausad.
- Gemensam profilarkitektur ska härledas från AGPR-2:s bevisade vertikala implementation; Storyteller-specifika harnessfiler får inte bli permanent ägare för alla AGPR-profiler.
- Exakt persistent profilformat, loggschema och mediamotorgräns är ännu inte låsta runtimekontrakt.
- AGPR-3:s captioning och bildgenerering får separeras i olika modell-/motorprofiler om faktisk evidens visar att det ger högre nytta. En captionspecifik extension skapas endast om faktisk AGPR-3-användning visar ett kvarstående UI-/leveransgap.
- AGPR-3:s första walking-skeleton ska kvalificera SANA-Sprint 0.6B direkt: en instruktion producerar en beständig bildfil och en uppföljande justering producerar en ny fil utan modellomladdning från disk. En director införs endast om direktvägen visar ett konkret gap och A/B bevisar nettopositiv nytta inom 8 GB-budgeten.
- AGPR-3:s snabba chatbildkvalitet behöver vara tillräcklig för iterativ användning. Maximal produktionskvalitet i separata ComfyUI-workflows är ett annat senare arbetsflöde. Inline-visning är inte ett baselinekrav.
- AGPR-4:s första vertikala implementation ska kunna vara ren text-till-tal-/ljudfilsgenerering. Om chatt/personlighet senare läggs till får den och ljudsyntesen vara separata tekniska komponenter inom samma AGPR-profil; en gemensam narrativ identitet kräver inte att en enda modell utför båda funktionerna.
- AGPR-4:s första baseline ska återge engelsk fiktion lokalt utan extern leverantörsmoderering eller projektpålagt innehållsfilter, men modellens faktiska unrestricted-beteende måste evalueras och får inte antas av lokal drift ensam.
- AGPR-4 kräver trovärdigt skratt, högintensivt skrik, minst en reproducerbar kvinnlig röst och icke-monoton, flexibelt styrbar narration. Flera valbara kvinnliga röstidentiteter är önskad baseline när kvaliteten kan bevaras.
- Dia2-1B är AGPR-4:s första kvalificeringskandidat. Den blir inte fryst baseline förrän ett godkänt kvinnligt referensklipp och de rollägda acceptansfallen har bevisat röststabilitet, exakt textåtergivning, skratt, skrik och säker 8 GB-drift.
- Team Master och AGPR-2 Storyteller äger texten samt placeringen av performance cues. AGPR-4 validerar/renderar mottagna cues och får inte själv ändra berättelsens händelser. Modellbunden taggvokabulär får inte hårdkodas i Storytellers permanenta basprompt innan Voice Masters adapter-/modellkontrakt är valt.
- En beständig ljudfil är AGPR-4:s första leveranskontrakt. SillyTavern-spelare är inte ett baselinekrav. Broker/API, automatisk unload/load/restore och retry-semantik är separata ännu olåsta integrationsbeslut.
- Image Captioning-hardening, generella extensions och ComfyUI förblir lågprioriterade tills Team Master ändrar ordningen.

## Kvalitetsmål

- Profiler ska optimera flexibilitet, reproducerbarhet, långsiktig stabilitet och maximal realistisk prestanda.
- Loggning ska vara omfattande men bounded, integritetsmedveten och uppdelad efter faktisk plattform-/motorägare.
- En generell SillyTavern-extensionmall skapas först från en konkret fungerande extension, inte som spekulativ supportarkitektur.
