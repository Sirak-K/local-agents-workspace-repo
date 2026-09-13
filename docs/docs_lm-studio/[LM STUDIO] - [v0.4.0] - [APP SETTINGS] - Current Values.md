# [LM STUDIO] - [APP SETTINGS]

**Inventerad:** 2026-09-13  
**Underlag:** LM Studio Settings-skärmbilder

---

## Hardware

### System

| Fält | Nuvarande värde |
|---|---|
| CPU compatibility | ✓ Compatible |
| CPU | AMD Ryzen 7 5800X 8-Core Processor |
| Architecture | x86_64 |
| CPU extensions | AVX, AVX2 |
| RAM | 31.66 GB |
| VRAM | 8.00 GB |

### GPUs

| Inställning / fält | Nuvarande värde |
|---|---|
| GPU-status | 1 GPU detected with CUDA |
| GPU | NVIDIA GeForce RTX 3070 Ti |
| GPU enabled | **ON** |
| VRAM Capacity | 8.00 GB |
| Backend | CUDA |
| deviceId | 0 |
| Limit Model Offload to Dedicated GPU Memory | **OFF** |
| Offload KV Cache to GPU Memory | **ON** |

**Limit Model Offload to Dedicated GPU Memory — OFF**  
`Allow model weights to offload to shared memory if dedicated GPU memory is full`

### Resource Monitor

| Fält | Visat värde |
|---|---:|
| RAM + VRAM | 0 GB |
| CPU | 0.00% |

### Guardrails → Model loading guardrails

| Val | Beskrivning | Nuvarande |
|---|---|---|
| OFF (Not Recommended) | No precautions against system overload | Nej |
| **Relaxed** | Mild precautions against system overload | **Ja — valt** |
| Balanced | Moderate precautions against system overload | Nej |
| Strict | Strong precautions against system overload | Nej |
| Custom | Set your own limit for maximum model size that can be loaded | Nej |

### Övriga kontroller som visas

| Kontroll | Status / text |
|---|---|
| Reset to default | Visas |
| Open in new window | Visas |
| Copy Info | Visas |
| Community | Visas |

---

## Runtime

### Runtime Selections

| Inställning | Nuvarande värde |
|---|---|
| GGUF | **CUDA 12 llama.cpp (Windows) — v2.37.0** |
| PTE | **ExecuTorch ASR (CUDA) — v0.0.8** |
| Auto-update selected Runtime Extension Packs | **ON** |
| Runtime updates channel | **Stable** |

### Engines & Frameworks

| Engine / Framework | Version | Beskrivning | Status |
|---|---:|---|---|
| CPU llama.cpp (Windows) | v2.37.0 | CPU-only llama.cpp engine | ✓ Latest version |
| CUDA 12 llama.cpp (Windows) | v2.37.0 | Nvidia CUDA 12.8 accelerated llama.cpp engine | ✓ Latest version |
| CUDA llama.cpp (Windows) | v2.37.0 | Nvidia CUDA accelerated llama.cpp engine | ✓ Latest version |
| Vulkan llama.cpp (Windows) | v2.31.2 → v2.37.0 | Vulkan accelerated llama.cpp engine | **Update available — 17.23 MB** |
| Harmony (Windows) | v0.3.6 | Chat history renderer and parser from OpenAI | ✓ Latest version |

### Filter / kontroller

| Kontroll | Nuvarande värde |
|---|---|
| Compatibility filter | **Compatible only** |
| Type filter | **All types** |
| Search | Tom |
| Check for updates | Tillgänglig |
| Vulkan release notes | 2.37.0 — Release notes |

---

## LM Link

| Inställning | Nuvarande värde |
|---|---|
| Enable LM Link | **ON** |
| Allow loading models on this machine | **ON** |
| Device identifier | **Värde visas inte i bilden** |
| Device name | **GNK** |

### Beskrivningar

| Inställning | Beskrivning |
|---|---|
| Enable LM Link | Create a secure and encrypted connection between your LM Studio devices |
| Allow loading models on this machine | When disabled, peers cannot discover or load this machine's models. |
| Device identifier | Randomly generated identifier for this device in the Link network |
| Device name | This name is shown to other devices in LM Link |

---

## Integrations

### Tool Call Confirmation

| Inställning | Nuvarande värde |
|---|---|
| Tools allowed to run without confirmation | **Inga** |

`Tools you allow to run without confirmation will appear here`

---

## Model Defaults

### Image Input

| Inställning | Nuvarande värde |
|---|---|
| Never exceed | **2048 px** |
| Begränsning aktiv | **ON** |

`Resize images such that the longest edge is no larger than the value above. Proportions are maintained.`

### Default Context Length

| Inställning | Nuvarande värde |
|---|---|
| Context length mode | **Custom value** |
| Custom value | **8192** |
| Model maximum | Ej valt |

**Custom value**  
`Set the default context length for loading new models. If the model's supported maximum context length is lower, that value will be used.`

**Model maximum**  
`Use the maximum context length supported by each model.`

### Model Loading Guardrails

| Val | Beskrivning | Nuvarande |
|---|---|---|
| OFF (Not Recommended) | No precautions against system overload | Nej |
| **Relaxed** | Mild precautions against system overload | **Ja — valt** |
| Balanced | Moderate precautions against system overload | Nej |
| Strict | Strong precautions against system overload | Nej |
| Custom | Set your own limit for maximum model size that can be loaded | Nej |

### Bypass Memory Load Warnings

#### Load Anyway

`Bypass system checks to force-load models even when resources are insufficient.`

