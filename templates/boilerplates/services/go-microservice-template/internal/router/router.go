package router

import (
	"log/slog"
	"net/http"

	"go-microservice-template/internal/health"
	"go-microservice-template/internal/middleware"
)

func New(service string, log *slog.Logger, ready func() bool) http.Handler {
	return middleware.RequestLogger(log, health.Handler(service, ready))
}
