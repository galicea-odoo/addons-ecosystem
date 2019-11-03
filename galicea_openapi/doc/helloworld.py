# pip install fastapi
# pip install email-validator
# pip install pydantic
# pip install starlette
# pip install uvicorn

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

def run_server():
    uvicorn.run(app)

if __name__ == '__main__':
    uvicorn.run(app, #'server:app', 
                host='127.0.0.1', port=8000, reload=True)