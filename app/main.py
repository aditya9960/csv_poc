# TODO Start point
from fastapi import FastAPI
from app.api.v1.routes import router


app = FastAPI(title="CSV Service")
app.include_router(router)
