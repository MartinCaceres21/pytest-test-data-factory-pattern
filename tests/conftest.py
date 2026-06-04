import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app
from tests import factories

logger = logging.getLogger(__name__)

FACTORY_CLASSES = (
    factories.RoleFactory,
    factories.AdminRoleFactory,
    factories.ViewerRoleFactory,
    factories.TenantFactory,
    factories.UserFactory,
    factories.AdminUserFactory,
    factories.ViewerUserFactory,
    factories.ProjectFactory,
    factories.EPDFactory,
)


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Test database created (in-memory SQLite)")

    session = TestingSessionLocal()
    for factory_class in FACTORY_CLASSES:
        factory_class._meta.sqlalchemy_session = session
    try:
        yield session
    finally:
        for factory_class in FACTORY_CLASSES:
            factory_class._meta.sqlalchemy_session = None
        session.close()
        Base.metadata.drop_all(bind=engine)
        logger.info("Test database torn down")


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    logger.info("FastAPI TestClient ready with isolated DB")
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db_session: Session):
    user = factories.AdminUserFactory()
    db_session.commit()
    logger.info(
        "Fixture admin_user: email=%s role=%s tenant_id=%d",
        user.email,
        user.role.name,
        user.tenant_id,
    )
    return user


@pytest.fixture()
def viewer_user(db_session: Session):
    user = factories.ViewerUserFactory()
    db_session.commit()
    logger.info(
        "Fixture viewer_user: email=%s role=%s tenant_id=%d",
        user.email,
        user.role.name,
        user.tenant_id,
    )
    return user
