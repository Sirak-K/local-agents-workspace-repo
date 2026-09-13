# :.: .: .:. :. :.: PROMPTS - SMALL :.: .: .:. :. :.:

# Catalog Improvements

Ok nu ska vi hantera en catalogs/-mapp i taget fast svepande och utförligt, alltså ska du använda exakt följande utgångspunkt, tumregelfråga eller mental vägledning: "Vad är den absolut mest försvarsbara och professionella mappstruktur för denna mapp som kan uppnås, med minimala och/eller betydliga/omfattande ändringar som tillåtna åtgärder?"

catalogs\observability\runtime_triage\runtime_triage_symptom_catalog.json

Nu redogör för exakt alla de mest centrala, GENERELLA och huvudsakliga samt ÖVERGRIPANDE ansvarsområden som denna mapp bör äga.

## REGLER OCH RIKTLINJER

- Granska ordentligt innan du svarar.
- Varje ansvarsområde som ska implementeras, behållas eller realiseras måste vara minst Hög i Försvarsbarhet.
- Passivt exponerad metadata & inte faktiskt används av projekt/backend = stale/dead = inte försvarbar som egen katalogfil.
- Föreslå inte onödigt fler filer än vad din ärliga, mest försvarsbara och egentliga bedömningslutsats föreslår/menar.
- Det är möjligt att ytans namn kommer att ändras eller förbättras.
- UTGÅ INTE(!) från hur den aktuella ytan just nu är implementerad FIL- och NAMNMÄSSIGT; låtsas som att mappen just nu är tom på FILER.
  -- MEN det du faktiskt oundvikligt behöver utgå ifrån är filernas innehåll, mer konkret att utvärdera/addressera alla de exakta JSON-Keys/JSON-data som dessa .json-katalogfiler just nu är implementerade med.

- Fynd-Tabellens kolumnstruktur:
  "#" "Ansvarsområde", "Vad mappen bör äga", "Försvarbarhet", "Föreslagen Plats" .

-- "Föreslagen Plats"-kolumnen
--- ENDAST FILNAMN, alltså inga sökvägar/mappar som värden.
--- Format: "<ansvarsområde>.<filformat>" (du ska alltså INTE låsa/bestämma filnamn, det är mitt jobb).

KOM IHÅG!!!! UTGÅ INTE FRÅN PROJEKTSPECIFIKA FRYSTA BESLUT OCH NUVARANDE IMPLEMENTATIONER, UTGÅ ENDAST FRÅN VAD ÄR PROFESSIONELLT OCH OBJEKTIVT KORREKT SAMT MEST FÖRSVARSBART!!!! VI HAR FRIHET ATT ÄNDRA VAD SOM HELST I HELA PROJEKTET OCH PROJEKTETS KODBAS/KÄLLKOD SAMT PERSISTENCE LAYER - DET ENDA PROJEKTLEDANDE UTGÅNGSPUNKTEN SOM ÄR LÅSBAR ÄR :"VAD ÄR PROFESSIONELLT OCH OBJEKTIVT KORREKT SAMT MEST FÖRSVARSBART!!!"

---

### Lista på NYA och/eller BEFINTLIGA Fält/Data-bärande Variabler, som bör, ska eller måste implementeras inom detta arbetsmoment

- Med en-menings-definitioner, format: "<koncept/fält>" = "definition"
  -- Endast om aktuellt annars exkludera Fält, alternativt lista faktiskt relevanta variabler/data-relaterade objekt. Alltså ignorera denna del om det inte är applicerbart för detta arbetsmoment.
  -- Endast FÄLTNAMN/JSON-KEYS som är UNIKA för den aktuella .json-filen, katalog-filen eller filen - jämfört med befintliga/nya/planerade katalogfilers innehåll.
  -- Listan ska vara alfabetiskt sorterad; A-Z = top-bottom.

EXEMPEL PÅ LISTANS INNEHÅLL:

`fältnamn/JSON-key` = <definition i en tydlig förenklad mening>
`fältnamn/JSON-key` = <definition i en tydlig förenklad mening>
`fältnamn/JSON-key` = <definition i en tydlig förenklad mening>

### Implementationsdetaljer som Koncist/Kompakt Exempel

- T.ex Ett JSON-structure exempel (per kodblock).
  -- Endast om aktuellt annars använd och utgå ifrån det mesta självklara praktiskt implementerbara implementationsdetalj-exemplet eller inget implementationsdetalj-exempel alls
  --- Alltså ignorera denna del om det inte är applicerbart för detta arbetsmoment.

---

# Förklara ARBETSMOMENT

Planeringsprocessen:

## Antaget Operativt Flöde (FLOW)

- FLOW-struktur/format där "<>" är placeholder för FLOW-aktörer (t.ex ansvarsområden):

