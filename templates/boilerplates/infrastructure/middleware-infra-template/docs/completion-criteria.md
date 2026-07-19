# Completion Criteria

Redis middleware infrastructure is complete only when:

- Docker Compose configuration is valid
- Redis starts successfully
- authenticated PING succeeds
- unauthenticated access is rejected
- SET / GET succeeds
- TTL behavior is verified
- memory and eviction settings are verified
- persistence choice is verified
- restart behavior matches the requirement
- backup / restore is verified or explicitly waived for volatile cache
- no unnecessary external exposure exists
- connection contract is available
- evidence is generated with secrets redacted

