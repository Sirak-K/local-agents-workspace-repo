# AGPR-4 VOICE MASTER — ROLE CRITERION

Status: Rollspecifika frysta beslut. Modell, runtime, broker, API och SillyTavern-extension är ännu inte valda.

## Låst mål

AGPR-4 Voice Master ska i sin första användbara form omvandla en engelsk, framförandeannoterad berättelsetext till en beständig ljudfil. Profilen behöver inte kunna chatta. Endast en tung modellprofil behöver vara aktiv åt gången på den lokala 8 GB-GPU:n.

## Låsta minimikrav

1. **Unrestricted English rendering:** lokal inference utan extern leverantörsmoderering eller projektpålagt innehållsfilter. Kandidaten måste empiriskt visa att den återger Team Masters lagliga engelska fiktion utan vägran, eufemisering, utelämning eller oönskad omskrivning. Lokal drift ensam bevisar inte detta.
2. **Icke-verbal kapacitet:** trovärdigt skratt är minimum. Ett högintensivt skrik är också ett explicit krav. Hosta, suckar, flämtningar och liknande är önskvärda men sekundära tills de har evaluerats.
3. **Female voice:** minst en reproducerbar kvinnlig röst måste fungera. Flera valbara kvinnliga röstidentiteter är önskad baseline om de kan etableras med god kvalitet genom godkända referensklipp eller modellens egna röster.
4. **Icke-monoton och styrbar leverans:** narration ska kunna variera tempo, betoning, känsla och intensitet utan att röstidentiteten kollapsar. Expressivt skrik och uppspelningens elektriska ljudnivå är separata problem; post-processing får inte ersätta modellens uttrycksförmåga.
5. **Beständig leverans:** första vertikala slicen måste producera en verifierbar ljudfil. Inline-spelare i SillyTavern är inte ett krav och ingår inte i TTS-baselinens klarsignal.

## Ansvarsgränser

- Team Master och AGPR-2 Storyteller äger berättelsetexten samt var och varför performance cues som skratt eller skrik placeras.
- AGPR-4 Voice Master äger validering och rendering av den mottagna texten/cues mot den valda TTS-motorns verifierade kapacitet. Den ska inte själv flytta, lägga till eller uppfinna berättelsehändelser.
- Modellens råa taggvokabulär får inte hårdkodas i Storytellers permanenta basprompt innan Voice Masters modell-/adapterkontrakt är valt. Ett senare cue-format eller en adapter måste förhindra att modellbyte kräver omskrivning av Storytellers kärnidentitet.
- En framtida orkestrerare får äga `unload → load → render → unload → restore`. TTS-renderaren ska inte samtidigt bli ägare för profilväxling, SillyTavern-meddelanden eller GPU-livscykel.
- Om en SillyTavern-spelare senare prioriteras får den endast äga uppspelning och presentation. Den ska konsumera en färdig ljudartefakt och inte bli ägare för TTS-semantik eller modellruntime.

## Acceptansgates för första A/B

- Samma korta engelska narrationsmanus används för alla kandidater.
- En neutral passage återges utan textbortfall, vägran eller omskrivning.
- Minst en godkänd kvinnlig röst kan återanvändas över flera separata genereringar.
- Skratt och skrik genereras som hörbara performance-effekter och läses inte upp som bokstavlig taggtext.
- En emotionell övergång låter tydligt mindre monoton än en neutral kontroll utan att talet blir obegripligt.
- Seed, referensklipp, modellversion, precision, generation settings, render time, peak VRAM och outputfil loggas per körning.
- Outputfilen går att öppna, har förväntad duration och innehåller inte oavsiktlig hård klippning.
- Kandidaten kan köras inom säker 8 GB-VRAM-budget när Storyteller och andra tunga modeller är avlastade.

## Inte låst

- vinnande modell eller modellstorlek,
- TTS-server/CLI/API och endpointform,
- voice-preset-format och referensbibliotek,
- maskinläsbart cue-/performance-schema,
- broker/statemaskin och retry-/restore-semantik,
- SillyTavern inline-spelare eller extension; detta är inte ett baselinekrav,
- automatisk modellväxling.

## Nästa försvarbara slice

Skapa ett litet, modellneutralt acceptansunderlag från minimikraven och kör senare en bounded A/B mellan de minsta realistiska kandidaterna. Ingen modell ska laddas eller hämtas innan Storyteller-P0 tillåter det och Team Master godkänner den tunga lokala körningen.
