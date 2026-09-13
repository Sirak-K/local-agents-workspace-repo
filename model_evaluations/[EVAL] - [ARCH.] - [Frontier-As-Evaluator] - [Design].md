# EVAL — CODEX-DESIGN

Status: första verktygsfria WORKER-screeningen är live genomförd mot Granite 4.1 3B: tre preliminära rubric-/strukturgodkännanden med bevarad evidens, inte bekräftad förmåga. Ett tidigare ogiltigt harnessförsök finns kvar. Övriga rounds är inte implementerade. Användarens gräns är högst 10 Evaluation Rounds och högst 5 Evaluation Round-Specific Tasks [ERST] per round. Designen använder 8 rounds med 3 ERST vardera.

## Syfte och ägarskap

- Dessa principer gäller alla framtida lokala agentkandidater, oberoende av modellfamilj, modellstorlek och profil. Ange först avsedd roll och användarens minimikrav; bedöm faktisk arbetsförmåga och instruktionsefterlevnad för den rollen. Trevlig chatt, självsäkra svar eller ett korrekt formatsvar räcker inte.
- Alla utvalda lokala agentkandidater ska utföra relevanta uppgifter och svara inom praktiskt rimlig tid; precision, korrekt utförande och pålitlighet väger alltid tyngre än hastighet, särskilt för WORKER-rollen. Mät verklig tid till användbart, verifierat resultat inklusive eventuell tool-användning och återhämtning, inte bara tokenhastighet. Ett snabbt fel är inte en förbättring. En korrekt men opraktiskt långsam kandidat ska beskrivas som sådan utifrån rollens verkliga arbetskrav; inga universella tidsgränser uppfinns utan uppgift och mätdata.
- Codex äger uppgiftsval, ordning, oberoende bedömning, evidens, retries, avbrott och förbättringsexperiment. Kandidaten äger den uppgiftstolkning, tool-use och det omdöme som mäts. Codex får inte lösa uppgiften åt modellen och sedan tillgodoräkna kandidaten resultatet.
- `LOCAL_AGENTS/AGENT-0-WORKER/` är modellneutral men rollspecifik och äger gemensam 0-WORKER-kontext, tools, skills, konkreta uppgifter, fixtures, runner och graders. Kandidatens modellundermapp äger endast modellspecifika fakta, konfiguration, template och explicit motiverade avvikelser. Evaluation-oberoende LM Studio-evidens ägs av sina separata strömmar under `LM-Studio_logs/`; en fullständig evalkörnings kontrakt, run-mappar, resultat, bedömningar och syntes ägs endast av `model_evaluations/<eval-id>/`. Denna gemensamma design äger generella EVAL-principer. Gemensam LM Studio-transport får återanvändas, men får inte äga roll- eller modellspecifik beteendepolicy.
- Håll systemet litet: en uppgiftskatalog, en runner, riktade beteendetester och faktisk evidens. Ingen ny plattform, parallell harness, gammal roadmap-återuppbyggnad eller supportarkitektur utan ett konkret behov i nästa probe.
- Alla designändringar ska vara realistiska, praktiskt genomförbara, icke-kosmetiska och försvarbara. Inför endast skydd och stöd som den aktuella förmågemätningen behöver; dokumentationsgranskning bevisar inte fungerande runtime.

## Prioriterad orsaksutredning vid dåligt utfall

Starta med arbetshypotesen att konfiguration eller evaldesign kan vara felaktig eller suboptimal, inte att kandidaten saknar förmågan. Utred i denna ordning:

1. Modellspecifika förutsättningar: faktisk modell-/instansidentitet, effektiv konfiguration, template och inferensinställningar; inte enbart avsedda värden i en fil.
2. Modellneutrala förutsättningar: faktisk kontextleverans, gemensam konfiguration, transport/runtime, tools och permissions.
3. Uppgiftskontrakt: tydlighet och förenlighet i instruktionerna, fixtures samt bedömarens antaganden och kontroll mot verklig evidens.
4. Kandidatens egna begränsningar: överväg först efter relevant oberoende verifiering av föregående lager och begränsa slutsatsen till den faktiskt prövade uppgiften och villkoren.

Ordningen är inte ett förutbestämt orsaksbesked. Flera fel kan samverka; okända effektiva värden eller otillräcklig evidens lämnar orsaken öppen. Frontier-evaluatorn är själv en probabilistisk LLM och kan misstolka beteende och komplexa samspel mellan modell, instruktion, konfiguration och tools. Dess analys och säkerhet i bedömningen är hypoteser, inte oberoende bevis. Projektet använder detta som särskilt försiktighetsmotiv, inte som en empiriskt fastställd generell jämförelse med andra LLM-uppgifter.

Eval-evidensen ska bevara kontrollerade lager och deras evidens/luckor, orsakshypotes, korrigeringens ägare, exakt ändring och länkat versionerat återtest. Korrigera rätt ägare utan att ge facit; avbryt vid behov enligt det verifierade stoppkontraktet och pröva ändrade villkor i ett nytt bounded försök. Bevara originalutfallet, säkerhetsgränser, tidigare verifierade styrkor och skillnaden mellan självständig baseline och assisterad diagnostik. Ingen tyst omklassificering, lättade kriterier eller blind sökning efter PASS.

## Hög ROI: praktisk lämplighet först

Frågan före varje probe: vilket minsta men meningsfulla test ger störst beslutsvärde om fortsatt utvärdering är värd resurserna?

