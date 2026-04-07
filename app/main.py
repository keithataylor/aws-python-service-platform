from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from app.api.routes import router, api_v1_router
from app.core.config import SERVICE_NAME
from app.core.policy_loader import load_agent_policy


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent_policy = load_agent_policy()
    yield
    
app = FastAPI(title=SERVICE_NAME, lifespan=lifespan)

app.state.agent_policy = load_agent_policy()

app.include_router(router)  
app.include_router(api_v1_router)

  
