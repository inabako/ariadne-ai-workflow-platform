package config

import (
	"testing"
	"time"
)

func TestLoadFromEnvDefaults(t *testing.T) {
	t.Setenv("SERVICE_NAME", "")
	t.Setenv("SHUTDOWN_TIMEOUT", "")

	cfg, err := LoadFromEnv()
	if err != nil {
		t.Fatalf("LoadFromEnv returned error: %v", err)
	}
	if cfg.ServiceName != "gateway-template" {
		t.Fatalf("unexpected service name: %s", cfg.ServiceName)
	}
	if cfg.HTTPAddr != ":8080" {
		t.Fatalf("unexpected HTTP addr: %s", cfg.HTTPAddr)
	}
	if cfg.ShutdownTimeout != 10*time.Second {
		t.Fatalf("unexpected shutdown timeout: %s", cfg.ShutdownTimeout)
	}
}

func TestLoadFromEnvOverrides(t *testing.T) {
	t.Setenv("SERVICE_NAME", "localty-realtime-gateway")
	t.Setenv("HTTP_ADDR", ":18080")
	t.Setenv("ENABLE_UDP_CONTROL", "false")
	t.Setenv("SHUTDOWN_TIMEOUT", "3s")

	cfg, err := LoadFromEnv()
	if err != nil {
		t.Fatalf("LoadFromEnv returned error: %v", err)
	}
	if cfg.ServiceName != "localty-realtime-gateway" {
		t.Fatalf("unexpected service name: %s", cfg.ServiceName)
	}
	if cfg.HTTPAddr != ":18080" {
		t.Fatalf("unexpected HTTP addr: %s", cfg.HTTPAddr)
	}
	if cfg.EnableUDPControl {
		t.Fatal("expected UDP control to be disabled")
	}
	if cfg.ShutdownTimeout != 3*time.Second {
		t.Fatalf("unexpected shutdown timeout: %s", cfg.ShutdownTimeout)
	}
}
