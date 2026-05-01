from fastapi import APIRouter
from pigenus.api.routes import health, auth, workers, jobs, memory, admin

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(workers.router)
api_router.include_router(jobs.router)
api_router.include_router(memory.router)
api_router.include_router(admin.router)
