# Redis Configuration

Redis configuration is selected from the requirement document and Terraform variables.

Required decisions:

- purpose: cache, session, temporary-state, distributed-lock, rate-limit, pubsub, or queue-helper
- version
- connection source
- external exposure
- authentication secret reference
- maxmemory
- maxmemory-policy
- persistence mode: none, rdb, aof, or rdb-aof
- default TTL
- backup / restore test
- evidence output

Human Check is required when:

- session data may be evicted by an allkeys policy
- Pub/Sub needs replay or strict delivery
- TLS is required but certificate source is not defined
- persistence is disabled for non-cache data

