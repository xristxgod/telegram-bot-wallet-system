from fastapi import APIRouter
from src.schemas import BodyRegUser, BodyBalance, ResponseUserMethod

from src.worker import WorkerUser
from config import logger

router = APIRouter(prefix="/user")

@router.post(
    "/reg", description="Sends a message to the notification bot that a new user has appeared",
    response_model=ResponseUserMethod, tags=["USER"]
)
async def reg_user(body: BodyRegUser):
    try:
        return ResponseUserMethod(
            message=(await WorkerUser.reg_user_text(body=body))
        )
    except Exception as error:
        logger.error(f"ERROR: {error}")
        return ResponseUserMethod(message=False)

@router.post(
    "/add", description="Sends a message to the notification bot about what happened to the deposit balance!",
    response_model=ResponseUserMethod, tags=["USER"]
)
async def add_balance(body: BodyBalance):
    pass

@router.post(
    "/dec", description="Sends a message to the notifier bot about what happened the balance debit!",
    response_model=ResponseUserMethod, tags=["USER"]
)
async def add_balance(body: BodyBalance):
    pass