from fastapi import FastAPI
from app.db import engine
from app import models
from app.routers import items

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(items.router)
