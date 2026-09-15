# GUIDE 4 — IMAGE MULTIMODALITY

**Mål:** Ge den valda AGENT-2-modellen lokal bildförståelse via KoboldCpp + korrekt `mmproj`, utan att förstöra den verifierade textprofilen.

**Källor:** [KoboldCpp mmproj/vision](https://github.com/LostRuins/koboldcpp/wiki) · [SillyTavern Image Captioning](https://docs.sillytavern.app/extensions/captioning/) · [Huihui Qwen3.5-9B GGUF](https://huggingface.co/mradermacher/Huihui-Qwen3.5-9B-abliterated-GGUF) · [Defiant Fable GGUF](https://huggingface.co/DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF)

**Förutsättning:** Guide 2 = PASS. Guide 3 behöver inte blockera vision, men textprofilen ska redan vara stabil.

---

# A. ChatGPT-ägd steg-för-steg guide

## A1. Identifiera exakt projector för vald modell

Team Master skickar exakt vinnande GGUF-fil.

ChatGPT verifierar därefter rätt `mmproj` mot samma modellfamilj/repository innan någon fil laddas ner.

- **Huihui:** använd endast en Qwen3.5-9B-kompatibel projector; mradermachers Huihui-repo publicerar separata `mmproj`-filer.
- **DefiantFable:** modellkortet anger att vision är aktiverad men kräver separat `mmproj`; välj projector från den verifierade Defiant/Qwen3.5-källan, inte en slumpmässig LLaVA-projector.

Projektorfakta dokumenteras endast i respektive modellmapp:

- `AG-2-MODEL-Huihui/`
- `AG-2-MODEL-DefiantFable/`

## A2. Bevara textprofilen

Vision ska vara en separat KoboldCpp-profil. ChatGPT behandlar:

- `TEXT` = verifierad Guide-2-profil utan mmproj.
- `VISION` = kopia av TEXT + exakt verifierad mmproj + eventuella VRAM-justeringar.

Vision får aldrig ersätta en fungerande textprofil före PASS.

## A3. Definiera bildtestet

Använd tre icke-känsliga lokala testbilder:

1. tydligt objekt + färg,
2. scen med flera objekt och spatial relation,
3. bild med kort, tydlig text.

Fråga exakt:

```text
1. Describe the main subject and its dominant colour.
2. List the visible objects and describe their relative positions.
3. Transcribe the clearly readable text. If any part is unclear, say so.
```

Bedöm endast sådant som faktiskt syns i bilden.

## A4. VRAM-regel

`mmproj` tar ytterligare minne. Om VISION-profilen inte ryms:

1. sänk context före aggressiv modellkvantisering,
2. sänk vid behov GPU Layers gradvis,
3. ändra en resursparameter åt gången,
4. behåll TEXT-profilen orörd.

## A5. Gate

Guide 4 = PASS först när modellen kan tolka bilder korrekt via SillyTavern/KoboldCpp och den separata TEXT-profilen fortfarande fungerar oförändrat.

---

# B. Team Master-ägd steg-för-steg guide

## B1. Ladda ner endast den verifierade mmproj-filen

Vänta på ChatGPT:s projectorval för exakt vald GGUF.

Ladda sedan ned **en** verifierad `mmproj` från den angivna källan. Lägg den lokalt tillsammans med eller nära modellfilen.

**STOP:** använd inte mmproj från annan arkitektur/familj på chans.

## B2. Skapa separat KoboldCpp VISION-profil

1. ladda den vinnande GGUF-modellen,
2. välj dess `mmproj` i KoboldCpp,
3. börja med samma inställningar som TEXT-profilen,
4. sänk initialt context till `8192` om textprofilen är högre,
5. Launch.

**PASS:** modell + projector laddas utan OOM eller projector/architecture-fel.

## B3. Konfigurera SillyTavern för lokal multimodalitet

I SillyTavern:

1. öppna `Image Captioning` i Extensions,
2. Source = `Multimodal`,
3. Provider = `KoboldCpp`,
4. använd den redan konfigurerade KoboldCpp-anslutningen,
5. lämna auto-captioning OFF under första testet.

SillyTavern kräver att multimodal modell + projections redan är laddade i KoboldCpp.

## B4. Kör kontrollerat visiontest

Kör A3:s tre bilder en i taget.

Notera:

```text
Model GGUF:
mmproj filename:
Context:
GPU layers:
VRAM:
Image 1 result:
Image 2 result:
Image 3 OCR result:
Errors:
```

**PASS:** svaren är visuellt grundade och inga uppenbara hallucinationer ersätter det synliga innehållet.

## B5. Testa vanlig chatt med bild i samma session

Efter A3-PASS:

1. skicka en bild med en vanlig fråga,
2. följ upp utan att skicka bilden igen,
3. kontrollera att modellen kan använda bildinformationen i följande turn,
4. kontrollera latency och VRAM.

## B6. Frys VISION-profilen

Spara KoboldCpp-konfigurationen separat från TEXT-profilen.

Rapportera B4-data till ChatGPT, som avgör om context/GPU Layers bör optimeras vidare.

**DONE:** AGENT-2 har separat verifierad TEXT- och VISION-runtime; textfilläsning och bildförståelse är separata kapaciteter och kan felsökas oberoende.