package worker

import (
	"context"
	"log/slog"
	"sync"
)

type Worker struct {
	name string
	log  *slog.Logger
	stop chan struct{}
	once sync.Once
}

func New(name string, log *slog.Logger) *Worker {
	return &Worker{name: name, log: log, stop: make(chan struct{})}
}

func (w *Worker) Start(ctx context.Context) error {
	w.log.Info("worker started", "component", "worker", "worker", w.name)
	go func() {
		select {
		case <-ctx.Done():
		case <-w.stop:
		}
		w.log.Info("worker stopped", "component", "worker", "worker", w.name)
	}()
	return nil
}

func (w *Worker) Stop(ctx context.Context) error {
	w.once.Do(func() {
		close(w.stop)
	})
	return nil
}
