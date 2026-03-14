from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from prompt import prompt

app = FastAPI()
templates = Jinja2Templates(directory="static")

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/number", response_class=HTMLResponse)
async def submit_form(request: Request, name: str = Form(...)):
    ratio, answer, g_name = prompt(name)
    return templates.TemplateResponse("number.html", {"request": request, "ratio": ratio, "answer": answer,"g_name":g_name})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)