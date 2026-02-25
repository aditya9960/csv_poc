# TODO Start point
from fastapi import FastAPI
from app.api.v1.routes import router
from app.core.database import Base, engine
from app.core.logging_middleware import RequestLoggingMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="CSV Service")
app.add_middleware(RequestLoggingMiddleware)
app.include_router(router)
