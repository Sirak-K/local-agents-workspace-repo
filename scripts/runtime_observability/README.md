# Runtime observability adapters — Plan 9 Step 4

Denna yta innehåller smala ägaradapters ovanpå `runtime_logging/`. De ersätter inte profiler, processorkestrering eller Codex förbättrade FF-only AutoPull-design.

## GitHub AutoPull

`github_autopull_capture.py` **utför inga Git-kommandon**. Den tar emot redan observerad state från den befintliga `scripts/github_autopull_chatgpts_repo_work/main_autopull_watcher.ps1` och persisterar exakt en `github_autopull`-capture när watcherns deduplicerade state faktiskt ändras. Idle polls med oförändrad state skapar därför ingen ny capture.

Den spårade watchern behåller sina befintliga säkerhetsgates: endast branch `main`, fetch till `origin/main`, tracked-dirty skip, pågående Git-operation skip, untracked-collisionkontroll, race guard, ancestry-kontroll och `merge --ff-only`. Observability-anropet är best-effort och får inte bli en ny gate för Git-säkerheten.

Caller-kontraktet skiljer explicit på local/remote SHA, tracked clean/dirty, fetch-resultat, ancestry/fast-forward-beslut, owner-local decision, outcome och reason. Specialfallen `updated`, `up_to_date`, `skipped_dirty`, `skipped_non_fast_forward` och `fetch_error` fail-closed-valideras; övriga befintliga watcher-säkerhetsstates kan fortfarande representeras utan att pressas in i en falsk universell state machine.

`install_main_autopull.ps1` använder fortsatt samma startup-/lock-/stopmodell men flyttar operativ evidens från `.git/main-autopull*.log` till `logs/github_autopull/`. Gamla textloggar migreras inte till den nya råsanningen.

## Host snapshot

`host_snapshot_capture.py` tar en enkel bounded snapshot för **explicit angivna relevanta PID:n**. PowerShell-frågan använder `Get-Process -Id` och gör ingen full processinventering. NVIDIA-frågan tar device-data och filtrerar compute-processrader till de relevanta PID:na. Rå command line samlas inte in.

Båda adapters skriver via den gemensamma atomiska/sanerande kärnan. Host-adaptern skapar ingen resident watcher; AutoPulls redan befintliga watcher förblir den enda ägande pollprocessen för Git-synk.