| Val | Beskrivning | Nuvarande |
|---|---|---|
| Requires holding Alt/Option | Only loads when manually confirmed with Alt/Option. | Nej |
| **No restriction (not recommended)** | Always allows loading, even if it may cause instability or crashes. | **Ja — valt** |

---

## Chat

### Chat Settings

| Inställning | Nuvarande värde |
|---|---|
| Allow only one new empty chat | **ON** |
| When selecting a model to load, first unload any currently loaded ones | **ON** |
| Move deleted chats and folders to Trash | **OFF** |
| Double click on a chat message to edit | **OFF** |
| Show token count in chat listings | **OFF** |
| Always show prompt template in Chat sidebar | **OFF** |
| Double click chat/folder renames | **OFF** |
| Sidebar sort | **Date created** |
| Sort direction | **Desc** |

**Allow only one new empty chat**  
`Allow at most one unsaved new chat tab at a time`

**Move deleted chats and folders to Trash — OFF**  
`Chats and folders you delete will be force deleted and cannot be recovered.`

### Keyboard Shortcuts

| Inställning | Nuvarande värde |
|---|---|
| Use `Shift + Enter` to send message | **OFF** |
| Use `Ctrl + R` to regenerate the last message in chat | **ON** |

### Conversation Auto-Naming

#### AI-generated Chat Names

| Alternativ | Beskrivning | Nuvarande |
|---|---|---|
| Never | Don't create AI-generated chat names | Nej |
| **Auto** | Decides whether to create names based on generation speed | **Ja — valt** |
| Always | Create AI-generated chat names regardless of generation speed | Nej |

---

## Developer

### Developer Mode

| Inställning | Nuvarande värde |
|---|---|
| Developer mode | **ON** |

`Shows advanced controls and settings.`

### On-Demand Loading and Model TTL

| Inställning | Nuvarande värde |
|---|---|
| JIT models auto-evict | **ON** |
| Max idle TTL | **60 minutes** |

**JIT models auto-evict**  
`Ensure at most 1 model is loaded via JIT at any given time (unloads previous model)`

**Max idle TTL**  
`JIT-loaded models will be automatically unloaded after being idle for the specified duration.`

### Local LLM Service (headless)

| Inställning | Nuvarande värde |
|---|---|
| Enable Local LLM Service | **ON** |

`Use LM Studio's LLM server without having to keep the LM Studio application open`

### Runtime Settings

| Inställning | Nuvarande värde |
|---|---|
| Use LM Studio Engine Protocol | **ON** |
| Llama.cpp Engine Log Level | **Info (default)** |
| LM Studio Extension Packs Download Channel | **Stable** |
| Auto-update selected Runtime Extension Packs | **ON** |
| Auto-delete least recently used Runtime Extension Packs | **ON** |

**Use LM Studio Engine Protocol**  
`Supported for Llama.cpp. Uses the new integration architecture to enable more frequent engine updates.`

**Llama.cpp Engine Log Level**  
`Controls the log level of supported runtime engines. Applies after loading or reloading a model.`

**LM Studio Extension Packs Download Channel**  
`Update channel for engine and other runtime updates`

### Experimental Settings

| Inställning | Nuvarande värde |
|---|---|
| Show debug info blocks in chat | **OFF** |
| Show Resource Consumption Widget | **OFF** |
| Enable model load configuration support in presets | **OFF** |
| When applicable, separate `reasoning_content` and `content` in API responses | **ON** |

**Show Resource Consumption Widget**  
`Display CPU/RAM usage in the app sidebar footer`

**Separate `reasoning_content` and `content` in API responses**  
`This setting will only work for "reasoning" models such as DeepSeek R1, its distilled variants, and other models that produce CoT in <think> and </think> tags.`

---

## Appearance

### General Appearance

| Inställning | Nuvarande värde |
|---|---|
| Color Theme | **Auto** |
| Navigation Bar position | **Left** |

### Chat Style

| Inställning | Nuvarande värde |
|---|---|
| View Mode | **Markdown** |
| Show tab strip scrollbar | **OFF** |
| Font Size | **Sliderposition visas, inget numeriskt värde** |
| Font Weight | **Normal** |
| Show Gen Info | **Last message only** |
| Scroll message to top on send | **ON** |
| Auto-latch onto generating message | **OFF** |
| Chat messages style | **Bubble** |
| Expand chat container to window width | **OFF** |

### Reasoning

| Inställning | Nuvarande värde |
|---|---|
| Expand reasoning blocks by default | **ON** |
| Show reasoning block vignette | **ON** |

---

## General

### App Language

| Inställning | Nuvarande värde |
|---|---|
| App Language | **English** |

`Choose app language (still in development)`

### General Settings

| Inställning | Nuvarande värde |
|---|---|
| Open downloads pane when starting a new model download | **OFF** |
| Always open full model loader panel | **OFF** |
| My Models: always show full model file name | **OFF** |
| Use LM Studio's Hugging Face Proxy | **ON** |
| Preset confirmation | **OFF** |

**Always open full model loader panel**  
`Skip the quick picker and open the full model loader instead.`

**Use LM Studio's Hugging Face Proxy**  
`Route Hugging Face downloads through LM Studio's proxy for improved reliability and compatibility.`

**Preset confirmation**  
`Display a confirmation dialog before saving new fields to the preset.`

### Models Directory

| Inställning | Nuvarande värde |
|---|---|
| Model downloads and indexing location | `C:\Users\SSIRA\.lmstudio\models` |

### App Info

| Fält / kontroll | Visat värde |
|---|---|
| Open app logs | **Open** |
| App home directory | `C:\Users\SSIRA\.lmstudio` |
| Report bug or send feedback | **Open in browser** |
