# Clean Architecture Layout

This project now exposes explicit architecture layers without changing runtime behavior.

## Layer map

- `app/domain`
  - Domain entities and business exceptions.
  - Re-exports existing domain models from `app/models`.
- `app/application`
  - Application orchestration (use cases/services) and ports.
  - `app/application/services` re-exports existing services from `app/services`.
  - `app/application/ports` re-exports repository interfaces.
- `app/infrastructure`
  - Framework and persistence adapters.
  - `app/infrastructure/persistence/sql` re-exports SQL repositories.
- `app/interfaces`
  - External interfaces/adapters (HTTP).
  - Current FastAPI adapters are still in `app/api` for compatibility.

## Import direction

Target direction for new code:

`interfaces -> application -> domain`

and

`application -> infrastructure` only at composition boundaries (dependency wiring), not in core domain logic.

## Current compatibility strategy

To keep behavior stable and avoid breaking APIs/tests:

- Existing modules remain in place (`app/services`, `app/repositories`, `app/models`, `app/api`).
- New layer packages provide stable import paths for progressive migration.
- Composition code (`app/api/dependencies.py`, `app/api/auth_deps.py`) now imports through clean-architecture layer packages.

## Next migration steps (optional)

1. Move implementation files physically into layer folders.
2. Keep temporary re-export shims to preserve old imports.
3. Remove legacy paths once all imports are migrated.
