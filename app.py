from http import HTTPStatus

from fastapi import FastAPI

from routes import auth, users
from schemas.utils import Message

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
async def root():
    return {"message": "Olá Mundo!"}
