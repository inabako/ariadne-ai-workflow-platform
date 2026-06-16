package websocket

import "testing"

func TestParseMessage(t *testing.T) {
	message, err := ParseMessage([]byte(`{"type":"command","command":"STOP","session_id":"operator-1"}`))
	if err != nil {
		t.Fatalf("ParseMessage returned error: %v", err)
	}
	if message.Command != "STOP" {
		t.Fatalf("unexpected command: %s", message.Command)
	}
}

func TestParseMessageRequiresType(t *testing.T) {
	if _, err := ParseMessage([]byte(`{"command":"STOP"}`)); err == nil {
		t.Fatal("expected missing type error")
	}
}
