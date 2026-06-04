# pytest-test-data-factory-pattern

A Python QA Automation lab demonstrating how the **Factory Pattern** simplifies test data generation for API, RBAC, and multi-tenant scenarios.

Built with FastAPI, pytest, factory_boy, SQLAlchemy, and SQLite.

## Why this project exists

Test suites become hard to maintain when data is created manually inside each test. This project shows a cleaner approach: factories centralize object creation, fixtures prepare isolated execution environments, and tests stay focused on behavior rather than setup.

## Technologies

| Area | Technology |
|---|---|
| Language | Python |
| API framework | FastAPI |
| Testing framework | pytest |
| Test data generation | factory_boy |
| Fake data | Faker |
| ORM | SQLAlchemy |
| Database | SQLite (in-memory for tests) |
| API client for tests | FastAPI TestClient / httpx2 |
| Test reports | pytest-html |

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Commands

```bash
# Run tests (generates report.html)
pytest -v

# Run the API locally
uvicorn app.main:app --reload
```

## Project structure

```
├── app/
│   ├── database.py       # SQLAlchemy engine, session, get_db dependency
│   ├── models.py         # Tenant, Role, User, Project, EPD
│   ├── schemas.py        # Pydantic request/response schemas
│   └── main.py           # FastAPI app and endpoints
├── tests/
│   ├── conftest.py       # db_session, client, admin_user, viewer_user fixtures
│   ├── factories.py      # factory_boy factories for all domain entities
│   ├── helpers.py        # auth_headers() utility
│   ├── test_health.py
│   ├── test_projects.py  # RBAC and tenant isolation tests
│   ├── test_epds.py      # EPD edge case tests
│   └── test_factories.py # Factory behavior tests
├── requirements.txt
└── pytest.ini
```

## Domain model

A small multi-tenant SaaS platform with four core entities:

```
Tenant
├── Users  (role: admin | viewer)
├── Projects
└── EPDs   (Environmental Product Declaration, with a gwp float field)
```

## Key design concepts

### Factory Pattern

Factories live in `tests/factories.py` and centralize object creation. Tests declare what they need without repeating setup logic:

```python
tenant = TenantFactory()
admin = AdminUserFactory(tenant=tenant)
project = ProjectFactory(tenant=tenant)
outlier_epd = EPDFactory(tenant=tenant, gwp=999999)
```

Relationships are resolved automatically via `SubFactory`. Overrides are explicit and local to the test that needs them.

### pytest fixtures

Fixtures in `conftest.py` prepare the execution environment:

- `db_session` — in-memory SQLite, created and dropped per test
- `client` — FastAPI `TestClient` with the DB dependency overridden
- `admin_user` / `viewer_user` — pre-committed users ready for use

Factories generate entities. Fixtures prepare the context in which tests run.

### Test isolation

Each test gets a fresh in-memory SQLite database. No shared state, no cleanup scripts, no ordering dependencies.

### Authentication

Authentication is intentionally simple: tests pass a user ID via the `X-User-Id` header, resolved against the test database. The focus is on test data generation and authorization logic, not auth infrastructure.

### Multi-tenant isolation

Tenant boundaries are enforced at the query level. Every list endpoint filters by the authenticated user's `tenant_id`. Direct access by ID to another tenant's resource returns 404.

### RBAC

Two roles: `admin` and `viewer`. Mutation endpoints (`POST /projects`, `DELETE /projects/{id}`, `POST /epds`) require the admin role and return 403 otherwise.

## API endpoints

```
GET  /health
GET  /projects
GET  /projects/{project_id}
POST /projects
DELETE /projects/{project_id}
GET  /epds
POST /epds
```

## Test coverage

| File | What it covers |
|---|---|
| `test_health.py` | `/health` returns 200 |
| `test_projects.py` | Admin can create/delete, viewer blocked, tenant isolation |
| `test_epds.py` | Valid EPD, negative gwp rejected, outliers, duplicates, incomplete payload |
| `test_factories.py` | Relationships auto-generated, overrides work |
