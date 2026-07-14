package app

import (
	"context"
	"errors"
	"log/slog"
	"net/http"
	"time"

	"go-microservice-template/internal/config"
	"go-microservice-template/internal/dispatcher"
	"go-microservice-template/internal/lifecycle"
	"go-microservice-template/internal/router"
	"go-microservice-template/internal/worker"
)

type App struct {
	cfg        config.Config
	log        *slog.Logger
	dispatcher *dispatcher.Dispatcher
}

func New(cfg config.Config, log *slog.Logger) *App {
	d := dispatcher.New()
	d.Register("PING", func(ctx context.Context, event dispatcher.Event) error {
		log.Info("ping received", "component", "dispatcher", "session_id", event.SessionID)
		return nil
	})
	d.Register("PONG", func(ctx context.Context, event dispatcher.Event) error {
		log.Info("pong received", "component", "dispatcher", "session_id", event.SessionID)
		return nil
	})
	d.Register("STOP", func(ctx context.Context, event dispatcher.Event) error {
		log.Warn("stop command received", "component", "dispatcher", "session_id", event.SessionID)
		return nil
	})
	return &App{cfg: cfg, log: log, dispatcher: d}
}

func (a *App) Run(ctx context.Context) error {
	healthServer := &http.Server{
		Addr:              a.cfg.HTTPAddr,
		Handler:           router.New(a.cfg.ServiceName, a.log, func() bool { return true }),
		ReadHeaderTimeout: 5 * time.Second,
	}
	manager := lifecycle.NewManager(
		worker.New("telemetry-fanout", a.log),
		worker.New("udp-packet-processing", a.log),
	)

	if err := manager.Start(ctx); err != nil {
		return err
	}
	errCh := make(chan error, 1)
	go func() {
		a.log.Info("health server starting", "component", "app", "addr", a.cfg.HTTPAddr)
		err := healthServer.ListenAndServe()
		if err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- err
			return
		}
		errCh <- nil
	}()

	select {
	case <-ctx.Done():
	case err := <-errCh:
		if err != nil {
			return err
		}
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), a.cfg.ShutdownTimeout)
	defer cancel()
	if err := healthServer.Shutdown(shutdownCtx); err != nil {
		return err
	}
	if err := manager.Stop(shutdownCtx); err != nil {
		return err
	}
	a.log.Info("gateway shutdown complete", "component", "app")
	return ctx.Err()
}
