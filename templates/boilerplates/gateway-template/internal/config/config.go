package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

type Config struct {
	ServiceName        string
	HTTPAddr           string
	WebSocketAddr      string
	UDPControlAddr     string
	UDPAnnounceAddr    string
	UDPTelemetryAddr   string
	ShutdownTimeout    time.Duration
	LogLevel           string
	EnableWebSocket    bool
	EnableUDPControl   bool
	EnableUDPAnnounce  bool
	EnableUDPTelemetry bool
}

func LoadFromEnv() (Config, error) {
	cfg := Config{
		ServiceName:        envString("SERVICE_NAME", "gateway-template"),
		HTTPAddr:           envString("HTTP_ADDR", ":8080"),
		WebSocketAddr:      envString("WEBSOCKET_ADDR", ":8081"),
		UDPControlAddr:     envString("UDP_CONTROL_ADDR", ":5005"),
		UDPAnnounceAddr:    envString("UDP_ANNOUNCE_ADDR", ":5006"),
		UDPTelemetryAddr:   envString("UDP_TELEMETRY_ADDR", ":5007"),
		ShutdownTimeout:    envDuration("SHUTDOWN_TIMEOUT", 10*time.Second),
		LogLevel:           envString("LOG_LEVEL", "info"),
		EnableWebSocket:    envBool("ENABLE_WEBSOCKET", true),
		EnableUDPControl:   envBool("ENABLE_UDP_CONTROL", true),
		EnableUDPAnnounce:  envBool("ENABLE_UDP_ANNOUNCE", true),
		EnableUDPTelemetry: envBool("ENABLE_UDP_TELEMETRY", true),
	}
	if cfg.ServiceName == "" {
		return Config{}, fmt.Errorf("SERVICE_NAME must not be empty")
	}
	if cfg.ShutdownTimeout <= 0 {
		return Config{}, fmt.Errorf("SHUTDOWN_TIMEOUT must be positive")
	}
	return cfg, nil
}

func envString(key, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}

func envBool(key string, fallback bool) bool {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	parsed, err := strconv.ParseBool(value)
	if err != nil {
		return fallback
	}
	return parsed
}

func envDuration(key string, fallback time.Duration) time.Duration {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	parsed, err := time.ParseDuration(value)
	if err == nil {
		return parsed
	}
	seconds, err := strconv.Atoi(value)
	if err != nil {
		return fallback
	}
	return time.Duration(seconds) * time.Second
}