```
START: <>
→ <>
→ <>
→ <>
→ <>
→ <>
```

## Lista på NYA och/eller BEFINTLIGA Fält/Data-bärande Variabler, som bör, ska eller måste introduceras i detta arbetsmoment

- Med en-menings-definitioner, format: "<koncept/fält>" = "definition"
  -- Endast om aktuellt annars exkludera Fält, alternativt lista faktiskt relevanta variabler/data-relaterade objekt. Alltså ignorera denna del om det inte är applicerbart för detta arbetsmoment.
  -- Endast FÄLTNAMN/JSON-KEYS som är UNIKA för den aktuella .json-filen, katalog-filen eller filen - jämfört med befintliga/nya/planerade katalogfilers innehåll.
  -- Listan ska vara alfabetiskt sorterad; A-Z = top-bottom.

EXEMPEL PÅ LISTANS INNEHÅLL:

`fältnamn/JSON-key` = <definition i en tydlig förenklad mening>
`fältnamn/JSON-key` = <definition i en tydlig förenklad mening>
`fältnamn/JSON-key` = <definition i en tydlig förenklad mening>

## Implementationsdetaljer som Koncist/Kompakt Exempel

- T.ex Ett JSON-structure exempel (per kodblock).
  -- Endast om aktuellt annars använd och utgå ifrån det mesta självklara praktiskt implementerbara implementationsdetalj-exemplet eller inget implementationsdetalj-exempel alls
  --- Alltså ignorera denna del om det inte är applicerbart för detta arbetsmoment.

## Föreslagna runtime-ytor och/eller filer (inkl. Katalogiserings-filer)

- Betona med fetstil text/rubrik inom parentes, ovanför eller bredvid/före förslaget, om det är befintlig eller nytt.
  --- Alltså ignorera denna del om det inte är applicerbart för detta arbetsmoment.

### START

För ARBETSMOMENTNAMN:
[DIMSPD]

---

# SÖK PÅ NÄTET

Sök på nätet för att verifiera empiriskt , minst 10 olika repos/hemsidor/källor; alltså DEEP RESEARCH om det aktuella.

# E2E

0. <E2E Slutsatser + Tasks>

1. Vad DU ska göra nu är att först förstå och sammanfatta problematikerna tydligt genom att mäta eller jämföra dom mot faktiska loggarna för dessa två Tasks som har utfört, så vi kan klargöra på översiktlig men konkret nivå vad som orsakar de problematiska utfallen/agentbeteenden - så att vi kan klargöra hur vi ska åtgärda sådant.

2. Nu generalisera starkt dvs abstrahera

Alla Mest Centrala och Viktigaste Task-specifika Slutsatser

på ett sätt som gör att det du skrev inte handlar inte bara om Task-specifikt, utan det ska handla om hur Agenten permanent och deterministiskt ska alltid förstå, och därmed bete sig dvs svara accordingly, baserat på en given Task-prompt.

3.  (EXTREMT KRITISKT!:) Förstår du nu att åtgärderna du ska implementera för att lösa detta, inte handlar om Task-specificiftet utan PERMANENT FÖRBÄTTRING i (förväntad) agentbeteende?

# ROADMAP-STEP ::: IMPLEMENT

Ok kör nästa icke-utförda RMS. Om det är Hög arbetsmängd bör du Aktivera 1 agent så att du säkerställer att ni arbetar tillsammans effektivt, smart och riskfritt enligt de mest rekommenderade och/eller frysta designbesluten.

# ROADMAP-STEP ::: EXPLAIN

Ok så för att jag ska veta exakt hur du har tänkt, förklara i 3 koncisa steg med korrekt ordning hur du hade utfört det mest rekommenderade nästa arbetet eller arbets-steget/-delen.

# LÄS AGENTS.MD

Läs igenom AGENTS.MD för refresher, med störst fokus på samtliga "WORKFLOW :::"-sektioner.

# LÅS BESLUT

Lås och formalisera de låsta besluten i en ny eller direkt-relevant och befintlig "docs\docs_plan\[PLAN] - [*] - [FRYSTA BESLUT].md"-fil

# TA BESLUTET ÅT MIG

- Ta de mest rekommenderade, framtidssäkra, logiskt/tekniskt korrekta och sofistikerade beslut gällande detta.
  -- ENLIGT DE RELATERADE OCH AKTUELLA TEKNOLOGIERS EGNA/SPECIFIKA OCH RELEVANTA OFFICIELLA STANDARDER ELLER BÄSTA DESIGNBESLUT OCH PRACTICES I ALLMÄNHET.
  (... OCH/ELLER ENLIGT VAD JAG EXPLICIT SAGT ATT JAG VILL HA OCH/ELLER GÖRA.)

# THE ONE THING

