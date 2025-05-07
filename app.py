from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException

from pathlib import Path
from static.utils import generate_faq, get_all_texts
import magic
import json
from typing import List

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
async def upload(files: List[UploadFile] = File(...)):
    for file in files:
        detector = magic.Magic(mime=True)
        if detector.from_buffer(await file.read(2048)) not in ALLOWED_MIME:
            continue  # skip invalid files
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

@app.get('/files/{filename}')
async def files(filename: str):
    path = UPLOAD_DIR / filename
    return FileResponse(path, filename=filename)


@app.get("/faq.json")
async def serve_faq():
    # Ensure that the file is updated and not cached
    if not Path("faq.json").exists():
        return Response("[]", media_type="application/json")
    
    content = Path("faq.json").read_text(encoding="utf-8")
    return Response(content, media_type="application/json", headers={
        "Cache-Control": "no-store"
    })



if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", reload=True, port=8000)
