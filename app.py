from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException

from pathlib import Path
from static.utils import generate_faq, get_all_texts
import magic
import fitz
import json

from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
assert key, "OPENAI_API_KEY is missing from .env or not loaded"

from openai import OpenAI
client = OpenAI(api_key=key)



UPLOAD_DIR = Path('uploads')
ALLOWED_MIME = {'application/pdf','text/plain'}
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    files = [p.name for p in UPLOAD_DIR.iterdir()]
    return templates.TemplateResponse('index.html', {'request': request, 'files': files})

@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    detector = magic.Magic(mime=True)
    if detector.from_buffer(await file.read(2048)) not in ALLOWED_MIME:
        return RedirectResponse('/', status_code=415)
    await file.seek(0)
    dest = UPLOAD_DIR / file.filename
    with dest.open('wb') as out:
        out.write(await file.read())

    # generate updated FAQ
    try:
        text = get_all_texts(UPLOAD_DIR)
        faq = json.loads(generate_faq(client, text))
        with open("faq.json", "w", encoding="utf-8") as f:
            json.dump(faq, f, indent=2, ensure_ascii=False)
        return JSONResponse({"status": "ok"}, status_code=200)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    path = UPLOAD_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    path.unlink()
    return {"status": "deleted"}

@app.get('/files')
async def list_files():
    return [f.name for f in UPLOAD_DIR.iterdir()]

@app.get("/faq.json")
async def serve_faq():
    return FileResponse("faq.json", media_type="application/json")



if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", reload=True, port=8000)