[KOM IHÅG!!!! UTGÅ INTE FRÅN PROJEKTSPECIFIKA FRYSTA BESLUT OCH NUVARANDE IMPLEMENTATIONER, UTGÅ ENDAST FRÅN VAD ÄR PROFESSIONELLT OCH OBJEKTIVT KORREKT SAMT MEST FÖRSVARSBART!!!! VI HAR FRIHET ATT ÄNDRA VAD SOM HELST I HELA PROJEKTET OCH PROJEKTETS KODBAS/KÄLLKOD SAMT PERSISTENCE LAYER - DET ENDA PROJEKTLEDANDE UTGÅNGSPUNKTEN SOM ÄR LÅSBAR ÄR :"VAD ÄR PROFESSIONELLT OCH OBJEKTIVT KORREKT SAMT MEST FÖRSVARSBART!!!"
]
Gällande detta ovan som är inuti hakparentes , ställ dig själv följande frågan och se om du finner något värdefullt: "What's the ONE Thing I can do such that by doing it everything else will be easier or unnecessary?" för hela projektets framtid scope.
Gällande detta, ställ dig själv följande frågan och se om du finner något värdefullt: "What's the ONE Thing I can do such that by doing it everything else will be easier or unnecessary?"

# Manuellt Arbete (Jag / Team Master)

Gällande dessa fynd:

Är detta/dessa (icke-triviala) aktuella/nästkommande Arbets-steg arbete något du behöver min input för
eller är det redan underförstått exakt hur du ska utföra på mest rekommenderade sätt enligt vad som förväntas?

Är det nåt som det aktuella arbetet kräver från mig som måste arbetas av mig manuellt
t.ex att jag måste göra något, köra ett visst kommando eller installera något - för att göra det arbete du nyss gjort meningsfullt och godkännbart?

- Utgå från att jag INTE vill ändra "grundregler".
- Utgå inte från att jag behöver själv göra E2E- eller smoke-tester för att göra det arbete du nyss gjort meningsfullt och godkännbart.

# GOOGLE AI

Om du behöver specifik och/eller avgörande information för att kunna hjälpa mig på absolut bästa sättet
som ger mig högst avkastning för eller gällande de aktuella förbättringar som vi talar om, så måste du nämna vad du vill se nu,
kompakt och bestämt.
Gällande att du ska kunna ge ännu mer tekniskt korrekta och (mitt-)projekt-specifika instruktioner än du redan gett.

# GET OUT OF "HOTFIX"-LOOP

Vi har nått en loop.

Grejen är såhär, jag vill göra mer drastiska/ och omfattande försök/åtgärder/experimentation för att snabbare ta reda på hur vår LLM kan förbättra sin inlärning
så mycket snabbare som möjligt - istället för att göra flera små och icke-lönsamma fixes som verkar endast förbättra LLMen marginellt
och det känns nu som att allting i projektet går mycket segt pga jag inte har en abstrakt eller helhets-riktning för hur allt kan gå snabbare.

(opt.)
T.ex efter vi har gjort denna träningsrunda som du föreslår,
så är det mest sannolikt att du kommer säga igen liknande typ "denna kategori har denna detalj som bör förbättras";
men dessa "hot fixes" känns inte lönsamt baserat på tiden det tar att A) implementera dom och sen B) träna på dom, det är det jag försöker förmedla här essentially.

### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### -----------

# :.: .: .:. :. :.: PROMPTS - LARGE :.: .: .:. :. :.:

# ------------------------------------ GRANSKNINGAR ------------------------------------

# FÖRBEREDSGRANSKNING ::: INFÖR ::: IMPLEMENTATION

- Börja förbered för den faktiska implementationen, utan att implementera något än, men du ska förbereda granskningsmässigt så att du vet exakt vad som ska göras så att när jag väl befaller dig att börja arbeta operativt så vet du redan exakt vad du ska göra, enligt de mest rekomm. designbesluten.
- Förberedsgranskning går ultimately ut på att göra/förbereda (read-only) så att du har dom mest effektiva, rekommenderade och sofistikerade förutsättningarna för att faktiskt utföra implementationen optimalt.
  - Förberedsgranskningens utförlighet eller omfattning ska endast vara så omfattande som det arbetsmomentets planering faktiskt kräver.
    -- Alltså om det inte behövs mycket ny insamling av information/kontext för planeringen så bör Förberedsgranskningens omfattning anpassas dvs reduceras/minimeras enligt den balansen, och samma åt andra hållet; om mycket planeringsinformation behöver sammanställas så bör granskningen göras enligt den nödvändiga omfattningen.

-- Du ska använda de associerade docs-filerna för att dokumentera din implementationsplan och dina fynd.

### `[PLAN] - [<ARBETSMOMENTNAMN>] - [FRYSTA BESLUT].md`

