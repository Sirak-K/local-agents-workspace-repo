# SILLYTAVERN STORYTELLER RUNTIME HARDENING — FRYSTA BESLUT

Detta är TAR-1:s rollspecifika härdning under den överordnade mål- och profilgränsen i `[PLAN] - [8] - [LOCAL AI ROLE PROFILES]`. TAR-1 är den primära och normalt använda Storyteller-agent-/modellprofilen. I SillyTavern interagerar Team Master med maximalt en individuell modell/agent-karaktär åt gången; smala TAR-2/TAR-3-mediaprofiler får vara helt avlastade och behöver inte kunna chatta.

## Syfte och prioritet

- P0 är en långsiktigt stabil, snabb och reproducerbar TAR-1 Storyteller-profil för SillyTavern + KoboldCpp + den exakta DefiantFable Qwen3.5-9B Q4_K_S-modellen.
- Profiler ska sparas först efter verifiering och ska äga tydliga runtime-, SillyTavern-, sampler- och acceptansvillkor.
- Image Captioning fungerar tillräckligt bra. Caption-hardening, egna extensions och ComfyUI är uttryckligen lägst prioriterade i detta arbetsmoment.

## Bevarad baslinje

- Den verifierade Text Completion-vägen, port `5001`, context `8192`, streaming ON och dess Advanced Formatting-rollback är regressionsbaslinje.
- Baslinjen får inte ändras i stället för att skapa en separat experimentprofil.
- Tidigare lyckad streaming, flerturnskontinuitet och frånvaro av synliga template-markörer ska skyddas i regressionsmatrisen.

## Modellnative kandidatväg

- Kandidatvägen är SillyTavern Chat Completion → Custom OpenAI-compatible → `/v1` → strukturerade `messages` → KoboldCpp Jinja → GGUF:ens inbäddade Qwen-template.
- Fast non-thinking väljs i KoboldCpp `1.120` med `--jinjathink false`. Qwen3.5 använder inte `/think` eller `/nothink`.
- SillyTavern Prompt Manager äger system-/meddelandekompositionen; Text Completion Instruct Mode är inte aktiv templateägare på kandidatvägen.
- Verifiering ska läsa både `message.content` och `message.reasoning_content`. Ett markerfritt `content` räcker inte som non-thinking-bevis.

## Kontext och prestanda

- Qwen3.5/mRoPE får inte beskrivas som om vanlig KoboldCpp Context Shift fungerar. KoboldCpp stänger av den för modellen.
- Verklig återanvändning beskrivs som FastForward + hybrid SmartCache. SmartCache förlänger inte kontextfönstret och återställer inte historik som SillyTavern har trunkerat.
- `8192` + F16 KV är bevisad baslinje. Q8 KV, 16k och därefter eventuellt 32k är experimentkandidater, inte frysta rekommendationer.
- Maximal realistisk prestanda betyder bäst verifierad balans mellan kvalitet, tid till första token, total tid, VRAM-/RAM-marginal, stabilitet och långchatt — inte flest aktiverade flaggor.

## Profil- och promotionskontrakt

- Native `.kcpps` är KoboldCpps maskinspecifika sparformat och `--config` ignorerar övriga CLI-argument. Därför får ett repoägt portabelt kontrakt inte låtsas vara en maskinoberoende `.kcpps` med lokala absoluta modellvägar.
- Den första repoägda profilytan ska vara transparent och verifierbar. En lokal `.kcpps` får exporteras efter PASS för bekväm uppstart, men är inte ensam revisionskälla.
- Profilytan ska vara TAR-1-specifik tills en fungerande vertikal implementation ger evidens för vilka delar som faktiskt bör generaliseras mellan TAR-profiler.
- Ingen kandidat blir rekommenderad profil förrän den bevarar baslinjens styrkor och klarar template/non-thinking, flerturn, långoutput, prestanda och relevant kontextgate.
- Tunga modell-/GPU-körningar startas först efter Team Masters uttryckliga godkännande. Offlinevalidering och read-only inventering får köras direkt.

## Ansvarsfördelning

- Codex äger standardkontroll, kritisk profilarkitektur, lokal process-/GPU-verifiering, A/B-eval, felklassificering och slutlig promotion.
- ChatGPT-caption-handoffen är vilande och får inte utföras. Ny ChatGPT-delegering skapas först när ett självständigt, substantiellt repo-only-arbete har ett låst kontrakt och lägre koordinationskostnad än nytta.
