from fastapi import APIRouter

from api.v1 import auth, events, friends, location, users, vendors


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(events.router)
api_router.include_router(users.router)
api_router.include_router(friends.router)
api_router.include_router(location.router)
api_router.include_router(vendors.router)
