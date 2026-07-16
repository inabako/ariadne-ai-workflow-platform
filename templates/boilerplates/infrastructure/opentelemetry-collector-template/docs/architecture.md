# Architecture

The template separates component packages from generated Collector configuration.

```text
selection manifest
  -> component catalog
  -> component manifests
  -> generated Collector config
  -> Terraform deployment unit
  -> health and smoke evidence
```

Runtime copies this template and registers evidence context. It does not own Collector configuration generation.