- Skapa detta "docs/docs_plan/"-dokument i rätt mapp om det inte redan existerar.
- Du kan redan nu, innan Förberedsgranskningen, låsa, dokumentera och/eller formalisera Frysta Beslut om dessa finns eller har explicit tydliggjorts.
- Du kan naturligtvis, efter Förberedsgranskningen, låsa, dokumentera och/eller formalisera nya eller flera Frysta Beslut.

### `[PLAN] - [<ARBETSMOMENTNAMN>] - [ROADMAP].md`

- Skapa detta "docs/docs_plan/"-dokument i rätt mapp om det inte redan existerar.
- Den förberedande granskningen ska alltså leda till en optimal och genomtänkt impl-roadmap, utan fluff och tveksamheter - men slösa inte tid eller resurser på onödigheter.
  -- Det är därför (oftast) mest logiskt att fylla i ROADMAP-filer EFTER att den faktiska Förberedsgranskning har gjorts eller utförts.
- Förtydligande: ROADMAP-tabeller ska alltid innehålla de faktiska operativa dvs implementerbara arbetsstegen för det aktuella arbetsmomentet, all annan info bör därför dokumenteras i [FRYSTA BESLUT]-filer.
- Vid varje utfört Roadmap-arbetspass ska ett svar, eller chattmeddelande (i ditt pågående arbete), utan att du nödvändigtvis avbryter arbetet, börja med "RMS #/#" så vi kan spåra den pågående RM-arbetsprocessen kontinuerligt.

#### Roadmap-kolumn: `Arbetsmängd`

- Syfte: Spårbarhet, kontroll och sofistikation.
- Det ska finnas en specifik Roadmap-tabellkolumn som, baserat på förhållandet mellan alla identifierade/befintliga Roadmap-steg, ska estimera (ungefärlig) arbetsmängd.
  -- Kolumnnamn: `Arbetsmängd`
  -- Värden: `Mycket Hög`, `Hög`, `Medel`, `Låg`

### START

- Gör nu Förberedsgranskningen för (att Implementera) Arbetsmomentnamn:

[Full Bionic Traceability]

---

# KRS AGENTIX ::: [CB-OPT]

Gör nu ett Redundansfynd- och Optimeringsfynd-sökningspass så vi säkerställer att källkod och kodbas är i optimalt och pristint skick/tillstånd efter de större implementationerna som inkluderas i hela `mcp-java-project/`-arbetet.

- Hjälpmedel/Ramverk/Utgångspunkt: `docs_project\docs_project_frameworks\[Z-FW] - [OPTIM.] - [INFO].MD`

- Målytor/Projektytor:
- PRIO-1) `mcp-server/domain/vf2`
- PRIO-2) Direkt-Relaterade och Berörda ytor.

---

Steg 1) Gör granskning `# FÖRBEREDSGRANSKNING ::: INFÖR ::: CB-OPTIMERINGSMOMENT` och skapa docs.

