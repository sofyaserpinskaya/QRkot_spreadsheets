from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate


USER_DELETE_ERROR = "Удаление пользователей запрещено!"


router = APIRouter()


router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix='/users',
    tags=['users'],
)


for route in router.routes:
    if route.path == '/users/{id}' and 'DELETE' in route.methods:
        router.routes.remove(route)


@router.delete(
    '/users/{id}',
    tags=['users'],
    deprecated=True
)
def delete_user(id: str):
    """Не используйте удаление, деактивируйте пользователей."""
    raise HTTPException(
        status_code=HTTPStatus.METHOD_NOT_ALLOWED,
        detail=USER_DELETE_ERROR
    )