1. Round 1 prövar grundläggande instruktionsefterlevnad, flerstegslogik och kunskapsgränser utan tools. Då blandas tidig kapacitetsbedömning inte ihop med fil-/verktygsproblem.
2. Endast efter godkänd Round 1 börjar filarbete i en liten ny playground. Tools används då där uppgiften kräver dem; Round 4 fördjupar tool-use, inte introducerar tools för första gången.
3. Bygg vidare till verkliga korta arbetsflöden först efter godkända relevanta grunduppgifter. Alla delresultat måste vara korrekta, inte bara slutsvaret.

- Högst tre små, rollrelevanta första prober innan beslut om fortsatt breddtest. Anpassa innehållet efter rollens krav och verkliga tools; namnen och fixtures är inte gemensamma runtime-kontrakt. Stoppa vid första relevant fel, inte efter en stor sweep.
- Följ den prioriterade orsaksutredningen: modellspecifik konfiguration, modellneutral konfiguration/runtime och därefter uppgift/fixtures/bedömare före modellskuld. Högst ett direkt motiverat korrigerat återtest av felet efter verifierad orsak; ingen blind retry-loop eller lång prompt-/samplersökning.
- Vid kvarstående relevant fel under verifierade villkor prioriteras en annan agentkandidat framför fler tester. Vid oklara villkor är kandidaten ännu inte bedömbar, inte diskvalificerad.
- Vid framgång: välj minsta nästa test som tydligt höjer beslutsvärdet för verklig 0-WORKER-användning; upprepa med nya indata när just tillförlitlighet för den förmågan behöver avgöras, inte av slentrian. En instruerad kodändring mäter inte självständig felsökning. Formatsvarsprober är begränsad diagnostik, inte bevis på verklig read/write-förmåga.
- Prober får inte vara avsiktligt orättvisa trick eller ge förväntade svar som sedan misstolkas som självständig problemlösning. Varje uppgift ska ha tydligt ansvar, genomförbara instruktioner och ett relevant framgångsvillkor.

## Round-struktur och godkännandegates

- Rounds och ERST är dokumentationsbegrepp, inte automatiskt nya runtime-filnamn, fält eller kommandon. Profilens katalog ska konkretisera uppgifterna utan att skapa en parallell harness.
- Transport-/profilförkontroll är en förutsättning, inte en dold extra Evaluation Round. Den ska inte skicka kapacitetsuppgifter eller räknas som modelframgång.
- Varje ERST ska före start ha exakt instruktion, input/fixtures, förväntat verifierbart resultat, tillåtna ändringar/tools/skills, kontextpolicy, deadline, bedömningsregel och stoppvillkor. Inga nya mål läggs till efter att modellens svar setts.
- Varje round har högst 5 distinkta ERST; detta förslag använder 3. Variationer/upprepningar hör till samma ERST, men har separat antal-körningar-/tidsbudget och får inte användas för att gömma nya uppgifter.
- Första screening: ett försök per ERST, stoppa vid relevant fel och granska orsaken. Högst ett motiverat återtest. Godkänt enskilt uppgiftsutfall ska rapporteras som just det; det är varken generell rollförmåga eller automatisk behörighet för oisolerat filarbete.
- Välj upprepning med färsk konversation och nya isomorfa indata endast när den behövs för ett konkret beslut om tillförlitlighet eller regressionsrisk. Ingen fast kvot av två extra syntetiska körningar gäller innan ett säkert, mer representativt diagnostiskt arbetsprov. Stoppa vid relevant fel; positiva enstaka resultat får inte felrapporteras som bred tillförlitlighet.
- Round godkänns endast när samtliga för rollen obligatoriska ERST har verifierad framgång, inga kritiska scope-/falsk-framgångsbrott och tillräcklig evidens. Goda medelvärden får inte dölja kritiska fel.
- Ej stödd runtime/tool/skill-funktion ger blockerad eller uttryckligen ej tillämplig round, inte modellfel eller påhittat PASS. Round 1 måste vara godkänd före Round 2. Senare progression kräver godkända relevanta föregående förmågor; ett motiverat rollspecifikt undantag redovisas och begränsar slutsatsen.
- Innan första kontrollerade Round 1-körningen måste runnern verkställa denna progressionsspärr, inte bara beskriva den i dokumentation. Diagnostiska transportprober är tillåtna utan att räknas som round-framgång.

### EVALUATION ROUND 1 — Inevitable Model-specific Limitations Exploration [IMSLE]

Namnet bevarar användarens utforskningsmål. Testerna visar praktisk lämplighet under kontrollerade villkor, inte bevis för absoluta eller oundvikliga viktbaserade modellgränser. Alla tre uppgifter skickas verktygsfritt via det godkända officiella SDK-undantaget i samma LM Studio-harness: färsk Chat med endast aktuell user-instruktion, utan projektägd System Prompt, rollfiler, tools/skills, projektfiler eller dold historik. Templatens effektiva standardkonditionering kontrolleras separat; ingen projektinjektion betyder inte bevisad okonditionerad basförmåga. Ingen structured-output-/JSON-grammatik används eftersom den kan maskera instruktionsefterlevnad. Native REST behåller inventeringsansvaret. Faktisk output granskas så att påhittad tool-use inte räknas som framgång.

1. Instruktioner och strukturerad transformation: ge en liten post med namn, heltalsvärde och ett irrelevant fält. Begär JSON med endast namn och värde ökat med ett. Bedöm rätt innehåll, datatyper och respekt för fältgränsen; modellen får inte facit.
2. Flerstegslogik: ge tre uttryckliga prioriterade routingregler och tre poster, varav en träffar flera regler. Begär korrekt destination per post i angiven ordning. Bedöm regelprioritet och samtliga beslut, inte vältalighet.
3. Grundning och osäkerhet: ge en kort faktatext där informationen för en efterfrågad jämförelse saknas. Begär endast slutsatser som underlaget stödjer och nödvändig kompletteringsfråga. Bedöm att saknade fakta inte uppfinns.

