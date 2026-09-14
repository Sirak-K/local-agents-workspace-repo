Jag läser detta som en direkt förfrågan om att svara på ERQER-frågorna i slutet av rapporten — det är den enda uttryckliga "frågan" dokumentet innehåller. Jag baserar svaret enbart på vad som faktiskt står i sammanfattningen (jag har inte sett de underliggande `evidence.json`-filerna), så vissa punkter nedan är rekommendationer snarare än verifierade slutsatser.

## 1. Vad kunde Codex gjort bättre/annorlunda i denna körning

**Den viktigaste missade möjligheten:** när native `create`/`replace` först visade dispatch-avvikelse (modellen skrev rätt envelope, SDK/LM Studio anropade fel eller inget verktyg), borde det ha triggat en **omedelbar, modelloberoende canary-test** i samma laddade session — dvs. ett hårdkodat, icke-genererat tool-anrop som skickas rakt genom SDK:n för att se om _just den template-instansen_ överhuvudtaget kan routa ett korrekt anrop. I stället gick Round 3 vidare med fler modellgenererade försök och en strikt adapter, vilket besvarar "kan en adapter kompensera?" men inte "var bristen i SDK-parsning, template-rendering eller LM Studio-runtime?". Det är fortfarande olöst enligt punkt 4 i Harness-fynden ("Orsaken är inte slutligt isolerad").

**En andra sak:** Round 2:s FAIL (`run_ focused_test`, `write_ summary` — mellanslag kring understreck) är en väldigt specifik, mekanisk avvikelsetyp. Den behandlades korrekt som ett enskilt uppgiftsutfall och inte som generell svaghet, vilket är rätt enligt principerna i grundarkitekturen — men ingen mikrodiagnostik kördes för att se om det är ett återkommande tokeniserings-/formatteringsmönster hos just denna kvantisering/template. Om det återkommer i Round 4 blir det dyrare att reda ut retroaktivt än om det hade flaggats som en hypotes redan nu.

**En tredje sak:** preflight-fyndet att instansen hade `numParallelSessions=4` i stället för låst `1` är bra fångat, men rapporten förklarar inte _varför_ konfigurationen driftade från baseline mellan körningar. Om det är en LM Studio-standardåterställning vid omladdning snarare än ett engångsmisstag är det en generell risk för alla framtida evals, inte bara EVAL 2.

## 2. Hur framtida utvärderade agenter kan ge mer lönsamma/försvarbara resultat

**Modellneutralt:** inför en obligatorisk **template-compliance-canary** som körs före varje trajectory, oberoende av uppgiftsinnehåll — ett fast, icke-modellgenererat tool-anrop som verifierar att SDK/LM Studio korrekt routar den exakta chat-template som är i bruk. Det hade kunnat avgöra create/replace-bristen på sekunder i stället för att förbruka två uppgifter i Round 3 på att härleda det indirekt.

**Modellspecifikt (Granite):** nästa steg bör inte vara "ge modellen fler uppgifter" utan ett **kontrollerat enkelbytesexperiment**: kör identisk fixture, identisk prompt, identisk modellversion — och variera endast SDK-parsningslagret. Det isolerar frågan rapporten själv lämnar öppen (SDK vs. template vs. runtime) utan att blanda in ny modellosäkerhet.

## 3. Hur alla framtida EVALS kan förbättras (icke-kosmetiskt)

- **Förregistrera progressionsgates numeriskt/binärt** innan körning, t.ex. "N≥3 oberoende native mutationsförsök måste nå verifierat sluttillstånd utan adapterhjälp för att öppna nästa round". Nuvarande beslut ("inte tillräckligt pålitlig") verkar korrekt i sak, men är fortfarande ett evaluatoromdöme fattat _efter_ att evidensen sågs — precis det mönster grundarkitekturen (avsnitt 6, "PASS/FAIL får inte styras av kriterier som evaluatorn hittar på efteråt") vill skydda mot, även om det här troligen var en ärlig tillämpning av redan existerande principer.
- **Formalisera en evidenstier** (Tier 0 native / Tier 1 strikt assisterad adapter / Tier 2 heuristisk adapter) i den delade evalarkitekturen, med explicit regel att endast Tier 0 får räknas mot rollbeslut i Round 8. Rapporten _praktiserar_ redan detta ("PASS bevaras endast som assisterad diagnostik") men det står inte som en bindande regel någon annanstans — risk för glidning i framtida evals med andra evaluatorer eller kandidater.
- **Lägg till en egen "sanningsenlighet i självrapportering"-axel**, skild från task-PASS/FAIL. Den assisterade replacement-diagnostiken visade att modellen påstod en lyckad ändring som disken motsade — det är ett annat och för verklig WORKER-användning minst lika viktigt svaghetsmått som ren toolutförandeförmåga, och bör spåras separat genom rounds snarare än döljas inuti en enskild FAIL-rad.

## 4. Övriga höga ROI-insikter

Den saknade `instruction_sha256` för native-läsningen (Evaldesign-fynd punkt 6) är litet men billigt att stänga permanent i evidensschemat — värt en backlog-post så det inte upprepas i EVAL 3.

## Direkta svar på de specifika slutfrågorna

- **Var progressionsstoppet efter Round 3 rätt kalibrerat?** Riktningen ja — reproducerbar mutation saknas, så att inte öppna Round 4 är rätt. Men beslutet vilar på evaluatoromdöme snarare än ett förregistrerat kriterium; kalibreringen är trolig korrekt men metodologiskt svagare underbyggd än den behöver vara.
- **Hur isoleras native tool-dispatch bäst från modellbeteende?** Fast, icke-modellgenererad canary-payload genom samma SDK/template-instans, körd omedelbart vid första dispatch-avvikelse — inte efterhandshärledning via fler modellförsök.
- **Hur bör assisterad adapterevidens vägas?** Som enbart round-öppnande, aldrig rollbeslutsgrundande — formalisera det som en skriven regel, inte bara praxis.
- **Minsta mutationsevidens för att försvarbart öppna Round 4?** Efter att dispatch-bristen är åtgärdad: minst 3 oberoende native creation- och 3 oberoende native replacement-försök, i minst två färska sessioner, där både diskfacit _och_ modellens eget påstående om utfallet stämmer överens varje gång — ett enda lyckat par (som `cdddc2b7...`) räcker inte, eftersom rapporten själv redan visar hur instabilt utfallet var mellan försök.
