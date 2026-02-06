from fastapi import FastAPI

app = FastAPI(title="Traffic Predictor API")

@app.get("/health")
def health():
    return {"status": "ok"}