Gate: de tre förstagångsuppgifterna måste vara verifierat slutförda innan ett fil-/tooldiagnostiskt prov övervägs. Därefter avgör separat verifierad tooltransport, isolerad playground, avbrott, tillåtna sidoeffekter och oberoende diskfacit om provet faktiskt får starta; inget syntetiskt repetitionsantal ersätter dessa gates. Kvarstående fel efter rättvis orsakskontroll kan motivera att kandidaten inte prioriteras vidare; oklara runtime-villkor får inte bevisa intern inkapacitet.

Orsakskontroll vid fel börjar med att kontrollera graderns parsning av det faktiska svaret mot uppgiftens låsta kontrakt. Harmlös whitespace ska accepteras för strukturell JSON-bedömning; extra text är ett fel endast om uppgiften uttryckligen kräver enbart JSON. Kriterierna får inte lättas efter att svaret setts. Kontrollera därefter konditionering, template, truncation och runtime före modellslutsats.
Innan Round 1 bedöms live ska dess deterministiska parser/bedömare provas mot några handskrivna kända goda och dåliga svar, inklusive harmlös whitespace och felaktiga datatyper. Detta är en liten kontraktskontroll, inte den separata handmärkta kalibreringen för kvalitativa omdömen.

WORKER-katalogen `instruction_following_catalog.json` äger de tre ursprungliga engelska uppgifterna, kontraktsversion/hash, 30 sekunder och högst 1024 outputtokens per uppgift. `instruction_following_grading.py` kontrollerar innehåll, typer, fältgränser, prioritet och ordning; grundningsuppgiften fick separat granskning mot tre förhandskända kriterier och tio kalibreringsexempel. De tre framgångarna visar slutförda uppgifter under den avlästa konfigurationen, men endast smal evidens för bred rollförmåga. Team Master har svarat efter sammanfattningen; nästa test valdes efter verklig WORKER-relevans och föregicks av isolerat filscope, bounded observation, separat stopp och diskfacit. En verifierad progressionsfunktion ska inte förväxlas med lyckad faktisk tool-exekvering.

### EVALUATION ROUND 2 — Read & Write (BASIC)

1. Läs en liten fil i en nästlad mapp och återge ett referensvärde som inte står i användarinstruktionen; ingen mutation.
2. Skapa en fil med angivet referensvärde och exakt specificerad encoding/radbrytning, läs tillbaka; bevara en kontrollfil.
3. Ersätt en uttryckligt angiven text i en fil; bevara alla andra bytes och verifiera slutresultatet.

Det första faktiska läsprovet gav ett relevant negativt baslinjeutfall. **Modellobservation:** Granite genererade en begriplig `<tool_call>`-begäran. **Harnessobservation:** LM Studio/SDK rapporterade den som vanlig text och startade inget verktyg. **Uppgiftsutfall:** filvärdena levererades inte; uppgiften klarades inte. Ett separat format-hint-försök misslyckades också. I ett nytt försök med strikt Granite-specifik tolkningsbrygga kördes samma begränsade läsverktyg och modellen gav båda diskverifierade värdena utan rollkontext; detta är villkorad framgång, inte retroaktiv baslinje-PASS. Läsverktygets in-flight-avbrott är verifierat, men inte varje framtida skrivverktygs stoppkontrakt. Ingen enstaka observation bevisar bred rolltillförlitlighet.

Gate: oberoende diskbedömning av rätt innehåll och scope samt rå modellbegäran, faktisk tool-exekvering och eventuell readback i samma evidenskedja. En korrekt fil ensam bevisar inte att modellen verifierade den. Missad uppgift och osäker felorsak redovisas separat; ett adapterat försök jämförs inte som om gränssnittet vore oförändrat.

### EVALUATION ROUND 3 — Read & Write (ADVANCED)

1. Ändra två JSON-värden, inklusive boolean, och bevara okända fält, listor och övriga värden; jämför struktur och datatyper.
2. Läs två små filer, koppla ihop poster via ID och skriv en korrekt sammanställning. En saknad match ska redovisas, inte uppfinnas.
3. Gör en precis ändring i svensk UTF-8-text med flera rader och bevara specificerade radbrytningar och orörda avsnitt; verifiera bytes där uppgiften kräver detta.

Gate: alla ändringar och bevarandekrav klaras på oberoende fixtures; formatkrav används endast när de ingår i den avsedda arbetsuppgiften.

### EVALUATION ROUND 4 — Tool usage

1. Välj rätt exponerat verktyg och korrekta argument för att lokalisera/läsa en efterfrågad fil; undvik irrelevanta anrop och fabricerade tools.
2. Kör ett litet förberett testkommando och tolka faktisk exitstatus/output, även när ett test avsiktligt misslyckas. Ett rapporterat misslyckat test kan vara korrekt agentbeteende.
3. Hantera en avsiktligt saknad fil med relevant diagnos eller kompletteringsfråga, utan repetitiva no-progress-anrop eller påhittad framgång.

Gate: bedöm tool-val/argument, resultatförankring och återhämtning separat från sluttext. Tool-loop övervakas av evaluatorn; permissions-/toolblockering skiljs från modellfel.

### EVALUATION ROUND 5 — Skill-användning

