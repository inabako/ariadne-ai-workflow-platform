package dispatcher

import (
	"context"
	"testing"
)

func TestDispatcherRoutesCommand(t *testing.T) {
	d := New()
	called := false
	d.Register("PING", func(ctx context.Context, event Event) error {
		called = true
		if event.SessionID != "session-1" {
			t.Fatalf("unexpected session id: %s", event.SessionID)
		}
		return nil
	})

	if err := d.Dispatch(context.Background(), Event{Command: "PING", SessionID: "session-1"}); err != nil {
		t.Fatalf("Dispatch returned error: %v", err)
	}
	if !called {
		t.Fatal("handler was not called")
	}
}

func TestDispatcherRejectsUnknownCommand(t *testing.T) {
	d := New()
	if err := d.Dispatch(context.Background(), Event{Command: "UNKNOWN"}); err == nil {
		t.Fatal("expected error for unknown command")
	}
}
