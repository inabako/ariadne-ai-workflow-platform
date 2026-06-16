package health

import (
	"encoding/json"
	"net/http"
)

type Status struct {
	Service string `json:"service"`
	Ready   bool   `json:"ready"`
}

func Handler(service string, ready func() bool) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, Status{Service: service, Ready: true})
	})
	mux.HandleFunc("/readyz", func(w http.ResponseWriter, r *http.Request) {
		isReady := ready()
		status := http.StatusOK
		if !isReady {
			status = http.StatusServiceUnavailable
		}
		writeJSON(w, status, Status{Service: service, Ready: isReady})
	})
	return mux
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(value)
}
