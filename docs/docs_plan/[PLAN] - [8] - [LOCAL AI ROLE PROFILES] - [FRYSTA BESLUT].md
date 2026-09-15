# LOCAL AI ROLE PROFILES — FRYSTA BESLUT

## Produkt- och plattformsgräns

- Slutmålet är lokalt hostade AI-profiler där Storyteller är den primära personliga chattagenten och Image Master/Voice Master har snäva mediaansvar.
- SillyTavern är minsta gemensamma UI och KoboldCpp är minsta gemensamma text-/konversationsmotor. De ersätts endast vid mycket hög verifierad ROI.
- `TAR` (`Target Agentic Role`) är en separat agentprofil och/eller modellprofil. En TAR behöver inte vara konverserande. TAR-identiteten är inte samma sak som en process, endpoint, modellfil eller inferensmotor.
- I SillyTavern får Team Master interagera med maximalt en individuell modell/agent-karaktär åt gången. Samtidig multi-agentorkestrering och parallella aktiva TAR-profiler ingår inte i produktkravet.
- Inaktiva TAR-profiler får vara helt avlastade från GPU och RAM. Profilbyte ska vara explicit, sekventiellt och reproducerbart genom `stop/unload → load → connect/select`; samtidig modellresidency och automatisk hot-swap är inte grundkrav.

## Fastställda TAR-profiler

- TAR-1 är `Storyteller`: primär och normalt vald profil för chatting and creating stories. DefiantFable Q4_K_S är nuvarande minimimodell och den befintliga F16-mmproj-filen är nuvarande visionkomponent.
- TAR-2 är `Image Master`: smal profil för captioning och/eller generating. Modell- och motorkontrakt är inte beslutade.
- TAR-3 är `Voice Master`: i sin primitiva form en smal ljudgenererings-/TTS-profil för emotionell novel narration. Den behöver inte kunna chatta. Realistisk icke-verbal kommunikation och chatt med samma narrativa röstidentitet är möjliga senare utökningar, inte första implementationens minimikrav.
- En TAR får definiera flera modell-/mediekomponenter när rollens kapacitet kräver det. De behöver inte vara residenta eller köras samtidigt; 8 GB VRAM-budgeten får hanteras genom sekventiell avlastning och laddning inom den valda TAR-profilens arbetsflöde.

## Implementations- och ägargräns

- TAR-1 är den enda aktiva implementationsprofilen tills dess stabila rekommenderade profil och återställningsväg har verifierats.
- Gemensam profilarkitektur ska härledas från TAR-1:s bevisade vertikala implementation; Storyteller-specifika harnessfiler får inte bli permanent ägare för alla TAR-profiler.
- Exakt persistent profilformat, loggschema och mediamotorgräns är ännu inte låsta runtimekontrakt.
- TAR-2:s captioning och bildgenerering får separeras i olika modell-/motorprofiler om faktisk evidens visar att det ger högre nytta.
- TAR-3:s första vertikala implementation ska kunna vara ren text-till-tal-/ljudfilsgenerering. Om chatt/personlighet senare läggs till får den och ljudsyntesen vara separata tekniska komponenter inom samma TAR-profil; en gemensam narrativ identitet kräver inte att en enda modell utför båda funktionerna.
- Image Captioning-hardening, generella extensions och ComfyUI förblir lågprioriterade tills Team Master ändrar ordningen.

## Kvalitetsmål

- Profiler ska optimera flexibilitet, reproducerbarhet, långsiktig stabilitet och maximal realistisk prestanda.
- Loggning ska vara omfattande men bounded, integritetsmedveten och uppdelad efter faktisk plattform-/motorägare.
- En generell SillyTavern-extensionmall skapas först från en konkret fungerande extension, inte som spekulativ supportarkitektur.
