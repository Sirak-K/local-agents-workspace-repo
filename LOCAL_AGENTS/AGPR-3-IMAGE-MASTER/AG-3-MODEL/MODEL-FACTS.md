# AGPR-3 IMAGE MASTER — MODEL FACTS

Status: Verifierade generatorfakta och vald första kvalificeringskandidat. Ingen slutlig baseline eller installation skapas genom detta dokument.

| Kandidat | Verifierad relevant kapacitet | Måste fortfarande bevisas lokalt |
|---|---|---|
| SANA-Sprint 0.6B 1024px | 0,6B diffusion transformer; 1–4 steg; 1024px; BF16; Apache 2.0 med separata Gemma-villkor för textencodern; officiell Diffusers-pipeline. | RTX 3070 Ti-VRAM, varm latens, Windows-runtime, faktisk chatbildkvalitet och revisionsföljsamhet. |
| Stable Diffusion 1.5 | Etablerad 512×512 latent diffusion med brett Diffusers/ComfyUI-ekosystem. | Faktisk chattkvalitet, optimerad generationstid och samresident director inom 8 GB. |
| SD-Turbo | Cirka 0,9B; 1–4 steg; officiellt optimerad för 512×512 och `guidance_scale=0.0`; lägre officiell kvalitet/prompt alignment än SDXL-Turbo. | Bildkvalitet för Team Masters chatbruk, faktisk VRAM/latens och paketresidency. |
| SDXL-Turbo | Cirka 3B; 1–4 steg; officiellt rekommenderad 512×512 och `guidance_scale=0.0`; starkare kvalitet/prompt alignment än SD-Turbo. | Om generator + director kan hållas operativt residenta på 8 GB utan oacceptabel offloadlatens. |

SANA-Sprint 0.6B är första kandidaten eftersom den ger en modern 1024px, fåstegsväg med lägre generatorstorlek än tidigare huvudförslag. SD-Turbo behålls som mogen reservhypotes; SDXL-Turbo och större modeller ska inte hämtas innan den mindre kandidaten underkänts.

Ingen director installeras i första kvalificeringen. Om direkt promptstyrning inte räcker får en liten director A/B-testas; dess totalminne omfattar mer än viktfilen och nyttan måste motivera extra runtime, KV-cache och offload.

Diffusers stöder model-, group- och sequential CPU offload. Offload kan minska VRAM men kan också öka latens kraftigt; den får endast användas om den bevarar AGPR-3:s no-reload-krav och acceptabel instruktion-till-bild-tid.

## Primärkällor

- SANA-Sprint 0.6B Diffusers: https://huggingface.co/Efficient-Large-Model/Sana_Sprint_0.6B_1024px_diffusers
- SANA-Sprint Diffusers: https://huggingface.co/docs/diffusers/api/pipelines/sana_sprint
- Stable Diffusion 1.5: https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5
- SD-Turbo: https://huggingface.co/stabilityai/sd-turbo
- SDXL-Turbo: https://huggingface.co/stabilityai/sdxl-turbo
- Diffusers memory optimization: https://huggingface.co/docs/diffusers/optimization/memory
