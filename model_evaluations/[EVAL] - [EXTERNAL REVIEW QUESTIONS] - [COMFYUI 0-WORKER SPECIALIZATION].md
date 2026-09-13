# External Review Questions — ComfyUI 0-WORKER Specialization

## Syfte

Detta dokument ska vidarebefordras till externa Frontier-reviewers. Målet är att få den mest beslutskraftiga informationen för att göra senare ComfyUI-specifika 0-WORKER-evals verklighetsnära, rättvisa, säkra och metodiskt försvarbara utan kosmetisk process eller facitläckage.

## Låst projektavsikt

- Tidiga evalfaser mäter teknologioberoende instruktion-, fil- och toolförmåga.
- `0-WORKER`-rollens absolut viktigaste och primära slutmål är professionellt, precist, välstrukturerat och verifierbart arbete i `comfy_ui_workspace`, främst att förstå, skapa, redigera, felsöka och kvalitetssäkra ComfyUI workflow-JSON. Den senare evalhalvan ska pröva just detta huvudmål.
- `model_evaluations/comfy_ui_eval-playground/workflows/` innehåller disponibla kopior. Kandidaten får kreativt arbeta med noder och länkar i unika per-ERST-kopior men får inte ändra produktionsworkflows.
- Kandidaten ska inte behöva ladda Team Masters ComfyUI-modeller/checkpoints, köa prompts eller starta bild-/videogenerering. Primärt facit är workflowets verifierade statiska slutläge, scope och diff.
- Relevant ComfyUI-konditionering är tillåten och förväntad i domänfasen, men samma semantiska modellneutrala paket ska provas före modellspecifika anpassningar.
- UI-workflow-JSON och backendens API prompt är olika artefakter. De får inte bedömas som om de hade samma struktur eller ansvar.

## Verifierade lokala förutsättningar

- Playgrounden innehåller flera verkliga UI-workflows i legacy schemaformat v0.4 med olika storlek och grafkomplexitet.
- Materialet innehåller både vanliga nodtyper och workflowstrukturer med subgrafer/projektspecifika nodtyper.
- En kopierad workflowfil är inte en komplett eller reproducerbar ComfyUI-runtime: nodimplementationer, frontend/backendversioner, modeller och övriga beroenden kan saknas eller drifta.
- Därför ska första ComfyUI-evalerna vara statiska workflow-/grafuppgifter, inte körbarhets- eller bildkvalitetstester.

## Obligatoriska frågor till reviewern

1. Vilket minsta ComfyUI-kontextpaket måste en lokal 3B WORKER få för att UI-workflow-redigering ska bli en rättvis domänmätning utan att lösningen eller graderfacit läcks?
2. Bör UI-workflow v0.4 och API prompt-format testas som två separata förmågor? Vilken av dem bör komma först när Team Masters huvudsakliga arbetsmaterial är UI-workflows?
3. Vilken helt statisk verifieringskedja ger starkast bevis för korrekt workflowarbete utan att ladda modeller eller köra GPU-generering?
4. Hur bör nodkontrakt begränsas till endast den aktuella fixturens berörda nodtyper så att en 3B-modell får nödvändiga fakta utan en överstor nodinventering?
5. Vilka versions- och ursprungsfält måste bindas i varje fixturemanifest för att ett resultat ska vara reproducerbart trots ComfyUI-, frontend- och custom-node-drift?
6. Hur bör graders verifiera node-id:n, link-id:n, slot-index, referenser, subgrafer, UUID-baserade nodtyper och `widgets_values` utan att felaktigt anta semantik som endast runtime känner till?
7. Hur utformas held-out ComfyUI-roadmaps som verkligen mäter workflow-/conditioningförståelse och inte bara generell JSON-redigering eller kopiering av ett närliggande svar?
8. Hur jämförs conditioned och unconditioned ComfyUI-prestation kausalt utan att samtidigt ändra System Prompt, uppgift, tools, fixture, sampling eller andra villkor?
9. När är en Granite-specifik presentations-/formatadapter metodiskt berättigad, och vilka kontroller krävs för att dess resultat inte felrapporteras som generell modellförmåga?
10. Vilka tre ComfyUI roadmap-ERST ger högst beslutsvärde för om agentinstallationen är värd att använda i Team Masters dagliga och regelbundna 0-WORKER-arbete? Den sista är tänkt att låta kandidaten skapa ett helt nytt strukturellt intakt UI-workflow från en låst palett av redan installerade/visade nodtyper, med generös bedömning av semantik och kosmetik men utan kritiska strukturfel; hur bör dess minimala PASS-kontrakt se ut?
11. Vilken exakt kompetensgräns bör skilja projektlokal workflow-/integrationsspecialist från utvecklare av upstream ComfyUI core, och hur kan evalen bevisa rätt nivå utan att bredda rollen ineffektivt?
12. Vad är den enda konkreta förberedelsen som, om den görs först, gör flest andra ComfyUI-evalförberedelser enklare eller onödiga?

## Önskat svarsformat

Reviewern bör prioritera endast höga eller mycket höga ROI-förändringar och svara i denna ordning:

1. Rekommenderat beslut och kort motivering.
2. Minsta obligatoriska kontext före första ComfyUI-ERST.
3. Minsta reproducerbara sandbox-/fixturekontrakt.
4. Tre rekommenderade ComfyUI-ERST i stigande svårighetsgrad med verifierbart facit; bedöm särskilt den föreslagna introduktionsuppgiften att döpa om exakt angivna noder utan andra förändringar.
5. Vad som uttryckligen inte bör byggas, injiceras eller testas ännu.
6. `The ONE Thing`: exakt en konkret nästa förberedelse.
7. Kända osäkerheter och vilka primärkällor eller experiment som kan lösa dem.
