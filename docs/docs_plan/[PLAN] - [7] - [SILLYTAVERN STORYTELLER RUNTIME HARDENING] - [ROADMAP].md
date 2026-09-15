# SILLYTAVERN STORYTELLER RUNTIME HARDENING — ROADMAP

| Steg | Arbetsmängd | Status | Systemplikt | Berörd Fil | Praktisk Impl. | Klarsignal |
|---:|---|---|---|---|---|---|
| 1 | Låg | Utförd | Lås extern/runtime-standard och prioritet innan implementation. | `docs_plan/FRYSTA BESLUT.md` | Separera Text/Chat Completion, non-thinking-ägare, cachebegrepp och profilgräns. | Inga centrala beslut bygger på Context Shift, shell-JSON eller caption-prioritet. |
| 2 | Låg | Pågår | Bevara bevisad baseline och skapa separat kandidatkontrakt. | `harness/` | Inventera launcher/verifierare och specificera transparent sparad profil utan att ändra baseline. | Exakta settings, ägare och negativa gränser är maskinverifierbara. |
| 3 | Medel | Pågår | Verifiering nära beteendet. | `harness/` | Härda acceptansprobe offline; implementera därefter kandidatlauncher samt template-/streamingkontroll. | Offlinekontroller PASS; ingen modellkörning krävs för strukturtesten. |
| 4 | Medel | Väntar på godkännande | Bounded vertikal A/B; skydda tidigare styrkor. | `harness/` | Kör baseline mot Chat Completion/non-thinking för flerturn, 1000–2000 ord, TTFT och total tid. | Kandidaten är nettopositiv eller klassad partial/mixed med exakt felägare. |
| 5 | Hög | Ej påbörjad | Optimera en variabelgrupp i taget med säker systemmarginal. | `harness/` | Pröva Q8 KV, 16k och vid nytta 32k; mät VRAM/RAM, stabilitet, cache och rollover. | Högsta praktiskt värdefulla stabila profil identifierad utan baseline-regression. |
| 6 | Medel | Ej påbörjad | TAR-1-profiler måste vara reproducerbara utan att bli falsk gemensam TAR-arkitektur. | `SillyTavern_UI/` | Spara godkända KoboldCpp-/SillyTavern-/samplerprofiler och dokumentera `stop/unload → load → connect/select` samt lokal `.kcpps`-export. | TAR-1:s rekommenderade profil och återställningsprofil kan väljas utan dold UI-state eller samtidig modell-/TAR-residency. |
| 7 | Låg | Ej påbörjad | Synka kritiska docs efter faktisk promotion. | `SillyTavern_UI/` | Uppdatera Guide 2, handoff, modellfakta och operativ användning med endast verifierade resultat. | Dokument, launchers, tester och faktisk runtime säger samma sak. |