Användarens benämning "SKILLS.md usage" avser förmågan att upptäcka och tillämpa agent-skills. Faktiskt filnamn, sökväg, discovery, laddning, promptinjektion och prioritet måste verifieras i den aktiva LM Studio-agentprofilen före test; Codex skill-kontrakt får inte antas gälla den lokala kandidaten. Inga nya skill-runtimefiler skapas från denna benämning ensam.

1. Explicit begärd toy-skill: tillämpa dess procedur på nya indata och producera det begärda verifierbara resultatet.
2. Implicit skill-val: erbjud en relevant och en irrelevant toy-skill; en rollrelevant uppgift ska leda till rätt discovery/användning utan att instruktionssvaret kopieras från skillen.
3. Ingen tillämplig skill: utför en uppgift som inte behöver någon av skillsen utan att aktivera irrelevant procedur eller bryta användarens negativa constraint.

Gate: bevisa både att LM Studio-requesten/profilen faktiskt exponerade rätt skillinnehåll och att proceduren följdes. Om exponeringen inte kan bevisas blir resultatet diagnostiskt/blockerat, inte en slutsats om modellens skill-kapacitet.

Skill-rubricen följer den aktuella lokala agentprofilens observerbara skillkrav, exempelvis resultatfält och arbetssteg, inte Codex/Claudes egna skill-konventioner. Ett parat med/utan-skill-experiment införs endast om vi senare behöver mäta förbättringens storlek; ingen fjärde ERST behövs nu.

### EVALUATION ROUND 6 — Korta realistiska arbetsflöden

1. Läs en liten kodfil och specifikation, implementera en avgränsad funktion, kör förberedda tester och rapportera verkligt resultat. Ge krav, inte lösningskoden.
2. Reproducera en liten bug, identifiera orsaken, fixa inom scope och verifiera både felreproduktion och tidigare godkända fall.
3. Kombinera källdata, en avgränsad filändring och slutkontroll i 3–5 beroende arbetssteg; bevara kontrollfiler och rapportera ofärdiga delsteg ärligt.

Gate: hela kedjan ska fungera utan att Codex matar modellen med varje delbeslut. Bedöm första försöket och eventuell tillåten korrigering separat.

### EVALUATION ROUND 7 — Kontext och återupptagning

1. Fortsätt samma korta arbetsflöde över flera chattmeddelanden och bevara tidigare krav, beslut och negativa constraints.
2. Starta färsk konversation och återuppta ett halvfärdigt arbete från en liten explicit sparad status och diskdata, utan dold tidigare chatt.
3. Återuppta efter dokumenterat fel eller blockerad deluppgift utan att radera felet, fabricera färdigställande eller blint repetera samma misslyckade steg.

Gate: verifiera vad som finns i faktisk kontext och på disk före/efter reset. Manuell ny konversation är tillåten när automatisk session-reset inte är säkert verifierad; automation får inte påstås finnas.

### EVALUATION ROUND 8 — Oberoende bekräftelse och regressionssäkerhet

1. Kör en tidigare godkänd rollkritisk uppgift med nya namn, värden och innehåll som inte användes vid tuning; bekräfta faktisk överföring, inte memorering.
2. Kör en motsvarande uppgift med en liten legitim störning, exempelvis ändrad filplacering eller saknad optional uppgift. Förväntad adaptation/stop ska vara fastställd före test.
3. Jämför bästa baseline och en enda motiverad förbättring på samma lilla låsta guard-uppgift med oberoende varianter/upprepningar; granska kvalitet, scope, falska påståenden, tool-loop och tidskostnad.

Gate: ingen kandidat förklaras bättre om en tidigare obligatorisk styrka regresserar. Slutresultatet är en roll- och miljövillkorad kapacitetsprofil, inte en universell modellranking.

## Playground och bedömning

- Från Round 2 skapar Codex en ny liten playground under kandidatens egen eval-yta för varje oberoende ERST; några triviala text-/JSON-/kodfiler och kontrollfiler, inga riktiga arbetsfiler eller hemligheter. Round 7:s fortsättningsdelar delar playground endast när kontinuitet är det avsiktligt testade.
- Snapshot före och efter, uttrycklig mutation-scope, separata input och resultaten. Skapa inte alla framtida fixtures eller skills innan nästa uppgift faktiskt kräver dem. Playground är inte säkerhetsisolering för godtycklig kod/shell.
- Exakt byte-/strängmatch endast för exakt specificerade kontrakt. I övrigt struktur-/typ-/funktionsbedömning och en fördefinierad rubric för förklaring, omdöme och ärlighet; grammatisk variation ska inte räknas som kapacitetsfel.
- Kalibrera gradern mot kända goda/dåliga resultat och mänsklig granskning. Codex/Claude-bedömning kompletterar, men ersätter inte fil-/toolbevis; skilj graderfel från agentfel.
- Bedömare och facit ska vara oåtkomliga genom kandidatens faktiskt exponerade verktyg. En separat mapp eller ett efterhands-hashskydd räcker inte. Verifiera läs-/traverseringsgränsen med en ofarlig kontrollfil utan facit innan fil-/toolresultat används som oberoende kapacitetsbevis; kontrollen upprepas efter ändrad LM Studio-version, permission eller tool-yta. Läckage gör resultatet kontaminerat. Kontrollen får inte ge kandidaten åtkomst till riktiga projektfiler eller hemligheter.
- Innan kvalitativa Codex/Claude-omdömen används som godkännandegate ska en liten handmärkt kalibreringsmängd om minst tio fall täcka korrekta, felaktiga och gränsnära svar. Deterministiska graders får riktade kända goda/dåliga fall för varje faktiskt infört kontrakt; skapa inte extra triviala tester för att fylla ett antal.
- Separera första försöket, assisterad korrigering, preliminär screening och bekräftad tillförlitlighet. Dokumentera nödvändiga respektive valfria förmågor för rollen före körning.

