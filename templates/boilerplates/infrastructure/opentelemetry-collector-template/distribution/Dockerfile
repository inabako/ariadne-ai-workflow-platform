FROM otel/opentelemetry-collector-builder:0.156.0 AS builder
WORKDIR /build
COPY builder-config.yaml /build/builder-config.yaml
RUN ocb --config=/build/builder-config.yaml

FROM alpine:3.20
RUN apk --no-cache add ca-certificates
COPY --from=builder /build/build/ariadne-otelcol/ariadne-otelcol /otelcol/ariadne-otelcol
ENTRYPOINT ["/otelcol/ariadne-otelcol"]
CMD ["--config=/etc/otelcol/config.yaml"]
