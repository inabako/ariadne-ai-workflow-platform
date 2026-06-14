package main

import (
	"context"
	"errors"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"gateway-template/internal/app"
	"gateway-template/internal/config"
	"gateway-template/internal/logger"
)

func main() {
	cfg, err := config.LoadFromEnv()
	if err != nil {
		slog.Error("configuration failed", "component", "cmd", "error", err)
		os.Exit(1)
	}

	log := logger.New(cfg.LogLevel)
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	gateway := app.New(cfg, log)
	if err := gateway.Run(ctx); err != nil && !errors.Is(err, context.Canceled) {
		log.Error("gateway stopped with error", "component", "cmd", "error", err)
		os.Exit(1)
	}
}
