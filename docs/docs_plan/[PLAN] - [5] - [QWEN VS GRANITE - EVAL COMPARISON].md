# Qwen vs Granite — praktiskt beslutsgrundande jämförelse

## 1. Beslut och syfte

Team Master har valt **Qwen2.5-7B-Instruct, Q4_K_M, från lmstudio-community**, som **prioriterad nästa 0-WORKER-kandidat** i samma LM Studio-harness. Arbetshypotesen är att Qwen kommer att prestera bättre och därför är mer sannolik att bli den praktiskt använda WORKER-modellen. Detta styr arbetsprioriteringen, men är inte ett redan bevisat prestationsresultat. Granite 4.1 3B Q4_K_M är tidigare kandidat och jämförelsereferens, inte överordnad Qwen. Permanent val för dagligt bruk eller generellt höjt storlekskrav är ännu inte beslutat.

Qwen får inte hållas som sekundär eller tvingas invänta mer Granite-arbete utan faktisk beslutsnytta. Korrekt arbetsutförande, tillförlitlighet, faktisk GPU-/minneskostnad och tid till verifierat användbart resultat ska avgöra om denna prioritering senare behöver ändras. Den introducerande jämförelsen är samtidigt en kompatibilitetskontroll: den ska hjälpa oss att skilja installationsskillnader från harness-/evalproblem.

Det yttersta målet är en tillförlitlig 0-WORKER som kan förstå, skapa, redigera och kvalitetssäkra ComfyUI workflow-JSON. Nästa prov ska avgöra vilken installation som ger oss en fungerande väg till meningsfulla förmågeprov—inte försöka kartlägga LM Studios interna motor uttömmande.

**The ONE Thing:** etablera en konkret fungerande native toolkedja med oberoende verifierat filresultat. Då kan senare eval mäta verkligt WORKER-arbete i stället för ett återkommande dispatchglapp.

Dokumentet formaliserar beslutad riktning, körmetod och utförd status i avsnitt 7. Det begränsade jämförelsepasset är nu genomfört: resultaten och evidensluckorna ägs av `model_evaluations/EVAL_5_2026-09-14-161840/[EVAL] - [EVAL_5_2026-09-14-161840] - [REPORT SUMMARY].md`. En lyckad native read är inte generell tool-/rollkvalificering.

## 2. Varför Qwen introduceras

