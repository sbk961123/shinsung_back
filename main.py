# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from router import tabber
app = FastAPI()
origins = ["*"]

# MiddleWare 설정. CORS Error 방지.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tabber.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
