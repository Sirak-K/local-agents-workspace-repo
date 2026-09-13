# FINAL PLATFORM DECISION — CONCLUSIONS

Status: Fastställda, fundamentalt försvarsbara designbeslut.  
Datum: 2026-09-13

Dessa slutsatser ersätter tidigare antaganden om att Bionic automatiskt är den centrala plattformen för all agentrelaterad verksamhet. De skiljer tydligt mellan två olika behov.

---

## 1. Utvärderingsplattform (Frontier-styrt modellurval)

**Primärt val: LM Studio (vanliga appen / Local Model API)**

För rent Frontier-styrt utvärderingsarbete (t.ex. IMSLE, grundläggande instruktionsefterlevnad, fil-/tool-prober, konfigurationsjämförelser) är LM Studio det första och rekommenderade valet.

### Motivering
- Tillräckligt stabil och dokumenterad OpenAI-kompatibel + native REST-API.
- Låg friktion att byta modell, låsa sampling, context och template.
- Redan i drift med relevanta kandidater (Granite 4.1 3B, Lumimaid, Qwen-varianter m.fl.).
- Högre ROI än att tvinga utvärdering genom Bionic under denna fas.

### Relevanta och plausibla alternativ
Prioriteringsordning för eventuellt byte:

1. **Ollama** — starkaste kandidaten vid behov av högre scriptbarhet, lägre overhead och mer deterministisk automation.
2. **llama.cpp server** — när maximal kontroll, determinism och minimal abstraktion prioriteras.

Byte från LM Studio sker endast om konkret runtime-evidens visar att det ger tydligt högre ROI (t.ex. stabilitetsproblem, otillräcklig API-omfattning, eller väsentligt bättre automation/determinism).

**Regel:** LM Studio förblir utvärderingsplattform tills ett verifierat scenario motiverar permanent byte.

---

## 2. Bionic är legacy/deprecated

**Beslut:** Bionic är legacy/deprecated och ska inte användas som utvärderingsplattform eller parallell aktiv harness framöver.

### Motivering
- Bionics unika värde (synliga Projects/Sessions, native agent-yta, skills i Bionic-kontext) är irrelevant under ren modellutvärdering.
- Sessions/Projects-API saknas officiellt → tvingar CDP + intern IPC, vilket introducerar onödig friktion, versionskänslighet och underhållskostnad.
- Att prioritera tillgång till Sessions/Projects-API framför en stabil utvärderingsyta är fel prioritetsordning.

Utvärdering ska ske så rent och kontrollerat som möjligt genom LM Studio. Bionic ska inte återintroduceras som prioriterad plattform utan ett nytt explicit Team Master-beslut grundat i runtime-evidens.

---

## 3. Lokal agent-harness

**Fastställt val: LM Studio Desktop / Local Model API**

LM Studio-baserat Frontier-as-Evaluator-arbete och dess plattform är projektets absoluta prioritet och styrande riktning just nu.

LM Studio är projektets primära och enda aktiva harness för Frontier-agenters kommunikation med lokala agentkandidater. Native REST API v1 används för kontrollerad inferens, stateful chat när uppgiften kräver det och LM Studio-integrerade MCP-verktyg när deras faktiska kontrakt är verifierat.

Bionic är legacy/deprecated och är inte aktiv evaltransport, sessionsägare eller loggägare. Framtida användargränssnitt eller agentplattformar kan utvärderas separat, men får inte ändra den aktiva harnessen utan ett nytt explicit beslut och runtime-evidens.

---

## Sammanfattning av de centrala besluten

| Behov | Fastställt val | Kommentar |
|-------|----------------|-----------|
| Frontier-styrd modellutvärdering | **LM Studio** | Native REST API v1 är primär transport |
| Kommunikation med lokala agentkandidater | **LM Studio Desktop / Local Model API** | Enda aktiva harness |
| Första roll- och modellaudition | **0-WORKER / Granite 4.1 3B** | Liten tool-enabled kandidat prövas före höjd storleksstandard |
| Bionic | **Legacy/deprecated** | Inte aktiv evaltransport, sessionsägare eller loggägare |

Dessa beslut är evidensdrivna och separerar harness, rå observability och evalspecifik evidens. De ska inte ändras utan ny runtime-evidens eller tydligt högre ROI.
