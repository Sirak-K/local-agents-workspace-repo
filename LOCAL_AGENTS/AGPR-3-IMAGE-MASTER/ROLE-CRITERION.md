# AGPR-3 IMAGE MASTER — ROLE CRITERION

Status: Rollspecifika beslut och en vald första kvalificeringskandidat. Slutlig generator, eventuell director, runtime och SillyTavern-integration låses först efter lokal gate.

## Låst mål

AGPR-3 Image Master ska vara en separat, smal bildprofil för snabb instruktion, bildgenerering och iterativ justering. Bilden ska sparas som en beständig fil. Maximal produktionskvalitet via dedikerade ComfyUI-workflows är ett separat senare arbetsflöde och får inte blockera den snabba baselinen.

Captioning är en sekundär hjälpfunktion och får inte styra den första implementationens arkitektur. Befintlig captioning och lokal JoyCaption-installation är tillräckliga utgångspunkter tills faktisk användning visar ett tydligt gap.

## Första kvalificeringsväg

- SANA-Sprint 0.6B 1024px är första generatorn som ska kvalificeras, inte slutligt fryst vinnare.
- Första walking skeleton går direkt från en strukturerad bildinstruktion till generator och beständig bildfil. En director får inte införas innan direktvägen visar ett konkret tolknings- eller revisionsgap.
- Generatorn ska förbli process-/RAM-resident under en aktiv AGPR-3-session så att senare iterationer inte laddar om modellvikter från disk. Full permanent VRAM-residency är inte ett krav; kontrollerad offload är tillåten om varm latens är acceptabel.
- Om en director senare A/B-testas måste den ge tydligt bättre instruktionsefterlevnad än direktvägen och fortfarande klara 8 GB-budgeten. Annars elimineras directoransvaret ur baselinen.
- Unified text+image-modeller blir kandidater först när de kan visa stabilare eller enklare faktisk drift än ett separerat director+generator-paket.

Kandidaten blir låst runtime först efter ett lokalt bevis utan OOM och utan modellomladdning mellan minst två bilditerationer.

## Ansvarsgränser

- Om en director blir motiverad äger den tolkning och promptförfining; den äger inte diffusionruntime eller bildfilskrivning.
- Generatoradaptern äger modellinput, generation settings, seed, bildgenerering och beständig outputfil.
- En framtida orkestrerare får äga laddning/avlastning av hela AGPR-3-paketet. Generatoradaptern ska inte samtidigt bli generell profilmanager.
- En framtida SillyTavern-yta får äga trigger och presentation. Inline-visning är önskvärd men inte ett baselinekrav; en korrekt sparad bildfil räcker för första walking skeleton.
- Högkvalitativa ComfyUI-workflows behåller sina egna modeller, prompts och outputkontrakt och ska inte pressas in i chatprofilens snabba runtime.

## Acceptansgates för första walking skeleton

- En initial sessionstart får ladda generatorn en gång.
- Team Master kan ge en bildinstruktion och få exakt en beständig bildfil.
- En uppföljande justering använder samma residenta session och producerar en ny bildfil utan att någon modellvikt laddas om från disk.
- Den effektiva generatorpromptens förändring är spårbar till användarens justering.
- Modellversioner, prompt, seed, dimensioner, steg/sampler, generationstid, total instruktion-till-fil-tid och peak VRAM loggas bounded per iteration.
- Två konsekutiva iterationer klarar 8 GB-GPU:n utan OOM, okontrollerad processökning eller samtidig residency med andra AGPR-profiler.
- Bildkvaliteten behöver vara tillräcklig för snabb chatiteration; den jämförs inte mot separata high-end ComfyUI-workflows i baselinegaten.

## Inte låst

- om en director alls behövs och i så fall modell/storlek,
- om SANA-Sprint 0.6B passerar som slutlig generator,
- exakt CPU/GPU-residency och offloadstrategi,
- generatorserver, CLI eller API,
- maskinläsbart request-/responseschema,
- automatisk AGPR-växling,
- inline-visning eller egen SillyTavern-extension,
- högkvalitativ ComfyUI-integration.
