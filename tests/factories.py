import factory

from app.models import EPD, Project, Role, Tenant, User


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "flush"


class RoleFactory(BaseFactory):
    class Meta:
        model = Role

    name = "viewer"


class AdminRoleFactory(RoleFactory):
    name = "admin"


class ViewerRoleFactory(RoleFactory):
    name = "viewer"


class TenantFactory(BaseFactory):
    class Meta:
        model = Tenant

    name = factory.Sequence(lambda n: f"Tenant {n}")


class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    role = factory.SubFactory(ViewerRoleFactory)
    tenant = factory.SubFactory(TenantFactory)


class AdminUserFactory(UserFactory):
    role = factory.SubFactory(AdminRoleFactory)


class ViewerUserFactory(UserFactory):
    role = factory.SubFactory(ViewerRoleFactory)


class ProjectFactory(BaseFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Faker("sentence")
    tenant = factory.SubFactory(TenantFactory)


class EPDFactory(BaseFactory):
    class Meta:
        model = EPD

    name = factory.Sequence(lambda n: f"EPD {n}")
    product_category = factory.Faker("word")
    gwp = factory.Faker("pyfloat", min_value=0, max_value=1000, right_digits=2)
    tenant = factory.SubFactory(TenantFactory)
