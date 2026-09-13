# LM Studio project-owned runtime log root

Denna rot äger endast evaluation-oberoende LM Studio-runtimeevidens. Genererade JSON-captures är lokala och Git-ignorerade; denna README beskriver den permanenta ägarstrukturen. Evalspecifik evidens och REPORT SUMMARY ägs separat av `model_evaluations/<eval-id>/`.

- `server_events/`: generella LM Studio-serverhändelser.
- `model_lifecycle_events/`: observerade model load/unload-state och förändringar.
- `model_io_events/`: explicit opt-in-capture av modellinput/-output.
- `host_resource_snapshots/`: relevanta LM Studio-processer, serverstatus och bounded hostresurser.
Fel lagras endast i den ström som äger händelsen. En separat generell fellogg eller ett separat manifest skulle duplicera sanningen och ska inte skapas. Generiska server-/modell-/hosthändelser får inte kopieras till `model_evaluations/`; de refereras med korrelations-id, tid och källfil när en eval behöver dem.

Captureimplementation och körkontrakt: [`LM-Studio_observability/README.md`](../LM-Studio_connections/LM-Studio_observability/README.md).
