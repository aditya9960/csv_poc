# TODO Start point
from fastapi import FastAPI
from app.api.v1.routes import router
from app.core.database import Base, engine
from app.core.logging_middleware import RequestLoggingMiddleware
from app.core.config import settings

# just for test cases running so i can use sqllite db instead of postgres
if settings.running_tests == "0":
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="CSV Service")
app.add_middleware(RequestLoggingMiddleware)
app.include_router(router)
