# Configuration application

Saving and reloading `config.yaml` report one result in the existing Settings
hint. "No application restart required" can include a short HTTP listener
restart; the desktop application itself stays open.

| Action/change | Application and feedback |
| --- | --- |
| Save | Persist first, then apply; report saved/applying until asynchronous work completes. |
| Reload from file | Run Config.init (which can publish MODE), refill, then validate the GUI fields before requesting live application. Report failure at any failed step. A published but unconfirmed MODE generation remains pending for a later same-mode save/reload retry. |
| Invalid form, write/read/parse failure | Show failure and retain the existing modal; never leave an old success visible. A reload error is not silently accepted. |
| Controls, logging, IP lists | Apply to subsequent operations/requests without restarting HTTP. Logging still follows the configured logging policy. |
| GUI language/theme | Apply live. The result is retained and translated, not erased by language changes. |
| Brightness MODE | Use the existing generation-checked background application. Clear the old software effect before switching; unrelated successful saves do not reset brightness. A failed pending generation can be retried, without clearing an already applied generation. |
| Config HOST/PORT changes while running/starting | Stop the current attempt, wait for its loop to close, then start the latest saved listener. No confirmation dialog. Rapid saves coalesce to the latest target. |
| HOST/PORT changes while stopped | Update startup defaults only; do not automatically start the service. |
| New listener fails | Try the previously running listener once. Report that the new configuration remains saved and whether the old service was restored or both attempts failed/stopped. |
| Manual stop or quit | During automatic stopping, the existing power button stays enabled as a cancel-restart action; one click cancels the queued target, duplicates are harmless. Ordinary stopping stays disabled. Quit cancels any queued restart. |
| User edits a form value again | Clear the old hint and tooltip. Results from the old operation cannot reappear. Focus alone, programmatic refill and translation do not count as edits. |

MODE meanings remain 0 = hardware-first/GUI overlay fallback, 1 = overlay-only,
2 = experimental Gamma. Abnormal termination in Gamma mode can leave a tint;
manual display calibration may be needed.

Only a **real Config HOST/PORT change** requests a restart. An unrelated save
does not replace a running manually selected bind. Detected/custom host choices,
custom IP text and an independently edited panel port are preserved. A panel
port still equal to the previous Config port follows the new default. If Config
HOST/PORT actually changes, the running service uses the **new Config bind** even
if the panel still contains an unsubmitted custom selection; its dirty indicator
continues to describe those unsubmitted panel parameters.

Automatic restart briefly disconnects clients. A changed host/port may invalidate
the old URL; use the actual listener shown in logs and the updated QR code.
`127.0.0.1`, `localhost` (local clients only) and `0.0.0.0` are supported GUI
Config bind choices. The wildcard QR uses the detected LAN IP as before.

Success is not announced before binding: the GUI worker observes the awaited
`asyncio.create_server` result on the Hypercorn serve task, resolves the requested
IPv4/localhost bind and verifies the serving socket's address, family and port.
Wildcard `0.0.0.0` must match a wildcard socket, not merely any socket on that
port. GUI port zero, IPv6 and Unix listener configurations are not supported by
this GUI confirmation path. Startup must not have already exited. Quart
`before_serving` alone is not a listen confirmation. The stopped snapshot is
sent only after the old event loop closes; the next start is queued to the Qt
worker. Listener application ends at confirmed readiness. Later health failures
update the panel state and logs only; they do not rewrite a finished or newer
save/reload hint. In-flight automatic restarts still report to the latest save
merged into that restart. Readiness is not a promise of permanent health, and
fake asyncio tests are not proof of a real Hypercorn/Windows integration.

Brightness and listener work belonging to the same save/reload are awaited
together. Unsupported platform/manager errors and restore failures are reported,
not described as "will succeed on the next request". A restart-required hint
is not a guarantee that restarting fixes drivers or Gamma calibration. Port
occupation and unavailable addresses alone report **service application
failure**, not a restart cure. Combined failures retain all reasons in the
tooltip/logs; an independent brightness/runtime restart requirement is still
shown even if binding also failed. A failed event-loop close explicitly requires
an application restart and forbids reuse of that worker.
After rollback, ordinary unchanged saves do not repeatedly retry a failed bind;
change HOST/PORT or stop/start explicitly after fixing the cause.

External file edits are applied by **Reload from file**. GUI service starts use
the already loaded configuration; they do not reread the file mid-operation.
No cross-process lock is added. Real Qt/Windows, Hypercorn and network testing
remains necessary; native IO that never returns cannot be safely killed.
