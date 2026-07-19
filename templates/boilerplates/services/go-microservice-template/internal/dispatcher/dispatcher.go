package dispatcher

import (
	"context"
	"fmt"
)

type Event struct {
	Command    string
	Payload    []byte
	SessionID  string
	RemoteAddr string
}

type Handler func(context.Context, Event) error

type Dispatcher struct {
	handlers map[string]Handler
}

func New() *Dispatcher {
	return &Dispatcher{handlers: make(map[string]Handler)}
}

func (d *Dispatcher) Register(command string, handler Handler) {
	d.handlers[command] = handler
}

func (d *Dispatcher) Dispatch(ctx context.Context, event Event) error {
	handler, ok := d.handlers[event.Command]
	if !ok {
		return fmt.Errorf("unsupported command: %s", event.Command)
	}
	return handler(ctx, event)
}
