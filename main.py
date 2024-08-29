from fastapi import FastAPI

from app_service.models.database import Base, engine
from app_service.views import router as serv_router


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(serv_router, prefix="/proba_path")

