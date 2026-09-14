# Extern beslutsgranskning — nästa praktiskt lönsamma WORKER-eval

## Uppdrag till extern Frontier

Hjälp Team Master och Codex välja **ett nästa steg som ändrar ett praktiskt installationsbeslut**, inte ännu en serie oklara FAIL. Detta dokument kan användas som hela frågeställningen. Rekommendationerna är granskningsunderlag, inte nya låsta projektbeslut. Ingen implementation eller körning efterfrågas av reviewern.

Projektets slutmål är en lokal 0-WORKER som tillförlitligt förstår, skapar, redigerar och verifierar Team Masters ComfyUI workflow-JSON. Grundläggande instruktion-/read/write-/toolförmåga prövas först; senare uppgifter använder disponibla kopior av verkliga workflows. Ingen checkpointladdning, bildgenerering eller kandidatskapad shell/kodexekvering behövs för dessa prov.

## Minsta relevanta faktaunderlag

- LM Studio Desktop är enda aktiva harness. Native REST v1 används för inventory/observability; officiell JavaScript-SDK 1.5.0 med godkänd auth-anpassning används för avbrytbar generering. Granites lokala kandidat är 4.1 3B Q4_K_M, 8192 laddad kontext och en samtidig prediction.
- Första verktygsfria screeningens tre uppgifter klarades enligt sina låsta kriterier. Det bevisar inte generell WORKER-förmåga. EVAL 2 innehöll en lyckad native SDK-read och en separat strikt adapter-assisterad creation, men ingen lyckad replacement. Exakta historiska projektkällor för EVAL 2 kan inte rekonstrueras från tillgängliga Git-blobs.
- EVAL 3 gav ingen lyckad native read/create/replace och blockerade senare rounds. Oklara uppgifts- eller dispatchfel bedöms inte som bevisade modellbrister eller bevisade backendbuggar.
- EVAL 4 körde exakt tre native read-diagnostikförsök: samma sparade instruktion, schema, fixture, source-set, avlästa konfiguration och laddade instans; färsk Chat varje gång, temperatur 0, max 512 outputtokens. Alla avslutades naturligt med `eosFound`, noll completed/active tools och oförändrad fixture. Ingen efterfrågad filinformation levererades.
- Fångad vanlig text: försök 1 gav `<tool_call>{` följt av JSON med `name=read_workspace_text` och `arguments.path=project/config/service.json`, men ingen avslutande envelope-tag. Försök 2 och 3 gav samma textbytes: `<tool_call>{` följt av enbart ett `path`-objekt och ingen avslutande tag. Försök 1 skilde sig vid teckenposition 16, alltså JSON-fältet `name` respektive `path` efter gemensamt prefix. Fragmenten rekonstruerar sluttexten; fragment är inte verifierade enskilda tokens. Temperatur 0 antas inte garantera determinism och faktisk trunkering är inte bevisad.
- Ingen av de publika SDK-toolrequest-callbacks nåddes i EVAL 4: start, namn, argumentfragment, parsed, finalized, failure eller dequeue. Ingen guard, handler eller receipt nåddes. Ingen publik text-till-native-parser-injektionshook är verifierad.
- Efterföljande **no-generation**-inspektion genom offentlig `applyPromptTemplate(chat, {toolDefinitions})` renderade den sparade instruktionen och det sparade effektiva tool-schemat. Renderingen innehöll rätt toolnamn/schema och full `name`/`arguments`/avslutande tag-vägledning. Tokenantalet var 255, som tidigare rapporterat. Detta är inte retroaktiv capture av den interna `.act()`-requesten; lika tokenantal bevisar inte lika inputbytes.
- Ingen projektägd WORKER-systemprompt/rollfil användes i read-serien. Tool-schema och template-genererad systemvägledning fanns däremot: detta är **inte** ett helt okonditionerat eller kontextfritt prov. Projektet tillåter kontrollerad roll-/interface-/domänkonditionering efter första screening.
- Bounded deterministisk tool-dispatch, read/write-scope, atomisk hashvillkorad mutation, readback, statisk validator och avbrott har separata verifieringar. Det bevisar toolimplementationernas kontroll, inte att Granite kan be om och använda dem. Kandidatens textbegäran får aldrig räknas som faktisk tool-exekvering.
- Codex införde därefter en gate: ordinarie kandidat-toolrunners kräver tre lyckade **kandidatstyrda** native reads under samma instans, oförändrade källor/runtime och högst 30 min reviewålder. Explicita bounded diagnostiklägen är separata. Denna gate ska ifrågasättas i granskningen; dess trösklar är inte statistiskt bevisad modellstandard eller oberoende modellneutral harnesskontroll.
- Begäransspecifikt avbrott och verkligt tool-/processstopp, skyddad skrivscope och oberoende readback är nödvändiga. Ingen annan harness, anonym auth-fallback, heuristisk argumentreparation eller borttagning av säkerhetsgränser föreslås. Modellen och servern är nu stoppade.

