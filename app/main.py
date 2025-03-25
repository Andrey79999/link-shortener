from fastapi import FastAPI
import sys
import os
sys.path.append(os.path.abspath("app"))
from api.endpoints.links import router
from middleware.request_logger import log_request

# from db.session import Base, engine
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener Service")
    
app.middleware("http")(log_request)

app.include_router(router, prefix="/api/links", tags=["links"])

@app.get("/")
def root():
    return {"message": "Welcome to URL Shortener Service"}
