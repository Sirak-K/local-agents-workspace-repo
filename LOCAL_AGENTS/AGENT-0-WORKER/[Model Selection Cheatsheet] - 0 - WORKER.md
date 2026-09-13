# Worker Model Selection — cheatsheet

**1. Skalär-proxyer ljuger för din specifika förmåga.**
Parameterantal, aggregerat benchmark-medel, modellens allmänna rykte — alla är indirekta proxyer. Bryt ner exakt vilken smal förmåga du faktiskt behöver (t.ex. "trogen flerstegs-tool-call-exekvering under låg tvetydighet") och kräv direkt evidens för just den axeln. Ett högt totalsnitt kan dölja att just din smala förmåga är svag, och tvärtom.

**2. Extern evidens är alltid en hypotes om din harness, aldrig ett faktum om den.**
Detta gäller permanent, oavsett hur rigorös publicistens egen metod var. Ett benchmark-tal genererat under någon annans villkor (deras prompt, deras kontext, deras tool-schema) säger inget garanterat om hur modellen beter sig under dina villkor. Lokal, kontrollerad replikering är den enda evidens som räknas — inte som försiktighetsprincip, utan som en strukturell sanning om vad ett mättal faktiskt bevisar.

**3. Bedöm felets form, inte bara dess frekvens.**
För en roll som agerar (tool-anrop, kodändringar) snarare än bara konverserar är en modell som misslyckas sällan-men-tyst-och-självsäkert strikt sämre än en som misslyckas oftare men alltid synligt. Ni har redan ett konkret exempel på detta: Granites felaktiga `<tool_call>`-textutmatning var ett _högljutt_ fel — strukturellt upptäckbart, harnessen kunde se att inget verktyg triggades. Det farliga scenariot hade varit om samma modell istället hade producerat ett syntaktiskt giltigt men semantiskt fel anrop som såg ut att lyckas. Prioritera modeller (och tool-scheman) som gör fel högljudda, inte bara modeller som minimerar felfrekvens.

**4. Skilj "kan besluta" från "kan exekvera ett redan fattat beslut".**
Det här är två olika förmågeaxlar som inte rör sig tillsammans mellan modellstorlekar eller generationer. Om uppströms-planeraren (frontier-modellen) redan har löst varje omdömesfråga, ska den lokala modellen mätas specifikt på trogen exekveringsprecision under låg tvetydighet — inte på generella resonemangsbenchmarks, som slår ihop båda axlarna och därför felprissätter ditt faktiska behov åt båda hållen.

**5. Din resursgräns är ett fast filter före kvalitetsjämförelsen, inte en förhandlingsbar dimension mot kapacitet.**
Den farliga kognitiva fällan är att låta en kapacitetslockelse få dig att "tänja" på en hård gräns (exakt det ni själva kände frestelsen till vid 14B/8GB-gränsfallet). Definiera resursgränsen först, byggd på faktiskt uppmätt overhead — inte den optimistiska siffran — och filtrera kandidatmängden innan du ens börjar jämföra kapacitet. Var extra misstänksam mot varje kapacitetsargument som kräver att gränsen mjukas upp för att fungera.
