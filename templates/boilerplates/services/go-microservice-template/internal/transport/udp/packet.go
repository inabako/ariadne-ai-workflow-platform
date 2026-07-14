package udp

import (
	"encoding/json"
	"fmt"
)

type Packet struct {
	Command string          `json:"command"`
	Payload json.RawMessage `json:"payload,omitempty"`
}

func ParsePacket(data []byte) (Packet, error) {
	var packet Packet
	if err := json.Unmarshal(data, &packet); err != nil {
		return Packet{}, fmt.Errorf("parse udp packet: %w", err)
	}
	if packet.Command == "" {
		return Packet{}, fmt.Errorf("udp packet command is required")
	}
	return packet, nil
}

func EncodePacket(packet Packet) ([]byte, error) {
	if packet.Command == "" {
		return nil, fmt.Errorf("udp packet command is required")
	}
	return json.Marshal(packet)
}
