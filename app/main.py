from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import os
import subprocess
from pathlib import Path

app = FastAPI(title="WebP Image Editor")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Ensure upload directory exists
UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Handle image upload and conversion to WebP."""
    try:
        # Save original file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Convert to WebP using cwebp
        output_path = UPLOAD_DIR / f"{file_path.stem}.webp"
        cwebp_path = "libwebp-1.5.0-linux-aarch64/bin/cwebp"
        
        result = subprocess.run(
            [cwebp_path, str(file_path), "-o", str(output_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return JSONResponse({
                "success": True,
                "message": "Image converted successfully",
                "webp_path": f"/static/uploads/{output_path.name}"
            })
        else:
            return JSONResponse({
                "success": False,
                "message": f"Conversion failed: {result.stderr}"
            }, status_code=400)
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
