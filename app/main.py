# TODO Start point
from fastapi import FastAPI
from app.api.v1.routes import router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CSV Service")
app.include_router(router)
