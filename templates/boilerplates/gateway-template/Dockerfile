FROM golang:1.22 AS build
WORKDIR /src
COPY go.mod ./
COPY . .
RUN go test ./...
RUN CGO_ENABLED=0 GOOS=linux go build -o /out/gateway ./cmd/gateway

FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /
COPY --from=build /out/gateway /gateway
EXPOSE 8080 8081 5005/udp 5006/udp 5007/udp
USER nonroot:nonroot
ENTRYPOINT ["/gateway"]
