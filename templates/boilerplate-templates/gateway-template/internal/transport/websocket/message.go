package websocket

import (
	"encoding/json"
	"fmt"
)

type Message struct {
	Type      string          `json:"type"`
	Command   string          `json:"command,omitempty"`
	SessionID string          `json:"session_id,omitempty"`
	Payload   json.RawMessage `json:"payload,omitempty"`
}

func ParseMessage(data []byte) (Message, error) {
	var message Message
	if err := json.Unmarshal(data, &message); err != nil {
		return Message{}, fmt.Errorf("parse websocket message: %w", err)
	}
	if message.Type == "" {
		return Message{}, fmt.Errorf("websocket message type is required")
	}
	return message, nil
}

func EncodeMessage(message Message) ([]byte, error) {
	if message.Type == "" {
		return nil, fmt.Errorf("websocket message type is required")
	}
	return json.Marshal(message)
}
