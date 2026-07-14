# Architecture

OpenLDAP is a shared directory service consumed by application and platform components through an identity connection contract.

The template owns directory runtime packaging, DN layout scaffolding, LDIF bootstrap, bind/search validation, TLS decision hooks, backup / restore hooks, and evidence collection. It does not own application authorization semantics or generated secrets.

