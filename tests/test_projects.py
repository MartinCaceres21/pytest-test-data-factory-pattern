from tests.factories import AdminUserFactory, ProjectFactory, ViewerUserFactory
from tests.helpers import auth_headers


def test_admin_can_create_project(client, admin_user):
    response = client.post(
        "/projects",
        json={"name": "Solar Plant", "description": "Tenant project"},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Solar Plant"
    assert response.json()["tenant_id"] == admin_user.tenant_id


def test_project_list_only_returns_current_tenant_projects(client, db_session):
    user = AdminUserFactory()
    own_project = ProjectFactory(tenant=user.tenant, name="Visible")
    other_project = ProjectFactory(name="Hidden")
    db_session.commit()

    response = client.get("/projects", headers=auth_headers(user))

    assert response.status_code == 200
    project_ids = {project["id"] for project in response.json()}
    assert own_project.id in project_ids
    assert other_project.id not in project_ids


def test_user_cannot_access_other_tenant_project(client, db_session):
    user = AdminUserFactory()
    other_project = ProjectFactory()
    db_session.commit()

    response = client.get(
        f"/projects/{other_project.id}",
        headers=auth_headers(user),
    )

    assert response.status_code == 404


def test_admin_can_delete_project(client, db_session):
    admin = AdminUserFactory()
    project = ProjectFactory(tenant=admin.tenant)
    db_session.commit()

    response = client.delete(
        f"/projects/{project.id}",
        headers=auth_headers(admin),
    )

    assert response.status_code == 204
    assert client.get(f"/projects/{project.id}", headers=auth_headers(admin)).status_code == 404


def test_viewer_cannot_delete_project(client, db_session):
    viewer = ViewerUserFactory()
    project = ProjectFactory(tenant=viewer.tenant)
    db_session.commit()

    response = client.delete(
        f"/projects/{project.id}",
        headers=auth_headers(viewer),
    )

    assert response.status_code == 403
