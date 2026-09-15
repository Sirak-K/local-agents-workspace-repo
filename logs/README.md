# Local runtime observability evidence

`logs/` är projektets lokala rot för evaluation-oberoende runtimeevidens från de producenter som ägs av Plan 9. Denna katalog är **inte** en generell fellogg, evalmotor, artefaktlagring eller ny orkestrerare.

## Ägarskap

Producenter skapar endast sin egen rot när den faktiskt används:

- `logs/sillytavern/`
- `logs/koboldcpp/`
- `logs/dia2/`
- `logs/diffusers/`
- `logs/host/`
- `logs/github_autopull/`
- `logs/profile_orchestration/` när en konkret framtida orkestreringsproducent finns.

`LM-Studio_logs/`, evaluation-resultat och genererade story-/bild-/ljudartefakter behåller sina befintliga ägare och kopieras inte hit.

Alla genererade `logs/**/*.json` är lokala och Git-ignorerade. Denna `README.md` är tracked. Atomiska tempfiler täcks av projektets globala `*.tmp`-ignore. Skapa inte tomma owner-mappar eller `.gitkeep`-träd i förväg.

## Operatörskommandon

Kör från projektrepot. Kommandona nedan är stdlib-only och startar inga modeller, servrar, GPU-frågor eller andra processer.

### Validera captures

```powershell
python -m runtime_logging validate --root logs
```

Valideringen läser `*.json` i deterministisk pathsortering, tillämpar samma dokumentkontrakt som writers och muterar ingenting. Exit code är `0` när alla funna captures är giltiga, annars `1`. Ett saknat/tomt `logs/` är giltigt och rapporteras med noll filer.

### Fråga efter owner/correlation/failure/artifact/evidence gap

```powershell
python -m runtime_logging query --root logs --owner koboldcpp
python -m runtime_logging query --root logs --correlation-id <32-lowercase-hex>
python -m runtime_logging query --root logs --failures-only
python -m runtime_logging query --root logs --has-artifact
python -m runtime_logging query --root logs --has-evidence-gaps
```

Filter kan kombineras. Resultatet är deterministiskt sorterade, kompakta summaries med relativ capture-path, owner/stream, operation/correlation, status, tider, stop reason samt artifact-/evidence-gap-count. Rå eventpayload, prompt, response, bild eller ljud skrivs inte ut av query-kommandot.

### Förhandsgranska retention

```powershell
python -m runtime_logging prune --root logs --owner koboldcpp --dry-run
```

`prune` är medvetet **dry-run-only** i ChatGPT-fasen. Det använder den nuvarande tracked retentionpolicyn och visar en deterministisk oldest-first plan, men raderar ingenting. `running`/ofullständiga captures ingår inte i deletionplanen och senaste failure/interrupt skyddas enligt policyn. Faktisk deletion och slutliga retentiontal ägs av Codex promotionsgate efter lokal mätning.

För reproducerbara offlinegates kan `--now-epoch-ms` anges till `prune`; normal operatörsanvändning använder aktuell UTC-tid.

## Integritetsgränser

- Pretty JSON UTF-8 utan BOM är den auktoritativa captureytan.
- Varje råhändelse har exakt en primär ägare.
- Full prompt/response/media är inte default runtimeevidens; content-bearing data minimeras/hashas om inte en producer uttryckligen opt-in:ar enligt policyn.
- Secrets, credentials och osäkra absoluta paths ska aldrig råpersistens.
- Query/validate/prune-dry-run är läsande operatörsverktyg; de får inte reparera, skriva om eller tyst ignorera ogiltiga captures.