docs/docs_plan/[PLAN] - [ROADMAP]- [CB-OPT-Iteration-# - <OPTIMERINGSMOMENTNAMN>]
docs/docs_plan/[PLAN] - [FRYSTA BESLUT] - [CB-OPT-Iteration-# - <OPTIMERINGSMOMENTNAMN>]

Steg 2) Återkom för Team Master (jag) klarsignal efter docs, så jag ska ge dig klartecken när du kan börja med första Roadmap-steget i och för CB-OPTIMERINGSMOMENTETS ITERATION.

---

## RIKTLINJER

### RIKTLINJE-1) OPTIMIZATION-SCOPES ::: Vad CB-OPT Främst Alltid Siktar På

#### OPTIMIZATION-SCOPE-1) KÄLLKOD & KODBAS

- Mål: Realistiskt maximal sofistikation enligt etablerad och modern standardpraxis samt Best Practices för och gällande de Direkt-relaterade och berörda källkodsfiler.
  -- (KODOPTIMERING, KODSTÄDNING & KODHYGIEN FÖR ÖKAD SOFISTIKATION I KODBAS)

#### OPTIMIZATION-SCOPE-2) ANSVARSDUBBLING ::: (redundans mellan två eller flera filers befintliga ansvar/innehåll) .

- Om en (positiv) eliminering av redundans leder till dvs resulterar i att en fil blir faktiskt onödig att ha kvar i projeket, och att det är helt riskfritt att ta bort den onödiga filen - då ska den faktiskt onödiga filen raderas.

#### OPTIMIZATION-SCOPE-3) TERMINOLOGI ::: Konsistent och Project-wide Naming Conventions

- Naming Conventions måste tillämpas på .java-filnamn!

- Styrande Ramverk: `mcp_java_project\docs\docs_frameworks\conventions\[PROJECT] - [CONVENTIONS] - [NAMING] - [CODEBASE].md.md`

-- Filnamn
-- Filers kodinnehåll & syntax-relaterade begrepp

##### FÖRBJUDEN TERMINOLOGI I RUNTIME, KODBAS OCH KÄLLKOD

- Begrepp som "RMS", "Roadmap", "VF", "VFAR" och "TODO-META" samt ARBETSMOMENTNAMN är dokumentativa styrnings-/planeringsbegrepp och ska inte användas inuti, eller som namn för, runtime-kodfiler, varken som syntax, kodidentifierare eller kodkommentarer.
  -- Undantag är mappnamn.

### RIKTLINJE-2) CORE ARCHITECTURE ::: mcp-server/-projektets mest viktigaste arkitekturella delar är 'foundation/' och 'domain/'

Notera: 'foundation/' och 'domain/'-mapparna/modulerna är projektkritiska arkitektoniska kärnbyggstenar så de ska hanteras med respekt och absolut inte mappnamn-ändras.
De har funnits med sen projektets begynnelse och bevaras medvetet med integritet.

- Se detta inte som begränsade faktorer utan som MCP Server-projektets arkitektoniska/arkitekturella originala och fortfarande aktuella sanning.

#### `mcp-server/foundation/`

Är: Domain-AGNOSTIC Top-Level Module = ett lager som ska fungera oberoende av domän.

#### `mcp-server/domain/`

Är: Domain-SPECIFIC (dvs Konsultförmedling i detta projekt) Top-Level Module.

---

### RIKTLINJE-3) NO TESTS ::: Skapa INTE Tester, Testfiler eller Test Suites.

---

### RIKTLINJE-4) EXISTING FOLDERS & FILES ::: Hantering av befintliga Projektfiler och Projektmappar

#### Projektfiler

- Filer kan merge:as dvs konsolideras om det är starkt rekommenderat t.ex till följd av en refaktorisering.
- Endast mycket starkt, dvs Hög ROI, rekommenderat bevis och belägg får leda till att en .java-fil raderas.
  -- Vi siktar alltså på att inga onödiga .java-filer eller död kod ska finnas kvar när det aktuella CB-OPT arbetet är färdigutfört.
- Undvik att byta filnamn om inte det faktiskt krävs för att bevara
  optimal kompatibilitet och koppling mellan Filens Ansvar, Filens Innehåll och Filens namn.

##### Projektfilers Filnamn

När förberedsgranskningen är helt klart bör du, endast om (det finns) filnamn som inte längre korrekt representerar det filinnehåll alltså filansvar som filen faktiskt bär/äger = Höga ROI codebase-polishing fynd, lyfta filnamnbytesförslag (i form av en kompakt fynd-lista ) - alltså endast för icke-trivialt dåliga/inkompatibla/motsägande filnamn ska du föreslå en lista OM DET ens finns sådana filnamnbytesförslag för runtime-filer inom aktuell målyta och/eller optimeringsmoment.

#### Projektmappar

Här vill vi vara mycket mer försiktiga och det är därför EXTREMT VIKTIGT OCH KRITISKT ATT DU ALDRIG Ändrar mappar eller mappars namn. Endast om det är Mycket Hög ROI samt etablerad standardpraxis så måste du notifiera mig om (garanterat) förbättrande och Mapp-relaterade ändringsförslag. När detta sker måste du lyfta ("raise") "[SPWIDPD]"-arbetsregeln och omedelbart stoppa ditt pågående arbete. FÖRTYDLIGANDE: Det innebär att det ska vara svårfunnet eller sällsynt att Mapp-relaterade ändringsförslag kan och ska ske eftersom jag ofta tänker extra starkt på att planera projektarkitekturer skalbart ur mapp-perspektiv (t.ex `foundation/` och `domain/`).

---

### RIKTLINJER-5) ROADMAP ::: Optimal mängd arbetskontext per arbetssteg

- Syfte: Vi vill undvika att hantera för stora arbete åt gången eftersom att vi vill arbeta på ett sätt som gör det principiellt omöjligt att agentiskt arbetskontext eller arbetsmoment-relaterad förståelse förloras och därmed att felaktigt eller oönskat arbete utförs.

- Roadmapstegen ska ha och vara enligt mest logiska, effektiva och smarta samt rekommenderade ordning av/för faktiskt implementation.

#### Roadmap-kolumn: `Arbetsmängd`

- Syfte: Spårbarhet, kontroll och sofistikation.
- Det ska finnas en specifik Roadmap-tabellkolumn som, baserat på förhållandet mellan alla identifierade/befintliga Roadmap-steg, ska estimera (ungefärlig) arbetsmängd.
  -- Kolumnnamn: `Arbetsmängd`
  -- Värden: `Mycket Hög`, `Hög`, `Medel`, `Låg`

#### Sammanställning av Arbetsresultat

Efter varje utfört CB-OPT-arbetssteg / RMS så ska du sammanställa dina arbetsresultat kompakt t.ex

EXEMPEL:

```
RMS-2 av 15 UTFÖRT
1. `foundation/<mappnamn>/<filnamn>.java`
2. `foundation/<mappnamn>/<filnamn>.java`
3. `foundation/<mappnamn>/<filnamn>.java`
4. `foundation/<mappnamn>/<filnamn>.java`

Verifieringar:
1. Backend clean compile
2. MCP initialize-payload smoke
3. Riktade stale-marker-sökningar
4. UTF-8/mojibake-kontroll

Nya tester/testfiler: inga.
```

---

---

# FÖRBEREDSGRANSKNING ::: INFÖR ::: CB-OPTIMERINGSMOMENT

(KODOPTIMERING, KODSTÄDNING & KODHYGIEN FÖR ÖKAD/MAXIMAL SOFISTIKATION I KODBAS)

## CB-OPT-FÖRBEREDSGRANSKNING ::: Formalisera din faktiska och operativa åtgärdsplan

Baserat på dina fynd i din CB-OPT-FÖRBEREDSGRANSKNING så ska du planera ditt kommande kodoptimeringsarbete.

- Plats: `[PLAN] - [<OPTIMERINGSMOMENTNAMN>] - [OPTIM.] - [ROADMAP]`

- Börja förbered för det faktiska CB-OPT-passet, utan att implementera något än, men du ska förbereda granskningsmässigt
  så att du vet exakt vad som ska göras - på ett sätt så att när jag väl befaller dig att börja arbeta operativt så vet du redan exakt vad du ska göra, enligt de mest rekomm. designbesluten.
- Förberedsgranskning går ultimately ut på att göra/förbereda (read-only) så att du har dom mest effektiva, rekommenderade och sofistikerade förutsättningarnaför att faktiskt utföra det faktiska CB-OPT-passet optimalt.

- Gör nu Förberedsgranskningen för OPTIMERINGSMOMENTNAMN:
  [CB-OPT-Iteration-1 - REACT APP]

# READ-ONLY-GRANSKNING ::: PROJECT STATE UPDATE

- Gör en snabb (read-only) översiktlig granskning av ai_training_grounds/-ytan och krs-agentic-ide-bridge/-ytan.

- Gör en snabb (read-only) översiktlig granskning av mcp-server/-ytan och lite i mcp-react-app/-ytan med 2 agenter, så att du får bättre förståelse för projektets nuvarande state.

# ------------------------------------ QUESTIONNAIRES ------------------------------------

## QUESTIONNAIRE ::: Question the Need

Gällande och/eller Inför: detta

- Är det värt att stanna upp och ställa frågor enligt (`C:\Users\SSIRA\AI_Folder\workspaces\comfy_ui_workspace\[ AGENTS ] - Prompts.md`) "# QUESTIONNAIRE ::: OPTIMERING-1"-formatet,
  eller finns det inga tydliga förbättringar eller optimeringar som sådana frågor kan bidra med?
  Det vill säga, endast om frågor kan leda till att avslöja dolda;
  A) Kritiska designbeslut som borde eller ska avgöras via mina preferenser/beslut  
  B) Möjligheter att undvika högt-sannolika flaskhalsar och/eller arkitekturella blind spots
  C) Förbättringssmöjligheter
  D) Optimeringsmöjligheter

