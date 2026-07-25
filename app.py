# app.py

from fastapi import FastAPI
from routes.ingestion_routes import router as ingestion_router
from routes.update_route import router as update_router
from routes.retrieval_route import router as retrieval_router
from routes.delete_route import router as delete_router
from routes.faq_route import router as faq_router

app = FastAPI(title="Context Retrieval Service")

# Register the ingestion route with the main application
app.include_router(ingestion_router)
# Register the update route with the main application
app.include_router(update_router)
# Register the retrieval route with the main application
app.include_router(retrieval_router)
# Register the delete route with the main application
app.include_router(delete_router)
# Register the update route with the main application
app.include_router(faq_router)

@app.get("/health")
def health_check():
    """
    Basic health check endpoint to verify the API is running.
    """
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Allows running the file directly for testing
    uvicorn.run(app, host="0.0.0.0", port=8000)
