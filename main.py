from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI ()
templates = Jinja2Templates(directory='templates')

@app.get('/', response_class=HTMLResponse)
async def index(request: Request): 
    return templates.TemplateResponse(
    request=request,
    name='index.html'
    )

@app.get('/login', response_class=HTMLResponse)
async def index(request: Request): 
    return templates.TemplateResponse(
    request=request,
    name='login.html'
    )


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, reload=True)
