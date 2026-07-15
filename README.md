# PV Engineering Platform — Phase 1

A utility-scale solar PV engineering platform. Phase 1 delivers the
foundation: authentication, organizations, projects, an equipment library,
the electrical hierarchy, and a framework-agnostic engineering engine with
structural validation. No electrical calculations yet — that's Phase 4+.

Stack: **Django 5 + PostgreSQL + Django Ninja + HTMX/Alpine + Tailwind**,
managed with `uv`, per the project's `Claude_Development_Specification`.

## What's here

- **Auth** — email-based login/signup (`apps.accounts`)
- **Organizations** — multi-tenant orgs with roles (Owner/Admin/Engineer/Viewer) and member management (`apps.organizations`)
- **Projects** — org-scoped PV projects (`apps.projects`)
- **Equipment library** — org-scoped Module, Cable, and PCS/inverter datasheets, with live HTMX search (`apps.equipment`)
- **Electrical hierarchy** — Site → PCS Instance → DC Circuit → String, plus Substations, MV Circuits, and POIs, with a full tree view and on-demand structural validation (`apps.electrical`)
- **`pv_engine`** — the framework-agnostic engineering engine (dataclasses + validation). Zero Django imports; unit-tested on its own.
- **API** — Django Ninja REST API mirroring the UI at `/api/v1/`, session-authenticated
- **122 tests** (pytest + pytest-django), **ruff** and **mypy** both clean

## Architecture

Two strict layers, per `CLAUDE.md`:

1. **Django** (`apps/*`) — persistence, auth, authorization, UI, API. Views call **services** (`apps/*/services.py`); services call `pv_engine`; results flow back up.
2. **`pv_engine`** (top-level package, not a Django app) — plain-Python dataclasses and validation functions. Never imports Django. Fully unit-testable in isolation (`pv_engine/tests/`).

```
apps/
  core/          shared abstract base models + view/form mixins
  accounts/      custom User model (email login), signup/login/logout
  organizations/ Organization, Membership (roles), permission mixins
  projects/      Project model + CRUD
  equipment/     ModuleType, CableType, PCSType (equipment *definitions*)
  electrical/    Site, PCSInstance, DCCircuit, String, Substation,
                 MVCircuit, POI (equipment *instances*, wired into a project)
pv_engine/
  equipment/     ModuleTypeSpec, CableTypeSpec, PCSTypeSpec dataclasses
  electrical/    SiteSpec, PCSInstanceSpec, ... ElectricalHierarchySpec
  validation/    equipment sanity checks + hierarchy structural validation
config/          Django settings, root urls, Django Ninja API aggregator
templates/       Django templates (Tailwind CDN + HTMX + Alpine)
```

### Key design decisions (documented here so they're easy to revisit)

- **Equipment library is org-scoped**, not a shared cross-org manufacturer
  catalog. Simpler for Phase 1; a shared catalog is a natural future
  enhancement.
- **Strings don't store individual module rows.** A `String` stores a
  `ModuleType` reference + `modules_per_string` count. At utility scale a
  plant can have hundreds of thousands of physically identical modules;
  storing one row per module would be both wasteful and wrong per the
  "derive, don't duplicate" rule. This is exactly the shape Phase 5's
  string-sizing calculations will need to consume directly.
- **Combiner boxes are a free-text tag, not a table**, for now.
  `String.combiner_identifier` records the grouping without a fake
  "instance of a definition that doesn't exist yet." `ROADMAP.md` marks
  Combiner boxes as a Phase 2 placeholder; this field can become a proper
  FK to a `CombinerType`-backed model then, without touching anything else
  in the hierarchy.
- **UUID primary keys** throughout, to avoid leaking sequential IDs across
  organizations and to keep API/URL identifiers stable.
- **`ValidationResult.__bool__` returns `is_valid`.** Convenient for `if
  result:` checks in Python, but it means Django template `{% if
  validation_result %}` is *wrong* when there are errors present (it would
  hide the report). Templates must use `{% if validation_result is not
  None %}`. Caught by `test_hierarchy_view_shows_errors_for_invalid_design`
  — worth knowing if you add another template that touches this object.

## Setup

Requires PostgreSQL running locally and [`uv`](https://docs.astral.sh/uv/).

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp .env.example .env
# edit .env: set SECRET_KEY and DATABASE_URL

# 3. Create the database (adjust to your local Postgres setup)
createdb pvplatform

# 4. Migrate
uv run manage.py migrate

# 5. Create an admin user (optional, for /admin/)
uv run manage.py createsuperuser

# 6. Run
uv run manage.py runserver
```

Visit `http://localhost:8000/`, sign up, create an organization, create a
project, add a site, and start wiring up PCS instances → DC circuits →
strings. Use "Validate design" on the hierarchy page to run structural
validation.

## Testing & code quality

```bash
uv run pytest              # 122 tests: pv_engine (pure Python) + Django apps
uv run ruff check .         # lint — clean
uv run mypy .                # type check — clean
```

`pv_engine` tests need no database at all. Django app tests use
`pytest-django` fixtures defined in the root `conftest.py` (organization
with owner/engineer/viewer memberships, a project, equipment, and a full
electrical hierarchy) so most tests stay a few lines long.

## API

Interactive docs at `/api/docs` (Django Ninja's built-in Swagger UI).
Session-authenticated — log in via the web UI first, then the same
session cookie works against `/api/v1/...`.

## What's deliberately not here yet

- Electrical calculations (string voltage/current sizing, voltage drop,
  short-circuit currents) — Phase 4+
- Full Combiner/Transformer/Switchgear equipment modeling — Phase 2
- Celery task execution (installed and configured, nothing queued yet)
- Email delivery for org invitations (members must already have an account)
