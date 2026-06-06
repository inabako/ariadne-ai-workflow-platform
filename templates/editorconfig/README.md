# EditorConfig Template

Use `target-repository.editorconfig` when a target repository shows mojibake or has no encoding policy.

The template keeps source files UTF-8 by default, but does not force `.bat` / `.cmd` files to UTF-8 because Windows batch files may intentionally use Shift_JIS.

`.editorconfig` stabilizes future reads and edits, but it does not repair files that were already saved with mojibake. If non-ASCII text remains unstable after reloading, use stable ASCII anchors or temporary ASCII markers for the narrow edit, then remove temporary markers before completion.