## Högst prioriterade frågor

### ONE Thing att pröva i granskningen — inte ett fryst beslut

**Bestäm vilket minsta leveransinterface som får räknas som ett användbart delmål utan att förväxlas med autonom 0-WORKER.** Måste nästa prov mäta självständig native toolanvändning, eller är ett separat prov av korrekt workflow-redigering med tillhandahållen filkontext också beslutsvärdefullt? Detta avgör vilka gates som faktiskt hör till uppgiften och om mer native dispatchfelsökning behöver föregå just det provet. Slutlig autonom read/write-rollkvalificering får inte tas bort.

En underagent rekommenderade att granska en **övervakad, schema-baserad workflow-editor** som alternativt delprov: modellen väljer ändringarna, levererar maskinvaliderbar ändringsdata och evaluatorns fasta mekanism applicerar den på en sandboxkopia utan semantisk reparation. SDK `.respond()` med Zod/JSON Schema är dokumenterat; constrained output är inte en parserinjektionshook och bevisar inte korrekt nodval. Fullständigt lyckad generering behövs för schemaöverensstämmelse; tokenlimit/avbrott kan ge ogiltigt svar. [Officiell Structured Response](https://lmstudio.ai/docs/typescript/llm-prediction/structured-response).

Detta alternativ är **inte implementerat, inte lokalt prestationsverifierat och inte valt**. Det återanvänder samma LM Studio-harness men förändrar mätobjekt och vem som läser/applicerar filen. Det får inte räknas som faktisk kandidat-toolanvändning, godkänd senare evalfas eller autonom WORKER. Eventuell separat ComfyUI-diagnostik före full toolkvalificering behöver ett explicit avgränsat beslut, inte en tyst fas-/gateförändring. De tre native-readkraven gäller i dag berörda toolrunners, inte redan alla tools-free körningar; frågan gäller deras sakliga ansvar och framtida tillämpning, inte ett påstående att tools-free vägen redan är blockerad.

### 1. Vilken information ändrar nästa praktiska beslut mest?

Välj exakt en viktigast kvarvarande informationslucka. Behöver vi främst avgöra om Granite kan göra användbart arbete med en tydlig deklarerad WORKER-/toolinstallation, verifiera en konkret presentations-/transportskillnad, eller något annat? Motivera mot ovanstående evidens. Ange vad varje möjligt utfall faktiskt får oss att göra annorlunda. Om ingen ny generering är värd kostnaden just nu, säg vilket viktigare arbete som kommer först.

Bedöm uttryckligen underagentens alternativa delprov ovan: ger det verkligt värde mot Team Masters slutmål, eller riskerar det att ersätta nödvändig autonom read/write med en annan enklare uppgift? Reviewer ska inte anta att det senare interfacet redan är godkänt.

### 2. Har Codex skapat en felriktad eller cirkulär startgate?

Skilj oberoende harness-/tool-/scope-/stoppkontroll från kandidatens native toolkompatibilitet och praktiska prestation. Är tre lyckade reads från samma kandidat och 30 min reviewålder proportionerliga, eller riskerar de att blockera just den användbara konditionerade förmåga som bör prövas? Föreslå den minsta eventuella korrigeringen och vilket verkligt säkerhets-/evidensbevis som måste kvarstå. Undvik både fler godtyckliga trösklar och att släppa igenom en uppgift utan faktisk exekvering.

### 3. Är mer konditionering en motiverad intervention — eller bara ännu ett hopp om PASS?

Toolnamn/schema och full envelopevägledning finns redan i den publika renderingen. Vilket specifikt ytterligare interface-/rollinnehåll skulle då ge ny beslutbar information? Om ett sådant prov rekommenderas: ange minsta exakta engelska instruktion/systemtext, meddelanderoll och vilken enda axel som ändras. Inga kända filvärden, uppgiftsfacit eller prompttweak-loopar. Ange hur utfallet avgränsas som konditionerad installationsförmåga, inte retroaktiv baselineframgång. Om ändringen saknar tillräcklig grund, rekommendera något annat uttryckligen.

### 4. Vilken dokumenterat möjlig väg inom LM Studio ger bäst praktisk avkastning?

Jämför högst två relevanta alternativ: nuvarande SDK `.act()` med deklarerad konditionering, befintlig strikt Granite-adapter eller annan konkret offentlig LM Studio-väg. Ge ingen katalog av möjligheter. Kan alternativet återanvända samma tools, isolering, verifiering och begäransspecifika stoppbevis? Markera vad som är dokumenterat, lokalt verifierat respektive oprövat. Förklara om en alternativ väg ändrar mätobjektet och vad vi i så fall får och inte får dra slutsatser om. REST-streamstängning får inte antas bevisa serverstopp.

Om schema-baserad `.respond()` väljs som ett av alternativen, pröva användbarhet och stopp-/appliceringskrav explicit. Utgå inte från att befintlig tools-free runner redan stödjer denna nya requestform eller att ett schema säkerställer semantisk korrekthet.

### 5. Vilket enda nästa experiment bör vi faktiskt köra?

Utforma en liten end-to-end-slice som följer svaren ovan. Ange förutsättningar, en explicit intervention, uppgift, antal försök och motiverad tids-/tool-/filbudget; vilka tidigare fungerande beteenden som måste bevaras; oberoende framgångsbevis; avbrotts-/exitvillkor; samt nästa beslut för PASS, praktiskt FAIL och ogiltigt harnessutfall. Grundläggande faktisk toolanvändning måste verifieras innan svårare ComfyUI-arbete. Om du föreslår en introducerande workflow-title-ändring efter denna kontroll: kräv bara rätt titel, skyddat scope och preservation, inte generering, kreativ elegans eller kosmetiska sidokrav.

### 6. När ska vi sluta investera i denna kombination?

Ange en proportionerlig exitregel för fortsatt Granite-/LM Studio-kompatibilitetsarbete: vilket begränsat utfall räcker för att fortsätta mot verkligt workflowarbete, byta installationsväg eller återkomma till Team Master om kandidatval? Ingen fullständig intern kausal förklaring eller modellvikternas absoluta gräns behöver bevisas. Förklara vilka cache/GPU/kernel-/omladdningsstudier som faktiskt kan undvaras och vilken direkt beslutsnytta som skulle krävas för att ändå göra någon av dem.

## Önskat svar — kort och beslutsorienterat

1. Din ONE Thing i en mening, med konkret leverans/bevis som gör nästa arbete enklare eller onödigt.
2. Rekommenderat nästa steg och viktigaste alternativet som du avråder från, med evidensgrund.
3. Svar på de sex frågorna; prioritera verkliga ändringar framför generell evalmetodik.
4. Ett enda experimentkontrakt och beslut per utfall — eller ett motiverat besked att inte generera ännu.
5. Källor och tydlig separation mellan fakta, hypotes och kvarstående osäkerhet. Tekniska mekanismer/API-claims ska stödjas av aktuella primärkällor; inga gissade hooks eller kausala lagerförklaringar.

## Källmaterial vid behov

- Senaste sammanfattning och separat inspektion: `EVAL_4_2026-09-14-152322/[EVAL] - [EVAL_4_2026-09-14-152322] - [REPORT SUMMARY].md`.
- Modellneutral design: `[EVAL] - [ ARCH. ] - [Frontier-As-Evaluator] - [Design].md`.
- Nuvarande startgate: `../LOCAL_AGENTS/AGENT-0-WORKER/agent-0-eval/tool_transport_review.py`; lässerie: `tool_transport_reproducibility.py` i samma yta.
- [Officiell LM Studio .act()-dokumentation](https://lmstudio.ai/docs/typescript/agent/act). Installerad SDK 1.5.0 d.ts exponerar `LLMApplyPromptTemplateOpts.toolDefinitions`; observerad inspektionsscope finns i evalens originalartifact.

Ingen extern reviewer behöver ha lokal LM Studio-/Windowsåtkomst för att besvara frågorna. Lokal exekvering och faktisk verifiering ägs fortsatt av Codex. Läs inte andra agentroller eller breda historiska loggar för denna granskning.
