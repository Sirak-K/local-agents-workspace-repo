# PREPARE FOR MASSIVELY IMPROVED EVALS — Roadmap

## ChatGPT-ägd implementation

| Steg | Arbetsmängd | Status | Systemplikt | Berörd Fil | Praktisk Impl. | Klarsignal |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Låg | Ej startad | Befintlig säker handoffmottagning | github_autopull_chatgpts_repo_work/*.ps1 | Rätta installerpath och docs; testa FF/dirty/divergens/stop i disponibla repos. | Befintlig watcher återanvänds; inga unsafe syncvägar. |
| 3 | Medel | Ej startad | Kanonisk evalroot efter flytt | agent-0-eval/evaluation_paths.py | Korrigera fyra Pythonrotägare, JS-imports, alla direkt berörda runners/tester; bind eval-id/run-id. | Offline imports och evidence/stop/assess/readiness/baseline rätt; ingen gammal wrapper eller omskriven historik. |
| 5 | Medel | Ej startad | Nästa teknologioberoende kontext-ERST | agent-0-eval/evaluation_contracts.py | Integrera hashbunden kontext/meddelanderoll/budget i befintlig runner; lås nästa Round 2-kontrakt och grader. | Färsk Chat; exakt deklarerat input; positiva/negativa kontraktfall gröna, ingen dold fallback. |
| 6 | Hög | Ej startad | Verklig bounded read/write | agent-0-tools/*.mjs | Implementera gemensam accesspolicy, workflowstora bounded reads och atomisk mutation; integrera worker_file_task-runner som ersättare. | Förväntad hash, allowlist, budgets och readback fungerar; gamla läs-/dispatch-/cancelprov bevaras innan ersättning tas bort. |
| 8 | Medel | Ej startad | Verkställbar tool-loop och säkra verifieringar | agent-0-eval/controlled_run.py | Integrera effektbaserad no-progress-watchdog och fast icke-tung validatoroperation utan shell/kandidatkodexekvering. | Loops stoppas med evidens; legitim återhämtning och normal completion bevaras; budgetgränser testade. |
| 11 | Hög | Ej startad | Första självvaliderande ComfyUI-slice | agent-0-eval/comfyui_workflow_grading.py | Från steg 10-underlag: unik WF-1-A-fixture, manifest, minimal domänkontext och rename-ERST med preservationgrader. | Korrekt rename PASS; fel nod/titel/extra ändring FAIL; ingen modellload/queue; end-to-end offline-evidens. |
| 12 | Hög | Ej startad | Senare grafmutationer | agent-0-eval/comfyui_workflow_validation.py | Utöka schema-/graf-/slot-/palett-/subgrafkontroller just-in-time; versionsbind små beroenden. | Kända goda fixtures och relevanta skadefall testade; okända kontrakt ger evidenslucka, inte falsk modell-FAIL. |
| 13 | Medel | Ej startad | Spårbar kandidat-skillanvändning | agent-0-skills/*/SKILL.md | Skapa 2–3 olika komplexa WORKER-skills i rollens skillyta; integrera explicit exponering/discovery. | Rätt innehåll/hash och faktisk procedur kan verifieras; ej Codex-skillaktivering. |
| 14 | Hög | Ej startad | Åtta rounds, tre ERST vardera | agent-0-eval/*_catalog.json | Integrera återstående recept/progression/graders med riktig filrunner; ComfyUI-roadmaps och ny-workflow-prov sist. | 8×3 design bevarad; exakt nästa uppgift redo; framtida fixtures skapas vid behov; inga tunga operationer. |
| 15 | Medel | Ej startad | Oberoende evidens och rapportsyntes | agent-0-eval/evaluation_contracts.py | Verifiera originalhash, retries, bedömning/evidensreferenser och REPORT SUMMARY-kompletthet; uppdatera direkt berörda docs. | Ogiltiga/assisterade försök separeras; fyra ERQER-frågeområden; inga automatiska ensamorsaksverdicts. |

Codex-ägda steg/status ägs separat av [Codex-roadmapen](<[PLAN] - [4] - [PREPARE FOR MASSIVELY IMPROVED EVALS] - [CODEX] - [ROADMAP].md>).
