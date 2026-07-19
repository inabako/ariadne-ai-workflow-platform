package session

import (
	"sync"
	"time"
)

type Session struct {
	ID         string
	RemoteAddr string
	LastSeen   time.Time
}

type Store struct {
	mu       sync.RWMutex
	sessions map[string]Session
}

func NewStore() *Store {
	return &Store{sessions: make(map[string]Session)}
}

func (s *Store) Upsert(session Session) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if session.LastSeen.IsZero() {
		session.LastSeen = time.Now().UTC()
	}
	s.sessions[session.ID] = session
}

func (s *Store) Get(id string) (Session, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	session, ok := s.sessions[id]
	return session, ok
}

func (s *Store) Delete(id string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.sessions, id)
}
