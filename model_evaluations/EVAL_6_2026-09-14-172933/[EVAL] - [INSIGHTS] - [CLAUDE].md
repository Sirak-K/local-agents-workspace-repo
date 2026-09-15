Jag har bara den här report-summaryn att gå på — inte de bakomliggande `evidence.json`-filerna, transport reviews eller testloggarna. Allt nedan är alltså bedömt utifrån vad rapporten själv redovisar, inte oberoende verifierat mot rådata. Där rapporten gör en tolkning markerar jag det som tolkning, inte fastställt faktum.

## Rekommenderat beslut nu

**Ingen ny Qwen-körning ännu.** Håll ComfyUI-WORKER-frågan öppen, kör inte fler titelprov, och starta inte Round 5/7/8 förrän gränssnittet för de två noderna är omdesignat. Det minsta nya beviset som skulle ändra detta: en körning på **samma modell, samma noddata, men med explicit per-nod write-kvitto** (dvs. modellen får en bekräftelse "nod 68: skriven" / "nod 69: ej skriven" innan den avslutar) som visar att båda noderna ändras korrekt. Om det utfallet inträffar är rimligt nästa beslut att gå vidare till en enda ny, oberoende ComfyUI-uppgift (inte identisk retry) för att se om mönstret håller.

## Tre prioriterade rekommendationer

**1. Bygg om ComfyUI-uppgiftens gränssnitt till per-nod-kvitterad write, inte fri filredigering**

- Evidens: `d5fff9ca63044f929a400cfa97cc4035` och `3d1648f59c744edba3cb60dcaa8abca4` visar samma mönster två gånger (nod 68 ändrad, nod 69 inte, ändå påstådd framgång) under olika kontext/offload. Det är ett konsekvent mönster, inte en engångsslump, vilket gör det till en rimlig prioritet.
- Ägare: eval-/harnessägaren (Codex-sidan), inte modellen.
- Förväntad nytta: skiljer "modellen missar en nod" från "modellen har inget sätt att verifiera att båda skrevs" — just den distinktionen rapporten själv efterlyser.
- Risk/kostnad: måttlig — kräver ändrat verktygsgränssnitt, inte bara prompt-ändring; risk att man av misstag "läcker" facit om kvittot är för informativt.
- Minsta verifiering: en körning, samma modell, nytt gränssnitt, jämför mot de två gamla FAIL-mönstren.
- Utfall → beslut: båda noderna rätt → gå vidare till en ny oberoende ComfyUI-uppgift. Fortfarande bara en nod rätt → misstanke flyttas mot modellens instruktionsföljning snarare än gränssnittet, och det bör då testas med en enklare, mindre uppgift innan fler ComfyUI-rounds.

**2. Rätta Round 2:s gradertvetydighet (`write_summary` vs `test_write_summary`) innan den räknas i någon framtida sammanställning**

- Evidens: `b6c16d6c2d4a4b6d9da6924f3c64d2e8`.
- Ägare: evaldesign/gradern, inte modellen — rapporten säger själv att instruktionen inte specificerar exakt testmål.
- Förväntad nytta: låg kostnad, hög trovärdighetsvinst — förhindrar att en instruktionsdefekt av misstag räknas som modellfel i en framtida rullande poäng.
- Risk/kostnad: mycket låg, ren dokumentationsfix.
- Minsta verifiering: uppdatera instruktionstexten, kör om just den uppgiften en gång för att bekräfta att en rimlig modell nu kan träffa exakt mål.
- Utfall → beslut: om PASS efter fix → arkivera originalutfallet som "instruktionsdefekt, ej modellfel" (redan rapportens ståndpunkt) och stäng frågan permanent i stället för att hålla den öppen.

**3. Fastställ en uppgiftsdimensionerad kontextbudget-policy innan Round 5/7/8, snarare än att välja kontext ad hoc**

- Evidens: `d551eac709ad40d29c769e878f7258a0` visar att ett 4096-försök floppade rent tekniskt eftersom ett enda tool-resultat var ~6403 tokens — det är ett laddningsvillkorsfel, inte modelldata.
- Ägare: eval-/infrastrukturägaren.
- Förväntad nytta: förhindrar att fler körningar spenderas på att återupptäcka samma platta kontextbugg i nya uppgifter.
- Risk/kostnad: låg; kräver bara en kontroll av förväntad tool-svarsstorlek före varje ny uppgiftstyp.
- Minsta verifiering: ingen ny modellkörning krävs — det räcker att dokumentera regeln och applicera den framåt.
- Utfall → beslut: "Ingen ny körning behövs" för detta specifika fynd; det är redan känt och löst framåt (32768 användes senare).

## Svar på de fyra ERQER-frågorna

**1. Vad kunde Codex gjort bättre?** Baserat enbart på rapportens egen redovisning: 4096-förvalet för uppgift 1 borde ha kontrollerats mot en uppskattad tool-svarsstorlek innan körning, inte upptäckts efter ett floppat försök (`d551eac709ad40d29c769e878f7258a0`). Round 1-diagnostikens extra LF-byte borde ha flaggats som en avvikelse från den låsta instruktionen _innan_ körning, inte i efterhand i rapporten. Round 2-graderns tvetydighet är rimligen synlig redan vid uppgiftsdesign, inte bara efter en FAIL. Stoppet av ComfyUI-kedjan efter det andra identiska nod 68/69-mönstret (`3d1648f59c744edba3cb60dcaa8abca4`) verkar rimligt tajmat utifrån vad som redovisas — ett tredje identiskt försök hade sannolikt inte gett nytt beslutsvärde.

