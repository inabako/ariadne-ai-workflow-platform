# DN Design Guidelines

Avoid:

- embedding one application name into the Base DN
- mixing users and groups in the same OU
- using the same account for administrators and applications
- using unstable organization names as structural DN components
- storing production secrets in LDIF

Recommended initial layout:

```text
dc=example,dc=local
  ou=people
  ou=groups
  ou=services
  ou=admins
```

Base DN and OU layout require Human Check before implementation.