---

## QUESTIONNAIRE ULTIMA ::: OPTIMERING-1

######

#####

####

###

- Efter att planeringen/implementationsplanen och alla frågor är färdiga och utförda så ska du direkt uppdatera/skapa en `[PLAN] - [<ARBETSMOMENTNAMN>] - [FRYSTA BESLUT].md`-fil.

Nu, vad är det mest viktigaste informationen som, när du har denna informationen,
som du endast kan få/erhålla (direkt) genom att (explicit) fråga mig (direkt), via/i Multi-Option-format (så jag kan trycka på svarsalternativ), och som garanterar att vi kommer ha den mest starkast och mest säkrast samt mest optimala utgångspunkten och planeringen för att implementera följande, på ett sätt som garanterar att inget önskat saknas när följande ARBETSMOMENTNAMN är helt färdigt eller utfört [PLANLÄGE = AKTIV]:

[<BIONIC AGENT - STORY & CHAT>]

###

####

#####

######

## QUESTIONNAIRE ::: OPTIMERING-2

- Har vi realistiskt maximerat riskfria optimeringar eller finns det realistiskt och faktiskt tydliga samt riskfria förbättrings- och/eller optimeringsmöjligheter som bör fastställas och/eller implementeras?

Gällande : alla ytor eller filer som berörts av AHOS-arbetet

---

# HANDOFF

Jag vill starta en ny Codex session med projektroten som "java-mcp-consultant-platform" så därför skapa en handoff till agenten som ska ta över härifrån:

---

