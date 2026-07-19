package udp

import "testing"

func TestParsePacket(t *testing.T) {
	packet, err := ParsePacket([]byte(`{"command":"PING","payload":{"seq":1}}`))
	if err != nil {
		t.Fatalf("ParsePacket returned error: %v", err)
	}
	if packet.Command != "PING" {
		t.Fatalf("unexpected command: %s", packet.Command)
	}
}

func TestParsePacketRequiresCommand(t *testing.T) {
	if _, err := ParsePacket([]byte(`{"payload":{}}`)); err == nil {
		t.Fatal("expected missing command error")
	}
}
