package metrics

import "sync/atomic"

type Metrics struct {
	webSocketConnections atomic.Int64
	udpPacketsReceived   atomic.Int64
	errorsTotal          atomic.Int64
}

func (m *Metrics) IncWebSocketConnections() {
	m.webSocketConnections.Add(1)
}

func (m *Metrics) IncUDPPacketsReceived() {
	m.udpPacketsReceived.Add(1)
}

func (m *Metrics) IncErrors() {
	m.errorsTotal.Add(1)
}

func (m *Metrics) Snapshot() map[string]int64 {
	return map[string]int64{
		"websocket_connections": m.webSocketConnections.Load(),
		"udp_packets_received":  m.udpPacketsReceived.Load(),
		"errors_total":          m.errorsTotal.Load(),
	}
}
