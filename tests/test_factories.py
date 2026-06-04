from tests.factories import AdminUserFactory, EPDFactory, ProjectFactory, TenantFactory


def test_factories_create_valid_related_objects(db_session):
    tenant = TenantFactory()
    admin = AdminUserFactory(tenant=tenant)
    project = ProjectFactory(tenant=tenant)
    epd = EPDFactory(tenant=tenant)

    db_session.commit()

    assert admin.role.name == "admin"
    assert admin.tenant_id == tenant.id
    assert project.tenant_id == tenant.id
    assert epd.tenant_id == tenant.id


def test_factory_overrides_are_supported(db_session):
    epd = EPDFactory(gwp=999999)

    db_session.commit()

    assert epd.gwp == 999999
