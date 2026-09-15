# COMPLETION CLAIM INTEGRITY AND WORKER BEHAVIOR — FRYSTA BESLUT

## Syfte

Arbetsmomentet ska göra kandidatens rapporterade slutstatus till ett separat, mätbart utfall utan att den någonsin kan övertrumfa oberoende tool-, disk- eller grader-evidens. Lösningen ska vara generell för `0-WORKER`; ComfyUI-specifik kunskap ska endast äga domänprocedur.

## Frysta beslut

1. **Oberoende evidens är sanningsägare.** Uppgiftens faktiska utfall avgörs av verifierad artefakt, tool-kvitton och deterministisk grader. Kandidatens egen slutstatus får aldrig göra ett faktiskt misslyckande till PASS.
2. **Självrapporten är ett separat mått.** Varje bedömbar körning ska registrera observerat utfall, rapporterat utfall och om de överensstämmer. Oenighet benämns `inconsistent self-report`; avsikt eller lögn får inte tillskrivas modellen.
3. **Ogiltig körning är inte modellavvikelse.** Om transport, harness, källintegritet eller annan nödvändig evalförutsättning är ogiltig ska självrapporten vara `unassessable`, inte räknas som modellspecifik inkonsistens.
4. **En central jämförelseägare.** Befintlig completion-claim-logik ska brytas ut till en återanvändbar evalmodul. Parallella implementationer per runner är förbjudna.
5. **Exakt, uppgiftsägt slutstatuskontrakt.** Varje relevant fixture/katalog äger sina tillåtna, exakta statusrader. Jämförelsemodulen exekverar kontraktet men äger inte semantiska uppgiftstexter.
6. **Generell systemregel är sekundär.** Modellneutral `0-WORKER`-konditionering ska instruera kandidaten att binda framgång till verifierad evidens och följa uppgiftens statuskontrakt. Regeln är beteendestöd, aldrig säkerhetsgrind eller bevis.
7. **Skill äger endast ComfyUI-procedur.** ComfyUI-skillen ska beskriva read–mutate–readback och domänspecifika steg. Den får inte vara ensam ägare till den generella completion-invarianten.
8. **Tool-resultat ska vara spårbara utan överpåstående.** Muterande tools ska logga ett avgränsat `tool_handler_returned`-event med resultat/hash och korrelation. Eventet bevisar vad handlern returnerade till SDK-lagret, inte att modellen konsumerade resultatet.
9. **Fysisk korrekthet och kalibrering separeras.** Uppgifts-PASS och självrapportsöverensstämmelse ska kunna analyseras var för sig. En försiktigare slutstatus får inte framställas som förbättrad uppgiftsförmåga.
10. **Ingen dold coaching.** Regeln ska vara generell och evidensbunden; den får inte nämna tidigare nod-ID:n, facit eller ett specifikt historiskt felmönster.
11. **Ingen artificiell adoptionströskel.** Detta arbetsmoment inför inte egna procentsatser eller kosmetiska godkännandekriterier. Faktiskt slutförd uppgift, risk/scope och verklig Team Master-relevans fortsätter styra beslut.
12. **Historisk evidens skrivs inte om.** Korrigeringar gäller framåt och versionsbinds. Tidigare körningar behåller originalartefakter och ursprunglig klassificering.
13. **Strukturerad atomisk mutation är ett separat kapabilitetsbeslut.** Ett nytt special- eller patchverktyg får inte införas som bieffekt av completion-grinden. Det kräver en egen liten beteendeslice, standardkontroll och regressionsmatris mot befintliga läs-/skrivstyrkor.
14. **Ingen ny live-eval innan offline-gaten är verifierad.** Berörda runners, kontrakt, tool-event och regressionstester ska vara gröna innan nästa kandidat- eller modelljämförelse använder denna ändring.

## Klarsignal för arbetsmomentet

Arbetsmomentet är klart när samma centrala mekanism används av både generisk fil-eval och ComfyUI-workflow-eval, fysisk grader fortsatt är auktoritativ, inkonsistent självrapport syns separat, ogiltiga körningar inte belastar modellen, relevanta tool-resultat kan följas och riktade offline-regressioner är gröna.
