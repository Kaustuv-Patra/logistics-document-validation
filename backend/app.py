from fastapi import FastAPI
from sqlalchemy import text

from db import engine

app = FastAPI(title="Logistics Document Validation API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db/health")
def db_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar_one()
    return {"db": "ok", "result": value}
