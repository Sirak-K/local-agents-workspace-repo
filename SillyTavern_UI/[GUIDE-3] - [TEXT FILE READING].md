# GUIDE 3 — TEXT FILE READING

**Mål:** Ge AGENT-2 säker och verifierad läsförmåga för textbaserade filer utan filskrivning.

**Källor:** [SillyTavern Data Bank / RAG](https://docs.sillytavern.app/usage/core-concepts/data-bank/)

**Förutsättning:** Guide 2 = PASS.

SillyTavern stöder direkt `.md`, `.txt`, HTML, ePUB och textbaserad PDF. PDF-stödet läser textlagret; scannade bild-PDF:er hör till Guide 4.

---

# A. ChatGPT-ägd steg-för-steg guide

## A1. Lås två separata läslägen

**Läge 1 — Direct attachment:** liten fil bifogas direkt till ett meddelande. Används först för att verifiera parser + modell.

**Läge 2 — Data Bank/RAG:** större/flera dokument indexeras och relevanta chunks hämtas. Aktiveras först efter Direct-attachment PASS.

Om Direct attachment fungerar men RAG missar fakta klassas felet som retrieval/chunking/embedding tills annat bevisats.

## A2. Definiera verifieringstestet

Varje testfil ska innehålla unika, påhittade fakta som modellen inte kan gissa. Exempel:

```text
Project codename: Silver Finch.
Caretaker: Mara Venn.
Archive room: C-17.
The red key opens only the northern cabinet.
```

Frågor:

1. `What is the project codename?`
2. `Who is the caretaker?`
3. `Which room contains the archive?`
4. `What exactly does the red key open?`
5. `Answer only from the supplied document.`

ChatGPT bedömer svar mot exakt källtext.

## A3. RAG-baslinje

När Direct attachment = PASS använder vi:

- Data Bank scope: **Chat attachments** först.
- Vector Storage: `Enabled for files` = ON.
- Embedding provider: `Local (Transformers)`.
- SillyTaverns dokumenterade defaultmodell är `jina-embeddings-v2-base-en`.
- Ändra inte chunk size, overlap, score threshold och retrieve count samtidigt.

ChatGPT analyserar retrievalfel och föreslår en parameterändring åt gången.

## A4. Gate

Guide 3 = PASS när vald Storyteller-modell korrekt kan:

- läsa `.md`,
- läsa `.txt`,
- läsa en PDF med riktigt textlager,
- återfinna fakta via Data Bank från minst två dokument,
- säga att information saknas när den inte finns.

---

# B. Team Master-ägd steg-för-steg guide

## B1. Testa Direct attachment först

Skapa lokalt:

- `test.md`
- `test.txt`
- `test.pdf` med verkligt textlager

Använd A2-fakta eller motsvarande unika testdata.

I SillyTavern: bifoga **en fil direkt till ett meddelande** och ställ A2-frågorna.

Kör varje format separat.

**PASS:** modellen återger fakta korrekt utan Data Bank/RAG.

## B2. Testa två dokument samtidigt

Skapa två filer med olika unika fakta. Bifoga dem och fråga efter fakta från båda.

**STOP:** om modellen inte kan läsa direktbifogade dokument. Aktivera inte RAG ännu; skicka filformat + felutfall till ChatGPT.

## B3. Aktivera Data Bank

I SillyTavern:

1. Magic Wand -> `Data Bank`,
2. lägg in testfiler som **Chat attachments**,
3. Extensions -> `Vector Storage`,
4. aktivera `Enabled for files`,
5. välj embedding source `Local (Transformers)`,
6. låt SillyTavern hämta embeddingmodellen,
7. vänta tills filerna är vektoriserade.

Data Bank-filer används inte för RAG när file vectorization är avstängd.

## B4. Verifiera retrieval

Ställ samma faktabaserade frågor igen. Lägg även till en fråga vars svar **inte** finns i dokumenten.

Notera:

```text
Direct attachment: PASS/FAIL
Data Bank: PASS/FAIL
Formats tested:
Correct facts:
Missed facts:
Hallucinated facts:
Noticeable latency:
```

Skicka resultatet till ChatGPT vid fel.

## B5. Verkligt dokumenttest

Efter testfixture-PASS:

1. lägg in en verklig `.md` eller `.txt`,
2. testa sammanfattning + specifik faktaextraktion,
3. lägg in en textbaserad PDF,
4. upprepa,
5. använd Global/Character scope först om du faktiskt vill återanvända filen i fler chattar.

**PASS:** textfiler fungerar både direkt och via Data Bank. Fortsätt till Guide 4.