- Granite har tidigare klarat den första verktygsfria screeningen. Senare toolutfall har blandat faktisk kandidatoutput med utebliven native dispatch; de bevisar inte ensam modellorsak.
- Den senaste tre-försöksdiagnostiken gav tre naturligt avslutade svar utan utförd read. Försök 2 och 3 gav identisk observerad text; detta är inte ett tillräckligt orsaksbevis för cache, uppvärmning, GPU eller Desktop-parser.
- Separat offentlig template-inspektion visade relevant toolnamn, schema och envelope-vägledning. Inspektionen var inte en capture av historisk intern `.act()`-input och löste inte dispatchproblemet.
- En annan dokumenterat relevant modellfamilj tillför en verklig intervention: kan samma projektverktyg och offentliga SDK-väg över huvud taget leverera en verifierad read med en annan installation?
- LM Studios officiella `.act()`-exempel använder Qwen2.5-7B-Instruct och dokumentationen beskriver positiva observationer av dess tool-use. Det ger en saklig grund för kompatibilitetskontrollen inom Qwens prioriterade kandidatur; lokal praktisk överlägsenhet ska fortfarande verifieras. [LM Studio: .act()](https://lmstudio.ai/docs/typescript/agent/act).

Använd den ordinarie Instruct-varianten, inte en befintlig abliterated/obliterated Qwen. Distribuerad modellkälla: [lmstudio-community/Qwen2.5-7B-Instruct-GGUF](https://huggingface.co/lmstudio-community/Qwen2.5-7B-Instruct-GGUF). Kontrollera faktisk lokal identifierare och kvantisering efter nedladdningen; ett förväntat namn är inte runtime-identitet.

### Verifierad lokal registrering, 2026-09-14

Originalfilen `Qwen2.5-7B-Instruct-Q4_K_M.gguf` finns i Team Masters `models/diffusion_models/` under `AI_Folder`. Den har registrerats med officiell `lms import --hard-link`: originalet är kvar, och ingen extra viktkopia har skapats. `fsutil hardlink list` visar båda namnen för samma fil. Filen ska behandlas som oföränderligt modellmaterial; en hard link är inte en isolerad kopia.

`lms ls --json` identifierar nu `qwen2.5-7b-instruct`, Q4_K_M, 4 683 073 952 byte, med katalogflaggan `trainedForToolUse=true`. Flaggan är metadata, inte verifierad toolkompatibilitet. LM Studio-relativ artefakt: `lmstudio-community/Qwen2.5-7B-Instruct-GGUF/Qwen2.5-7B-Instruct-Q4_K_M.gguf`.

Filstorleken matchar [distributionskatalogens metadata](https://huggingface.co/api/models/lmstudio-community/Qwen2.5-7B-Instruct-GGUF/tree/main?recursive=false&expand=false). Där angiven SHA-256 är `3e357ab3eda2c442f25c0080bb8998eedc05fd16ce1728eacff9ccc5c3d240c6`; den är **distributionsreferens**, inte en påstått uppmätt lokal hash. Hela viktfilen har inte lästs/hashats under förberedelsen. Storleksmatchning ensam är inte kryptografiskt integritetsbevis.

Vid den ursprungliga förberedelsen uppskattade read-only `lms load --estimate-only` med 4096 kontext, full GPU-offload och parallel 1 Qwen till **4,71 GiB** GPU-minne och Granite till **2,32 GiB**. Det var uppskattningar, inte uppmätta lastgarantier eller lämpliga kontextvärden för alla uppgifter. Senare EVAL 6 körde faktiska predictions och verifierade Qwens 32768-kontext med 85 % offload för sista ComfyUI-försöket; se dess rapport. Efter EVAL 6 är servern åter stoppad och inga modeller laddade.

## 3. Vad jämförelsen kan och inte kan isolera

Mätobjektet är först **praktisk modellinstallations-/harnesskompatibilitet**, inte en ren vikter-mot-vikter-kapacitetsjämförelse.

| Gemensamt och låst inom ett aktuellt jämförelsepar | Legitima installationsskillnader, alltid redovisade |
| --- | --- |
| Samma exakta user-instruktion, fixturebytes och semantiska function-schema | Modellvikter, 3B/7B, träning och tokenizer |
| Samma projektkällor, SDK/auth-anpassning och installerad runtimeidentitet | Modellens egen effektiva chat-template och toolformat |
| Samma samplingkrav, output-/round-/tool-/tidsbudget och färsk Chat | Modell-/fil-/instansidentitet och modellberoende tooltolkning |
| Samma read-only-handler, scope, kontroll och uppgiftskrav | Eventuella nödvändiga resurs-/loadskillnader, uttryckligen noterade |

Tvinga inte Granites template eller XML-format på Qwen. Samma function-schema ska levereras genom respektive korrekt standardinterface. Olika renderade inputbytes eller condition-hashes är därför inte automatiskt ett evalfel: jämför gemensamma fält och redovisa modellberoende fält separat.

Temperatur 0 är ett låst samplingkrav, inte garanterad determinism. Q4_K_M hos två familjer innebär inte identisk kvalitetsförlust. Ett bättre Qwen-utfall bevisar inte att alla 3B-modeller är otillräckliga, att Granite-vikterna är felaktiga eller att samma resultat gäller ComfyUI-arbete.

### Historik kontra ett nytt matchat par

Referens: `model_evaluations/EVAL_4_2026-09-14-152322/`, dess REPORT SUMMARY och `transport_review.json` i run `ac0556c76ec04d9d81ea2a35c9e51449`.

Projektkällor har ändrats efter denna diagnostik. EVAL 4 är därför historisk referens, **inte automatiskt en samtidigt källmatchad Granite-arm**. EVAL 2:s äldre native read-PASS saknar dessutom tillräckligt rekonstruerbara exakta villkor för ett ärligt historiskt kontrollpar.

Om ett Qwen-utfall motiverar en direkt aktuell jämförelse körs ett nytt litet Granite-kontrollprov med samma nu frysta källor och recept. Gamla resultat skrivs inte om. Käll-/runtimeändring mellan armar gör paret icke-matchat tills skillnaden redovisats; jämförelsen får då inte presenteras som att endast modellinstallationen ändrades.

## 4. Minsta nästa prov: en native read

Återanvänd `agent-0-eval/worker_file_read_evaluation.py`, dess `run()`-API och den redan implementerade fasta diagnostikfixturen. Ingen ny harness, textparser, generell jämförelseplattform eller ny toolhandler behövs.

| Del | Låst kontrakt |
| --- | --- |
| Fixture | `project/config/service.json`: `service_name=render-worker`, `queue_name=render-diagnostic`, `retry_limit=3`, befintlig oförändrad note |
| User-instruktion | `Read project/config/service.json using the available file tool. Tell me the queue_name and retry_limit from that file. Do not guess values or modify files.` |
| Tool | Endast befintlig `read_workspace_text`, befintligt exakt schema och handler |
| Konditionering | Färsk Chat, ingen projektägd systemprompt, rollfil, skill eller ComfyUI-kontext; standardtemplate och toolinterface redovisas |
| Generering | Officiell SDK `.act()`, temperature 0, högst 512 tokens/prediction, 2 prediction-rounds, 2 toolanrop, ingen parallell toolkörning |
| Planerad load | 4096 context, parallel 1, full GPU-offload om aktuell resurskontroll fortsatt tillåter detta; en modell åt gången. Effektiv load/prediction-konfiguration verifieras, ingen dold draftmodell |
| Diagnostikval | `diagnostic_delay_ms=0`, `tool_format_hint=False`, `granite_text_tool_bridge=False`, `reproduction_fixture=tool_transport_reproducibility.FIXTURE` |
| Budget | En Qwen-read först, 30 s körbudget och 5 s stoppbudget enligt befintlig runner; separat modelladdningstid redovisas |
| Scope | En unik disponibel run-workspace; inga produktionsfiler, shellverktyg, ComfyUI-modeller eller genereringar |
| Bedömning | Diagnostik, ingen kandidatpoäng eller automatiskt kvalificerad Evaluation Round |

Det fasta `reproduction_fixture`-argumentet är den befintliga explicita diagnostikvägen och används inte för att kringgå ordinarie kandidatgates. Dess `run()`-API används under Codex kontroll; vanlig read-CLI kräver fortsatt transportreview. För att behålla In-The-Loop ska Codex köra kontrollen som en separat pågående process, publicera känt eval-/run-id och följa `evidence.json`; ett blockerat verktygsanrop i chatten får inte bli enda kontrollvägen.

**Uppgiften är klarad** först när rätt fil faktiskt lästs genom native dispatch, oberoende handler-/receipt-evidens styrker detta, slutleveransen korrekt anger båda filvärdena och fixturen är oförändrad. Formatestetik, antal ord eller nya sidokriterier får inte underkänna uppgiften. Korrekt gissning utan read är inte genomförd read-uppgift.

Den första readen kan ändra nästa installationsbeslut men bevisar inte tillförlitlighet. Den befintliga tre-read-serien är ett separat, begränsat startvillkor för ordinarie toolrunners—inte nästa prov som automatiskt måste köras eller en statistisk förmågetröskel.

## 5. Hög-ROI-datapunkter och evidensägare

| Fråga att besvara | Minsta relevanta evidens | Vad fyndet kan ändra |
| --- | --- | --- |
| Slutfördes den faktiska uppgiften? | Sluttext, faktisk read-receipt och oförändrade fixturehashar | Om installationen kan gå vidare till riktade WORKER-prov |
| Var i den publika kedjan avviker armarna? | Genererade fragment/råtext → publika toolrequest-events → guard → handler → receipt → finaltext | Vilket lager som behöver undersökas eller rättas först; frånvaro är inte ensamorsaksbevis |
| Levererades rätt interface? | Exakt schema/instruktion, effektiv tools-konfiguration; vid motiverat behov separat offentlig render med tooldefinitioner | Template-/kontextleveransåtgärd, inte reflexmässig modellanklagelse |
| Var jämförelsen kontrollerad? | Source-set och rekonstruerbara projektbytes, SDK/Node/Zod-identitet, instans, effektiv prediction/load-konfiguration | Om skillnaden får användas som aktuell installationsjämförelse |
| Var resultatet användbart i praktiken? | Tid till verifierat resultat, separat loadtid, observerad resursnivå, eventuella stopp | Om installationen är värd nästa avgränsade uppgift; ingen generell hastighetsranking från en read |
| Är det en återkommande skillnad som behöver verifieras? | Aktuellt matchat Granite-prov eller en uttryckligen motiverad transportreview | Fortsätta med fungerande installation eller stoppa blockerad tool-eval; ingen automatisk repetitionsstudie |

Modelloutput och modellvillkor är observationer; dispatch/stopp och runtimehypoteser hör till harness-/anslutningsägaren; slutförd uppgift, jämförbarhet och beslutsvärde hör till evalägaren. Använd samma runreferenser, inte duplicerade råloggar. Tvetydiga negativa utfall hålls utanför modellspecifik prestationsbedömning.

Spara rå och partiell evidens, synliga fel och luckor. Fragmentskillnad är inte automatiskt tokenskillnad och avslöjar inte i sig kernel/cacheorsak. Saknade toolcallbacks gör inte all rå modelltext till en komplett native toolrequest.

## 6. Resultatstyrda beslut—inte nya körningar av hopp

| Observerat utfall under verifierade villkor | Försvarbar slutsats | Nästa praktiska åtgärd |
| --- | --- | --- |
| Qwen klarar read; Granite finns bara som äldre FAIL-referens | En Qwen-installation fungerar här; historisk regression och ensam Granite-orsak är inte isolerade | Överväg ett aktuellt matchat Granite-prov endast om detta ändrar installationsvalet; annars prioritera vidare kvalificering av fungerande väg |
| Qwen klarar read; aktuellt matchat Granite-prov klarar inte read | Installationsberoende kompatibilitetsskillnad under angivna villkor | Fortsätt Qwens redan prioriterade kandidatprov; ingen slutsats om ensam vikters brist |
| Båda aktuella armar klarar read | Aktuell native read-väg finns för båda; gamla dispatchproblem är inte därmed förklarade eller allmänt lösta | Fortsätt i första hand med Qwens minsta verklighetsnära nästa uppgift; ändra prioritering endast med relevant faktisk evidens |
| Qwen klarar inte read | Qwen är inte en fungerande kontroll i detta prov; gemensamt fel eller annan kompatibilitetsbrist är fortfarande möjliga | Stoppa expansion till full tool-eval. Granska första konkreta evidensavvikelsen och presentera motiverad åtgärd/alternativ för Team Master |
| Tool läser rätt fil, men slutleveransen är fel | Dispatchvägen fungerade; uppgiften som helhet slutfördes inte | Separera toolresultat från output-/instruktionsutfall och verifiera villkoren före modellspecifik negativ slutsats |
| Auth-, identitets-, fixture-, controller- eller stoppbevis brister | Ogiltigt eller overifierat försök, inte modell-FAIL | Bevara försöket, rätta verifierad brist hos rätt ägare; endast nytt länkat försök efter motiverad korrigering |

Ingen fem-/tio-omladdningsserie, godtycklig 4/5-tröskel eller oförändrad full eval är beslutad. En ny generering måste ha ett eget beslut som kan ändras. En misslyckad installation får inte belönas med obegränsat nya försök, men inte heller förklaras vara en dålig modell utan isolerande evidens.

## 7. Förberedelse och operativ ordning

| Ordning | Konkret arbete | Status/klarsignal |
| --- | --- | --- |
| 1 | Granska befintlig read-runner, model-argument, SDK, sourcecapture, kontroll och separerade callbacks | Förberett: ordinarie model-argument är generiskt; Granite-adapter är explicit och avstängd i kontrollreceptet |
| 2 | Riktad offline-regression av transportreview, generiskt modellval, paths/ownership, screening, avbrott och read-tool/eventcapture | 2026-09-14: 44 Python-tester och 4 Node-tester passerar; 3 opt-in live-tester är inte körda. Befintligt modellvals-test omfattar både Granite och Qwen; mock-PASS är inte live Qwen-PASS |
| 3 | Inventera exakt Qwen-artefakt/kvantisering och spara tillgänglig distributions-/filidentitet | Utfört: officiell hard-link-import, indexerad identifierare och matchande distributionsstorlek; lokal helfilshash är inte uppmätt |
| 4 | Kontrollera aktuell server/auth, vald backend och resurser; välj liten tillräcklig context/loadbudget före generering | Utfört: giltig/ogiltig SDK-auth samt aktuellt Qwen-cancel/normal-completion passerade. Effektiv load matchar 4096/full GPU/parallel 1; exakt backend-build är inte fångad |
| 5 | Skapa nytt eval-/run-id, frys gemensamma villkor, kör en avbrytbar native Qwen-read och följ disk/public events | Utfört: `EVAL_5_2026-09-14-161840`, Qwen-read klarad via faktisk native handler/receipt, båda rätta värdena och oförändrad fixture |
| 6 | Tillämpa beslutsmatrisen; högst ett ytterligare matchat Granite-read-prov inom det första jämförelsepasset om motiverat | Utfört: aktuellt Granite-read inte klarat. Samma källor/recept/klientruntime; olika anropsposition efter load redovisas som confound, inte ensam modellorsak |
| 7 | Skriv en gemensam REPORT SUMMARY med faktisk uppgiftsstatus, lagerseparerade fynd, luckor och nästa beslut | Utfört: rapport direkt under nya evalhemmet; fortsatt Qwen-kvalificering prioriteras, inga fler genereringar efter sammanfattningspasset |

Första jämförelsepassets genereringsbudget är därmed **högst två read-försök**, ett per installation, sammanlagt högst 60 s ordinarie körbudget plus eventuella separata stoppbudgetar. Modelladdning är inte gratis och mäts separat. Saknat verifierat stopp avbryter passet; en ny arm startas inte medan föregående aktivitet är overifierad. Verkligt server-/backendfel rättas först, inte genom fler kandidatkörningar.

Säkra resursinställningar och observationer dokumenteras före start, utan att optimera varje modell tills den får PASS. Om ett gemensamt lastvillkor inte är rimligt för båda ska avvikelsen redovisas som en praktisk installationsjämförelse, inte döljas som matchad kapacitetsmätning.

Evalspecifik evidens ägs av `model_evaluations/<eval-id>/<run-id>/`. Generella model load/unload-, server- och hosthändelser ligger i respektive befintlig ström under `LM-Studio_logs/`, med tidsintervall/referens; ingen ny allmän fellogg eller extra redundant manifestyta. Full model-I/O-capture är fortsatt explicit opt-in.

## 8. Vad ett möjligt modellbyte senare kräver

Read-PASS är inte write-PASS, generell autonomi eller ComfyUI-expertis. Qwen är redan prioriterad nästa **rollkandidat** och följer projektets modellneutrala screening/trajectory och klasspecifika säkerhets-, transport- och stoppkrav; Granites screeningpoäng ärvs inte. Det introducerande kompatibilitetsprovet behöver däremot inte föregås av en ny full screening eftersom det mäter kompatibilitet och ger ingen kandidatpoäng. Vidare kvalificering ska vara lönsam och rollrelevant, inte en ursäkt för mer Granite-felsökning.

Det praktiska valet behöver senare stöd av verifierad read/write/readback, scoped JSON-mutation och relevant ComfyUI-workflowarbete med samma semantiska domänkontext. Kontextens nytta, tillförlitlighet, kostnad och tid till användbart resultat ska vägas in—inte endast vilket modellnamn som vann en introducerande read.

Den temporära kandidatprioriteringen till Qwen är beslutad. Permanent val för Team Masters dagliga bruk kräver rollrelevant kvalificering och Team Masters beslut. Granite behöver inte avskrivas för att Qwen får prioritet, men tidigare Granite-status är inte skäl att nedprioritera Qwen.

## 9. Rapporten ska göra jämförelsen lätt att förstå

Sammanfatta i denna ordning: **vad skulle utföras → klarades uppgiften per installation → vad skiljde faktiskt → vad är bevisat respektive öppet → vad bör vi göra härnäst och varför**. En kort jämförelsetabell ska skilja uppgiftsutfall från native dispatch, scope, jämförbarhet och tillåten slutsats.

Besvara särskilt: vilka tidigare antaganden om harness/eval ändrades, vilka fynd endast gäller en installation, vilka evaldesignproblem faktiskt verifierades, och vilken konkret vidare uppgift nu ger högst ROI. Inkludera de etablerade fyra ERQER-frågeområdena. Undvik både falsk vikter-ensamorsak och ett nytt tekniskt rabbit hole.

## 10. Beslutad fortsättning: full Qwen-trajectory från början

Team Master beställde en ny sammanhängande Qwen-kandidat-eval från Round 1. **EVAL 6 startades och erbjöd alla nio unika historiska Granite-uppgifter**, men fullföljde inte 8×3-trajectoryn: tvåfilsuppgiften i Round 4 och den första ComfyUI-uppgiften i Round 6 gav praktiskt ofullständiga resultat. Den källbundna [EVAL 6-rapporten](../../model_evaluations/EVAL_6_2026-09-14-172933/%5BEVAL%5D%20-%20%5BEVAL_6_2026-09-14-172933%5D%20-%20%5BREPORT%20SUMMARY%5D.md) äger utfallet och stoppbeslutet. EVAL 5:s kompatibilitetsprov ersätter inte denna kandidat-eval.

EVAL 6 fick ett nytt tidsbundet eval-id vid verklig start; inga historiska resultat, preflight-id:n eller loaded-instance-referenser ärvdes som nya körbevis. Qwen är prioriterad kandidat; inga nya Granite-genereringar behövdes för den historiska sidjämförelsen. Ny körning får inte starta bara för att återstående platser finns: varje förslag behöver en konkret testbar hypotes och förväntat beslutsvärde.

Round 1–3 återanvände befintliga låsta uppgifter/runners. Fungerande read/write var ett nödvändigt men inte tillräckligt skäl för progression; EVAL 6 visade att mer komplexa tvåfils- och ComfyUI-uppgifter inte därmed är kvalificerade. Senare adaptiva uppgifter låses före respektive ERST med exakt instruktion, fixture, kontext, toolbudget, oberoende verifiering och relevanta successkrav. Det är planerad just-in-time-konkretisering, inte tillstånd att hitta på graderkrav efter output. Alla 24 platser finns i `worker_task_catalog.json`; adaptiva recept får inte beskrivas som redan exekverbara.

## 11. Historiskt uppgiftsregister för sidjämförelsen

| Round | Uppgift till Qwen | Granite-referens | Historiskt uppgiftsutfall | Kontrollerad jämförelsestatus |
| --- | --- | --- | --- | --- |
| 1 | `record_transformation` | EVAL 2 / `67d63fdd85924fe8b15933c9bf701498` | Klarad | Samma instruktion, katalogens tools-free villkor |
| 1 | `priority_routing` | EVAL 2 / `f1bb794b867f411498f5dda18a408f31` | Klarad | Samma instruktion och grader |
| 1 | `evidence_bound_comparison` | EVAL 2 / `d2a5190e35554ae9b2e130df430ec7a1` | Klarad enligt separat rubricreview | Samma instruktion/rubric; bevara separat kvalitativ granskning |
| 2 | `nested_record_edit` | EVAL 2 / `7262e5f1aa764051b15585aa0f1fdb4b` | Klarad | Samma instruktion och exakt systemkontexthash |
| 2 | `context_priority_selection` | EVAL 2 / `b8e9b420d3f5450595fa015422b39d49` | Klarad | Samma instruktion och exakt systemkontexthash |
| 2 | `evidence_selected_limit_task` | EVAL 2 / `0058228f2df54a94ab7ba885dbf96ded` | Inte klarad i det sparade försöket | Samma instruktion/kontext/expected JSON; ingen generell negativ modellslutsats ärvs |
| 3 | `nested_file_read` | EVAL 2 / `8683149a046a4655bff9fe876dcf2755`; EVAL 3 / `5cd4009469354fc08b2b5fc7d281f9e5` | EVAL 2 klarad; EVAL 3 ingen native read | Samma avgränsade läsuppgift med färskt diskvärde; fixturebytes och äldre runtime skiljer, historiska utfall bevaras båda |
| 3 | `file_creation_readback` | EVAL 3 / `67fe808dea5a4d459f802f1bf717aa1d` | Ingen native creation, uppgiften inte klarad | Version 2: samma katalog-/kontexthash och full genererad instruktion inklusive fixture-SHA-värden |
| 3 | `literal_text_replacement` | EVAL 3 / `5f929214d5b8455eb1acca72e4b5d8d5` | Ingen mutation, uppgiften inte klarad | Version 2: samma katalog-/kontexthash och full genererad instruktion inklusive fixture-SHA-värden |

Verifierat read-only under denna förberedelse: de första sex instruktionernas SHA-256 matchar EVAL 2. De tre Round 2-kontextfilernas bytes matchar både dagens katalog och historisk systemkontext. För create/replace matchar dagens katalog, kontext och **hela runner-instruktionen** EVAL 3; jämförelse av enbart kataloginstruktionen hade felaktigt missat de tillagda SHA-värdena.

EVAL 1:s första screening/filläsning samt EVAL 2–5:s upprepade/diagnostiska reads finns som ytterligare historisk evidens till samma uppgiftsfamiljer. De blir inte nya självständiga kandidatuppgifter eller flera röster i en PASS-kvot. Native och assisted/Granite-adapterresultat är separata kolumner; Qwen ska inte tvingas använda en Granite-adapter för att efterlikna en tidigare workaround. EVAL 2:s äldre creationkontrakt har rättats; dess native och assisted utfall får jämföras som relaterad historik, inte som identiskt version 2-prov.

Tabellen innebär **historisk uppgiftsmatchning**, inte byte-identisk total runtime eller ensam vikters A/B. Vid faktisk Qwen-run verifieras och sparas aktuell instruktion/context/catalog/source/runtimeidentitet och avvikelser från denna referens. Fixturemål och graders skickas inte till kandidaten som extra facit.

## 12. Hela trajectoryn och fortsättningsbesluten

| Round | Tre befintliga uppgiftsplatser | Granite-status | Qwens nästa beslutsvärde |
| --- | --- | --- | --- |
| 1 | Transformation, prioritetsrouting, evidensbunden jämförelse | Utförd | Är kandidaten värd fortsatt förmågeutvärdering? |
| 2 | Nästlad JSON-edit, aktuell/arkiverad kontext, roadmap-resume | Utförd | Kan den följa relevant kontext och exakta beroende instruktioner? |
| 3 | Native read, creation/readback, literal replacement | Utförd till mutationsgate | Kan den faktiskt utföra och verifiera grundläggande read/write? |
| 4 | Tvåfils-ID-join, verkligt validatorutfall, bounded toolfel/återhämtning | Inte utförd | Klarar installationen användbara flerfil-/felkedjor? |
| 5 | Beroende JSON-edit/summary, trusted fail-to-pass-reparation, svensk UTF-8-preservation | Inte utförd | Klarar den mer avancerat arbete utan regression/scopebrott? |
| 6 | Workflowtitlar med skill, graf-/skillval, workflowdiagnos | Inte utförd | Kan den arbeta med ComfyUI-format och observerbar skillprocedur? |
| 7 | Workflow-feature-roadmap, bugfix-roadmap, multifile/resume | Inte utförd | Klarar den sammanhängande realistiskt sandboxarbete? |
| 8 | Held-out-roadmap, workflowregression, nytt workflow från känd nodpalett | Inte utförd | Är modellen/installationens praktiska förmåga värd Team Masters dagliga bruk? |

Round 4–8 ger ny Qwen-rollinformation även utan Granite-motpart. Redovisa inte dem som att Qwen vunnit uppgifter Granite misslyckats med. Ingen gemensam totalscore blandar Qwens eventuella 24 uppgifter med Granites nio; jämför överlappet för sig och ny rollkvalificering för sig.

EVAL 6:s status: Round 1 formella gate missades på outputformat; dess andra två uppgifter gav diagnostiskt innehåll men inte byte-identiska formella försök. Round 2: två PASS och en eval-/grader-tvetydig automatisk FAIL. Round 3: native read och literal replacement klarade, creation inte. Round 4: första tvåfilsuppgiften inte klarad; övriga två ej utförda. Round 5 ej utförd. Round 6: första titeluppgiften inte klarad ens i det sista 32768-kontextförsöket; övriga två ej utförda. Round 7–8 ej utförda. Se rapporten för run-id:n, originalevidens och skillnaden mellan `invalid` och faktiskt uppgiftsutfall.

Alla nio överlappande uppgifter ska erbjudas när säkerhets-/runtimeförutsättningarna tillåter det. Ett avgränsat icke-kritiskt exakt-outputfel i Round 2 behöver inte utesluta ett oberoende säkert filprov; evaluatorn dokumenterar beslutet enligt befintlig design. Stoppa vid kritisk säkerhetsbrist, overifierat stopp, ogiltiga villkor eller obrukbar toolkedja—inte för att en enda poäng är låg, och inte genom att ändra facit för att få fortsatt progression.

## 13. Konkret operativ förberedelse och körordning

| Ordning | Operativ åtgärd | Förberedd status / klarsignal |
| --- | --- | --- |
| 1 | Verifiera Qwen-artefakt, välj explicit identity-readbudget, skapa nytt evalhem vid start | Artefakt indexerad; readiness/baseline har nu `--max-model-bytes`. För den valda filen används 4683073952 bytes; standard 4 GiB kvarstår |
| 2 | Starta localhostserver och ladda Qwen med uppgiftsanpassad, säkert maximal kontext; fånga bounded generell observability | EVAL 6 visade att 4096 inte rymmer ett helt workflow-toolresultat. Qwen stöder 32768; laddning vid 32768/85 % GPU/parallel 1 verifierades med cirka 1,6 GiB ledigt GPU-minne. Ny faktisk körning kräver alltid aktuell resurskontroll. |
| 3 | Färska cancel/normal-completion-bevis, tools-free readiness och baseline i samma nya evalhem | Befintliga runners; budget 1024 outputtokens för screeningbaseline enligt katalog. EVAL 5:s avlastade instans används inte som nytt livebevis |
| 4 | Kör Round 1:s tre låsta uppgifter en i taget, granska tredje svaret mot rubric | Kontrakt, graders och kvalitativ kalibrering verifierade offline; ingen automatisk retry |
| 5 | Kör Round 2:s tre låsta kontextuppgifter, med rätt systemkontext per uppgift | Instruktioner/kontexthashar verifierade mot historiken; skyddade/passerade delar bevaras |
| 6 | Verifiera aktuell read-transportreview och klasspecifikt tool-/mutationsstopp före respektive toolklass | Befintliga gates bevarade; små preflightprober är separat integrationsbevis, aldrig kandidatpoäng |
| 7 | Kör Round 3 read/create/replace med rätt review och unik per-run-workspace | Befintliga kontrakt/runners; native respektive faktisk readback/diskverifiering, inga text-till-tool-workarounds |
| 8 | Efter verifierad basic-kedja: lås och utför nästa Round 4–5-ERST utifrån största relevanta kvarvarande osäkerhet | Adaptiva recept finns; exakt fixture/toolkoppling/grader färdigställs före respektive försök, inte efter output |
| 9 | Före ComfyUI: använd versionsbundet sandbox-/nodkontrakt och modellneutral domänkontext, sedan Round 6–8 | Befintlig title-fixture/skill och playground återanvänds. Övriga held-out-/grafrecept låses före användning; statisk struktur är inte genereringsbevis |
| 10 | Uppdatera sidjämförelse efter varje ERST och avsluta med en REPORT SUMMARY | Per uppgift: Qwen-run/utfall, Granite-referens/utfall, native receipts, integritet, tid, villkorsskillnader och tillåten orsaksslutsats |

Körningen hålls under Codex löpande kontroll med befintliga start/inspect/stop-ytor; ingen monolitisk svepstart som måste invänta alla rounds. Kandidaten får ingen åtkomst till historiska svar, graderfacit eller andra evalers raw-data. Bevara original vid korrigering och gör endast nytt versionerat försök när verklig eval-/harnessbrist motiverar det.

Nu kända kandidatbudgetar: Round 1–2 högst 30 s per uppgift, Round 3 read 30 s och create/replace 45 s vardera; sammanlagt högst 300 s ordinarie genereringsbudget för nio uppgifter. Separata stopp-/preflight-/loadkostnader redovisas, inte göms i kandidatlatens. Senare ERST får exakt bounded budget i sitt låsta kontrakt; inget ogrundat antal omtag eller obegränsad motorfelsökning.

Readiness/baseline läser modellidentitet strömmande för SHA-256 och kontrollerar ändrade bytes/metadata. Explicit större bytebudget ändrar **inte** GPU-/RAM-admission, gör ingen modellkopiering och ger ingen kandidat åtkomst till vikter. Hela Qwen-filen har inte hashats under denna förberedelse; verklig identity-capture utförs av evaluatorn i den operativa baselinekedjan.

Startklara kontrakt ska inte blandas med senare adaptiva recept. Fyra redan implementerade uppgifter som felaktigt stod som framtida design i trajectorykatalogen pekar nu på sina befintliga verkliga kontrakt/runners; inga nya uppgifter, uppgifts-ID:n, extra rounds eller graderkrav har introducerats.

Ursprunglig förberedelseverifiering: 37 riktade Python-tester och 4 Node-tester PASS; därefter har EVAL 6 utfört live Qwen-generering, baseline, uppgifter och riktade efterfixregressioner. Den ursprungliga förberedelsesiffran är **inte** EVAL 6:s slutliga testkvot. Vid rapportens avslut var servern stoppad och inga modeller laddade.
