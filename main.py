from fastapi import FastAPI

# Start with the simplest possible FastAPI app
app = FastAPI(title="Todo API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Hello from Vercel! 🚀", "status": "working"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Test endpoint without database
@app.get("/test")
def test():
    return {
        "message": "Test endpoint working",
        "framework": "FastAPI",
        "platform": "Vercel"
    }