Jag försökte hämta repot (`https://github.com/Sirak-K/local-agents-workspace-repo`) men fick ett 404 — troligen privat eller otillgängligt för mig. Svaret nedan bygger därför enbart på de fem projektdokumenten (arkitekturstate, Frontier-as-Evaluator-design, PFMIE-frysta beslut, Project Direction-frysta beslut, och själva frågedokumentet), vilket räcker för en substantiell granskning eftersom de redan låser det mesta av kontext, rounds och gates.

---

## 1. Rekommenderat beslut och kort motivering

**UI-workflow och API prompt ska testas separat, och UI-workflow går först.** Team Masters faktiska arbetsmaterial är UI-workflow-JSON, och ni har redan låst att de är olika artefakter med olika ansvar. Att testa API prompt-formatet först skulle mäta fel artefakt och riskera att en falsk transfer-slutsats dras (UI→API tappar strukturer som groups, `title` vs nodtyp, och `widgets_values`-ordning). Håll API prompt helt utanför scope tills UI-kompetens är bevisad — introducera det bara om Team Master uttryckligen utökar kontraktet, i linje med hur ni redan hanterar liknande utökningar.

**Granite-specifik adapter (fråga 9) är endast berättigad** när samma semantiska paket reproducerbart (flera seeds) misslyckas av rent format-/dispatch-skäl, adaptern ändrar bara presentation/dispatch (inga nya lösningsfakta), och rapporten uttryckligen märker resultatet "modell + scaffolding" snarare än ren modellförmåga — vilket redan är er egen regel, bara understruken här.

**Kompetensgränsen mot upstream ComfyUI-core (fråga 11):** gränsen bör dras vid _"ändrar/utökar grafer och projektlokal integrationskod med redan installerade nodtyper och dokumenterade lokala kontrakt"_ vs _"implementerar nya nodklasser, custom-node Python-backends eller ändrar ComfyUI:s kärn-dispatch/scheduler"_. Ingen ERST ska någonsin kräva att kandidaten skriver en ny nodklass eller kärn-backend-kod — det är strukturellt en annan roll och skulle bredda 0-WORKER ineffektivt.

## 2. Minsta obligatoriska kontext före första ComfyUI-ERST

Det paket ni redan planerat i PFMIE §7 är rätt avgränsat — jag ser inget att lägga till, bara att hålla det strikt:

- `comfyui_workflow_contract.md` — v0.4-strukturerna som faktiskt berörs (nodes, links, groups, ev. subgrafer), inte hela specen.
- `comfyui_project_contract.md` — lokala regler: vad som är redigerbart/skyddat, tillåtna nodtyper för uppgiften.
- `comfyui_mutation_verification.md` — proceduren snapshot → scoped mutation → parse/strukturkontroll → referensintegritet → diff → sluttillstånd.
- `comfyui_node_palette.json` — **uppgiftsreducerad**, endast de nodtyper aktuell fixture faktiskt berör (svar på fråga 4).
- `context_manifest.json` — version/hash/ursprung för varje ingående källa.

## 3. Minsta reproducerbara sandbox-/fixturekontrakt

- En unik kopia per muterande ERST, aldrig den delade playground-kopian.
- `fixture_manifest.json`: relativ aliaspath, ursprungshash + saneringshash, format/version, exakt tillåtna ändringar, bevarandekrav, relevant nodpalett-subset.
- Skyddade kontrollfiler + facit oåtkomliga genom kandidatens faktiskt exponerade tools — verifiera detta med en ofarlig läcka-kontroll **innan** första riktiga körning, och upprepa efter varje ändrad LM Studio-version eller tool-yta (redan er egen regel — bara att inte glömma bort den när ComfyUI-fasen börjar).
- Mutation kräver expected-before-hash, fil-/anrops-/skrivbudget, atomisk commit, oberoende efterkontroll; stopp före commit ska lämna originalfixturen orörd.
- Inga modeller/checkpoints laddas, ingen GPU-kö. PASS grundas uteslutande på statiskt verifierat slutläge.

## 4. Tre rekommenderade ComfyUI-ERST, stigande svårighet

