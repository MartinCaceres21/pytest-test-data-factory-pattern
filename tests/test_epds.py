from tests.factories import AdminUserFactory, EPDFactory
from tests.helpers import auth_headers


def test_admin_can_create_valid_epd(client, admin_user):
    response = client.post(
        "/epds",
        json={
            "name": "Concrete EPD",
            "product_category": "concrete",
            "gwp": 123.45,
        },
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 201
    assert response.json()["gwp"] == 123.45
    assert response.json()["tenant_id"] == admin_user.tenant_id


def test_epd_list_only_returns_current_tenant_epds(client, db_session):
    user = AdminUserFactory()
    own_epd = EPDFactory(tenant=user.tenant)
    other_epd = EPDFactory()
    db_session.commit()

    response = client.get("/epds", headers=auth_headers(user))

    assert response.status_code == 200
    epd_ids = {epd["id"] for epd in response.json()}
    assert own_epd.id in epd_ids
    assert other_epd.id not in epd_ids


def test_negative_gwp_is_rejected(client, admin_user):
    response = client.post(
        "/epds",
        json={
            "name": "Invalid EPD",
            "product_category": "steel",
            "gwp": -10,
        },
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 422


def test_outlier_positive_gwp_is_allowed(client, admin_user):
    response = client.post(
        "/epds",
        json={
            "name": "Outlier EPD",
            "product_category": "cement",
            "gwp": 999999,
        },
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 201
    assert response.json()["gwp"] == 999999


def test_duplicate_epd_names_are_easy_to_generate(db_session):
    user = AdminUserFactory()
    first_epd = EPDFactory(tenant=user.tenant, name="Duplicate EPD")
    second_epd = EPDFactory(tenant=user.tenant, name="Duplicate EPD")

    db_session.commit()

    assert first_epd.id != second_epd.id
    assert first_epd.name == second_epd.name


def test_missing_required_epd_fields_are_rejected(client, admin_user):
    response = client.post(
        "/epds",
        json={"name": "Incomplete EPD"},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 422
