# Component Extension

Add a component by creating a package under `receivers/`, `processors/`, `exporters/`, `connectors/`, or `extensions/`.

Required files:

- `manifest.yaml`
- `config.yaml`
- `test-config.yaml`
- `examples/`
- `tests/`
- `README.md`

Then register the component in `manifests/catalog.yaml`.