Skapa en utförlig agent handoff på minst 800 ord och max 1000 ord dvs 800-1000 ord.
Denna handoff ska inte bara förklara nästan allt du kommer ihåg vi har arbetat tillsammans med
inom hela denna chattsession, med mest fokus och prioritet på det mest senaste implementationerna/arbete,
men också förklara tydligt MEN Utan för mycket implementationsdetaljer (for brevity)
hur du har använt de mest relevanta och aktuella projektytorna,  
med främst och störst fokus på:

- mest aktuella projektytor
- mest aktuella och styrande arbeten/planeringar

.. och De mest Permanenta, Viktiga, Aktuella och Centrala Kärndelarna i projektet.

---

# MODULARISERING

1. Denna följande fil innehåller för mycket kod:

context_inventory\backend_java\java_mcp_bridge_client.py

Vad är det mest rekommenderade, kodbaskompatibla/projektkompatibla och renaste sätt
att modularisa dvs dela upp denna fil till flera filer, specifikt till

3-4 olika filer,

5-10 olika filer,

utan förlust av nödvändig information som måste bevaras i projektet eller kodbasen?

På ett sätt som gör att denna filen som ska brytas upp dvs modulariseras sedan kan tas bort ALTERNATIVT bytas namn (och ansvar) på.
Vi ska byta namn på den filen som modulariseringen sker kring, till baserat på vad dens nya roll (efter modulariseringen) förväntas att ansvara över.
Syftet är att inte ha konflikt/dissonans mellan gammalt filnamn och nytt ansvarsområde (i/för kodfilen).

Svara; utan implementationsdetaljer, i tabellformat, endast Nya Filer (att modularisera till) och vad den befintliga filen återstår med och ska heta.

---

Förklara på abstrakt nivå ;
A) Vilket ansvar som den stora bef. filen har idag
och
B) vilka ansvar som de nya föreslagna Modulariseringsfilerna kommer leler förväntas att ta emot

---

- Ge mig sedan det FULLSTÄNDIGA resultaten av modulariseringen.

# REDUNDANS

## REDUNDANS ::: Specifika Projektområden

Aktivera 2 agenter och analysera hela:
`runtime_and_inference`

och ta reda på om det finns redundanta/expired filer/filinnehåll
som garanterat inte används eller är tydligt legacy och därmed borde raderas.

## REDUNDANS ::: Hela Projektet

OBS! Du ska inte ändra projektstrukturen i detta steg, endast granska och sammanställ granskningsresultatet effektivt såhär:

"Antal Kod-Filer Som Innehåller Garanterat Onödig/Död Eller Expired Innehåll och Därför är Riskfritt eller Kostnadsfritt att Ta Bort : "
"Antal Kod-Filer Som Inte Ska Tas bort Men Vars Innehåll Måste Addresseras För Att Undvika (framtida) Problem som t.ex Flaskhalsar och/eller Död Kod: "
"Antal Kod-Filer Som Behöver Klargöras och/eller Diskuteras Kring: "

"Antal Kod-Mappar Som Riskfritt Kan Tas Bort: "
"Antal Kod-Mappar Som Behöver Klargöras och/eller Diskuteras Kring: "

- Ok, baserat på detta, för varje, eller det enda aktuella, viktigaste problemområde,
  redogör för, och formalisera, en permanent koncis formulering som ämnar
  att motverka att problemområdet någonsin ever ens kan vara möjligt igen i vårt MCP Server projekt igen.
  max 200 ord per område.

### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### -----------

---

### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### ----------- ### -----------

# GRANSKA DOCS

för att säkerställa eller verifiera att de inte innehåller något innehåll som inte tydligt kan bestyrkas och/eller stödjas av nuvarande projekttillstånd/projektinnehåll och/eller projektriktning:

Du kan även ta bort dokument som verkligen inte används eller behövs längre därifrån, alternativt konsolidera/merge:a.
NOTERA: Du ska inte göra överdrivna ändringar i docs official, bara uppdatera genom att ersätta och omformulera - radera endast absolut filer och filinnehåll som garanterat ALDRIG kommer att användas eller behövas.

## Uppdatera (om behov finns) Dokument för våra: Official Docs

- docs_official\*

---

## Uppdatera (om behov finns) Filer för vår: Database/Schema/Persistence

- docs_db\db_scripts\seed_static_reference_data.sql
- docs_db\db_scripts\seed_minimal_data_bootstrap.sql
- docs_db\db_scripts\init_db_schema.sql
- docs_db\db_scripts\erase_all_db_contents.sql
- mcp-server\src\main\resources\db\migration\postgresql\V1\_\_baseline_schema.sql

---

## Uppdatera (om behov finns) Dokument för: Project Breakdown