## Rätt testförutsättningar

- Bevisa exakt modell/kvantisering, aktiv agentprofil, Working Directory, färsk konversation och idle-state före en kontrollerad förmågekörning. Modellval ensamt bevisar inte profilval.
- Skilj sparad modellkonfiguration från session-overrides och faktisk inference. En fil eller avsedd inställning bevisar inte runtime-beteende.
- System Prompt är inte hela modellens input: redovisa också projekt-/AGENTS-kontext, historik, aktuellt användarmeddelande, tool-scheman och tool-resultat. En tom promptfil bevisar inte okonditionerad modell eller automatisk filinjektion.
- Registrera modell, Thinking/budget där tillämpligt, sampling, sampling-seed, effektiv context/overflow, prompt/template, tools/skills, LM Studio-/runtimeversion och deras evidensursprung. Okända nödvändiga fält innebär diagnostisk körning, inte kontrollerad baseline. Anta inte att alla modellfamiljer stöder samma inställningar eller tool-kontrakt.
- Fresh context per oberoende probe; attachment är inte reset. Avvisa dold/paginerad tidigare historik. Lång kontext och återupptagning provas separat först när korta uppgifter fungerar.
- Inga settings- eller promptändringar mitt i en mätning. När Thinking jämförs ska sampling och övriga villkor hållas fasta. Thinking plus olika samplers är en konfigurationsjämförelse, inte ett isolerat Thinking-test.
- Hårda förkontroller före varje probe: exakt låst konversation, avsedd modell/profil, Working Directory när filer berörs, verifierad färsk historik och idle-state samt nödvändig permission/tool-yta. Om dessa inte kan bevisas får körningen endast vara en uttrycklig transport-/miljödiagnos, inte en bedömning av kandidatens förmåga. Kontrollerad baseline kräver dessutom verifierade, oförändrade relevanta konfigurationsvillkor. Full byte-exakt renderad modellinput och komplett intern reasoning får vara okända med tydlig begränsning; de blockerar inte automatiskt en annars verifierad beteendemätning.
- Konfigurationsfingerprint beräknas deterministiskt med SHA-256 över UTF-8 JSON med sorterade nycklar och fast serialisering: modellfilens verifierade identitet/kvantisering, relevanta effektiva sampling-/Thinking-/context-värden, template, System Prompt-innehåll och exponerat tool-/skill-manifest. Varje ingående värde har evidensursprung och verifieringsstatus; okänd är inte samma värde som avstängd eller tom. LM Studio-/runtimeversion och övrig miljö registreras separat och måste också vara oförändrade vid kausala jämförelser. Sessionsidentitet, task och fixture-variant hålls utanför konfigurationshashen och registreras separat. Ett hashvärde av okända/sparade fält verifierar inte effektiv konfiguration; förändring under probe ogiltigförklarar mätningen.

## Kommunikation och evidens

- Kommunikation går till verklig lokal kandidat genom samma LM Studio-harness. Godkänt transportundantag: officiell JavaScript-SDK för avbrytbar evalgenerering; native REST API v1 för modellinventering och generell observability. SDK 1.5.0 har ett uttryckligt godkänt, versionsbegränsat auth-undantag enligt officiell tokenmappning; ingen anonym fallback. Spara det faktiskt använda transportkontraktet, SDK-resultat/statistik respektive native svar, tool-resultat och runtimefel. SDK-chat ska inte framställas som native REST-stateful storage eller få påhittade `response_id`:n.
- Bastransporten verifieras av `LM-Studio_connections/LM-Studio_for_codex/codex_lm_studio_connection_smoke.ps1`. Tool-, skill-, Working Directory- och stateful-kontrakt måste få egna riktade verifieringar först när nästa faktiska probe behöver dem; en grön textprobe bevisar inte agentparitet.
- Registrera LM Studio-/runtimeversion, endpoint, serverstatus, modellinstans och verifierad/blockerad/ej körd status. Främmande inmatning eller ändrad sessionskedja under probe ogiltigförklarar mätningen.
- Disk- och tool-evidens väger tyngre än modellens egna påståenden. Kontrollera faktiskt resultat, bevarade filer, dokument-/instruktionsseparation och eventuell falsk framgångsrapport.
- Spara exakt instruktion, native svar/tool-evidens/runtime-fel, tillgänglig konfiguration och dess osäkerheter, källfingerprints, ändrade filer, bedömning, avbrott och variant. Markera otillräcklig/paginerad evidens som ofullständig.
- Fixtures och loggresultat är separata: playground i profilens eval-yta, evaluation-oberoende rå evidens i sina ägarströmmar under `LM-Studio_logs/` och evalspecifika körningsfiler direkt under `model_evaluations/<eval-id>/<run-id>/`. Varje körning får unik sandbox och unik loggfil. LM Studios interna loggar förblir externa källor som fångas read-only. Ingen destruktiv återställning eller automatisk radering av tidigare evidens. Pretty/multiline JSON, UTF-8 utan BOM, läsbara tidsstämplar och relativa projektsökvägar där absoluta inte krävs.
- Lokal sandbox är inte OS-isolering. Varje runner måste redovisa exakt vilka filer och gränser dess grader faktiskt övervakar; begränsat filskydd får inte beskrivas som skydd av hela disken. Codex måste granska native tool-evidens innan vidare godkännande.
- Round 4/6:s kod-/kommandoexekvering väntar på verifierad OS-/processisolering och faktiska resursgränser, eller användarens explicita godkännande av en konkret dokumenterad begränsning av skaderadien. Testa skyddet med en ofarlig gränsöverträdelse mot disponibla kontrollfiler före tillit; container/VM/restricted account är kandidater, inte automatiskt valda komponenter. Ett godkännande av begränsad isolering gör inte åtkomligt facit oberoende.
- Server-, model lifecycle-, model-I/O- och hostobservationer ska fångas separat under `LM-Studio_logs/server_events/`, `model_lifecycle_events/`, `model_io_events/` och `host_resource_snapshots/`, med källa, tidsintervall och luckor. `model_io_events` är explicit opt-in. Observerad processförsvinnande är inte en bevisad krasch, och en native app-logg är inte automatiskt full inference-input. Capture ska vara read-only mot källorna, unik per körning och bounded i tid/disk; ingen ändring av original-loggar eller automatisk uppladdning av känslig raw-data.
- Skilj modellfel från transport-, harness-, runtime-, verktygs-, permissions- och miljöfel. Tomt svar eller context-/toolfel är inte automatiskt modellinkapacitet.

