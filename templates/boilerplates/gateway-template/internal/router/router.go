package router

import (
	"log/slog"
	"net/http"

	"gateway-template/internal/health"
	"gateway-template/internal/middleware"
)

func New(service string, log *slog.Logger, ready func() bool) http.Handler {
	return middleware.RequestLogger(log, health.Handler(service, ready))
}