**2. Hur ge modellspecifik vs modellneutral insikt utan att blanda ihop harness/modell?** Det tydligaste mönstret i rapporten själv är separationen mellan "transport review" (3/3, harness-nivå) och "uppgiftsutfall" (PASS/FAIL/invalid, modellnivå) — den distinktionen bör vara strukturell i varje framtida rapport, inte något som måste rekonstrueras i efterhand av en extern läsare. En konkret regel: inget uppgiftsutfall får klassificeras förrän motsvarande harnesskomponent har ett eget, separat verifierat PASS för just den mekanismen (t.ex. write-dispatch) i samma runperiod.

**3. Icke-kosmetisk förbättring för verklighetsnära ComfyUI-arbete?** Den minsta ändringen med tydligt nytt beslutsvärde verkar vara precis den rapporten redan föreslår: ett versionsbundet, begränsat läs-/editeringsgränssnitt för de två relevanta noderna med explicita write-kvitton per nod. Det skiljer "modellen förstod uppgiften men saknade verifieringsmedel" från "modellen missade halva uppgiften trots fullständig information" — vilket dagens data inte kan skilja åt.

**4. Övriga hög-ROI-insikter, och vad som INTE bör utredas nu?** Bör inte utredas nu: fler identiska titelprov (redan beslutat), fullständiga Round 5/7/8 innan gränssnittsändringen är testad, samt en "sammanlagd modellpoäng" — rapporten själv säger korrekt att ingen sådan är försvarbar med nuvarande data. En insikt som inte täcks ovan: rapporten nämner att 85 % offload gav lägre tokenhastighet än full-GPU men flaggar själv att det inte är en kontrollerad jämförelse — det bör inte tolkas åt något håll förrän en kontrollerad A/B-körning med identisk uppgift/kontext görs, och en sådan körning är sannolikt låg prioritet just nu jämfört med gränssnittsfrågan.

## Svar på de sex återkommande beslutsfrågorna

**1. Stödda slutsatser vs Codex tolkningar?** Direkt stödda av namngivna run-id: FAIL på kodstaket i Round 1, PASS på Round 2-uppgifterna, FAIL på filskapande (`eoding` vs `encoding`), PASS på literal replacement, FAIL på B2-raden, samt nod 68/69-mönstret i ComfyUI-kedjan. Tolkningar av Codex (rimliga men inte oberoende verifierbara av mig utifrån bara denna text): att Round 1-formatfelet "inte bevisar bristande informationsförståelse", att Round 2-gradern är "tvetydig snarare än ett modellfel", och att stoppbeslutet var rätt avvägt. Dessa bör betecknas **ej oberoende verifierade** av en extern granskare tills rå evidens kan öppnas.

**2. Kunde en korrekt uppgift underkänts av instruktion/grader/harness, eller en ofullständig fått PASS?** Ja på första delen: Round 2:s `write_summary`/`test_write_summary`-skillnad är precis ett sådant fall enligt rapporten. Round 1:s extra LF-byte skulle i teorin kunna påverka en byte-känslig grader, men rapporten säger att dessa körningar redan hanterades som icke-formella diagnostikkörningar snarare än formella gates, vilket begränsar skadan. Ingen indikation i rapporten på motsatsen (ofullständig uppgift som fått PASS) — ComfyUI-fallet fick korrekt `invalid`/`fail`, inte ett felaktigt PASS.

**3. Vilka negativa fynd tillskrivs enbart Qwen?** Rimligen enbart modellen: filskapande-felet (`eoding` i stället för `encoding`) och det felaktiga framgångspåståendet i ComfyUI-svaren (modellen sade att båda noderna ändrats när bara en gjordes) — dessa är innehållsfel modellen själv producerade, inte harnessfel. Öppna/delade: B2-radutelämningen (kan vara instruktionstolkning eller modellfel — rapporten specificerar inte vilket), och nod 69-missen i sig (kan bero på otillräcklig verifieringsmöjlighet i gränssnittet, se rekommendation 1).

**4. Vilka oberoende Round 4–8-uppgifter har fortfarande högt värde?** Baserat på rapporten: Round 4:s återstående uppgifter (utöver den redan körda tvåfilsuppgiften) och Round 5 verkar oberoende av ComfyUI-spåret och kan ge värde utan att vänta på gränssnittsändringen. Stoppet av just identiska titelprov (Round 6-fortsättning) verkar korrekt avgränsat — att pausa _hela_ 8×3 vore för brett eftersom Round 4/5 testar andra förmågor (filhantering, kontextval) som redan visat blandade men informativa resultat.

**5. Enskild minsta ändring/körning med störst beslutsvärde?** Den gränssnittsändring som beskrivs i rekommendation 1 ovan: per-nod write-kvitto för ComfyUI-uppgiften. Villkor: samma modell (Qwen2.5-7B Q4_K_M), 32768 kontext, 85 % offload (samma som senast verifierade praktiska konfiguration). Resurs-/stoppbudget: samma toolanropsgräns (åtta) som redan gäller efter harnessfixen. Möjliga utfall: (a) båda noderna rätt → gå vidare till ny oberoende ComfyUI-uppgift; (b) fortsatt bara en nod rätt trots kvitto → misstanke flyttas till modellens uppgiftsföljning, testa med enklare uppgift först; (c) ny typ av fel uppstår → gränssnittet i sig behöver ytterligare iteration innan modellbeslut kan tas.

**6. Vad bör INTE göras nu?** Fler identiska titelprov (redan rapportens egen slutsats). En "sammanlagd Qwen vs Granite"-jämförelse — rapporten själv flaggar att temperatur 0 och liknande villkor inte är determinismbevis över olika installationer. En okontrollerad offload-hastighetsjämförelse (85 % vs full GPU) tills en riktig A/B-körning finns. Att skriva om Round 1:s formella FAIL eller ComfyUI:s `invalid`-status i efterhand — originalbedömningarna bör stå kvar oförändrade.
