from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app_service.views import router as serv_router
from app_account.views import router as account_router

app = FastAPI()

# app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", ])
app.add_middleware(GZipMiddleware, minimum_size=2048, compresslevel=5)
# app.add_middleware(AuthenticationMiddleware, backend=)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],  # Specify allowed methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(serv_router, prefix="/proba_path")
app.include_router(account_router, prefix="/account")

