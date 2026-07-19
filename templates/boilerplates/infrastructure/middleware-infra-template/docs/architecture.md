# Architecture

Redis is a shared middleware service consumed by applications and platform components through a connection contract.

The template owns Redis runtime packaging, network isolation, persistence selection, backup / restore hooks, and evidence collection. It does not own application cache semantics, session business rules, or generated secrets.

