Planen avser **AGPR-2-STORYTELLER**, en separat agent-/modellprofil. Maximalt en AGPR är aktiv åt gången. Rollen är en avsiktligt enkel, lokal och snabb personlig chattagent — optimerad för långa engelska fiktion-/story-konversationer snarare än agentarbete. Den behöver varken skriva filer, använda avancerade tools eller ha beständigt minne mellan sessioner.

### Målet

AGPR-2 ska främst:

- föra naturliga, längre engelska konversationer om fiktion, berättelser och roleplay,
- ha **maximal content-freedom** och så lite onödiga refusals/begränsningar som möjligt,
- kunna läsa användartillhandahållna dokument och använda relevant innehåll i samtalet,
- prioritera **snabb respons, låg turn-latens och smidig flerturnschatt** framför avancerad agentfunktionalitet,
- fungera bra på **RTX 3070 Ti 8 GB VRAM + 32 GB RAM, Windows**.

Ingen cross-session-memory krävs. Efter ungefär 50 turns är kontexttrunkering eller liknande acceptabelt.

### Vald teknisk riktning

Den försvarbara huvudstacken är:

**SillyTavern → KoboldCpp → lokal GGUF-modell**

**KoboldCpp** väljs som inferens/backend för lång flerturnschatt, GPU-kontroll, OpenAI-kompatibel Chat Completion och praktisk promptåteranvändning. För den valda Qwen3.5/mRoPE-modellen stänger KoboldCpp av vanlig **Context Shift**. Den verkliga optimeringsytan är **FastForward + hybrid SmartCache**: stabila promptprefix och återanvändbara checkpoints kan minska ombearbetning, men de förlänger inte kontextfönstret och bevarar inte historik som SillyTavern har trunkerat bort.

**SillyTavern** är chattgränssnittet eftersom det är väl anpassat för personlig chatbot/storytelling och har **Data Bank** för dokumentinmatning/RAG.

LM Studio kan fortfarande fungera som enklare reservlösning, men **Bionic är överdimensionerat för denna roll** och Open WebUI bedöms mindre optimerat för just story/chat-use-caset.

### Modellstrategin

Den aktiva kandidaten är den redan verifierade **DefiantFable Qwen3.5-9B Q4_K_S**-GGUF:en. SillyTavern `1.19.0` → KoboldCpp `1.120` → modellen fungerar redan end-to-end med streaming och flerturnskontinuitet. Den bevisade Text Completion-konfigurationen bevaras som regressionsbaslinje; den ersätts inte innan en separat modellnative Chat Completion-profil visar ett nettopositivt resultat.

Modellbyte eller tyngre quant är inte nästa steg. Först optimeras och bevisas den exakta befintliga modellen under kontrollerade profiler.

### Kontext och VRAM

Den bevisade startpunkten är **8192 tokens**, Flash Attention, F16 KV och AutoFit. Q8 KV och högre context ska prövas som separata kandidater, först 16k och därefter 32k endast om systemmarginal, stabilitet och praktisk responstid motiverar det. Maximal annonserad modellcontext är inte i sig ett lämpligt lokalt driftmål.

Om VRAM inte räcker optimeras context, KV-typ och GPU-offload i den ordningen som ger bäst verifierad helhetsnytta. Inget profilvärde markeras som rekommenderat enbart för att det teoretiskt får plats.

### Dokumentläsning

Filkapaciteten ska medvetet hållas **bred**, inte story-specifik.

Agenten bör kunna få exempelvis:

**`.md`, `.txt`, `.pdf`, HTML/ePub och annan praktiskt extraherbar text.**

SillyTaverns Data Bank används för detta. Dokument kan göras:

- globala, om de ska finnas tillgängliga hela tiden,
- eller chat-specifika, om de endast gäller en viss session.

PDF-hanteringen avser i första läget **textlagret**, inte visuell förståelse av PDF-sidor.

Det finns inget krav på kodfiler eller avancerad filsystemagent. Agenten behöver i huvudsak **läsa och använda innehåll**, inte modifiera filer.

### Multimodalitet

Multimodalitet är redan funktionellt bevisad men är uttryckligen lågprioriterad. Image Captioning, egna extensions och ComfyUI ska inte konkurrera med Storyteller-konfiguration, stabilitet, prestanda eller sparade profiler.

### Konkret implementationsordning

Den aktiva ordningen är:

1. Bevara den fungerande Text Completion-baslinjen oförändrad.
2. Skapa en separat Chat Completion-profil med backend-Jinja och `--jinjathink false`.
3. Bygg en verifierare som granskar både synligt svar och separat reasoningfält.
4. Genomför en bounded A/B för template, flerturnskontinuitet, 1000–2000 ord och cache-/latensbeteende.
5. Optimera context/KV/offload stegvis med faktisk VRAM-, stabilitets- och tidsmätning.
6. Spara endast profiler som klarar regressionsmatrisen; dokumentera SillyTavern Prompt Manager och samplers per profil.
7. Ta dokument/RAG senare och caption/extensions/ComfyUI sist.

### Kärnan i beslutet

Det här ska alltså **inte** utvecklas till ännu en avancerad tool-agent.

AGPR-2:s designfilosofi är nästan motsatsen:

> **En liten, snabb, lokal, innehållsfriare och storykompetent personlig chatbot, med bra dokumentläsning och lång flerturnschatt — och så lite runtimekomplexitet som möjligt.**

Det viktigaste experimentet är därför inte att lägga till fler funktioner, utan att först bevisa att **KoboldCpp + SillyTavern + en ~9B Qwen3.5-baserad GGUF** faktiskt ger den snabba, naturliga och långlivade chattupplevelse rollen kräver.
