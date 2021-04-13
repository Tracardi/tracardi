import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from .routers import console, event, rule, source, profile, segment, auth, session, action


_local_dir = os.path.dirname(__file__)

application = FastAPI()
application.mount("/app",
                  StaticFiles(
                      html=True,
                      directory=os.path.join(_local_dir, "frontend")),
                  name="frontend"),

application.include_router(console.router)
application.include_router(event.router)
application.include_router(rule.router)
application.include_router(source.router)
application.include_router(profile.router)
application.include_router(segment.router)
application.include_router(session.router)
application.include_router(auth.router)
application.include_router(action.router)

application.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
