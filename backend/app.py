from fastapi import FastAPI

app = FastAPI(title="Logistics Document Validation API")


@app.get("/health")
def health_check():
    return {"status": "ok"}