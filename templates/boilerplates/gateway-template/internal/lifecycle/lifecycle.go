package lifecycle

import (
	"context"
	"errors"
	"sync"
)

type Component interface {
	Start(context.Context) error
	Stop(context.Context) error
}

type Manager struct {
	mu         sync.Mutex
	components []Component
	started    []Component
}

func NewManager(components ...Component) *Manager {
	return &Manager{components: components}
}

func (m *Manager) Start(ctx context.Context) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	for _, component := range m.components {
		if err := component.Start(ctx); err != nil {
			return err
		}
		m.started = append(m.started, component)
	}
	return nil
}

func (m *Manager) Stop(ctx context.Context) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	var result error
	for i := len(m.started) - 1; i >= 0; i-- {
		if err := m.started[i].Stop(ctx); err != nil {
			result = errors.Join(result, err)
		}
	}
	m.started = nil
	return result
}