Utan att ändra på vilka Huvudsektioner (#, t.ex "# ) TECHNOLOGIES") som finns,
uppdatera följande fil utan att lägga till fluff,
du får endast ändra befintlig information t.ex ersätta expired information med korrekt och/eller relevant information:

- docs_project\[PROJECT] - [BREAKDOWN].md

---

## Uppdatera (om behov finns) Dokument för: Official Project

docs_official\docs_official_project\*

## Uppdatera (om behov finns) Dokument för: Strategy

docs\docs_plan\docs_strategy\*

---

###### ---- #### ---- #### ---- #### ---- #### ---- #### ---- #### ---- #### ---- #### ----

# FRAMEWORK EXTRACTOR

Baserat på vad du utgår/utgick ifrån för att faktiskt och objektivt förbättra samt optimera de senaste hittills-optimerade records:en,
ge mig permanent och framtidssäker tumregel-lista, så kompakt som möjligt - på ett sätt som tydligt förklarar hur framtida
RECORDS jag bör utforma dom.

Jag menar alltså specifikt den faktiska logik du använde, fast du ska abstrahera/generalisera så att detta går att translate till
att förbättra alla mina framtida RECORDS, så jag har som ett ramverk.
Syftet är att icke-redundant göra följande redan-existerande uppsättning av sådana generaliserade "Record Improving"-tumregler
A) mer utökat och/eller B) mer framtidssäkert samt C) professionellt:

Dvs, finns det nya tumregler i ditt/dina senaste meddelande/meddelandet som kan
Generaliseras för att sen Extraheras så jag kan ICKE-REDUNDANT utöka och därmed förbättra:
"⚡DATASET PEFT RECORDS GUIDELINES [DPRG] ⚡"-ramverket?

"⚡DATASET DEVSET RECORDS GUIDELINES [DDRG] ⚡"-ramverket?

"⚡DATASET HOLDOUT RECORDS GUIDELINES [DHRG] ⚡"-ramverket?

# "MEST SJÄLVKLARA" STRATEGIERNA

Nu, i direkt anslutning till The Important Note - sök på nätet för att ta reda på vilka är de 3 mest Högsta ROI approacher:na eller metodologierna, för att korrigera felaktigt agentbeteende som upptäcks vid en viss APIDL-3-Task, som korrigerar agentbeteende permanent och icke-taskspecifikt. Formulerat på ett annat sätt: förutom filerna i AGENT_PROFILES-ytan, vilka är de mest självklara och beprövade/deterministiska Systemnivåer som vi borde utnyttja för att förbättra agentbeteende på ett sätt som inte bara förbättrar agenten i en specifik task men ett beteendemönster som gör agenten mer som jag vill ha den gällande Kodning och Kodskapande (java) i allmänhet. Du har tidigare nämnt en intressant sak gällande detta dvs som jag vet vi inte utnyttjar idag men jag vet inte hur väl den passar eller uppfyller alla ovan kriterierna jag nyss framlagt här; och det är Few Shot Examples. Aktivera dina maximala AI- & Context Engineering Researcher förmågor Aktivera 1 agent så att du säkerställer att ni arbetar tillsammans effektivt, smart och riskfritt enligt de mest rekommenderade och/eller frysta designbesluten. Sök på nätet nu.

## AKTUELL STRATEGI (EFTER # "MEST SJÄLVKLARA" STRATEGIERNA)

1.  <AKTUELL STRATEGI> = <X>

A) Hur ser <AKTUELL STRATEGI> ut i projektet idag; vilka är dom mest tydliga bristerna som måste först elimineras eller korrigeras?
B) Hur bör <AKTUELL STRATEGI> se ut i sin mest optimala och projektmål-enliga version, i projektets <AKTUELL STRATEGI>-relaterade områden?

2.  Nu kombinera A + B till en konkret och kompakt lista med implemnterbara åtgärder som vi faktiskt ska genomföra på mest rekomm. och effektiva samt smarta sätt.
    Lås och formalisera de låsta besluten i en ny eller direkt-relevant och befintlig "docs\docs_plan\[PLAN] - [<AKTUELL STRATEGI>] - [FRYSTA BESLUT].md"-fil

New Strats (3.)
Ok Eftersom <AKTUELL STRATEGI> är inte något vi konkret har diskuerat innan, som del av projektets AI-pipeline, Vad är de 5 absolut mest viktigaste och relevanta sakerna att veta om <AKTUELL STRATEGI>?

---

### CLARIFICATION

Har du redan förstått och reliserat att implementerbara lösningar på/för alla identifierade "Brister" från samtliga (A) ska dokumenteras i Frysta Belsut filerna? annars måste du uppdatera dessa .md-filer. Vi ska alltså främst i följande "<AKTUELL STRATEGI>"-relaterat arbete fokusera på att Åtgärda alla (A)-brister för [NIOTUF] att sedan impl. de optimala och rekommenderade (B)-versioner genom (C)-fynd.
