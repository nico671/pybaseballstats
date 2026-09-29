# Public API hardening: release notes draft

Release version and date are not set. This file describes local changes and is not a publication record.

- Source modules now export fetch functions only. Team enums moved to `pybaseballstats.enums`. Existing enum classes keep their identity. `GUARDIANS` and `DIAMONDBACKS` are preferred names; old spellings remain aliases. Umpire Scorecards adds `TIGERS=DET`.
- `umpire_scorecards.game_type_options()` was removed. The game type codes are in the [usage guide](../usage_docs/umpire_scorecards.md).
- Wrong argument types now raise `TypeError`; invalid values raise `ValueError`. Request, browser, parsing, and required-source-structure failures inside package calls raise `RuntimeError`, with an underlying cause where one exists.
- Valid no-match responses return empty results of the documented type. Umpire name matching is exact. A missing umpire never expands a query to all umpires. Failed Statcast chunks and Retrosheet shards fail the full request.
- Statcast header-only CSV results keep their columns. Pitch-by-pitch functions return a `LazyFrame` by default, or a `DataFrame` with `force_collect=True`. A later lazy `.collect()` can raise a Polars exception.
- Arm strength, catcher pop time, pitch arsenals, and pitch movement resolve omitted seasons to the current year when called. Explicit season arguments keep their meaning.
- Working fetch function paths and parameter names remain the same. Private implementation module paths and function pickle locations are not supported.

See the [migration guide](public-api-migration.md) for exact import changes.
