Planen för **AGENT-2-STORYTELLER** är i praktiken en avsiktligt enkel, lokal och snabb personlig chattagent — optimerad för långa engelska fiktion-/story-konversationer snarare än agentarbete. Den ska vara frikopplad från **AGENT-0-WORKER** och behöver varken skriva filer, använda avancerade tools eller ha beständigt minne mellan sessioner.

### Målet

AGENT-2 ska främst:

- föra naturliga, längre engelska konversationer om fiktion, berättelser och roleplay,
- ha **maximal content-freedom** och så lite onödiga refusals/begränsningar som möjligt,
- kunna läsa användartillhandahållna dokument och använda relevant innehåll i samtalet,
- prioritera **snabb respons, låg turn-latens och smidig flerturnschatt** framför avancerad agentfunktionalitet,
- fungera bra på **RTX 3070 Ti 8 GB VRAM + 32 GB RAM, Windows**.

Ingen cross-session-memory krävs. Efter ungefär 50 turns är kontexttrunkering eller liknande acceptabelt.

### Vald teknisk riktning

Den försvarbara huvudstacken är:

**SillyTavern → KoboldCpp → lokal GGUF-modell**

**KoboldCpp** väljs som inferens/backend främst för lång flerturnschatt, GPU-kontroll och framför allt **Context Shift**, så att hela gamla konversationen inte behöver processas om vid varje ny tur.

**SillyTavern** är chattgränssnittet eftersom det är väl anpassat för personlig chatbot/storytelling och har **Data Bank** för dokumentinmatning/RAG.

LM Studio kan fortfarande fungera som enklare reservlösning, men **Bionic är överdimensionerat för denna roll** och Open WebUI bedöms mindre optimerat för just story/chat-use-caset.

### Modellstrategin

Första kandidaten behöver inte laddas ned alls:

**Huihui-Qwen3.5-9B-abliterated**, som redan finns installerad, används först för att verifiera hela runtimekedjan.

Det första testet ska alltså avgöra om:

- KoboldCpp fungerar korrekt,
- full eller nästan full GPU-offload fungerar,
- hastigheten är acceptabel,
- längre konversationer fungerar,
- SillyTavern-integrationen fungerar,
- dokument kan tillföras genom Data Bank.

Därefter är den primära alternativa kandidaten:

**Qwen3.5-9B “Defiant Fable” Heretic/Uncensored**, eftersom den bygger på ungefär samma kapacitetsklass men är mer explicit tränad för **fiction/prosa/roleplay** snarare än vanlig instruct-chat.

Den lämpliga kvantiseringen för 8 GB VRAM är ungefär **Q4_K_S** snarare än en tyngre quant, för att lämna utrymme åt kontext/KV-cache.

Det betyder att modellen inte ska bytas innan själva plattformen är verifierad. Huihui fungerar som **runtime-baslinje**, därefter kan Defiant Fable jämföras på faktisk story-/chatkvalitet.

### Kontext och VRAM

Startpunkten är ungefär:

- **12 288–16 384 tokens context**
- **Flash Attention**
- **Q8 KV-cache / `quantkv 1`**
- så mycket **GPU-offload** som 8 GB VRAM tillåter.

KoboldCpp Context Shift ska sedan hantera att äldre konversation gradvis faller ur när kontexten fylls. Det betraktas här som ett avsiktligt beteende, inte som ett problem som måste lösas med permanent memory.

Om VRAM inte räcker ska man först optimera context/KV/offload snarare än att automatiskt bygga en komplicerad CPU-offload-arkitektur. En lägre modellquant är också ett möjligt senare steg.

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

Multimodalitet är **relevant men uttryckligen fas 2**.

Först ska textchatten bevisas fungera bra.

Därefter kan en lämplig **`mmproj`** kopplas in för bildförståelse. Det är därför rimligt att ha mmproj-filen nedladdad redan från början, men inte ladda den under den initiala textutvärderingen eftersom den inte behövs för vanlig dokumenttext.

### Konkret implementationsordning

Den frysta planen är alltså:

1. **Installera senaste CUDA-KoboldCpp på Windows.**
2. **Starta med redan installerade Huihui-Qwen3.5-9B-abliterated.**
3. Konfigurera **CuBLAS/CUDA, maximal GPU-offload, Flash Attention, cirka 12–16k context och Q8 KV-cache**.
4. Testa modellen först direkt genom KoboldCpp/Kobold Lite och verifiera faktisk GPU/VRAM-användning och responsivitet.
5. **Installera SillyTavern** och anslut det till KoboldCpp på localhost.
6. Skapa endast den minimala persona/systemkonfiguration som behövs för en personlig storyteller-chatbot.
7. Testa längre flerturnschatt.
8. Testa **Data Bank** med verkliga `.md`, `.txt` och `.pdf`.
9. När runtimekedjan fungerar: jämför Huihui med **Defiant Fable**.
10. Först när textagenten är godkänd: börja experimentera med **mmproj/multimodalitet**.

### Kärnan i beslutet

Det här ska alltså **inte** utvecklas till ännu en avancerad tool-agent.

AGENT-2:s designfilosofi är nästan motsatsen:

> **En liten, snabb, lokal, innehållsfriare och storykompetent personlig chatbot, med bra dokumentläsning och lång flerturnschatt — och så lite runtimekomplexitet som möjligt.**

Det viktigaste experimentet är därför inte att lägga till fler funktioner, utan att först bevisa att **KoboldCpp + SillyTavern + en ~9B Qwen3.5-baserad GGUF** faktiskt ger den snabba, naturliga och långlivade chattupplevelse rollen kräver.
