from fastapi import APIRouter, Depends, Request

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.database.models import User
from src.schemas import UserModel
from src.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["contacts"])

limiter = Limiter(key_func=get_remote_address)

from pprint import pprint


@router.get("/me", response_model=UserModel)
@limiter.limit("2/minute")
async def get_current_user_info(
    request: Request,
    user: User = Depends(get_current_user),
):
    pprint(dict(request.headers))
    return user
