# Ollama Integration

`OllamaAdapter` is a narrow local model adapter. It builds a request for `/api/generate` and converts the response into `ModelResponse`.

This template does not require Ollama for tests. Keep mock adapter tests as the default and add environment-specific integration tests separately.

