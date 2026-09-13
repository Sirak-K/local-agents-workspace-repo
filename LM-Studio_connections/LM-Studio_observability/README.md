# LM Studio evaluation-independent observability

Denna modul fångar generell LM Studio- och hostevidens utan att bedöma en modell och utan att ladda en modell. Varje invocation är tids-/storleksbegränsad och skapar exakt en unik, atomiskt uppdaterad pretty-JSON-fil. Samma `--correlation-id` kan ges till flera samtidiga strömmar så att en senare eval-run kan referera till dem utan att kopiera rådata.

## Strömmar

| Script | Loggägare | Primär källa | Viktig gräns |
|---|---|---|---|
| `capture_server_events.py` | `LM-Studio_logs/server_events/` | `lms log stream --source server --json` | Bounded tid, event och källbytes. |
| `capture_model_lifecycle_events.py` | `LM-Studio_logs/model_lifecycle_events/` | Autentiserad `GET /api/v1/models` med state-diff | Observerar load-state men tillskriver inte obelagd orsak. |
| `capture_model_io_events.py` | `LM-Studio_logs/model_io_events/` | `lms log stream --source model --filter input,output --json` | Kräver explicit känslighetsbekräftelse. |
| `capture_host_resource_snapshots.py` | `LM-Studio_logs/host_resource_snapshots/` | Avgränsad process-, serverstatus- och NVIDIA-snapshot | Ingen full processlista eller kommandorad samlas in. |

Fel stannar i ägarströmmen som vanliga strukturerade event; ingen separat `error_logs` finns. `model_evaluations/<eval-id>/` skapas tillsammans med en konkret eval och får endast innehålla evalkontrakt, run-evidens, bedömningar, REPORT SUMMARY och referenser/hashar till dessa råa captures.

## Säkerhetskontrakt

- `LM_API_TOKEN` läses endast från processmiljön och skrivs aldrig till logg.
- Bearer-värden, secret-liknande fält och undvikbara absoluta sökvägar redigeras före persistens.
- Långa strängar lagras som ordnade textbitar med längd och SHA-256 för läsbarhet utan horisontell långrad.
- Varje fil innehåller lokala och UTC-tidsstämplar, capture-/korrelations-id, källmetod, gränser, stoppskäl, räknare, händelser och explicit evidenslucka.
- CLI-loggformatet behandlas som versionskänsligt. Okända JSON-fält bevaras efter sanering.
- CLI-läsaren har högst åtta buffrade rader och 256 KiB per källrad. Alla captures har 8 MiB tak för färdig JSON, högst 300 sekunders begärd capturetid och högst 1000 events/samples. Pollintervallet får inte vara kortare än 0,5 sekunder. Källtimeout/processavslut kan lägga till en kort dokumenterad sluttid.
- Atomisk filersättning återförsöks högst sex gånger vid Windows-fil-låsning (sammanlagt högst 0,75 sekunders retryväntan); permanent låsning får aldrig döljas som framgång.
- Sanerade loggar är inte byte-exakta original. CLI-poster får SHA-256 över sina ursprungliga källbytes, och långa sanerade texter får separat hash. Filterbaserad redaction kan inte garantera att godtyckliga hemligheter i fri text upptäcks; model-I/O ska därför endast fånga kontrollerade, hemlighetsfria sessioner.
- Inga scripts anropar model load/unload eller chat. Ett `lms`-status-/loggkommando kan initialisera LM Studios lätta bakgrundstjänst men laddar inte en modell.

## Körning

Kör bara de strömmar den aktuella operationen behöver. För en framtida sammanhängande capture används samma egenvalda korrelations-id i varje kommando.

```powershell
python LM-Studio_connections/LM-Studio_observability/capture_server_events.py --duration-seconds 60 --correlation-id local-operation
python LM-Studio_connections/LM-Studio_observability/capture_model_lifecycle_events.py --duration-seconds 60 --correlation-id local-operation
python LM-Studio_connections/LM-Studio_observability/capture_host_resource_snapshots.py --duration-seconds 60 --interval-seconds 5 --correlation-id local-operation
python LM-Studio_connections/LM-Studio_observability/capture_model_io_events.py --duration-seconds 60 --acknowledge-sensitive-content --correlation-id local-operation
```

Utan angivet `--correlation-id` används capturens eget unika id. För samstämmig tidscoverage måste de valda strömmarna köras parallellt; kommandona ovan körda i följd ger separata tidsintervall. Ingen bakgrundsbevakare installeras eller autostartas. En enkel host-snapshot fås med defaultvärdet `--duration-seconds 0`. Avbrytning med Ctrl+C färdigställer filen med status `interrupted`; atomisk omskrivning bevarar senast kompletta JSON-version även vid ett oväntat avbrott. Oväntat hårt avbrott kan lämna `running` och upp till 0,5 sekund ej checkpointade CLI-event; det är ofullständig evidens, aldrig en färdig capture.

## Coverage som inte är etablerad

- Polling bevisar inte varför load/unload skedde, missar möjliga korta transitions och fångar inte automatiskt misslyckade loadförsök. CLI-serverloggen kan ge kompletterande händelser, men full runtime-/crashcoverage är inte verifierad.
- LM Studios interna chatstate, desktopchattar och godtycklig historik exporteras inte av dessa scripts.
- LM Studio-/backendversion är inte automatiskt verifierad av en CLI-version. CLI-captures registrerar CLI-versionen; nödvändiga app-/backendversioner ska bindas separat i en konkret eval-run.
- Dessa captures är generiska råkällor. Ingen kontrollerad kapacitetsbedömning eller evalspecifik sessionsarkivering är ännu genomförd av modulen.
