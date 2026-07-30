# Storage

The template includes `SQLiteJobStore` as a local durable baseline.

Use SQLite for local development and single-node runs. Move to PostgreSQL or another shared store only when multiple runtime processes need coordinated state.

