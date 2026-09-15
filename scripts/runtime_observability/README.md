# Runtime observability adapters — Plan 9 Step 4

Denna yta innehåller smala ägaradapters ovanpå `runtime_logging/`. De ersätter inte profiler, processorkestrering eller Codex förbättrade lokala AutoPull-watcher.

## GitHub AutoPull

`github_autopull_capture.py` **utför inga Git-kommandon**. Den tar emot redan observerad state från den lokala FF-only-watchern och persisterar exakt en `github_autopull`-capture för ett verkligt försök eller en state change. Den ska inte anropas för varje idle poll.

Caller-kontraktet skiljer explicit på local/remote SHA, tracked clean/dirty, fetch-resultat, ancestry/fast-forward-beslut, outcome och reason. `updated` accepteras endast när tracked state är ren, fetch lyckades och ancestry är fast-forward. Denna adapter är repo-sidan av flytten bort från ad-hoc `.git/*.log`; den lokala watcher-inkopplingen måste göras mot den faktiska Codex-förbättrade implementationen och får inte gissas här.

## Host snapshot

`host_snapshot_capture.py` tar en enkel bounded snapshot för **explicit angivna relevanta PID:n**. PowerShell-frågan använder `Get-Process -Id` och gör ingen full processinventering. NVIDIA-frågan tar device-data och filtrerar compute-processrader till de relevanta PID:na. Rå command line samlas inte in.

Båda adapters skriver via den gemensamma atomiska/sanerande kärnan och skapar ingen resident watcher eller background service.