## Förbättring utan regression

- Etablera och bevara en återställbar, otunad baseline och bästa verifierade konfiguration. Varje kandidat ska adressera ett observerat fel med en tydlig hypotes och en ändrad variabel.
- Ta en läsbar snapshot av den otunade kandidatkonfigurationen före första kontrollerade Round 1-proben och registrera det separata konfigurationsfingerprintet från första körningen. Okända eller ej runtime-verifierade värden ska märkas som sådana; en sparad snapshot får inte ensam kallas verifierad effektiv baseline.
- Testa felet och tidigare godkända beteenden. Behåll endast reproducerbar förbättring utan regression; återställ försämringar och redovisa blandade resultat som blandade.
- Målet är att den behållna konfigurationen blir bättre. Att varje nytt försök eller varje stokastiskt modellsvar ALLTID blir bättre kan inte garanteras och får inte utlovas.
- Tuning ska förbättra verkligt rollrelevant agentbeteende, inte memorering av testsvaret eller evalspecifika kryckor. Använd nya uppgiftsvarianter som inte användes för att utforma ändringen.
- Variation av fixtures är inte variation av modellens sampling-seed. Ett fixed-seed-resultat är diagnostik. Bekräfta beslut om förbättrad konfiguration med minst tre verifierade sampling-seeds, fem vid nära/varierande resultat när runtime stöder detta. Om seed inte kan verifieras: redovisa begränsningen och gör oberoende upprepningar utan att kalla dem en kontrollerad seed-jämförelse.
- Modellinställningar får ändras genom verifierade LM Studio-API-/CLI-kontrakt eller uttryckligt kontrollerad appkonfiguration, följt av runtime-readback. Ändring får inte ske mitt i en eval-run, och inställningar för en modell får inte automatiskt ärvas av en annan.

## In-The-Loop: observation, avbrott och evaldesignkorrigering

