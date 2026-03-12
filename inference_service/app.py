from fastapi import FastAPI

app = FastAPI(title="Edge AI Inference Service")


@app.get("/health")
def health_check():
    """Return service health status."""
    return {"status": "healthy", "service": "edge-ai-inference"}
