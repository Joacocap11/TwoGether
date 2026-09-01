from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .db import Base, engine
from .routers import auth,users,places,content,dashboard,media
app=FastAPI(title='TwoGether API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
settings.upload_path.mkdir(parents=True,exist_ok=True)
app.mount('/uploads',StaticFiles(directory=str(settings.upload_path)),name='uploads')
app.include_router(auth.router,prefix='/api/v1'); app.include_router(users.router,prefix='/api/v1'); app.include_router(places.router,prefix='/api/v1'); app.include_router(content.router,prefix='/api/v1'); app.include_router(dashboard.router,prefix='/api/v1'); app.include_router(media.router,prefix='/api/v1')
@app.get('/health')
def health(): return {'status':'ok'}
