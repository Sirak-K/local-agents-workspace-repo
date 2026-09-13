# [PLAN] — GROK TO LM STUDIO SETUP — ROADMAP

Status: Aktiv plan  
Datum: 2026-09-13  
Syfte: Etablera en stabil, lågfriktions kommunikationsväg från Grok till LM Studio (vanliga appen) för Frontier-styrt utvärderingsarbete.

Detta följer det fastställda beslutet i `FINAL PLATFORM DECISION - CONCLUSIONS.md`:  
**LM Studio är primär utvärderingsplattform.** Bionic används inte för utvärdering.

---

## Övergripande strategi

Vi etablerar två komplementära vägar (i prioritetsordning):

1. **Direkt REST / OpenAI-kompatibel API** (högsta ROI för ren utvärdering)
2. **MCP-server som wrapper mot LM Studio** (när vi vill att Grok ska använda tools/list_models/load etc. via MCP-standarden)

Båda vägarna pekar mot samma Local Server: `http://127.0.0.1:1234`

---

## Steg-för-steg — Fas 0: Förberedelse (görs nu)

### 0.1 Uppdatera LM Studio
- Uppdatera till **0.4.24 (build 1)** eller senare.
- Verifiera att Local Server startar utan fel.

### 0.2 Kontrollera Local Server
- Öppna **Developer → Local Server**
- Status ska vara **Running**
- Reachable at: `http://127.0.0.1:1234`
- Bekräfta att följande endpoints syns:
  - `GET /api/v1/models`
  - `POST /api/v1/chat`
  - OpenAI-compatible: `/v1/chat/completions`, `/v1/models` etc.

### 0.3 Ladda en testmodell
- Ladda minst en modell (t.ex. Granite 4.1 3B Q4_K_M eller en liten Qwen) så att API:t kan svara.
- Notera exakt modellnyckel (t.ex. `granite-4.1-3b`).

### 0.4 (Valfritt men rekommenderat) Skapa API Token
- Gå till Server Settings → Manage Tokens
- Skapa en token med lämpliga rättigheter
- Spara den säkert (används senare vid behov)

---

## Fas 1: Direkt REST-väg (primär för utvärdering)

Detta är den enklaste och mest pålitliga vägen för prober.

### 1.1 Verifiera att API:t svarar
Kör från terminal (eller låt Grok göra det):

```bash
curl http://127.0.0.1:1234/api/v1/models
```

Förväntat: lista över tillgängliga/laddade modeller.

### 1.2 Testa chat-endpoint
```bash
curl http://127.0.0.1:1234/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DIN_MODELLNYCKEL",
    "input": "Svara bara med ordet OK",
    "temperature": 0
  }'
```

### 1.3 OpenAI-kompatibel väg (användbar från många klienter)
```bash
curl http://127.0.0.1:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DIN_MODELLNYCKEL",
    "messages": [{"role": "user", "content": "Svara bara med ordet OK"}],
    "temperature": 0
  }'
```

När dessa två fungerar är den grundläggande kommunikationsvägen etablerad.

---

## Fas 2: MCP-väg (Grok ↔ LM Studio via MCP)

Behövs när vi vill att Grok ska kunna lista modeller, ladda/avlasta, eller använda mer strukturerade tools mot LM Studio.

### 2.1 Alternativ A — Använd befintlig community MCP-server (snabbast)
Det finns färdiga MCP-servrar som wrapper LM Studio, t.ex.:
- `portertech/lm-studio-mcp-server`
- `infinitimeless/LMStudio-MCP`

Exempelkonfiguration (för Grok / Claude Desktop / andra MCP-klienter):

```json
{
  "mcpServers": {
    "lmstudio": {
      "command": "npx",
      "args": ["-y", "@portertech/lm-studio-mcp-server"],
      "env": {
        "LMSTUDIO_HOST": "127.0.0.1",
        "LMSTUDIO_PORT": "1234"
      }
    }
  }
}
```

### 2.2 Alternativ B — Tunn egen MCP-server (rekommenderas långsiktigt)
Skapa en minimal stdio-MCP-server som bara exponerar de tools vi faktiskt behöver:
- `list_models`
- `chat` / `generate`
- eventuellt `load_model` / `unload_model`

Den pekar sedan mot `http://127.0.0.1:1234`.

Detta ger full kontroll och undviker externa beroenden.

### 2.3 Lägg till i Grok
När MCP-servern körs:
- I Grok Desktop / Grok Build: lägg till som custom MCP (stdio eller HTTP beroende på implementation).
- Verifiera med `list tools` att de förväntade tools syns.

---

## Fas 3: Första kontrollerade smoke-test

När både REST och (eventuellt) MCP fungerar:

1. Ladda en känd modell i LM Studio.
2. Från Grok: skicka en deterministisk probe (`temperature=0`).
3. Verifiera att svaret kommer tillbaka korrekt.
4. Dokumentera:
   - Exakt modellnyckel
   - Använd endpoint (native `/api/v1/chat` eller OpenAI-kompatibel)
   - Sampling-inställningar
   - Eventuell MCP-tool som användes

---

## Prioriterad ordning framåt

| Prioritet | Aktivitet                              | Status     | Kommentar |
|-----------|----------------------------------------|------------|---------|
| 1         | Uppdatera LM Studio till 0.4.24+       | Pågår      | Du gör detta nu |
| 2         | Verifiera Local Server + endpoints     | Nästa      | Fas 0.2–0.3 |
| 3         | Direkt REST smoke-test                 | Hög        | Fas 1 |
| 4         | Välj/bygg MCP-wrapper                  | Medel      | Fas 2 (kan vänta) |
| 5         | Första riktiga utvärderingsprobe       | Efter 3    | IMSLE-stil |

---

## Viktiga principer (låsta)

- Utvärdering sker **inte** via Bionic.
- Vi prioriterar determinism, kontroll och scriptbarhet.
- REST-vägen är alltid tillgänglig som fallback även om MCP läggs till.
- Alla konfigurationsändringar ska vara reproducerbara och dokumenterade.

---

## Nästa konkreta handling efter uppdatering

När LM Studio 0.4.24 är installerad och Local Server körs:

1. Ladda en modell.
2. Kör de två curl-testerna i Fas 1.
3. Rapportera resultatet (fungerar / felmeddelande).

Därefter går vi vidare till antingen första riktiga probe eller MCP-wrapper beroende på behov.