- Implementationsbeslut: pågående SDK-prediction får separat `cancel()` utan att strömmen överges; slutlig `stopReason == userStopped` är serverns begäransspecifika stoppkvitto. Tidsgräns är bara trigger/deadline, inte bevis. Kvittot måste knytas till den egna predictionen; naturligt slutförande som hinner före stopp är ett annat utfall. SDK-undantaget undviker kostsam unload/reload. Se [SDK cancellation och stoppstatistik](https://lmstudio.ai/docs/typescript/llm-prediction/cancelling-predictions).
- Ägda Windows-toolprocesser skapas suspenderade, tilldelas ett separat Job Object före resume och tillåts inte breakaway. Stopp stänger nya dispatches, terminerar bara den egna jobgruppen och verifierar `ActiveProcesses == 0`; redan gjorda skrivningar återställs inte. Detta är processlivscykelkontroll, inte en säkerhetssandbox eller stoppgaranti för externa MCP-servrar. Se [Windows Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).
- Avbrott kräver ett konkret skäl. Vid verifierad konfigurations-/evaldesignbrist följer orsaksutredning och ett nytt länkat versionerat försök; stopp eller tweak sker inte för sin egen skull. Första implementerade kontrollslicen är diagnostisk och får inte räknas som audition eller som färdig round-/graderimplementation.

- Runnern ska låta Frontier-evaluatorn läsa bounded inkrementell evidens och begära stopp medan en ERST fortfarande körs. Start, observation och avbrott ska gå att orkestrera utan ett slutresultatblockerande anrop som tar bort Codex beslutsmöjlighet. Detta är en ansvarskravbild, inte beslut om nya runtimefilnamn eller en extra plattform.
- Native `POST /api/v1/chat` med `stream: true` ger SSE-event för bland annat meddelanden, eventuell reasoning, tool-anrop/-resultat och fel. Använd tillgängliga sådana event som evidens, inte som garanti för komplett intern reasoning, framtida toolkontroll eller möjlig injektion av ett nytt meddelande mitt i genereringen. Se [LM Studio streaming events](https://lmstudio.ai/docs/developer/rest/streaming-events).
- Verifiera separat hur exakt aktiv request/generering faktiskt avbryts i installerad LM Studio-version. Hitta inte på en cancel-endpoint och anta inte att klientdisconnect, lokal runner-kill, timeout eller modellsjälvrapport betyder serverstopp. Vid tools krävs dessutom verifierad spärr för nya dispatches och bounded stopp-/cleanup-policy för redan pågående tools och deras subprocesser. Polling efter avslutad request bevisar inte ensam att ett tool saknar eftereffekter.
- Före en ERST låses observationens maxlatens, stoppbudget och verifieringsmetod efter uppgiftens verkliga risk och runtime. Förkontrollen ska med ofarlig disponibel uppgift visa att evaluatorn kan läsa aktuell evidens, begära avbrott före färdigställande och verifiera upphörd generering; före toolarbete ska motsvarande test täcka ett pågående tool och frånvaro av nya dispatches/oväntade sena effekter. Lägg också ett proportionerligt regressionstest som visar att samma transport fortfarande slutför en legitim uppgift utan avbrott. Verifieringen upprepas efter förändring som kan påverka kontraktet. Saknad eller misslyckad stoppverifiering blockerar berörd eval.
- Ingrip vid säkerhets-/scopeproblem, no-progress, konkret eval-/harnessbrist eller tydligt saknat fortsatt informationsvärde. Avbryt inte rutinmässigt vid varje tveksamt resonemang: interimtext kan vara ofullständig och återhämtning kan vara en del av kandidatens förmåga. Ett tidigt avbrott får inte ersätta oberoende orsaksgranskning.
- Vid misstänkt missförstånd: kontrollera originalinstruktionens innebörd och prioritering, fixtures, tillgänglig kontext/tools/permissions och graderns förväntningar. Dokumentera konkret belägg för design-/harnessbrist, kandidatbeteende eller oklar orsak; missförstånd ensamt belägger inte vilken ägare som är fel. Ändra endast den brist som faktiskt identifierats.
- Spara partiella SSE-/tool-/diskeffekter och exakt evaluatorbeslut med tidsstämplar, skäl, stopphandling, begärt respektive verifierat stopp och eventuella kvarvarande processer. Avbrutet är inte färdigt PASS/FAIL; tidigare verifierbara observationer får redovisas utan att ett ofärdigt resultat överklassificeras. Stopp är inte rollback: verifiera fixture-/diskstate innan fortsatt arbete.
- En korrigerad ERST får versionerad instruktion/fixture/grader/förutsättning och nytt länkat försök efter verifierat stopp, riktat graderskydd och färsk kontrollerad kontext. Försökets egna villkor låses före start. Bevara originalets evidens och ogiltighetsorsak; attribuera inte ett ogiltigt evalförsök till modellen och slå inte ihop olika uppgiftsversioner i en kausal jämförelse.
- Direkt korrigering i samma task/session får användas i separat märkt assisterad diagnostik om runtime faktiskt stöder det, men får aldrig rapporteras som självständig baseline-framgång. Ge inte kandidaten facit för att få ett lyckat resultat. Förutbestämda följdfrågor eller återkoppling i ett uttryckligen interaktivt taskkontrakt bedöms enligt det kontraktet; oplanerad coaching skiljs ut.
- Ett omtag ska ha dokumenterad förväntad nytta och bounded budget och följa befintliga återtest-/regressionsgates. Hög ROI styr val av relevant nästa test och reparation av verkliga evalbrister, inte obegränsad omformulering tills kandidaten lyckas.

## Resursbudget, avbrott och slutsats

- En bounded probe i taget, normalt 60 sekunders deadline och versionsverifierat request-/genereringsavbrott inom uppgiftens separat låsta stoppbudget. Deadline är en yttergräns, inte krav att invänta den före evaluatorstopp. Ingen automatisk modelladdning, obegränsad loop eller tung lokal arbetslast utan explicit godkännande.
- Automatisk no-progress-watchdog ska ägas av evaluatorn; initial policy för tool-use är tre konsekutiva likvärdiga tool-anrop utan relevant framsteg. Varje runner måste redovisa om övervakningen faktiskt är implementerad och verifierad: timeout är inte samma skydd. Full tool-use-sweep väntar på verifierad sådan övervakning; en enda tool-ERST kräver redan fungerande evaluatoravbrott och bounded tool-/processhantering.
- Likvärdighet ska bedömas via observerad effekt, inte bara tool-namn/argument: relevanta innehållshashar, exitstatus och nytt meningsfullt resultat. Ändrad mtime, varierade argument eller ny brusoutput räcker inte som framsteg. Olikartade resultat som legitimt reducerar osäkerhet kan vara framsteg även utan filändring. Om tillräcklig native tool-evidens saknas kan watchdog inte påstås verifierad; använd deadline och blockera full tool-sweep.
- Varje exekverande probe ska före start ha tids-, tool-, process-, fil- och total skrivbudget som den faktiska verktygs-/isolationsytan kan verkställa, inte bara gradern upptäcka i efterhand. Claudes 15–20 anrop, en subprocess och små filbudgetar är startförslag, inte verifierade eller generellt låsta runtime-gränser. Välj minsta rimliga budget för nästa konkreta uppgift och testa att gränsen faktiskt stoppar arbetet.
- Efter första lämplighetsgaten: små motiverade experiment, inte en uttömmande sökning. Stoppa en felundersökning efter tre välmotiverade kandidater utan reproducerbar förbättring på oberoende varianter, eller när nästa steg kräver otillgänglig funktion eller separat tyngre körning.
- Slutsatsen ska ange vad modellen demonstrerat, vad som är opålitligt, miljö-/toolblockerare och återstående osäkerhet under namngivna modell/runtime/prompt/tool/context-villkor. Få eller många ändliga LM Studio-körningar bevisar inte modellvikternas absoluta, tekniskt oundvikliga interna gränser.
- Green grader-tests bevisar bedömningens beteende, inte kandidatens förmåga. Ange alltid om live-prober faktiskt körts och vad som blockerar dem.
- Uppdatera denna design, katalogens ordning och README när användaren ändrar riktningen. Ändra inte Git-index/history utan separat exakt instruktion.

## REPORT SUMMARY och extern förbättringsgranskning

- Varje fullständig evalkörning ska avslutas med exakt en syntesfil i evalkörningens rot: `[EVAL] - [<eval-id>] - [REPORT SUMMARY].md`. Filen är en spårbar sammanställning för beslut och extern granskning, inte ny rå evidens, parallell grader eller ersättning för `evidence.json` och `assessment.json`.
- Eval-id ska vara evalkörningens redan etablerade, unika id. Rapporten listar alla ingående run-id:n och skiljer giltiga bedömningskörningar från ogiltiga försök, avbrottsdiagnostik, assisterade försök och senare angränsande diagnostik. Ett efterhandskonstruerat run-id får inte presenteras som om det kom från runtime.
- Rapporten ska vara självbärande men källbunden: syfte, kandidat och evaluator; låsta villkor och evidensluckor; uppgifter, råa svar och ursprungliga bedömningar; verklig 0-WORKER-relevans; avbrotts-/kontrollbevis; kända begränsningar; samt en relativ evidensförteckning med run-id, fil och relevant datapekare eller hash när tillgängligt.
- Modellobservationer, LM Studio-/SDK-/harnessobservationer, uppgiftsutfall och evaluatorns egna processbrister ska ligga i tydligt separata avsnitt. Rapporten får inte göra ett observerat samspel till bevisad ensamorsak, räkna en textskriven tool-begäran som exekverad tool eller räkna ett harness-assisterat resultat som en retroaktiv baseline-framgång.
- PASS/FAIL ska återge de låsta kriterier som faktiskt användes. Väsentliga kvalitetsbrister redovisas separat utan kosmetisk efterhandsbedömning, nya sidokriterier eller ändring av originalevidens. Ändrad analys ska versionsmärkas i rapportens revisionshistorik; råa körningsfiler skrivs aldrig om för att passa syntesen.
- Rapporten ska avslutas med `EXTERNAL-REVIEW-QUESTIONS-EVAL-RESULT [ERQER]` och exakt dessa fyra frågeområden: vad namngiven Frontier-evaluator kunde ha gjort mycket bättre eller annorlunda; hur framtida kandidater kan ge mer användbara och försvarbara insikter på modellspecifik och modellneutral nivå; hur framtida EVALS kan förbättras icke-kosmetiskt och icke-trivialt; samt övriga mycket höga eller höga ROI-insikter evaluatorn bör adressera eller implementera.
- Externa reviewers ska ombes prioritera konkreta ändringsförslag och för varje förslag ange evidensgrund, berörd ägare/lager, förväntad nytta, risk eller tradeoff och minsta verifiering. Rapporten ska synliggöra osäkerheter och öppna frågor så att reviewern kan ifrågasätta Codex analys, inte bara bekräfta den.
- En delningskopia får redigera token, onödiga absoluta sökvägar eller annan känslig rådata, men varje redigering måste märkas och får inte förändra det bedömningsrelevanta innehållet. Ingen automatisk extern uppladdning ingår i rapportprocessen.

## Implementationsstatus och Claude-granskning

Den tidigare Granite-/Bionic-bundna provkatalogen och runnern har tagits bort från den modellneutrala `AGENT-0-WORKER/agent-0-eval/`-ytan enligt NIOTUF. Endast metodiskt innehåll som återverifieras mot denna design får omderiveras. En begränsad läsuppgiftsrunner och isolerad filfixture är live verifierade; fullständig read/write-/skillkonfiguration och no-progress-watchdog för senare uppgifter är inte verifierade.

Implementerat och live verifierat 2026-09-13: native anslutning, separat generisk observability (23 tester), SDK-start/insyn/stopp och ägda Windows-jobgrupper (16 avbrotts-/authprov gröna inklusive live stopp/normal completion), samt tre tools-free uppgifter med graders/progressionsspärrar (11 tester gröna). Färsk konversation utan projektägd systeminjektion, verklig modell- och konfigurationsreadback, `userStopped` och tre naturliga IMSLE-slut har observerats. Första uppgiften gav först ett korrekt svar men ogiltigt harnessutfall när rå SDK-konfiguration felaktigt jämfördes mot redigerad loggevidens; rätt ägare korrigerades och nya live-gates/nytt versionerat försök kördes. De tre giltiga uppgifterna nådde låsta kriterier, men detta är endast smal preliminär evidens. Tredje svaret var onödigt långt och innehöll ett tveksamt exempel; ingen efterhandsändring av rubric gjordes. Efter Team Masters svar kördes första isolerade filläsningen: ordinarie tool-väg misslyckades, strikt Granite-brygga gav separat korrekt filbaserat svar, och ett pågående läsverktyg avbröts verifierat. Detta räcker inte för skrivarbete eller externa/delade MCP-processer; varje ny toolklass behöver eget scope- och stoppbevis.

Källkontrollerade allmänna principer: uppgiftsspecifika kriterier, automatiserad bedömning kalibrerad mot mänsklig granskning och iteration med representativa fall enligt [OpenAI Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices); granska händelsekedjan för tool-/workflowfel enligt [Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals). Dessa metodprinciper återanvänds lokalt; ingen OpenAI evalplattform eller SDK införs.
