.PHONY: run test lint build docker-build docker-up docker-down

run:
	go run ./cmd/gateway

test:
	go test ./...

lint:
	go vet ./...

build:
	go build ./cmd/gateway

docker-build:
	docker build -t gateway-template:local .

docker-up:
	docker compose up --build

docker-down:
	docker compose down
