# PyQt Template

This is a boilerplate for PyQt GUI applications. Copy this directory to a new app directory, then edit only the copy.

## Responsibilities

- `cmd/app.py`: application entrypoint only
- `gui/windows`: window composition and user action wiring
- `gui/widgets`: reusable display/input widgets
- `gui/viewmodels`: UI state and service orchestration
- `services`: feature-level application services
- `network`: communication input/output only
- `lifecycle`: explicit start/stop ownership
- `mocks`: test and development doubles
- `tests`: unit and smoke tests

## External I/O Rule

`MainWindow.__init__` must not start UDP, WebSocket, GStreamer, discovery, telemetry polling, watchdogs, files, subprocesses, threads, or timers.

Start external I/O only through `AppLifecycle.start()` or a specific service `start()`.

## Commands

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python -m pip install -r requirements.txt
.\\.venv\\Scripts\\python -m pytest
.\\.venv\\Scripts\\python cmd\\app.py
```

## Localty Extension Points

- Add real UDP control in `network/udp_client.py`.
- Add telemetry receiver under `network/`.
- Add GStreamer receiver behavior in `network/gstreamer_receiver.py`.
- Add widgets for video, telemetry, controls, connection state, and logs.
- Keep robot motion, physical STOP, real camera quality, and field network checks as bench or human-check evidence.

## Guardrails

- Do not update widgets directly from background threads.
- Do not put communication logic in widgets.
- Do not make services impossible to replace with mocks.
- Do not add tests that require real external I/O unless the issue test case explicitly requires it.