**ERST-A (introduktion): döp om exakt namngivna noders synliga `title`, inga andra ändringar.**
Det här är en bra första uppgift — men av ett annat skäl än domänförståelse. Den mäter i praktiken _skalpellprecision_: klarar kandidaten att skilja `title` från `type`, node-id, "Node name for S&R" och `widgets_values`, och att lämna allt annat i den parsade JSON:en identiskt? Det är ett välkänt och lätt-graderbart felläge (fyra distinkta sätt att göra fel), kräver ingen nodsemantik, och ger er en ren strukturell disciplin-gate innan ni lägger på verklig grafförståelse. **Rekommendation: behåll den exakt som planerat, men rapportera den uttryckligen som en struktur-/precisionsgate — inte som bevis på ComfyUI-domänkompetens.** Full parsed-JSON-likhet utanför tillåtna paths är rätt facit; kalibrera mot fyra kända fel (fel titel, fel nod, ändrad type, oavsiktlig sidoeffekt på widget/länk).

**ERST-B: scoped feature-roadmap — lägg till/koppla en meningsfull nod/länk i ett befintligt workflow enligt avgränsad instruktion.** Facit: målnod/länk existerar, referensintegritet håller, resten av grafen är byte-/strukturellt orörd utanför tillåten path.

**ERST-C: bugfix-roadmap på avsiktligt skadat workflow.** Facit: fail-to-pass verifierat (den skadade egenskapen är reparerad) OCH tidigare fungerande egenskaper är bevarade — bägge krävs, inte bara en av dem.

Detta matchar redan er Round 6/7-design; jag ser ingen anledning att lägga till en fjärde mellanuppgift.

## 5. Vad som uttryckligen inte bör byggas, injiceras eller testas ännu

- API prompt-format (se punkt 1).
- Full nodinventering — endast uppgiftsreducerad palett.
- GPU-generering eller frontend-runtime-validering som PASS-krav (statisk verifiering räcker; frontend-öppning är i så fall en separat, uttryckligt avgränsad delclaim).
- Nya nodklasser/custom-node-backends — det är upstream-core, utanför rollen (fråga 11).
- Stora subgraf-tunga fixtures innan den enkla nod-/länk-fixturen är bevisat självvaliderande.
- Granite-specifik presentationsadapter innan reproducerbar, seed-stabil evidens finns för att felet är format snarare än förmåga.
- Round 8 (held-out slutaudition) innan Round 6–7 är godkända enligt era egna progressionsspärrar.

## 6. `The ONE Thing`

**Bygg och hash-bind det modellneutrala domänkontextpaketet (de fem filerna i punkt 2) samtidigt som ni validerar den första självvaliderande basfixturen (WF-1-A) i en enda bounded slice.** Detta är redan flaggat hos er som obligatorisk preflight-gate, och det är det enda steget som samtidigt löser upp svaren på frågorna om nodkontrakt-scope (4), versions-/ursprungsfält (5), och sandbox-kontrakt (punkt 3) — allt annat ComfyUI-arbete väntar på just detta.

## 7. Kända osäkerheter och vad som kan lösa dem

- **Frontend-/nodversionsdrift:** matchar er faktiskt installerade ComfyUI-frontend v0.4-specen exakt, eller finns lokal drift (custom nodes, UUID-baserade typer)? Löses endast genom verklig read-only inventory av den aktiva lokala miljön — inte genom att läsa dokumentationen. Ni har redan noterat detta ("installerade nodfakta kräver verklig read-only inventory"); det gäller specifikt de nodtyper som förekommer i WF-1-A.
- **`widgets_values`-semantik:** är ordningen rent positionell eller kopplad till nodens definierade widget-lista? Kan bara avgöras genom att faktiskt inspektera nodedefinitionerna för de nodtyper som fixturen berör — inte antas generellt.
- **Grading av UUID-baserade/okända nodtyper:** om nodedef saknas för en typ måste gradern hålla sig till strukturell välformning (id-unikhet, referensintegritet) och avstå från semantiska påståenden den inte kan bevisa. Löses genom att uttryckligen markera vilka nodtyper i paletten som har verifierad nodedef och vilka som bara är "visade".
- **Format- vs förmågefel hos Granite:** går inte att avgöra utan empirisk, seed-repeterad evidens från Round 6–7 med samma semantiska paket som andra kandidater — precis det experiment ni redan planerat, men det bör köras innan någon adapterdiskussion tas på allvar.
- **Läckageboundary under verklig tool-yta:** era graders/facit är bara bevisat oåtkomliga i teorin tills den ofarliga kontrollfils-testen faktiskt körts mot den riktiga exponerade tool-ytan — en dokumenterad regel utan körd verifiering är inte samma sak som en verifierad gräns.
