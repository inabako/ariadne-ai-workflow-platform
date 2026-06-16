package lifecycle

import (
	"context"
	"testing"
)

type fakeComponent struct {
	name  string
	calls *[]string
}

func (f fakeComponent) Start(ctx context.Context) error {
	*f.calls = append(*f.calls, "start:"+f.name)
	return nil
}

func (f fakeComponent) Stop(ctx context.Context) error {
	*f.calls = append(*f.calls, "stop:"+f.name)
	return nil
}

func TestManagerStopsInReverseOrder(t *testing.T) {
	var calls []string
	manager := NewManager(
		fakeComponent{name: "first", calls: &calls},
		fakeComponent{name: "second", calls: &calls},
	)
	if err := manager.Start(context.Background()); err != nil {
		t.Fatalf("Start returned error: %v", err)
	}
	if err := manager.Stop(context.Background()); err != nil {
		t.Fatalf("Stop returned error: %v", err)
	}
	want := []string{"start:first", "start:second", "stop:second", "stop:first"}
	for i, value := range want {
		if calls[i] != value {
			t.Fatalf("call %d = %s, want %s", i, calls[i], value)
		}
	}
}
