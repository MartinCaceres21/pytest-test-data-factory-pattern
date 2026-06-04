# pytest-test-data-factory-pattern

A small Python QA Automation project focused on **pytest**, **factory_boy**, **FastAPI**, **API testing**, **RBAC**, and **multi-tenant test data generation**.

The goal is to demonstrate how the **Factory Pattern** can be used to create realistic, reusable, and isolated test data for backend API and integration tests.

## Why this project exists

Many automation suites become hard to maintain because test data is created manually inside each test. This creates duplication, hidden dependencies, and fragile scenarios.

This project explores a cleaner approach:

- Use factories to generate test data.
- Use pytest fixtures to prepare reusable test context.
- Use API tests to validate RBAC and tenant isolation.
- Use a small FastAPI app as a realistic testing target.
- Use SQLite as a lightweight test database.

## Target scenario

The sample system simulates a small multi-tenant SaaS platform.

Main entities:

- `Tenant`
- `User`
- `Role`
- `Project`
- `EPD`

The tests will validate scenarios such as:

- Users can access data from their own tenant.
- Users cannot access projects from another tenant.
- Viewers cannot delete projects.
- Admins can create and manage tenant resources.
- EPD data can be generated with normal values, invalid values, and outliers.
- API responses respect expected contracts.

## Technologies

| Area | Technology |
|---|---|
| Language | Python |
| API framework | FastAPI |
| Testing framework | pytest |
| Test data generation | factory_boy |
| Fake data | Faker |
| ORM | SQLAlchemy |
| Database | SQLite |
| API client for tests | FastAPI TestClient / httpx |
| Optional linting | Ruff |
| Optional formatting | Black |

## Project phases

### Phase 1 — Project setup

Create the basic Python project structure.

Expected files:

```text
pytest-test-data-factory-pattern/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_health.py
├── requirements.txt
├── pytest.ini
└── README.md
```

Checkpoint:

```bash
pytest
```

Expected result:

```text
1 passed
```

### Phase 2 — FastAPI minimal app

Add a small API with a health endpoint.

Endpoint:

```http
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

Checkpoint:

```bash
pytest tests/test_health.py
```

### Phase 3 — Domain models

Create SQLAlchemy models for:

- Tenant
- User
- Project
- EPD

Relationships:

```text
Tenant
├── Users
├── Projects
└── EPDs
```

Checkpoint:

- Tables can be created in SQLite.
- Test database can be reset between tests.

### Phase 4 — pytest fixtures

Create reusable fixtures for:

- test database session
- FastAPI test client
- authenticated user context

Example:

```python
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
```

Checkpoint:

- Tests do not depend on external services.
- Each test starts with isolated data.

### Phase 5 — factory_boy factories

Create factories for:

- TenantFactory
- UserFactory
- AdminUserFactory
- ViewerUserFactory
- ProjectFactory
- EPDFactory

Example usage:

```python
tenant = TenantFactory()
admin = AdminUserFactory(tenant=tenant)
project = ProjectFactory(tenant=tenant)
```

Checkpoint:

- Factories create valid domain objects.
- Relationships are generated automatically.
- Overrides are possible when needed.

### Phase 6 — API endpoints

Implement simple endpoints:

```http
GET /projects
GET /projects/{project_id}
POST /projects
DELETE /projects/{project_id}
GET /epds
POST /epds
```

Checkpoint:

- Endpoints work through tests.
- No manual database setup is needed inside test bodies.

### Phase 7 — RBAC tests

Add tests for permissions.

Examples:

```python
def test_admin_can_delete_project():
    pass


def test_viewer_cannot_delete_project():
    pass
```

Checkpoint:

- Admin actions are allowed.
- Viewer actions are blocked.
- Permission errors are explicit.

### Phase 8 — Multi-tenant isolation tests

Add cross-tenant scenarios.

Examples:

```python
def test_user_cannot_access_other_tenant_project():
    pass


def test_project_list_only_returns_current_tenant_projects():
    pass
