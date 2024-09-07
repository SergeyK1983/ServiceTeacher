from fastapi import FastAPI

from core.database import Base, engine
from app_service.views import router as serv_router
from app_account.views import router as account_router


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(serv_router, prefix="/proba_path")
app.include_router(account_router, prefix="/account")

