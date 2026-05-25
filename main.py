from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from fastapi.middleware.cors import CORSMiddleware

from app.routers import posts, users
from app.db.init_db import init_db

async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    #allow_credentials=True,
    #allow_methods=["*"],
    #allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(posts.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/scalar', include_in_schema=False)
def get_docs_scalar():
    return get_scalar_api_reference(
        openapi_url= app.openapi_url,
        title="Scalar API"
    )