```

Checkpoint:

- Tenant A cannot access Tenant B data.
- List endpoints filter by tenant.
- Direct access by ID is blocked.

### Phase 9 — EPD and edge case data

Use factories to generate:

- valid EPDs
- duplicate EPDs
- missing fields
- outlier GWP values
- invalid negative values

Example:

```python
outlier_epd = EPDFactory(gwp=999999)
invalid_epd = EPDFactory(gwp=-10)
```

Checkpoint:

- Edge cases are easy to create.
- Test data remains readable.

### Phase 10 — Documentation and final polish

Add documentation explaining:

- Factory Pattern
- pytest fixtures
- factory_boy
- RBAC testing
- multi-tenant testing
- test isolation

Checkpoint:

- A reader can clone the repo and run tests quickly.
- The README explains why the design matters.
- The project can be discussed in a technical interview.

## Core design ideas

### Factory Pattern

Factories centralize object creation.

Instead of repeating test data setup in every test, tests request the data they need:

```python
user = UserFactory(role="admin")
project = ProjectFactory(tenant=user.tenant)
```

This makes tests shorter, more readable, and easier to maintain.

### pytest fixtures

Fixtures prepare reusable context:

- app client
- database session
- authentication headers
- default tenant
- default users

Factories generate entities. Fixtures prepare the execution environment.

### Test isolation

Each test should be independent.

A test should not depend on data created by another test. This project will use a test database setup that can be recreated or rolled back between tests.

### Multi-tenant safety

Multi-tenant systems must protect customer boundaries.

The most important validations are negative scenarios:

- A user cannot list another tenant's projects.
- A user cannot access another tenant's project by ID.
- A user cannot modify another tenant's EPD.
- A response must not leak metadata from another tenant.

## Definition of done

The project is considered complete when:

- The FastAPI app runs locally.
- pytest executes all tests successfully.
- factory_boy is used for test data generation.
- RBAC scenarios are covered.
- Multi-tenant isolation scenarios are covered.
- EPD edge cases are covered.
- The README explains the architecture clearly.

## Setup guide

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest -v
```

Run the API locally:

```bash
uvicorn app.main:app --reload
```

## Interview positioning

A concise way to explain this project:

> I built a small Python API testing lab using FastAPI, pytest, and factory_boy. The goal was to demonstrate how the Factory Pattern helps generate reusable and isolated test data for RBAC and multi-tenant scenarios. The tests validate tenant isolation, role-based permissions, API behavior, and edge cases such as invalid or outlier EPD data.

## Current implementation

This repository now includes a compact working version of the planned testing lab:

- FastAPI app with `/health`, `/projects`, and `/epds` endpoints.
- SQLAlchemy models for tenants, users, projects, and EPDs.
- Lightweight test authentication using the `X-User-Id` header.
- pytest fixtures for isolated in-memory SQLite sessions and API clients.
- factory_boy factories for tenants, users, projects, and EPD data.
- Tests for health checks, RBAC, tenant isolation, factories, and EPD edge cases.
- GitHub Actions CI workflow that installs dependencies and runs `pytest -v`.

## Implementation notes

Authentication is intentionally simple because this project focuses on test data generation, authorization scenarios, and tenant boundaries. Tests create users with factories, commit them to the isolated test database, and pass their ID through `X-User-Id`.

Each test uses an in-memory SQLite database created from the SQLAlchemy metadata. This keeps test data independent and avoids external services.

Factories live under `tests/` because they are testing tools, not production code. They centralize object creation and make scenario setup explicit:

```python
tenant = TenantFactory()
admin = AdminUserFactory(tenant=tenant)
project = ProjectFactory(tenant=tenant)
outlier_epd = EPDFactory(tenant=tenant, gwp=999999)
```

## Roadmap checklist

- [x] Create project structure
- [x] Add FastAPI health endpoint
- [x] Add pytest configuration
- [x] Add SQLAlchemy models
- [x] Add test database fixture
- [x] Add FastAPI test client fixture
- [x] Add factory_boy factories
- [x] Add project endpoints
- [x] Add EPD endpoints
- [x] Add RBAC tests
- [x] Add tenant isolation tests
- [x] Add EPD edge case tests
- [x] Add documentation examples
- [x] Add GitHub Actions CI
