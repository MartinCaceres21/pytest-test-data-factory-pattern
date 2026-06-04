from app.models import User


def auth_headers(user: User) -> dict[str, str]:
    return {"X-User-Id": str(user.id)}
