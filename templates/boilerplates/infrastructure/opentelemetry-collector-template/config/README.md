# Collector Configuration

`base.yaml` is the minimal Collector configuration. Generated configuration is written to `generated/collector.yaml`.

Rules:

- Component fragments define only their own receiver, processor, exporter, connector, or extension section.
- `service.pipelines` and `service.extensions` are generated from a selection manifest.
- Generated config must not contain literal secrets.
- If a configured component is not enabled in `service`, it is not considered active.
