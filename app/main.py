from fastapi import FastAPI

from api.endpoints.links import router as links_router
from api.endpoints.user import router as user_router
from middleware.request_logger import log_request

from db.session import Base, engine
# #Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener Service")
    
app.middleware("http")(log_request)

app.include_router(links_router, prefix="/api/links", tags=["links"])
app.include_router(user_router, prefix="/api/user", tags=["user"])

@app.get("/")
def root():
    return {"message": "Welcome to URL Shortener Service"}
