from fastapi import APIRouter

from app.routers.user_router import router as user_router
from app.routers.auth_router import router as auth_router
from app.routers.data_router import router as data_router
from app.routers.user_skill_router import router as user_skill_router

router = APIRouter()
router.include_router(user_router)
router.include_router(auth_router)
router.include_router(data_router)
router.include_router(user_skill_router)
