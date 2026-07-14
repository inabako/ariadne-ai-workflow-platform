# Completion Criteria

OpenLDAP identity infrastructure is complete only when:

- Docker Compose configuration is valid
- OpenLDAP starts successfully
- Base DN exists
- required OUs exist
- test user exists
- test group exists
- group membership is resolvable
- administrator DN bind succeeds
- application bind account can search
- test user bind succeeds
- invalid password bind is rejected
- TLS behavior matches the requirement
- backup / restore is verified
- no unnecessary external exposure exists
- identity connection contract is available
- evidence is generated with secrets and real user data redacted

