from collections.abc import Sequence
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import create_db_and_tables, get_db
from app.models import EPD, Project, Role, User
from app.schemas import EPDCreate, EPDRead, HealthResponse, ProjectCreate, ProjectRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="pytest-test-data-factory-pattern", lifespan=lifespan)


def get_current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> User:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    user = db.get(User, x_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
        )
    return user


def require_admin(user: User) -> None:
    if user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )


@app.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/projects", response_model=list[ProjectRead])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Sequence[Project]:
    statement = select(Project).where(Project.tenant_id == current_user.tenant_id)
    return db.scalars(statement).all()


@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@app.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    require_admin(current_user)
    project = Project(
        name=payload.name,
        description=payload.description,
        tenant_id=current_user.tenant_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    require_admin(current_user)
    project = db.get(Project, project_id)
    if project is None or project.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    db.delete(project)
    db.commit()


@app.get("/epds", response_model=list[EPDRead])
def list_epds(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Sequence[EPD]:
    statement = select(EPD).where(EPD.tenant_id == current_user.tenant_id)
    return db.scalars(statement).all()


@app.post("/epds", response_model=EPDRead, status_code=status.HTTP_201_CREATED)
def create_epd(
    payload: EPDCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EPD:
    require_admin(current_user)
    epd = EPD(
        name=payload.name,
        product_category=payload.product_category,
        gwp=payload.gwp,
        tenant_id=current_user.tenant_id,
    )
    db.add(epd)
    db.commit()
    db.refresh(epd)
    return epd
