# NARRATIVE/STORY TEXT TO --> IMAGE TO --> VIDEO PRODUCTION BLUEPRINT (Skapa Bilder --> till Videos baserat på Berättelser)

## STORY COMPOSITION PLAN

### `1 INTER-KF-Interval` (= 2 KEYFRAMES) = `6s`

### `1 SEGMENT` = `2 INTER-KF-Intervals` (= 3 KEYFRAMES) = `12s`

### `1 SEGMENT` = 12s

### `2 SEGMENTS` = 24s

#### MINST `2 SEGMENTS` = `1 SCENE/VIDEO-CLIP`

### `3 SEGMENTS` = 36s

### `4 SEGMENTS` = 48s

#### MINST `4 SEGMENTS` = `2 SCENES/VIDEO-CLIPS`

### `1 SCENE` = More than `2 SEGMENTS` = 24s>

### More than 2> segments = 1 Scen (term. context: narrative/abstract)

(om existerar som ett koncept)

### More than 2> segments = 1 Clip (term. context: technical/videos)

(om existerar som en faktisk videofil)

---

# Prompt-Realized - Actual Desired Bionic-Generated Textual Target-Format:

```
SEGMENT-1-PROMPTS (Stycke 0-100 ord från full story:n)
(Första Prompt-realiserbara delen i en Full-version Story, t.ex dom första 100 orden i en Full-version Story används som derivat för SEGMENT-1-PROMPTS)

WF-1-A
<Keyframe-specific Prompt for REFERENCE PRODUCTION>

WF-2-A
<Keyframe-specific Prompt for SHARED VISUAL CONTINUITY>
<Keyframe-specific Prompt for START>
<Keyframe-specific Prompt for MID>
<Keyframe-specific Prompt for END>

WF-3
(.. osv för samtliga prompt-noder vars prompt-fält som ska och kan ta emot text.)

---

SEGMENT-2-PROMPTS (Stycke 100-200 ord från full story:n)

WF-1-A
<Keyframe-specific Prompt for REFERENCE PRODUCTION>

WF-2-A
<Keyframe-specific Prompt for SHARED VISUAL CONTINUITY>
<Keyframe-specific Prompt for START>
<Keyframe-specific Prompt for MID>
<Keyframe-specific Prompt for END>

WF-3
.. osv för samtliga prompt-noder vars prompt-fält som ska och kan ta emot text.

---

SEGMENT-3-PROMPTS
..
...




```

Notera, en .md-fil eller någon annan mer hög ROI filtyp ska genereras, det som jag la in som <placeholder> är faktiska ComfyUI-prompts som Bionic-modellen ska skapa, BASERAT PÅ Full versionen av story:n. Så bionic-modellen måste ha förmågan att bearbeta Full-texten på ett sätt som gör att den kan skapa dom bästa KF-specifika promptsen.

Detta innebär att modellen måste förstå exakt hur varje prompt-nod förväntar sig att prompt-texter är strukturerade.

Utöver det så behöver såklart inte alla prompt-noder ta hela de 100 orden av en Segment inom Prompt-Realized-kontextet, utan dom 100 orden styr hur Comfyui ska visuellt representera Segment 1 (12sek), genom mer än ett workflow men koherent.

# SCENE/SEGMENT COMPOSITION PLAN

## Technical Relations

WF-1-A's [OUTPUT] = WF-1-B's [INPUT]
WF-1-B's [OUTPUT] = WF-2-A's [INPUT]
WF-2-A's [OUTPUT] = WF-3's [INPUT]
WF-2-B's [OUTPUT] = WF-3's [INPUT]
WF-3's [OUTPUT] = WF-4's [INPUT]
WF-4's [OUTPUT] = WF-5's [INPUT]

---

## Temporal Transition Plan

Exempel:

```
SEG-1-KF-(A) <-- FIRST REFERENCE PRODUCT, NOT INHERITED
SEG-1-KF-B
SEG-1-KF-[C] --> TO BE INHERITED
<-->
SEG-1-KF-[C] <-- IS INHERITED REFERENCE PRODUCT
SEG-2-KF-B
SEG-2-KF-[C] --> TO BE INHERITED
<-->
SEG-2-KF-[C] <-- IS INHERITED REFERENCE PRODUCT
SEG-3-KF-B
SEG-3-KF-[C] --> TO BE INHERITED
<-->
SEG-3-KF-[C] <--  IS INHERITED REFERENCE PRODUCT
SEG-4-KF-B
SEG-4-KF-[C]

... OSV

```

---

WF-1-A) T2I - REF. PROD.
WF-1-B) I2I - REF. EDIT
WF-2-A) I2I - KEY. PROD. - REFERENCE-GUIDED
WF-2-B) T2I - KEY. PROD. - PURE
WF-3) I2V - SEG. PROD.
WF-4) V2V - ASSEMBLY
WF-5) V2V - UPSCALE
